const state = { project: null, versions: [], selected: null, preview: null };

const byId = (id) => document.getElementById(id);
const toast = byId("toast");

function showToast(message, isError = false) {
  toast.textContent = message;
  toast.classList.toggle("error", isError);
  toast.classList.remove("hidden");
  window.clearTimeout(showToast.timeout);
  showToast.timeout = window.setTimeout(() => toast.classList.add("hidden"), 5600);
}

async function api(path, options = {}) {
  const response = await fetch(path, {
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
    ...options,
  });
  const payload = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(payload.error || `Request failed (${response.status})`);
  return payload;
}

function formatDate(value) {
  if (!value) return "Unknown time";
  const date = new Date(value);
  const delta = Date.now() - date.getTime();
  if (delta < 60_000) return "just now";
  if (delta < 3_600_000) return `${Math.floor(delta / 60_000)} min ago`;
  if (delta < 86_400_000) return `${Math.floor(delta / 3_600_000)} hr ago`;
  return date.toLocaleDateString();
}

function escapeHtml(value) {
  return String(value || "").replace(/[&<>'"]/g, (char) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", "'": "&#039;", '"': "&quot;",
  }[char]));
}

function renderProject() {
  const project = state.project;
  byId("projectName").textContent = project.project_id;
  byId("projectBreadcrumb").textContent = project.project_id;
  byId("contentDir").textContent = project.content_dir;
  byId("activeBranch").textContent = project.active_workspace.branch;
  byId("workspaceStatus").textContent = project.active_workspace.is_branch_workspace
    ? `Editing ${project.active_workspace.branch}`
    : "Editing main workspace";
  const files = project.files.length ? project.files : ["No generated files yet"];
  byId("fileTree").innerHTML = files.map((file) => `<li title="${escapeHtml(file)}">${escapeHtml(file)}</li>`).join("");
}

function renderTimeline() {
  const timeline = byId("timeline");
  byId("timelineSubtitle").textContent = `${state.versions.length} Git versions · select one to preview or fork`;
  byId("timelineCount").textContent = state.versions.length ? `${state.versions.length} checkpoints` : "";
  if (!state.versions.length) {
    timeline.innerHTML = '<div class="muted">No commits found. Create your first checkpoint after generating a UI.</div>';
    return;
  }
  timeline.innerHTML = state.versions.map((version) => {
    const selected = state.selected && state.selected.commit_sha === version.commit_sha;
    const branches = (version.branches || []).map((branch) => `<span class="chip branch">${escapeHtml(branch)}</span>`).join("");
    const prompt = version.prompt ? `<p class="version-prompt">${escapeHtml(version.prompt)}</p>` : "";
    const preview = version.latest_preview && version.latest_preview.status === "ready"
      ? '<span class="chip">● preview ready</span>' : "";
    return `<article class="version-card ${selected ? "selected" : ""}" data-sha="${version.commit_sha}" tabindex="0">
      <div class="version-head"><div><h2 class="version-message">${escapeHtml(version.message || "Untitled checkpoint")}</h2><div class="version-meta"><span class="chip">${version.short_sha}</span>${branches}${preview}</div></div><time class="version-date">${formatDate(version.created_at)}</time></div>
      ${prompt}
    </article>`;
  }).join("");
  timeline.querySelectorAll(".version-card").forEach((card) => {
    card.addEventListener("click", () => selectVersion(card.dataset.sha));
    card.addEventListener("keydown", (event) => {
      if (event.key === "Enter" || event.key === " ") selectVersion(card.dataset.sha);
    });
  });
}

function selectVersion(sha) {
  state.selected = state.versions.find((version) => version.commit_sha === sha) || null;
  state.preview = state.selected && state.selected.latest_preview && state.selected.latest_preview.status === "ready"
    ? state.selected.latest_preview : null;
  renderTimeline();
  renderPreview();
}

function renderPreview() {
  const selected = state.selected;
  const preview = state.preview;
  byId("previewButton").disabled = !selected;
  byId("branchButton").disabled = !selected;
  byId("selectionLabel").textContent = selected
    ? `${selected.message} · ${selected.short_sha}`
    : "Choose a version to inspect it.";
  byId("previewState").textContent = preview ? "Online" : selected ? "Not started" : "Idle";
  byId("inspectorMessage").textContent = selected ? (selected.message || "Untitled checkpoint") : "No checkpoint selected";
  byId("inspectorMeta").innerHTML = selected
    ? `<span class="chip">${escapeHtml(selected.short_sha)}</span>${(selected.branches || []).map((branch) => `<span class="chip branch">${escapeHtml(branch)}</span>`).join("")}<span class="chip">${escapeHtml(formatDate(selected.created_at))}</span>`
    : "";
  byId("inspectorPrompt").textContent = selected
    ? (selected.prompt || "No prompt was recorded for this checkpoint.")
    : "Select a version from the timeline to see its details and preview it in an isolated sandbox.";
  byId("previewEmpty").classList.toggle("hidden", Boolean(preview));
  byId("previewFrame").classList.toggle("hidden", !preview);
  byId("stopButton").classList.toggle("hidden", !preview);
  byId("previewLogs").classList.add("hidden");
  byId("previewUrl").textContent = preview ? preview.preview_url : "No container running";
  if (preview) byId("previewFrame").src = preview.preview_url;
  else byId("previewFrame").removeAttribute("src");
}

async function load() {
  try {
    const [project, history] = await Promise.all([api("/api/project"), api("/api/versions")]);
    state.project = project;
    state.versions = history.versions;
    const selectedSha = state.selected && state.selected.commit_sha;
    state.selected = state.versions.find((version) => version.commit_sha === selectedSha) || state.versions[0] || null;
    state.preview = state.selected && state.selected.latest_preview && state.selected.latest_preview.status === "ready"
      ? state.selected.latest_preview : null;
    renderProject();
    renderTimeline();
    renderPreview();
  } catch (error) {
    showToast(error.message, true);
  }
}

byId("refreshButton").addEventListener("click", load);
byId("checkpointToggle").addEventListener("click", () => byId("checkpointForm").classList.toggle("hidden"));
byId("checkpointForm").addEventListener("submit", async (event) => {
  event.preventDefault();
  try {
    const result = await api("/api/checkpoints", {
      method: "POST",
      body: JSON.stringify({ message: byId("checkpointMessage").value, prompt: byId("checkpointPrompt").value }),
    });
    byId("checkpointForm").reset();
    byId("checkpointForm").classList.add("hidden");
    showToast(result.already_clean ? "Nothing new to commit in the generated app." : `Checkpoint ${result.short_sha} created.`);
    await load();
  } catch (error) { showToast(error.message, true); }
});
byId("previewButton").addEventListener("click", async () => {
  if (!state.selected) return;
  byId("previewButton").disabled = true;
  byId("previewButton").textContent = "Starting…";
  try {
    state.preview = await api(`/api/versions/${state.selected.commit_sha}/preview`, { method: "POST", body: "{}" });
    showToast(`Preview started at ${state.preview.preview_url}`);
    renderPreview();
    await load();
  } catch (error) {
    byId("previewLogs").textContent = error.message;
    byId("previewLogs").classList.remove("hidden");
    showToast(error.message, true);
  } finally {
    byId("previewButton").textContent = "Start preview";
    byId("previewButton").disabled = false;
  }
});
byId("branchButton").addEventListener("click", async () => {
  if (!state.selected) return;
  const defaultName = `design/from-${state.selected.short_sha}`;
  const branchName = window.prompt("Name the new branch", defaultName);
  if (branchName === null) return;
  try {
    const result = await api(`/api/versions/${state.selected.commit_sha}/branch`, {
      method: "POST", body: JSON.stringify({ branch_name: branchName }),
    });
    showToast(`Created ${result.branch}. Agent edits now target its isolated worktree.`);
    await load();
  } catch (error) { showToast(error.message, true); }
});
byId("stopButton").addEventListener("click", async () => {
  if (!state.preview) return;
  try {
    await api(`/api/previews/${state.preview.preview_id}/stop`, { method: "POST", body: "{}" });
    state.preview = null;
    renderPreview();
    showToast("Preview stopped and its snapshot was removed.");
    await load();
  } catch (error) { showToast(error.message, true); }
});

load();
