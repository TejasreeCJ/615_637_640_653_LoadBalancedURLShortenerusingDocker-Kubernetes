# Use Python 3.12
FROM python:3.12

# Set the working directory
WORKDIR /app

# Copy application files
COPY . /app

# Install dependencies
RUN pip install flask redis

# Expose the port
EXPOSE 5000

# Run the Flask app
CMD ["python", "app.py"]
