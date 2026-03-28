import os
import requests
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips
import google.generativeai as genai

def create_magic_video(audio_filename, visual_keywords, api_key):
    try:
        audio_path = os.path.join('static/audio', audio_filename)
        if not os.path.exists(audio_path):
            print(f"VIDEO ENGINE: Audio file {audio_path} not found.")
            return ""
            
        audio = AudioFileClip(audio_path)
        
        # 1. Use Gemini API to create detailed image prompts
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        prompt = f"Create exactly 3 short, highly descriptive visual prompts (under 10 words each) for an educational video about these keywords: '{visual_keywords}'. Separate them with a pipe '|' character. Do not include any other text."
        response = model.generate_content(prompt)
        raw_prompts = [p.strip() for p in response.text.split('|') if p.strip()]
        
        # Fallback if Gemini formatting fails
        if len(raw_prompts) < 3:
            raw_prompts = [f"{visual_keywords} concept illustration 1", f"{visual_keywords} concept illustration 2", f"{visual_keywords} concept illustration 3"]
            
        # 2. Download the 3 images from Pollinations AI
        img_paths = []
        os.makedirs('static/images', exist_ok=True)
        for i, p in enumerate(raw_prompts[:3]):
            img_path = os.path.join('static/images', f"img_{os.urandom(4).hex()}.jpg")
            url = f"https://image.pollinations.ai/prompt/{requests.utils.quote(p)}?width=1280&height=720&nologo=true"
            img_data = requests.get(url).content
            with open(img_path, 'wb') as f:
                f.write(img_data)
            img_paths.append(img_path)
            
        # 3. Compile the video
        video_filename = f"video_{os.urandom(4).hex()}.mp4"
        output_path = os.path.join('static/videos', video_filename)
        os.makedirs('static/videos', exist_ok=True)

        duration = max(2.5, audio.duration / 3.0)
        clips = [ImageClip(img).set_duration(duration) for img in img_paths]
        
        video = concatenate_videoclips(clips, method="compose").set_audio(audio)
        video.write_videofile(output_path, fps=24, codec="libx264", audio_codec="aac")
        
        # Cleanup images
        for img in img_paths:
            if os.path.exists(img):
                os.remove(img)
                
        return video_filename
    except Exception as e:
        print(f"VIDEO ENGINE ERROR: {e}")
        return ""