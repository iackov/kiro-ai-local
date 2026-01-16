FROM node:20-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install --production

# Copy application (after npm install to avoid overwriting node_modules)
COPY index.js ./

# Create logs directory
RUN mkdir -p /logs

EXPOSE 8002

CMD ["node", "index.js"]
