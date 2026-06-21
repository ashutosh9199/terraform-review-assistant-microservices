# syntax=docker/dockerfile:1

# ---- build: compile the React app ----
FROM node:20-alpine AS build
WORKDIR /app
# Empty base URL => the SPA calls the API same-origin at /api/* (nginx proxies
# it to the gateway). Local `npm run dev` is unaffected: with the var unset at
# dev time, the app falls back to http://localhost:8000.
ARG VITE_API_BASE_URL=""
ENV VITE_API_BASE_URL=${VITE_API_BASE_URL}
COPY package.json package-lock.json* ./
RUN npm ci || npm install
COPY . .
RUN npm run build

# ---- runtime: unprivileged nginx (non-root, listens on 8080) (capstone §7) ----
FROM nginxinc/nginx-unprivileged:1.27-alpine
# nginx-unprivileged runs as a non-root user (UID 101) and cannot bind :80.
# Gateway upstream is env-substituted into the config at container start.
ENV GATEWAY_UPSTREAM=api-gateway:8000
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/templates/default.conf.template
EXPOSE 8080
