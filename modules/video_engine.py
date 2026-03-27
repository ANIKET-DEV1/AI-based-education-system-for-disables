import os
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips

def create_magic_video(audio_filename, visual_keywords):
    audio_path = os.path.join('static/audio', audio_filename)
    audio = AudioFileClip(audio_path)
    
    # For Hackathon: We use a placeholder logic. 
    # Real world: You'd fetch images from Unsplash API using visual_keywords
    placeholder_img = "static/images/lesson_bg.jpg" # Make sure this exists!
    
    video_filename = f"video_{os.urandom(3).hex()}.mp4"
    output_path = os.path.join('static/videos', video_filename)
    os.makedirs('static/videos', exist_ok=True)

    # Create a 3-image slideshow based on audio duration
    duration = audio.duration / 3
    clips = [ImageClip(placeholder_img).set_duration(duration) for _ in range(3)]
    
    video = concatenate_videoclips(clips, method="compose").set_audio(audio)
    video.write_videofile(output_path, fps=24, codec="libx264")
    
    return video_filename