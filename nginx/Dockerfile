FROM nginx:1.21-alpine

EXPOSE 80
EXPOSE 443
RUN rm /etc/nginx/conf.d/default.conf
COPY nginx.conf /etc/nginx/conf.d

