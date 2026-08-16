FROM nginx:alpine

COPY nginx.conf /etc/nginx/nginx.conf
RUN chown -R 101:101 /usr/share/nginx/html

USER 101:101
EXPOSE 8080
