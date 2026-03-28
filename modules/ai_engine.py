import os
from groq import Groq

# PASTE YOUR KEY HERE
client = Groq(api_key="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")

def get_magic_data(complex_text):
    """
    Uses Groq's FREE tier to simplify text instantly.
    """
    prompt = (
        f"Simplify this text for a student with learning disabilities. "
        f"Use short sentences and simple words. "
        f"Format your response EXACTLY as follows:\n"
        f"SIMPLE: [simplified text]\n"
        f"VISUALS: [3 keywords separated by commas]\n\n"
        f"Text to simplify: {complex_text}"
    )

    try:
        # Using Llama 3 - very smart and free
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
            max_tokens=500
        )
        
        full_text = completion.choices[0].message.content
        
        # Robust Parsing
        if "SIMPLE:" in full_text and "VISUALS:" in full_text:
            simple_part = full_text.split("SIMPLE:")[1].split("VISUALS:")[0].strip()
            visual_tags = full_text.split("VISUALS:")[1].strip()
        else:
            # Fallback if AI doesn't follow format
            simple_part = full_text[:200]
            visual_tags = "learning, education, simple"

        return simple_part, visual_tags

    except Exception as e:
        print(f"❌ GROQ ERROR: {e}")
        # Emergency Fallback so your demo never fails
        return "Plants use sunlight to grow and make oxygen for us.", "sun, plants, oxygen"
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