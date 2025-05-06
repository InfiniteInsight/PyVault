FROM node:18-alpine

# Install bun
RUN npm install -g bun

# Set working directory
WORKDIR /app

# Copy package files
COPY package.json bun.lock ./

# Install dependencies
RUN bun install --frozen-lockfile

# Copy project files
COPY . .

# Build the project
RUN bun run build

# Expose the port
EXPOSE 4173

# Start the application
CMD ["bun", "run", "preview", "--host", "0.0.0.0"]