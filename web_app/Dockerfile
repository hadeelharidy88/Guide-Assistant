FROM node:18-slim  

# Install http-server globally
RUN npm install -g http-server

# Set the working directory
WORKDIR /app

# Copy the HTML file
COPY index.html .

# Expose port 8080
EXPOSE 8080

# Health check (optional, but recommended)
HEALTHCHECK CMD curl --fail http://localhost:8080/ || exit 1

# Start http-server
CMD ["http-server", ".", "--port", "8080", "--cache", "-1"] # Disable caching
