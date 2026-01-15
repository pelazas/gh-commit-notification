# Use a lightweight Python image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY app.py .

# Expose the port (Flask default 5000)
EXPOSE 5000

# Run with Gunicorn for production stability
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]