import os
from google import genai


# 1. Initialize the client (Ensure your API key is correct!)
client = genai.Client(api_key="AIzaSyDStYjX0TnUNIJDg7AUJUzI3lY842NndSk")

def get_magic_data(complex_text):
    # Use 'gemini-1.5-flash' - it is the most stable for v1beta calls
    model_id = "gemini-1.5-flash" 
    
    prompt = (
        f"Simplify this for a person with learning disabilities: {complex_text} "
        f"Format your response EXACTLY like this: "
        f"SIMPLE: [your simple text here] VISUALS: [3 keywords]"
    )
    
    try:
        response = client.models.generate_content(model=model_id, contents=prompt)
        full_text = response.text
        
        # 2. Parsing logic
        simple_text = full_text.split("SIMPLE:")[1].split("VISUALS:")[0].strip()
        visual_tags = full_text.split("VISUALS:")[1].strip()

        # We return TWO values to match your view.py expectation
        return simple_text, visual_tags

    except Exception as e:
        print(f"❌ AI ERROR: {e}")
        # Return fallback text so the app doesn't crash
        return "Plants use sunlight to make food and oxygen.", "nature, sun, plants"
def generate_magic_lesson(complex_text):
    """
    Returns a dictionary for the run_magic route.
    """
    simple, audio, visuals = get_magic_data(complex_text)
    return {
        "simple": simple,
        "audio": audio,
        "images": visuals
    }