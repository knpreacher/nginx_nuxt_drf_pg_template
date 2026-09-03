# сборка: ставим зависимости и билдим SSR
FROM node:22-alpine AS build
WORKDIR /app
RUN corepack enable
COPY app/package.json app/yarn.lock app/.yarnrc.yml ./
RUN yarn install --immutable
COPY app/ ./
RUN yarn build

# рантайм: только собранный сервер, без исходников
FROM node:22-alpine AS runtime
WORKDIR /app
ENV NODE_ENV=production PORT=3000 HOST=0.0.0.0
COPY --from=build /app/.output ./.output
EXPOSE 3000
CMD ["node", ".output/server/index.mjs"]
