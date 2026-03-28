import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

# Securely load the client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def get_magic_data(complex_text, language="Simple English"):
    """
    Uses Groq's FREE tier to simplify text instantly.
    """
    lang_instruction = ""
    if language == "Hindi":
        lang_instruction = "Write the simplified text in Hindi (Devanagari script). "

    prompt = (
        f"Simplify this text for a student with learning disabilities. "
        f"Use short sentences and simple words. "
        f"{lang_instruction}"
        f"Format your response EXACTLY as follows:\n"
        f"SIMPLE: [simplified text]\n"
        f"VISUALS: [3 keywords separated by commas]\n\n"
        f"Text to simplify: {complex_text}"
    )

    try:
        # FIXED: Added 'llama-3.1-8b-instant' as the model
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
            max_tokens=500
        )
        
        full_text = completion.choices[0].message.content
        
        if "SIMPLE:" in full_text and "VISUALS:" in full_text:
            simple_part = full_text.split("SIMPLE:")[1].split("VISUALS:")[0].strip()
            visual_tags = full_text.split("VISUALS:")[1].strip()
        else:
            simple_part = full_text[:200]
            visual_tags = "learning, education, simple"

        return simple_part, visual_tags

    except Exception as e:
        print(f"❌ GROQ ERROR: {e}")
        return "Plants use sunlight to grow and make oxygen for us.", "sun, plants, oxygen"


def generate_magic_lesson(complex_text):
    """
    Returns a dictionary for the run_magic route.
    """
    # Updated to handle the 2-value return
    simple, visuals = get_magic_data(complex_text)
    return {
        "simple": simple,
        "audio": "CC_VOICE",
        "images": visuals
    }


def generate_quiz_content(categories, difficulty, num_questions):
    """
    Uses Groq to generate quiz questions using the fast 8b model.
    """
    topic = ", ".join(categories)
    prompt = (
        f"Generate {num_questions} MCQ questions on {topic}.\n"
        f"Difficulty: {difficulty}.\n"
        f"Provide Question, 4 options (A,B,C,D), Correct answer, and Explanation."
    )

    try:
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant", # Faster for simple tasks like quizes
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=2000
        )
        return completion.choices[0].message.content
    except Exception as e:
        print(f"❌ GROQ QUIZ ERROR: {e}")
        return "Error generating quiz. Please try again."


def summarize_text(text, summary_type="Short", output_format="Paragraph", language="Normal English"):
    """
    Uses the smart 70b model to summarize extracted PDF text.
    """
    format_instruction = "bullet points" if output_format == "Bullet Points" else "a paragraph"
    lang_instruction = "Use very simple words suitable for learning disabilities." if language == "Easy Language" else ""
    if language == "Hindi": lang_instruction = "Write the summary in Hindi."
    
    length = "a brief 2-3 sentence" if summary_type == "Short" else "a detailed"
    
    prompt = (
        f"Provide {length} summary in {format_instruction} format. {lang_instruction}\n"
        f"Format EXACTLY as: SUMMARY: [text] BULLETS: [b1 | b2 | b3] CONCEPTS: [c1 | c2 | c3]\n"
        f"Text: {text[:3000]}"
    )

    try:
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
            max_tokens=1000
        )
        
        full_text = completion.choices[0].message.content
        
        # Parsing logic (Matches your current view logic)
        summary = full_text.split("SUMMARY:")[1].split("BULLETS:")[0].strip() if "SUMMARY:" in full_text else full_text
        bullets_raw = full_text.split("BULLETS:")[1].split("CONCEPTS:")[0].strip() if "BULLETS:" in full_text else ""
        concepts_raw = full_text.split("CONCEPTS:")[1].strip() if "CONCEPTS:" in full_text else ""
        
        return {
            "summary": summary,
            "bullets": [b.strip() for b in bullets_raw.split("|") if b.strip()],
            "concepts": [c.strip() for c in concepts_raw.split("|") if c.strip()]
        }
    except Exception as e:
        print(f"❌ GROQ SUMMARIZE ERROR: {e}")
        return {"summary": "Error generating summary.", "bullets": [], "concepts": []}