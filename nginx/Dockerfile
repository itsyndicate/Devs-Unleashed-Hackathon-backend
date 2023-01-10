FROM nginx:1.21-alpine

EXPOSE 80
EXPOSE 443
RUN rm /etc/nginx/conf.d/default.conf
COPY nginx.conf /etc/nginx/conf.d
RUN apk add --update python3 py3-pip && apk add certbot && pip install --no-input certbot-nginx
RUN certbot --non-interactive --nginx --agree-tos --no-eff-email --no-redirect --email 'ivan.n@itsyndicate.org' -d "backend.guard-lite.com"
