"""
Celery Worker Configuration and Guide

This file contains configuration and commands for running Celery workers efficiently
for podcast generation. Different configurations are provided based on the scale
and requirements of the system.

Basic Usage:
-----------
# Start Redis (if not running):
redis-server

# Start a single worker (development):
celery -A celery_app worker -P solo -l INFO

Advanced Usage:
-------------
# Start multiple workers with different queues:
celery -A celery_app worker -Q audio_queue -c 2 -n audio_worker@%h -l INFO
celery -A celery_app worker -Q video_queue -c 1 -n video_worker@%h -l INFO

Performance Tips:
---------------
1. Use separate queues for audio and video processing
2. Audio generation can handle multiple concurrent tasks
3. Video processing is resource-intensive, limit concurrency
4. Monitor memory usage and adjust concurrency accordingly
5. Use dedicated workers for different task types
"""

from kombu import Exchange, Queue

# Define exchanges
default_exchange = Exchange('default', type='direct')
audio_exchange = Exchange('audio', type='direct')
video_exchange = Exchange('video', type='direct')

# Define queues
task_queues = (
    Queue('celery', default_exchange, routing_key='celery'),
    Queue('audio_queue', audio_exchange, routing_key='audio'),
    Queue('video_queue', video_exchange, routing_key='video'),
)

# Task routing
task_routes = {
    'celery_app.tasks.generate_audio': {'queue': 'audio_queue'},
    'celery_app.tasks.create_video': {'queue': 'video_queue'},
}

# Task time limits (in seconds)
task_soft_time_limit = 1800  # 30 minutes
task_time_limit = 3600      # 1 hour

# Optimization settings
optimize_settings = {
    'worker_prefetch_multiplier': 1,    # Prevent worker from prefetching too many tasks
    'worker_max_tasks_per_child': 50,   # Restart worker after 50 tasks to prevent memory leaks
    'task_acks_late': True,             # Only acknowledge task after completion
    'task_reject_on_worker_lost': True, # Reject task if worker dies
    'task_soft_time_limit': task_soft_time_limit,
    'task_time_limit': task_time_limit,
    'worker_concurrency': 2,            # Number of worker processes
    'task_default_queue': 'celery',     # Default queue
    'task_default_exchange': 'default', # Default exchange
    'task_default_routing_key': 'celery', # Default routing key
}

# Example of running with optimal settings:
"""
# For audio processing:
celery -A celery_app worker \\
    -Q audio_queue \\
    -c 2 \\
    -n audio_worker@%h \\
    -l INFO \\
    --max-memory-per-child=1024000 \\
    --max-tasks-per-child=50

# For video processing:
celery -A celery_app worker \\
    -Q video_queue \\
    -c 1 \\
    -n video_worker@%h \\
    -l INFO \\
    --max-memory-per-child=2048000 \\
    --max-tasks-per-child=50
"""
