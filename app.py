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

    age = db.Column(db.Integer)

    weight = db.Column(db.Float)

    height = db.Column(db.Float)

    goal = db.Column(db.String(100))

    activity = db.Column(db.String(100))

    diet = db.Column(db.String(100))
class Progress(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))

    current_weight = db.Column(db.Float)

    energy = db.Column(db.Integer)

    sleep = db.Column(db.Integer)

    notes = db.Column(db.Text)

    created_at = db.Column(db.DateTime, default=db.func.now())
@login_manager.user_loader
def load_user(user_id): 
    return db.session.get(User, int(user_id))


@app.route("/")
@login_required
def home():
    return render_template(
        "index.html",
        user=current_user
    )
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
@login_required
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

        if current_user.is_authenticated:
           current_user.age = age
           current_user.weight = weight
           current_user.height = height
           current_user.goal = goal
           current_user.activity = activity
           current_user.diet = diet

        db.session.commit()

        prompt = f"""
You are an expert fitness coach.

User Details:
Name: {name}
Age: {age}
Weight: {weight} kg
Height: {height} cm
BMI: {bmi}
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

        error = str(e)

    if "RESOURCE_EXHAUSTED" in error or "429" in error:
        message = (
            "⚠️ AI Plan Generator is temporarily unavailable because the daily request limit has been reached."
        )

    elif "503" in error:
        message = (
            "⚠️ AI Plan Generator is currently busy. Please try again shortly."
        )

    else:
        message = (
            "⚠️ Unable to generate your fitness plan at the moment. Please try again later."
        )

    return jsonify({
        "success": False,
        "bmi": "",
        "plan": message
    }), 500

@app.route("/analyze_week", methods=["POST"])
@login_required
def analyze_week():

    try:
        data = request.get_json()

        current_weight = data["currentWeight"]
        energy = data["energy"]
        sleep = data["sleep"]
        notes = data["notes"]

        # Save progress in database
        progress = Progress(
            user_id=current_user.id,
            current_weight=current_weight,
            energy=energy,
            sleep=sleep,
            notes=notes
        )

        db.session.add(progress)
        db.session.commit()

        prompt = f"""
You are an expert fitness coach.

Analyze this weekly fitness report.

Current Weight: {current_weight} kg
Energy Level: {energy}/5
Sleep Quality: {sleep}/5

Weekly Notes:
{notes}

Generate:

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

        message = str(e)

    if "RESOURCE_EXHAUSTED" in message or "429" in message:
        answer = "⚠️ GRINDBOT AI has reached the daily free API limit. Please try again later."
    elif "503" in message:
        answer = "⚠️ GRINDBOT AI is temporarily busy. Please try again in a few moments."
    else:
        answer = "⚠️ An unexpected error occurred. Please try again."

    return jsonify({
        "answer": answer
    }), 500
@app.route("/history")
@login_required
def history():

    history = Progress.query.filter_by(
        user_id=current_user.id
    ).order_by(
        Progress.created_at.desc()
    ).all()

    return render_template(
        "history.html",
        history=history
    )
@app.route("/chat_ai", methods=["POST"])
@login_required
def chat_ai():

    try:
        data = request.get_json()

        question = data["question"]

        prompt = f"""
You are GRINDBOT, an expert AI Fitness & Nutrition Coach.

The user asked:

{question}

Rules:
- Give beginner-friendly advice.
- Keep the answer clear and practical.
- If nutrition is asked, suggest healthy foods.
- If workouts are asked, suggest safe exercises.
- Motivate the user at the end.
- Keep the answer under 300 words.
"""

        response = client.models.generate_content(
            model="gemini-2.5-flash-lite",
            contents=prompt
        )

        return jsonify({
            "answer": response.text
        })

    except Exception as e:
        traceback.print_exc()


        return jsonify({
        "answer": "⚠️ GRINDBOT AI is currently busy. Please try again in a few moments."
    }), 500
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)