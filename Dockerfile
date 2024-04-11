# Use the official Python image as the base image
FROM python:3.9-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory in the container
WORKDIR /app

# Set the PYTHONPATH environment variable to include the /app directory
ENV PYTHONPATH "/modules:${PYTHONPATH}"

# Copy the dependencies file to the working directory
COPY modules/requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire modules directory to the working directory in the container
COPY modules /app/modules

COPY modules/upload_images.py /app

# Expose the port your app runs on
EXPOSE 5000

# Command to run the application
CMD ["python", "upload_images.py"]
