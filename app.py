from flask import Flask, render_template, request, jsonify, redirect, url_for
from google import genai
from dotenv import load_dotenv
import os
import traceback
from flask_sqlalchemy import SQLAlchemy
from flask_login import (
    LoginManager,
    UserMixin,
    login_user,
    login_required,
    logout_user,
    current_user
)

# Load .env file
load_dotenv()

# Create Gemini client
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

app = Flask(__name__)
app.config["SECRET_KEY"] = "grindbot-secret-key"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.String(100), unique=True, nullable=False)

    email = db.Column(db.String(100), unique=True, nullable=False)

    password = db.Column(db.String(100), nullable=False)
@login_manager.user_loader
def load_user(user_id): 
    return User.query.get(int(user_id))


@app.route("/")
@login_required
def home():
    return render_template("index.html")
@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        if User.query.filter_by(email=email).first():
            return "Email already exists!"

        user = User(
            username=username,
            email=email,
            password=password
        )

        db.session.add(user)
        db.session.commit()

        return redirect(url_for("login"))

    return render_template("register.html")
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        user = User.query.filter_by(email=email).first()

        if user and user.password == password:
            login_user(user)
            return redirect(url_for("home"))

        return "Invalid Email or Password"

    return render_template("login.html")
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))


@app.route("/test")
def test():
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents="Say Hello"
        )
        return response.text
    except Exception as e:
        traceback.print_exc()
        return str(e)


@app.route("/generate_plan", methods=["POST"])
def generate_plan():
    try:
        data = request.get_json()

        name = data["name"]
        age = data["age"]
        weight = data["weight"]
        height = data["height"]
        goal = data["goal"]
        activity = data["activity"]
        diet = data["diet"]

        bmi = round(weight / ((height / 100) ** 2), 2)

        prompt = f"""
You are an expert fitness coach.

User Details:
Name: {name}
Age: {age}
Weight: {weight} kg
Height: {height} cm
BMI: {bmi}
Goal: {goal}
Goal: {goal}
Activity Level: {activity}
Diet Preference: {diet}

Generate:

1. A beginner-friendly 7-day workout plan.
2. A healthy Indian diet plan.
3. Three fitness tips.

Keep the response simple and easy to understand.
"""

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        return jsonify({
            "bmi": bmi,
            "plan": response.text
        })

    except Exception as e:
        traceback.print_exc()

        return jsonify({
            "bmi": "",
            "plan": f"Error: {str(e)}"
        }), 500

@app.route("/analyze_week", methods=["POST"])
def analyze_week():

    try:
        data = request.get_json()

        current_weight = data["currentWeight"]
        energy = data["energy"]
        sleep = data["sleep"]
        notes = data["notes"]

        prompt = f"""
You are an expert fitness coach.

Analyze this weekly fitness report.

Current Weight: {current_weight} kg
Energy Level: {energy}/5
Sleep Quality: {sleep}/5

Weekly Notes:
{notes}

Generate:

Generate a professional fitness report.

Include:

1. Personalized Workout

2. Personalized Diet

3. BMI Analysis

4. Daily Water Intake

5. Calories Recommendation

6. Protein Recommendation

7. Motivation Quote

8. Safety Tips

9. Weekly Goal

10. Final Summary

Keep the response motivational and beginner friendly.
"""

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        return jsonify({
            "report": response.text
        })

    except Exception as e:
        traceback.print_exc()

        return jsonify({
            "report": str(e)
        }), 500
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)