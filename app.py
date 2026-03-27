from flask import Flask,session

app = Flask(__name__)
app.secret_key = "secretADS-BuiltItOn"
from view import view,auth
app.register_blueprint(view)
app.register_blueprint(auth)


if __name__ == "__main__":
    app.run(debug=True)