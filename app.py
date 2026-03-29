import os
from flask import Flask, session
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", os.urandom(32).hex())

# Session configuration
app.permanent_session_lifetime = timedelta(hours=2)  # Sessions expire after 2 hours

# Initialize CSRF protection
csrf = CSRFProtect(app)

# Initialize rate limiter
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"]
)

from view import view, auth
app.register_blueprint(view)
app.register_blueprint(auth)

if __name__ == "__main__":
    app.run(debug=True)