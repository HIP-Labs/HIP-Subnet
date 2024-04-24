#!/bin/bash

sudo ufw allow 3001 && uvicorn frontend:app --host 0.0.0.0 --port 3001
