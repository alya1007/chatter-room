# Use a lightweight Python image
FROM python:3.10-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements.txt to the container
COPY requirements.txt .

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy all the gateway application code to the container
COPY . .

# Expose the port that the Gateway service will use
EXPOSE 5000

# Start the Gateway service
CMD ["python", "gateway.py"]
