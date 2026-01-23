#!/bin/sh
set -e
#
# Create logs directory if it doesn't exist
#
mkdir -p logs
chown -R appuser:appuser logs

# Execute the main command


exec gosu appuser "$@"
