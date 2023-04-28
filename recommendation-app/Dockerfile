#Image node
FROM node:latest AS build

# Set working directory
WORKDIR /app

# Copy source code
COPY . /app

# Install dependencies
RUN npm install

# Build app
RUN npm run build

FROM nginx:latest

COPY --from=build /app/dist/recommendation-app/ /usr/share/nginx/html

# Expose port 4200
EXPOSE 80

