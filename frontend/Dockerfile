# Stage 1: Build the React application
FROM node:18-alpine as builder
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
# Make API URL available at build time if needed, but proxy is better
# ENV REACT_APP_API_URL=/api
RUN npm run build

# Stage 2: Serve the static files with Nginx
FROM nginx:stable-alpine
# Copy built assets from the builder stage
COPY --from=builder /app/dist /usr/share/nginx/html
# Copy custom Nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf
# Expose port 80
EXPOSE 80
# Start Nginx
CMD ["nginx", "-g", "daemon off;"]
