hygen realted stuff are in video_creator/hygen.py

1. fastapi unviconer server with python run_api.py
2. swagger is runing on http://0.0.0.0:8011/api/docs#
3. in main.py task data is entered in db and task id is create 
3. then we call celery_app/tasks.py for audio and video task bg /celery proes 
4. audio task will call generate_conversation and generate_audio_task will call and generate audio path, welcome audio and video
5.then it calls create_podcast_video(
    audio_path
    welcome_audio_path
    video_path
    title
    description
    category
)
then  maker = PodcastVideoMaker()
    return maker.create_video(
then 

video_creator/podcast_video_maker.py
        output_path = self._creator.create_video(
            audio_path=audio_path,
            welcome_audio_path=welcome_audio_path,
            config=config,
            job_id=job_id,
            request_dict=request_dict
        )

this is where all intro, hyenge, short videos etc are genreated and entered in database 
then we call update_job_status(job_id, 'video_created')
then we run all crons 
crons 
cron/monitor_heygen_videos.py

this we need to run first to get all video process done for hgyen 
cron/cron_video_creator.py this combined all video paths and create final video 
cron/youtube_metadata_cron.py
this create youtbe meta data like title, descriptoin, thumbnais etc
all videos in this wil need approal before it is upload 
then we run youtube_upload_cron to upload to youtbe and get all data from youtbe and update datrabaes lke yotube url, thumnail etc etc
cron/mix_approved_podcasts.py, this combines all audio files in gien order and creates final audio file
cron/upload_to_transistor.py, this uploads final video to transistor and updates database
