#!/bin/bash

# ##############################################################################
#                          CRON WRAPPER SCRIPT
#
# This script sets up the full user environment before running the scheduler.
# This ensures that the cron job runs in the exact same context as a
# manual run, which solves environment-related browser crashes.
# ##############################################################################

# Change to the directory where all your Python scripts are located.
# IMPORTANT: Replace '/home/ubuntu' with the correct path to your project folder if it's different.
cd /home/ubuntu

# Load all the user's environment variables, including PATH.
# This is a critical step.
source /home/ubuntu/.profile

# Define the path to the scheduler log file.
LOGFILE="/home/ubuntu/scheduler.log"

# Add a timestamp to the log file for this run.
echo "--- Wrapper script started at $(date) ---" >> $LOGFILE

# Execute the Python scheduler using xvfb-run, redirecting all output (stdout and stderr)
# to the log file.
/usr/bin/xvfb-run --auto-servernum --server-args="-screen 0 1280x1024x24" /usr/bin/python3 /home/ubuntu/scheduler.py >> $LOGFILE 2>&1

echo "--- Wrapper script finished at $(date) ---" >> $LOGFILE


