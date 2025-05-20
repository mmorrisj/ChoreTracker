#!/bin/bash

# This script initializes the Docker environment for the Family Chore Tracker application
# on a Raspberry Pi 5 or any Debian-based system.

echo "Initializing Family Chore Tracker application..."

# Check if .env file exists, create from example if not
if [ ! -f .env ]; then
    echo "Creating .env file from example..."
    cp .env.example .env
    echo "Please edit the .env file to set secure passwords before proceeding."
    echo "You can do this by running: nano .env"
    exit 1
fi

# Ensure docker is running
if ! docker info > /dev/null 2>&1; then
    echo "Docker does not seem to be running. Starting Docker..."
    sudo systemctl start docker
    sleep 5
fi

# Build and start the application
echo "Building and starting the application..."
docker compose down
docker compose up -d --build

# Display status message
echo "Application is now starting!"
echo "It will be available at http://localhost:5000 or http://$(hostname -I | awk '{print $1}'):5000"
echo ""
echo "To view logs, run: docker compose logs -f"
echo "To stop the application, run: docker compose down"
echo ""
echo "Thank you for using Family Chore Tracker!"