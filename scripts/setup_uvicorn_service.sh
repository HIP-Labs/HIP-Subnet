#!/bin/bash

# Define the service unit file path
SERVICE_FILE="/etc/systemd/system/uvicorn_frontend.service"

# Define the content of the service unit file
SERVICE_CONTENT="[Unit]
Description=UVicorn Frontend Service
After=network.target

[Service]
User=ubuntu
Group=ubuntu
WorkingDirectory=/home/ubuntu/HIP-Subnet
ExecStart=/home/ubuntu/HIP-Subnet/venv/bin/uvicorn frontend:app --host 0.0.0.0 --port 5001
Restart=always

[Install]
WantedBy=multi-user.target"

# Write the service unit file
echo "$SERVICE_CONTENT" | sudo tee "$SERVICE_FILE" > /dev/null

# Reload systemd
sudo systemctl daemon-reload

# Enable the service
sudo systemctl enable uvicorn_frontend

# Start the service
sudo systemctl start uvicorn_frontend

# Check the status of the service
sudo systemctl status uvicorn_frontend