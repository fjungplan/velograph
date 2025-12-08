# frontend/Dockerfile

# --- Stage 1: Build the React App ---
FROM node:22-alpine as builder

WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm ci

# Copy the source code
COPY . .

# CRITICAL: This bakes the API URL into the React app at build time
ARG VITE_API_URL
ENV VITE_API_URL=${VITE_API_URL}

# Build the static files (creates /app/dist)
RUN npm run build

# --- Stage 2: Serve with Nginx ---
FROM nginx:alpine

# Copy the built files from Stage 1
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy the nginx config you just created
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]