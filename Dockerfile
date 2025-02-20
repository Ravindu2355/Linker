# Use an official Python runtime as a parent image
#FROM python:3.10-slim
#FROM python:3.10

# Set the working directory
#WORKDIR /app

# Copy the current directory contents into the container at /app
#COPY . .

# Install ffmpeg
#RUN apt-get update && apt-get install -y ffmpeg && apt-get clean
#RUN apt -qq update && apt -qq install -y git python3 python3-pip ffmpeg

# Install Python dependencies
#COPY requirements.txt .
#RUN pip3 install --no-cache-dir -r requirements.txt

# Expose the port the app runs on (not strictly necessary for a Telegram bot)
#EXPOSE 8000

# Run the bot when the container launches
#CMD gunicorn --bind 0.0.0.0:8000 app:app & python3 bot.py
#CMD python3 bot.py
# Use a base image with both Python and Node.js
FROM node:18-bullseye-slim

# Install Python 3.10 and required dependencies
RUN apt update && apt install -y python3 python3-pip ffmpeg

# Set the working directory
WORKDIR /app

# Copy project files
COPY . .

# Install Python dependencies
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Install Node.js dependencies
COPY package*.json ./
RUN npm install

# Expose ports
EXPOSE 8000  
#Node.js server port (adjust if needed)
# EXPOSE 8443  # (If needed for Pyrogram)

# Run both Node.js server and Python bot in parallel
CMD npm start & gunicorn --bind 0.0.0.0:8000 app:app & python3 bot.py
