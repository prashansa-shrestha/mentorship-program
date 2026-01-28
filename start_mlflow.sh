#!/bin/bash

echo "Cleaning up old MLflow processes"
sudo lsof -ti:5000 | xargs sudo kill -9 2>/dev/null
sleep 2

# Navigate to experiments directory
cd ~/Desktop/Prashansa/project_repositories/mentorship-program/experiments


echo "Starting MLflow UI on port 5000..."
mlflow ui --backend-store-uri sqlite:///$(pwd)/mlflow.db --port 5000



