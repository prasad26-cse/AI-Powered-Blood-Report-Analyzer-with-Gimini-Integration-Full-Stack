#!/usr/bin/env python3
"""
Windows-specific Celery worker startup script
Handles Windows permission and process pool issues
"""

import os
import sys
from celery import Celery
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def start_celery_worker():
    """Start Celery worker with Windows-compatible settings"""
    print("Starting Celery worker for Windows...")
    
    # Set Windows-specific environment variables
    os.environ['FORKED_BY_MULTIPROCESSING'] = '1'
    
    # Import the Celery app
    from celery_app import celery_app
    
    # Start the worker with Windows-compatible settings
    celery_app.worker_main([
        'worker',
        '--loglevel=info',
        '--pool=solo',  # Use solo pool for Windows
        '--concurrency=1',  # Single worker process
        '--without-gossip',  # Disable gossip for single worker
        '--without-mingle',  # Disable mingle for single worker
        '--without-heartbeat',  # Disable heartbeat for single worker
    ])

if __name__ == '__main__':
    start_celery_worker() 