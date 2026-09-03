# prod: TLS-терминация + прокси на frontend/backend
FROM nginx:1.27-alpine

COPY conf.d/default.conf /etc/nginx/templates/default.conf.template
# entrypoint nginx:alpine сам гоняет envsubst по /etc/nginx/templates/*.template
ENV NGINX_ENVSUBST_OUTPUT_DIR=/etc/nginx/conf.d

COPY cert-reload.sh /docker-entrypoint.d/99-cert-reload.sh
RUN chmod +x /docker-entrypoint.d/99-cert-reload.sh
