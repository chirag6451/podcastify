# Celery Task Debug Guide

## Current Issue
The video generation task is running but not showing progress in Celery logs. This happens because:

1. Audio task completes and returns successfully
2. Video task starts but its progress is not visible
3. No proper task chaining between audio and video tasks

## Solution Steps

### 1. Improve Task Chaining
In `celery_app/tasks.py`, modify the task chain:

```python
if os.getenv('CELERY_PROCESS') == 'true':
    # Use chord to ensure proper task chaining
    video_task = chord(
        generate_audio_task.s(request_dict, config, job_id),
        create_video_task.s(config, job_id, request_dict)
    )()
```

### 2. Add Progress Logging
In `video_creator/podcast_video_maker.py`, add progress logging:

```python
def create_video(self, config, audio_path, welcome_audio_path, job_id, request_dict):
    logger.info(f"Starting video creation for job {job_id}")
    # Add progress logging
    self.current_task.update_state(
        state='PROGRESS',
        meta={'current': 0, 'total': 100}
    )
    ...
```

### 3. Monitor Progress
To monitor task progress:

```bash
# View all tasks
redis-cli -h localhost KEYS "*"

# View specific task status
redis-cli -h localhost GET celery-task-meta-[task-id]

# Monitor Celery logs
tail -f celery.log
```

### 4. Task Status Check
Check task status in Python:

```python
from celery.result import AsyncResult

def check_task_status(task_id):
    result = AsyncResult(task_id)
    return {
        'status': result.status,
        'info': result.info
    }
```

### Additional Debugging Steps

#### Check if Celery worker is running
```bash
ps aux | grep celery
```

#### Check active tasks in Redis
```bash
redis-cli info
redis-cli -h localhost KEYS "*"
```

#### Check status of the most recent task
```bash
redis-cli -h localhost GET celery-task-meta-4fb7670a-734e-4a59-9939-f8933f06c370
```

#### Check if there are any ffmpeg processes running
```bash
ps aux | grep ffmpeg

tail -f /Users/chiragahmedabadi/dev/podcraftai/logs/celery_tasks.log
```