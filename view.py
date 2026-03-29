import os
from flask import Blueprint, jsonify, render_template, request, redirect, session, url_for
from models import Helper
from modules.ai_engine import generate_magic_lesson, get_magic_data, generate_quiz_content, summarize_text

view = Blueprint('view', __name__)
auth = Blueprint('auth', __name__)
db = Helper()

# --- AUTH ROUTES ---

@view.route('/')
def home():
    if "user_id" in session:
        return redirect(url_for("view.dashboard"))
    return render_template("loginRegister.html")

@auth.route('/login', methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        user_id = db.auth_user(username, password)
        if user_id:
            session["user_id"] = user_id
            session["username"] = username
            return redirect(url_for("view.home"))
        error = "Invalid username or password"
    return render_template("loginRegister.html", error=error)

@auth.route('/register', methods=["GET", "POST"])
def register():
    error1 = None
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        confirm = request.form.get("confirm_password")

        if password != confirm:
            return render_template("loginRegister.html", error="Passwords do not match")

        result = db.insert_user(username, email, password)
        if result == 2:
            error1 = "Username or email already exists"
        elif result == False:
            error1 = "Registration failed"
        else:
            return redirect(url_for("auth.login"))
    return render_template("loginRegister.html", error1=error1)

@auth.route('/logout')
def logout():
    session.clear()
    return redirect(url_for("auth.login"))

# --- MAIN VIEW ROUTES ---

@view.route('/dashboard')
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))
    stats = db.get_user_stats(session["user_id"])
    return render_template("dashboard.html", stats=stats)

@view.route('/chatbot')
def chatbot():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))
    return render_template("chatbot.html")

@view.route('/document')
def document():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))
    return render_template("document.html")

@view.route('/activity')
def activity():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))
    progress = db.get_user_progress(session["user_id"])
    stats = db.get_user_stats(session["user_id"])
    return render_template("activity.html", progress=progress, stats=stats)

@view.route('/simplifier')
def simplifier():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))
    return render_template("simplifier.html")

@view.route('/quiz')
def quiz():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))
    return render_template("quiz.html")

@view.route('/pdf-summarizer')
def pdf_summarizer():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))
    return render_template("PDFSummarizer.html")

@view.route('/doc-convert')
def doc_convert():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))
    return render_template("documentConvert.html")

# --- API ROUTES ---

@view.route('/run-magic', methods=['POST'])
def run_magic():

    try:
        data = request.get_json()
        text = data.get('text')
        language = data.get('language', 'Simple English')
        
        simple_text, visual_tags = get_magic_data(text, language)
        
        video_url = ""
        try:
            import gtts
            import os
            audio_filename = f"audio_{os.urandom(4).hex()}.mp3"
            audio_path = os.path.join('static/audio', audio_filename)
            os.makedirs('static/audio', exist_ok=True)
            
            # Limit TTS length for faster hackathon video logic
            short_audio_text = simple_text[:400] 
            tts = gtts.gTTS(text=short_audio_text, lang='hi' if language == 'Hindi' else 'en')
            tts.save(audio_path)

            from modules.video_engine import create_magic_video
            GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
            if not GEMINI_API_KEY:
                print("GEMINI_API_KEY is not set in environment")
            else:
                video_filename = create_magic_video(audio_filename, visual_tags, api_key=GEMINI_API_KEY)
                
                if video_filename:
                    video_url = f"/static/videos/{video_filename}"
        except Exception as ve:
            print(f"Full Video Engine pipeline failed: {ve}")

        db.save_lesson(
            user_id=session.get("user_id"),
            title=text[:30],
            original=text,
            simplified=simple_text,
            audio="CC_VOICE",
            video=video_url
        )

        return jsonify({
            "success": True,
            "simple_text": simple_text,
            "visual_tags": visual_tags,
            "video_url": video_url
        })

    except Exception as e:
        print(f"BACKEND ERROR: {e}")
        return jsonify({"error": str(e)}), 500


@view.route('/generate_quiz', methods=['POST'])
def generate_quiz():
    try:
        context_text = ''
        difficulty = 'simple'
        num = 5

        if request.content_type and request.content_type.startswith('application/json'):
            data = request.get_json() or {}
            context_text = data.get('text', '').strip()
            difficulty = data.get('difficulty', 'simple')
            num = int(data.get('num', 5))
        else:
            # support form + file upload (pdf)
            context_text = request.form.get('text', '').strip()
            difficulty = request.form.get('difficulty', 'simple')
            num = int(request.form.get('num', 5))

            file = request.files.get('file')
            if file and file.filename.lower().endswith('.pdf'):
                import PyPDF2
                reader = PyPDF2.PdfReader(file)
                pdf_text = ''
                for page in reader.pages:
                    text_page = page.extract_text()
                    if text_page:
                        pdf_text += text_page + '\n'
                if pdf_text.strip():
                    context_text = pdf_text.strip()

        if not context_text:
            return jsonify({"success": False, "error": "Please provide text or document content."}), 400

        num = max(5, min(num, 8))

        quiz_content = generate_quiz_content(context_text, difficulty, num)

        if isinstance(quiz_content, list):
            return jsonify({"success": True, "quiz": quiz_content})

        return jsonify({"success": False, "error": "Quiz generation returned unexpected result.", "raw": quiz_content}), 500

    except Exception as e:
        print(f"QUIZ ERROR: {e}")
        return jsonify({"success": False, "error": "Error generating quiz. Please try again."}), 500


@view.route('/submit_quiz', methods=['POST'])
def submit_quiz():
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Unauthorized'}), 401

    try:
        data = request.get_json() or {}
        text = data.get('text', '').strip()
        score = int(data.get('score', 0))
        total = int(data.get('total', 0))
        difficulty = data.get('difficulty', 'simple')
        title = data.get('title', f"Quiz session ({difficulty.capitalize()})")

        # Save the quiz as a lesson and progress record
        lesson_id = db.save_lesson(
            user_id=session.get('user_id'),
            title=title,
            original=text,
            simplified='',
            audio='QUIZ',
            video=''
        )

        if lesson_id:
            db.save_progress(session.get('user_id'), lesson_id, score, difficulty)

        return jsonify({'success': True, 'saved': True, 'score': score, 'total': total})

    except Exception as e:
        print(f"SUBMIT QUIZ ERROR: {e}")
        return jsonify({'success': False, 'error': 'Could not submit quiz results.'}), 500


@view.route('/summarize-pdf', methods=['POST'])
def summarize_pdf():
    try:
        file = request.files.get('file')
        summary_type = request.form.get('summaryType', 'Short')
        output_format = request.form.get('format', 'Paragraph')
        language = request.form.get('language', 'Normal English')

        if not file:
            return jsonify({"error": "No file uploaded"}), 400

        # Extract text from PDF
        import PyPDF2
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"

        if not text.strip():
            return jsonify({"error": "Could not extract text from PDF"}), 400

        result = summarize_text(text, summary_type, output_format, language)
        return jsonify({"success": True, **result})

    except Exception as e:
        print(f"PDF SUMMARIZE ERROR: {e}")
        return jsonify({"error": str(e)}), 500


@view.route('/chatbot-ask', methods=['POST'])
def chatbot_ask():
    if "user_id" not in session:
        return jsonify({"success": False, "error": "Unauthorized"}), 401

    data = request.get_json() or {}
    message = data.get('message', '').strip()
    if not message:
        return jsonify({"success": False, "error": "Empty message provided"}), 400

    from groq import Groq
    from groq import PermissionDeniedError, NotFoundError, BadRequestError
    from dotenv import load_dotenv

    load_dotenv()
    groq_key = os.getenv("GROQ_API_KEY")
    if not groq_key:
        return jsonify({"success": False, "error": "GROQ_API_KEY is not set in environment"}), 500

    client = Groq(api_key=groq_key)

    system_prompt = """You are the SunoPadho Help Assistant — a friendly guide that helps users navigate and use the SunoPadho AI education platform. You should ONLY answer questions related to the application and its features. If a user asks something unrelated, politely redirect them to the app features.

Key app features:
- Dashboard: shows learning stats and quick navigation.
- Magic Simplifier: simplifies text and gives visual tag hints.
- AI Quiz Generator: creates MCQ quizzes from text or topics.
- Document Reader: summarizes PDFs into paragraph or bullets.
- Activity Tracker: records progress and scores.

User guidance:
- Tell them how to use the page they are on, and give concise steps.
- Offer 2-3 example commands they can ask.
- Keep answers short, friendly, and emoji-rich.

If you don't know something, suggest they try existing features or ask a different question."""

    models_to_try = [
        "openai/gpt-oss-120b",
        "moonshotai/kimi-k2-instruct",
        "groq/compound-mini"
    ]

    last_error = None
    for model in models_to_try:
        try:
            completion = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message}
                ],
                temperature=0.5,
                max_tokens=400
            )
            reply = completion.choices[0].message.content
            return jsonify({"success": True, "reply": reply, "model": model})

        except (PermissionDeniedError, NotFoundError, BadRequestError) as e:
            last_error = e
            print(f"CHATBOT model {model} failed: {e}")
            continue

        except Exception as e:
            print(f"CHATBOT unexpected error with model {model}: {e}")
            last_error = e
            continue

    warning_text = f"Unable to complete via AI models: {str(last_error)}"
    fallback = "Hi! I’m SunoPadho assistant, I can’t access AI right now.\n- Try: 'How do I use the Magic Simplifier?' or 'Generate a quiz for chapter text'.\n- Or navigate Dashboard/Quiz/Summarizer from sidebar."

    return jsonify({
        "success": True,
        "reply": fallback,
        "model": None,
        "warning": warning_text
    })