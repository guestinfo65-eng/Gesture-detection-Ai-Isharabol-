FROM python:3.11-slim

WORKDIR /app

# Copy project files
COPY . .

# Expose port
EXPOSE 8080

# Run the server
CMD ["python", "server.py"]
