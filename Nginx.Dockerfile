FROM node:24.7 as build
WORKDIR /app
COPY frontend/package*.json .
RUN npm ci
COPY frontend .
RUN npm run build:prod

FROM nginx:1.29.4-alpine3.23
COPY config/nginx/prod /etc/nginx/templates
COPY --from=build /app/dist /usr/share/nginx/html