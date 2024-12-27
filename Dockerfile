# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory
WORKDIR /usr/src/app

# Install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the bot script and other necessary files
COPY bot.py .
COPY config.env .

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Run the bot
