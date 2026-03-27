import os
from flask import Blueprint, jsonify, render_template, request, redirect, session, url_for
from models import Helper
from modules.ai_engine import generate_magic_lesson, get_magic_data
from modules.video_engine import create_magic_video

view = Blueprint('view', __name__)
auth = Blueprint('auth', __name__)
db = Helper()

# --- 🚪 AUTHENTICATION ROUTES ---

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

# --- 🚀 MAIN VIEW ROUTES ---

@view.route('/dashboard')
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))
    # Optionally fetch recent lessons to show on dashboard
    return render_template("dashboard.html")

@view.route('/chatbot')
def chatbot():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))
    return render_template("chatbot.html") # Make sure this file exists

@view.route('/document')
def document():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))
    return render_template("document.html") # Make sure this file exists
@view.route('/activity')
def activity():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))
    return render_template("activity.html") # Make sure this file exists

@view.route('/simplifier')
def simplifier():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))
    return render_template("simplifier.html") # Renders the UI for magic simplifier

# --- 🪄 MAGIC ENGINE API ---

@view.route('/run-magic', methods=['POST'])
def run_magic():
    try:
        data = request.get_json()
        text = data.get('text')
        
        # 1. AI Logic (Simplified Text + Visual Keywords)
        # Assuming get_magic_data now only returns (simple_text, visual_tags)
        simple_text, visual_tags = get_magic_data(text)
        
        # 2. Video Logic (Optional - set to empty if not ready)
        video_url = "" 
        # video_filename = create_magic_video(visual_tags)
        # video_url = f"/static/videos/{video_filename}"

        # 3. Database Save
        db.save_lesson(
            title=text[:30],
            original=text,
            simplified=simple_text,
            audio="CC_VOICE", # Marking that we use the built-in CC
            video=video_url
        )

        return jsonify({
            "success": True,
            "simple_text": simple_text,
            "visual_tags": visual_tags,
            "video_url": video_url
        })

    except Exception as e:
        print(f"❌ BACKEND ERROR: {e}")
        return jsonify({"error": str(e)}), 500