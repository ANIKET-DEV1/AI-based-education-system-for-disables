import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

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
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
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
        print(f"GROQ ERROR: {e}")
        return "Plants use sunlight to grow and make oxygen for us.", "sun, plants, oxygen"


def generate_magic_lesson(complex_text):
    """
    Returns a dictionary for the run_magic route.
    """
    simple, visuals = get_magic_data(complex_text)
    return {
        "simple": simple,
        "audio": "CC_VOICE",
        "images": visuals
    }


def generate_quiz_content(categories, difficulty, num_questions):
    """
    Uses Groq to generate quiz questions.
    """
    topic = ", ".join(categories)
    prompt = (
        f"Generate {num_questions} MCQ questions on {topic}.\n"
        f"Difficulty: {difficulty}.\n"
        f"Provide:\n"
        f"- Question\n"
        f"- 4 options (A, B, C, D)\n"
        f"- Correct answer\n"
        f"- Short explanation\n"
    )

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=2000
        )
        return completion.choices[0].message.content

    except Exception as e:
        print(f"GROQ QUIZ ERROR: {e}")
        return "Error generating quiz. Please try again."


def summarize_text(text, summary_type="Short", output_format="Paragraph", language="Normal English"):
    """
    Uses Groq to summarize extracted PDF text.
    """
    format_instruction = "bullet points" if output_format == "Bullet Points" else "a paragraph"
    lang_instruction = ""
    if language == "Easy Language":
        lang_instruction = "Use very simple words and short sentences suitable for a student with learning disabilities."
    elif language == "Hindi":
        lang_instruction = "Write the summary in Hindi."
    
    length = "a brief 2-3 sentence" if summary_type == "Short" else "a detailed"
    
    prompt = (
        f"Provide {length} summary of the following text in {format_instruction} format. "
        f"{lang_instruction}\n\n"
        f"Also provide:\n"
        f"- 3 bullet point highlights\n"
        f"- 3 key concepts\n\n"
        f"Format your response EXACTLY as:\n"
        f"SUMMARY: [your summary]\n"
        f"BULLETS: [bullet1 | bullet2 | bullet3]\n"
        f"CONCEPTS: [concept1 | concept2 | concept3]\n\n"
        f"Text: {text[:3000]}"
    )

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
            max_tokens=1000
        )
        
        full_text = completion.choices[0].message.content
        
        summary = full_text
        bullets = []
        concepts = []
        
        if "SUMMARY:" in full_text:
            summary = full_text.split("SUMMARY:")[1]
            if "BULLETS:" in summary:
                summary = summary.split("BULLETS:")[0].strip()
        
        if "BULLETS:" in full_text:
            bullets_raw = full_text.split("BULLETS:")[1]
            if "CONCEPTS:" in bullets_raw:
                bullets_raw = bullets_raw.split("CONCEPTS:")[0]
            bullets = [b.strip() for b in bullets_raw.strip().split("|") if b.strip()]
        
        if "CONCEPTS:" in full_text:
            concepts_raw = full_text.split("CONCEPTS:")[1].strip()
            concepts = [c.strip() for c in concepts_raw.split("|") if c.strip()]
        
        return {
            "summary": summary,
            "bullets": bullets,
            "concepts": concepts
        }

    except Exception as e:
        print(f"GROQ SUMMARIZE ERROR: {e}")
        return {
            "summary": "Error generating summary. Please try again.",
            "bullets": [],
            "concepts": []
        }