# syntax=docker/dockerfile:1

# Build do site estático
FROM node:24-alpine AS build
WORKDIR /app

COPY package.json package-lock.json .npmrc ./
RUN --mount=type=cache,target=/root/.npm npm ci

COPY . .
RUN npm run build

# Imagem final: só o nginx e os arquivos estáticos (sem Node)
FROM nginx:1.30-alpine

COPY nginx/security-headers.conf /etc/nginx/snippets/security-headers.conf
COPY nginx/default.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/build /usr/share/nginx/html
