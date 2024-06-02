#!/bin/bash

sudo ufw allow 5001 && uvicorn frontend:app --host 0.0.0.0 --port 5001
