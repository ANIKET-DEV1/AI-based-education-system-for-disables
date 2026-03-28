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
        
        simple_text, visual_tags = get_magic_data(text)
        
        video_url = ""

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
        data = request.get_json()
        categories = data.get('categories', [])
        difficulty = data.get('difficulty', 'Easy')
        num = data.get('num', '5')

        quiz_text = generate_quiz_content(categories, difficulty, num)
        return jsonify({"quiz": quiz_text})

    except Exception as e:
        print(f"QUIZ ERROR: {e}")
        return jsonify({"quiz": "Error generating quiz. Please try again."}), 500


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
    try:
        data = request.get_json()
        message = data.get('message', '')

        from groq import Groq
        client = Groq(api_key=os.getenv("GROQ_API_KEY"))

        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a helpful, patient AI tutor for students with learning disabilities. Use simple words, short sentences, and be encouraging. Explain concepts in an easy-to-understand way."},
                {"role": "user", "content": message}
            ],
            temperature=0.7,
            max_tokens=500
        )

        reply = completion.choices[0].message.content
        return jsonify({"success": True, "reply": reply})

    except Exception as e:
        print(f"CHATBOT ERROR: {e}")
        return jsonify({"error": str(e)}), 500