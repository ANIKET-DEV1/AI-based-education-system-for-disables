import os
from typing import Tuple
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

# Securely load the client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def get_magic_data(complex_text: str, language: str = "Simple English") -> Tuple[str, str]:
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
            model="openai/gpt-oss-120b",
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


def generate_quiz_content(context_text, difficulty, num_questions):
    """
    Uses Groq to generate quiz questions from provided document text.
    """
    difficulty_instruction = {
        'simple': 'Keep questions easy and focused on direct facts.',
        'medium': 'Use intermediate challenge with some inference required.',
        'difficult': 'Use harder critical-thinking questions based on details.'
    }.get(difficulty.lower(), 'Use a balanced difficulty.')

    prompt = (
        f"Based on the following text, generate {num_questions} multiple-choice questions. "
        f"Each question should include 4 options (A,B,C,D), the correct answer letter, and a short explanation. "
        f"Difficulty: {difficulty.capitalize()}. {difficulty_instruction}\n\n"
        f"Text:\n{context_text[:4500]}\n\n"
        f"Output must be valid JSON like:\n"
        f"{{\n  \"quiz\": [\n    {{\n      \"question\": \"...\",\n      \"options\": [\"...\", \"...\", \"...\", \"...\"],\n      \"answer\": \"A\",\n      \"explanation\": \"...\"\n    }}\n  ]\n}}"
    )

    try:
        completion = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=2000
        )

        full_text = completion.choices[0].message.content
        import json
        try:
            parsed = json.loads(full_text)
            if isinstance(parsed, dict) and 'quiz' in parsed and isinstance(parsed['quiz'], list):
                if parsed['quiz']:
                    return parsed['quiz']
            # if parsed but not in expected format, fallback below
            print('QUIZ PARSE WARNING: parsed output unexpected, falling back')
        except json.JSONDecodeError:
            print('QUIZ PARSE ERROR: JSON decode failed, falling back')

    except Exception as e:
        print(f"❌ GROQ QUIZ ERROR: {e}")

    # Fallback question generator (non-AI) if API call fails or returns bad data
    cleaned_text = ' '.join(context_text.replace('\n', ' ').split())
    sentences = [s.strip() for s in cleaned_text.split('.') if s.strip()]
    basic_questions = []
    for i, sentence in enumerate(sentences[:num_questions]):
        if ' is ' in sentence:
            subject, remainder = sentence.split(' is ', 1)
            q = f"What is {subject.strip()}?"
            choices = [
                sentence.strip()[:min(50, len(sentence.strip()))],
                'A process that involves multiple steps',
                'A concept unrelated to the topic',
                'An unknown definition'
            ]
            basic_questions.append({
                'question': q,
                'options': [choices[0], choices[1], choices[2], choices[3]],
                'answer': 'A',
                'explanation': f"{subject.strip()} is defined in the text as: {sentence.strip()}"
            })
        else:
            q = f"Which statement best describes: {sentence[:60]}... ?"
            basic_questions.append({
                'question': q,
                'options': ['Correct description', 'Incorrect option', 'Maybe true', 'Not related'],
                'answer': 'A',
                'explanation': 'Generated fallback question for text content.'
            })

    return basic_questions



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
            model="openai/gpt-oss-120b",
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

        # Fallback local summarization when Groq is unavailable.
        text_clean = ' '.join(text.replace('\n', ' ').split())
        sentences = [s.strip() for s in text_clean.split('.') if s.strip()]
        if not sentences:
            return {"summary": "No text found in PDF.", "bullets": [], "concepts": []}

        if summary_type == 'Detailed':
            summary_sentences = sentences[:min(6, len(sentences))]
        else:
            summary_sentences = sentences[:min(3, len(sentences))]

        summary_fallback = ' '.join(summary_sentences)
        bullets_fallback = [s.strip() + '.' for s in summary_sentences[:3]]

        # Derive simple concepts (frequent words excluding stopwords)
        stopwords = set(["the","and","is","in","to","of","a","for","with","on","as","that","this","it","from","by"])
        words = [w.lower().strip('.,?!:;') for w in text_clean.split() if w.isalpha() and w.lower() not in stopwords]
        concepts = []
        for w in sorted(set(words), key=lambda x: words.count(x), reverse=True):
            if w not in concepts and len(concepts) < 5:
                concepts.append(w)

        return {
            "summary": summary_fallback,
            "bullets": bullets_fallback,
            "concepts": concepts[:3]
        }
