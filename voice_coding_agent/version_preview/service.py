"""Backend operations for the versioned UI preview milestone.

Git remains the source of truth. Runtime-only state, preview metadata, and
materialised snapshots live under ``.runtime/version_preview`` and are never
committed with a generated project.
"""

from __future__ import annotations

import io
import json
import os
import re
import shutil
import socket
import subprocess
import tarfile
import time
import urllib.request
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


DEFAULT_CONTENT_DIR = "voice_coding_agent/ai_arena"
DEFAULT_IMAGE = "codewhisper-static-preview:v2"


class VersionPreviewError(RuntimeError):
    """An expected error that is safe to show to the API caller."""


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe_branch_fragment(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9._/-]+", "-", value.strip()).strip("-./")
    return cleaned or "version"


def _safe_directory_name(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "-", value).strip("-") or "workspace"


class VersionPreviewService:
    """Own Git, worktree, metadata, and Docker preview operations."""

    def __init__(
        self,
        repo_root: Optional[Path] = None,
        content_dir: Optional[str] = None,
        project_id: Optional[str] = None,
    ) -> None:
        default_root = Path(__file__).resolve().parents[2]
        self.repo_root = Path(
            repo_root or os.getenv("VERSION_PREVIEW_REPO_ROOT", default_root)
        ).expanduser().resolve()
        self.content_dir = (content_dir or os.getenv(
            "VERSION_PREVIEW_CONTENT_DIR", DEFAULT_CONTENT_DIR
        )).strip("/")
        self.project_id = project_id or os.getenv("VERSION_PREVIEW_PROJECT_ID", "codewhisper")
        self.runtime_root = self.repo_root / ".runtime" / "version_preview"
        self.snapshots_root = self.runtime_root / "snapshots"
        self.worktrees_root = self.runtime_root / "worktrees"
        self.previews_path = self.runtime_root / "previews.json"
        self.active_path = self.runtime_root / "active_workspace.json"
        self.events_path = self.runtime_root / "events.jsonl"

    def _ensure_runtime(self) -> None:
        self.runtime_root.mkdir(parents=True, exist_ok=True)
        self.snapshots_root.mkdir(parents=True, exist_ok=True)
        self.worktrees_root.mkdir(parents=True, exist_ok=True)

    def _git(
        self,
        args: List[str],
        *,
        cwd: Optional[Path] = None,
        check: bool = True,
        timeout: int = 45,
        text: bool = True,
    ) -> subprocess.CompletedProcess:
        target = Path(cwd or self.repo_root)
        result = subprocess.run(
            ["git", "-C", str(target), *args],
            capture_output=True,
            text=text,
            stdin=subprocess.DEVNULL,
            timeout=timeout,
            check=False,
        )
        if check and result.returncode:
            detail = (result.stderr or result.stdout or "Git command failed.").strip()
            raise VersionPreviewError(detail)
        return result

    def _docker(self, args: List[str], *, timeout: int = 180) -> subprocess.CompletedProcess:
        try:
            result = subprocess.run(
                ["docker", *args],
                capture_output=True,
                text=True,
                stdin=subprocess.DEVNULL,
                timeout=timeout,
                check=False,
            )
        except FileNotFoundError as error:
            raise VersionPreviewError("Docker is not installed or is not on PATH.") from error
        except subprocess.TimeoutExpired as error:
            raise VersionPreviewError("Docker operation timed out.") from error
        if result.returncode:
            detail = (result.stderr or result.stdout or "Docker command failed.").strip()
            raise VersionPreviewError(detail)
        return result

    def _read_json(self, path: Path, default: Any) -> Any:
        if not path.exists():
            return default
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return default

    def _write_json(self, path: Path, value: Any) -> None:
        self._ensure_runtime()
        temporary = path.with_suffix(path.suffix + ".tmp")
        temporary.write_text(json.dumps(value, indent=2, ensure_ascii=False), encoding="utf-8")
        temporary.replace(path)

    def _record_event(self, action: str, **details: Any) -> str:
        self._ensure_runtime()
        event = {
            "trace_id": uuid.uuid4().hex,
            "timestamp": _utc_now(),
            "project_id": self.project_id,
            "action": action,
            **details,
        }
        with self.events_path.open("a", encoding="utf-8") as event_file:
            event_file.write(json.dumps(event, ensure_ascii=False) + "\n")
        return event["trace_id"]

    def _assert_repository(self) -> None:
        self._git(["rev-parse", "--is-inside-work-tree"])

    def _validate_commit(self, commit_sha: str) -> str:
        if not re.fullmatch(r"[0-9a-fA-F]{4,64}", commit_sha or ""):
            raise VersionPreviewError("Commit SHA must contain only hexadecimal characters.")
        return self._git(["rev-parse", "--verify", f"{commit_sha}^{{commit}}"]).stdout.strip()

    def _workspace_root(self) -> Path:
        state = self._read_json(self.active_path, {})
        configured = state.get("worktree_path")
        if configured:
            path = Path(configured)
            if path.exists() and (path / ".git").exists():
                return path
        return self.repo_root

    def active_workspace(self) -> Dict[str, Any]:
        workspace = self._workspace_root()
        branch = self._git(["branch", "--show-current"], cwd=workspace).stdout.strip() or "detached"
        commit_sha = self._git(["rev-parse", "HEAD"], cwd=workspace).stdout.strip()
        content_path = workspace / self.content_dir
        return {
            "worktree_path": str(workspace),
            "branch": branch,
            "commit_sha": commit_sha,
            "content_path": str(content_path),
            "is_branch_workspace": workspace != self.repo_root,
        }

    def agent_working_directory(self, fallback: Optional[Path] = None) -> Path:
        """Return the active worktree's agent directory when a branch was selected."""
        workspace = self._workspace_root()
        candidate = workspace / "voice_coding_agent"
        if candidate.is_dir():
            return candidate
        return Path(fallback or Path.cwd())

    def _version_from_commit(self, commit_sha: str) -> Dict[str, Any]:
        raw = self._git(
            [
                "show",
                "-s",
                "--date=iso-strict",
                "--format=%H%x1f%P%x1f%D%x1f%aI%x1f%s%x1f%b",
                commit_sha,
            ]
        ).stdout.rstrip("\n")
        fields = raw.split("\x1f", 5)
        if len(fields) != 6:
            raise VersionPreviewError("Could not read commit metadata.")
        sha, parents, decorations, created_at, message, body = fields
        branches = []
        for part in decorations.split(","):
            value = part.strip().removeprefix("HEAD -> ")
            if value and not value.startswith("origin/") and not value.startswith("tag: "):
                branches.append(value)
        prompt = ""
        for line in body.splitlines():
            if line.startswith("CodeWhisper-Prompt:"):
                prompt = line.split(":", 1)[1].strip()
                break
        return {
            "commit_sha": sha,
            "short_sha": sha[:8],
            "parent_shas": [parent for parent in parents.split() if parent],
            "branches": branches,
            "created_at": created_at,
            "message": message,
            "prompt": prompt,
        }

    def _preview_records(self) -> Dict[str, Dict[str, Any]]:
        return self._read_json(self.previews_path, {})

    def _save_preview_records(self, previews: Dict[str, Dict[str, Any]]) -> None:
        self._write_json(self.previews_path, previews)

    def versions(self, limit: int = 50) -> List[Dict[str, Any]]:
        self._assert_repository()
        safe_limit = max(1, min(int(limit), 200))
        history = self._git(
            [
                "log",
                "--all",
                "--topo-order",
                "--date=iso-strict",
                f"--max-count={safe_limit}",
                "--format=%H",
            ]
        ).stdout.splitlines()
        previews = self._preview_records()
        result = []
        for sha in history:
            version = self._version_from_commit(sha)
            matching = [entry for entry in previews.values() if entry.get("commit_sha") == sha]
            if matching:
                version["latest_preview"] = max(matching, key=lambda item: item.get("created_at", ""))
            result.append(version)
        return result

    def project_info(self) -> Dict[str, Any]:
        self._assert_repository()
        active = self.active_workspace()
        content_path = Path(active["content_path"])
        files = []
        if content_path.is_dir():
            files = [
                str(item.relative_to(content_path))
                for item in sorted(content_path.rglob("*"))
                if item.is_file()
            ][:80]
        return {
            "project_id": self.project_id,
            "repo_root": str(self.repo_root),
            "content_dir": self.content_dir,
            "content_exists": content_path.is_dir(),
            "files": files,
            "active_workspace": active,
            "preview_image": os.getenv("VERSION_PREVIEW_IMAGE", DEFAULT_IMAGE),
        }

    def create_checkpoint(self, message: str, prompt: str = "") -> Dict[str, Any]:
        self._assert_repository()
        message = message.strip()
        if not message:
            raise VersionPreviewError("A checkpoint message is required.")
        workspace = self._workspace_root()
        content_path = workspace / self.content_dir
        if not content_path.exists():
            raise VersionPreviewError(
                f"Nothing to checkpoint yet: {self.content_dir} does not exist in the active workspace."
            )
        self._git(["add", "--", self.content_dir], cwd=workspace)
        staged = self._git(["diff", "--cached", "--quiet"], cwd=workspace, check=False)
        if staged.returncode == 0:
            version = self._version_from_commit(self._git(["rev-parse", "HEAD"], cwd=workspace).stdout.strip())
            version["already_clean"] = True
            return version
        if staged.returncode != 1:
            raise VersionPreviewError((staged.stderr or staged.stdout).strip())
        commit_message = message
        if prompt.strip():
            commit_message += "\n\nCodeWhisper-Prompt: " + prompt.strip()
        self._git(["commit", "-m", commit_message], cwd=workspace, timeout=90)
        commit_sha = self._git(["rev-parse", "HEAD"], cwd=workspace).stdout.strip()
        state = self._read_json(self.active_path, {})
        if state:
            state["commit_sha"] = commit_sha
            state["updated_at"] = _utc_now()
            self._write_json(self.active_path, state)
        trace_id = self._record_event(
            "create_checkpoint",
            commit_sha=commit_sha,
            branch=self._git(["branch", "--show-current"], cwd=workspace).stdout.strip(),
            prompt=prompt.strip(),
            status="success",
        )
        version = self._version_from_commit(commit_sha)
        version["trace_id"] = trace_id
        return version

    def branch_from_version(self, commit_sha: str, branch_name: Optional[str] = None) -> Dict[str, Any]:
        self._assert_repository()
        commit_sha = self._validate_commit(commit_sha)
        if branch_name:
            branch_name = _safe_branch_fragment(branch_name)
        else:
            branch_name = "design/{project}-{sha}-{stamp}".format(
                project=_safe_branch_fragment(self.project_id),
                sha=commit_sha[:8],
                stamp=datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S"),
            )
        valid_name = self._git(["check-ref-format", "--branch", branch_name], check=False)
        if valid_name.returncode:
            raise VersionPreviewError("Branch name is not valid.")
        exists = self._git(["show-ref", "--verify", "--quiet", f"refs/heads/{branch_name}"], check=False)
        if exists.returncode == 0:
            raise VersionPreviewError(f"Branch '{branch_name}' already exists. Choose a different name.")
        self._ensure_runtime()
        worktree_path = self.worktrees_root / _safe_directory_name(branch_name)
        if worktree_path.exists():
            raise VersionPreviewError(f"Workspace path already exists: {worktree_path}")
        self._git(["worktree", "add", "-b", branch_name, str(worktree_path), commit_sha], timeout=90)
        state = {
            "branch": branch_name,
            "commit_sha": commit_sha,
            "worktree_path": str(worktree_path),
            "created_at": _utc_now(),
        }
        self._write_json(self.active_path, state)
        trace_id = self._record_event(
            "branch_from_version",
            commit_sha=commit_sha,
            branch=branch_name,
            worktree_path=str(worktree_path),
            status="success",
        )
        return {**state, "content_path": str(worktree_path / self.content_dir), "trace_id": trace_id}

    def _snapshot_directory(self, commit_sha: str, preview_id: str) -> Path:
        target = self.snapshots_root / preview_id
        target.mkdir(parents=True, exist_ok=False)
        archive = self._git(["archive", "--format=tar", commit_sha, self.content_dir], text=False)
        with tarfile.open(fileobj=io.BytesIO(archive.stdout), mode="r:") as tar:
            for member in tar.getmembers():
                candidate = (target / member.name).resolve()
                if target.resolve() not in candidate.parents and candidate != target.resolve():
                    raise VersionPreviewError("Snapshot archive contained an unsafe path.")
            tar.extractall(target)
        content = target / self.content_dir
        if not content.is_dir():
            raise VersionPreviewError(f"Commit does not contain {self.content_dir}.")
        if not (content / "index.html").is_file():
            raise VersionPreviewError(
                "Static previews require an index.html file in " + self.content_dir + "."
            )
        return content

    def _container_is_running(self, container_id: str) -> bool:
        result = subprocess.run(
            ["docker", "inspect", "-f", "{{.State.Running}}", container_id],
            capture_output=True,
            text=True,
            stdin=subprocess.DEVNULL,
            check=False,
        )
        return result.returncode == 0 and result.stdout.strip().lower() == "true"

    def _ensure_preview_image(self, image: str) -> None:
        """Build the local non-root static runtime on first preview use."""
        if image != DEFAULT_IMAGE:
            return
        inspected = subprocess.run(
            ["docker", "image", "inspect", image],
            capture_output=True,
            text=True,
            stdin=subprocess.DEVNULL,
            check=False,
        )
        if inspected.returncode == 0:
            return
        docker_dir = Path(__file__).resolve().parent / "docker"
        self._docker(
            [
                "build",
                "--tag", image,
                "--file", str(docker_dir / "Dockerfile"),
                str(docker_dir),
            ],
            timeout=240,
        )

    def _reserve_host_port(self) -> int:
        """Ask the OS for an available localhost port before creating a container."""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
            probe.bind(("127.0.0.1", 0))
            return int(probe.getsockname()[1])

    def _wait_for_preview(self, url: str, container_id: str) -> None:
        deadline = time.monotonic() + 12
        last_error = "preview did not answer"
        while time.monotonic() < deadline:
            try:
                with urllib.request.urlopen(url, timeout=1.5) as response:
                    if 200 <= response.status < 500:
                        return
            except Exception as error:  # A container normally needs a short startup window.
                last_error = str(error)
            time.sleep(0.4)
        logs = self._docker(["logs", "--tail", "40", container_id], timeout=30).stdout.strip()
        raise VersionPreviewError(f"Preview health check failed: {last_error}.\n{logs}")

    def preview_version(self, commit_sha: str) -> Dict[str, Any]:
        self._assert_repository()
        commit_sha = self._validate_commit(commit_sha)
        previews = self._preview_records()
        for preview in previews.values():
            if preview.get("commit_sha") == commit_sha and self._container_is_running(preview.get("container_id", "")):
                preview["status"] = "ready"
                self._save_preview_records(previews)
                return preview

        self._ensure_runtime()
        preview_id = "preview_" + commit_sha[:8] + "_" + uuid.uuid4().hex[:6]
        image = os.getenv("VERSION_PREVIEW_IMAGE", DEFAULT_IMAGE)
        source_dir = None
        container_name = "codewhisper-" + _safe_directory_name(preview_id)
        host_port = self._reserve_host_port()
        try:
            source_dir = self._snapshot_directory(commit_sha, preview_id)
            self._ensure_preview_image(image)
            container_id = self._docker(
                [
                    "run", "--detach", "--name", container_name,
                    "--label", f"codewhisper.preview_id={preview_id}",
                    "--label", f"codewhisper.commit_sha={commit_sha}",
                    "--network", os.getenv("VERSION_PREVIEW_NETWORK", "bridge"),
                    "--read-only",
                    "--tmpfs", "/tmp:rw,noexec,nosuid,size=16m",
                    "--pids-limit", "128",
                    "--memory", "256m",
                    "--cpus", "0.50",
                    "--cap-drop", "ALL",
                    "--security-opt", "no-new-privileges",
                    "--user", "101:101",
                    "--publish", f"127.0.0.1:{host_port}:8080",
                    "--volume", f"{source_dir}:/usr/share/nginx/html:ro",
                    image,
                ],
                timeout=240,
            ).stdout.strip()
            preview_url = f"http://127.0.0.1:{host_port}/"
            self._wait_for_preview(preview_url, container_id)
        except Exception:
            if "container_id" in locals() and container_id:
                subprocess.run(["docker", "rm", "-f", container_id], capture_output=True, text=True)
            snapshot_root = source_dir.parent if source_dir else self.snapshots_root / preview_id
            shutil.rmtree(snapshot_root, ignore_errors=True)
            raise

        trace_id = self._record_event(
            "preview_version",
            commit_sha=commit_sha,
            preview_id=preview_id,
            container_id=container_id,
            preview_url=preview_url,
            status="ready",
        )
        preview = {
            "preview_id": preview_id,
            "commit_sha": commit_sha,
            "container_id": container_id,
            "container_name": container_name,
            "source_dir": str(source_dir),
            "preview_url": preview_url,
            "status": "ready",
            "created_at": _utc_now(),
            "trace_id": trace_id,
        }
        previews[preview_id] = preview
        self._save_preview_records(previews)
        return preview

    def preview(self, preview_id: str) -> Dict[str, Any]:
        preview = self._preview_records().get(preview_id)
        if not preview:
            raise VersionPreviewError("Preview was not found.")
        preview["status"] = "ready" if self._container_is_running(preview.get("container_id", "")) else "stopped"
        return preview

    def preview_logs(self, preview_id: str) -> Dict[str, Any]:
        preview = self.preview(preview_id)
        logs = self._docker(["logs", "--tail", "120", preview["container_id"]], timeout=30).stdout
        return {"preview_id": preview_id, "logs": logs}

    def stop_preview(self, preview_id: str) -> Dict[str, Any]:
        previews = self._preview_records()
        preview = previews.get(preview_id)
        if not preview:
            raise VersionPreviewError("Preview was not found.")
        subprocess.run(
            ["docker", "rm", "-f", preview.get("container_id", "")],
            capture_output=True,
            text=True,
            stdin=subprocess.DEVNULL,
            check=False,
        )
        snapshot_path = Path(preview.get("source_dir", "")).parent
        if snapshot_path.parent == self.snapshots_root:
            shutil.rmtree(snapshot_path, ignore_errors=True)
        preview["status"] = "stopped"
        preview["stopped_at"] = _utc_now()
        preview["trace_id"] = self._record_event(
            "stop_preview",
            commit_sha=preview.get("commit_sha"),
            preview_id=preview_id,
            container_id=preview.get("container_id"),
            status="stopped",
        )
        previews[preview_id] = preview
        self._save_preview_records(previews)
        return preview

    def recent_events(self, limit: int = 100) -> List[Dict[str, Any]]:
        if not self.events_path.exists():
            return []
        events = []
        for line in self.events_path.read_text(encoding="utf-8").splitlines()[-max(1, limit):]:
            try:
                events.append(json.loads(line))
            except ValueError:
                continue
        return list(reversed(events))


def active_agent_working_directory(fallback: Optional[Path] = None) -> Path:
    """Convenience accessor used by command-oriented agent tools."""
    return VersionPreviewService().agent_working_directory(fallback)
