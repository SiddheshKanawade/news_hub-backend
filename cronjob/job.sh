#!/bin/bash

# Echo statements to show the progress
echo "Starting the script..."

# Initialize Conda (required to activate Conda environments in scripts)
source /home/siddhesh/miniconda3/etc/profile.d/conda.sh

conda init bash

# Echo statement to confirm Conda is initialized
echo "Conda initialized."

# Activate the Conda environment
conda activate news
echo "Activated Conda environment: your_env_name"

# Run the Python script
echo "Running Python script..."
python /home/siddhesh/Desktop/Siddhesh/Projects/news_aggregator/cronjob/upload_articles.py

# Echo statement to indicate completion
echo "Python script execution completed."

# Optional: Deactivate the Conda environment after running the script
conda deactivate
echo "Conda environment deactivated."
