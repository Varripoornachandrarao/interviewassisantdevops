FROM nginx:stable-alpine

# Copy static files
COPY . /usr/share/nginx/html

# Copy nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Remove nginx.conf from html root to keep it clean
RUN rm /usr/share/nginx/html/nginx.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
