FROM node:18-alpine

# Set working directory
WORKDIR /app

# Install dependencies first (leverage Docker cache)
COPY package*.json ./
RUN npm install

# Copy project files
COPY . .

# Expose Vite development port
EXPOSE 5173

# Run the local development server with host binding enabled
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
