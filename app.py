import os
from flask import Flask, session
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "secretADS-BuiltItOn")

from view import view, auth
app.register_blueprint(view)
app.register_blueprint(auth)

if __name__ == "__main__":
    app.run(debug=True)