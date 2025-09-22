from flask import Flask, render_template, request, redirect, session
from pymongo import MongoClient
from datetime import datetime
from bson.objectid import ObjectId
import hashlib
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.date import DateTrigger
from twilio.rest import Client

app = Flask(__name__)
app.secret_key = "supersecretkey"  # change this in real project

# MongoDB connection
client = MongoClient("mongodb://localhost:27017/")
db = client["medicine_db"]
users = db["users"]
reminders = db["reminders"]

# Twilio configuration
TWILIO_ACCOUNT_SID = "AC2a0654e97aa82b0d922e0d70ad644be8"
TWILIO_AUTH_TOKEN = "39ccbc11bc882a8aab6009b2a40a413b"
TWILIO_PHONE_NUMBER = "+12602977969"  # your Twilio number in E.164 format
twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# Password hashing
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Initialize APScheduler
scheduler = BackgroundScheduler()
scheduler.start()

# Function to send SMS
def send_sms(to, message):
    try:
        twilio_client.messages.create(
            body=message,
            from_=TWILIO_PHONE_NUMBER,
            to=to
        )
        print(f"SMS sent to {to}")
    except Exception as e:
        print(f"Failed to send SMS to {to}: {e}")

# Function to schedule medicine reminders
def schedule_reminder(med):
    # Get user from DB
    user = users.find_one({"_id": ObjectId(med["user_id"])})
    if not user or not user.get("mobile"):
        print("No mobile number found for user.")
        return

    # Ensure mobile number has +countrycode format
    mobile_number = user["mobile"]
    if not mobile_number.startswith("+"):
        print("Mobile number must include country code in E.164 format, e.g., +911234567890")
        return

    # Convert date + time to datetime
    med_datetime = datetime.strptime(f"{med['date']} {med['time']}", "%Y-%m-%d %H:%M")
    message = f"Hello {user['name']}, it's time to take your medicine: {med['medicine_name']} ({med['dosage']})."

    # Job that sends SMS and updates reminder status
    def reminder_job():
        print(f"Triggering reminder for {user['name']}")
        send_sms(mobile_number, message)
        reminders.update_one({"_id": ObjectId(med["_id"])}, {"$set": {"status": "pending"}})

    trigger = DateTrigger(run_date=med_datetime)
    scheduler.add_job(reminder_job, trigger=trigger)
    print(f"Reminder scheduled for {mobile_number} at {med_datetime}")

@app.route("/")
def home():
    if "user_id" not in session:
        return redirect("/login")

    today = datetime.now().strftime("%Y-%m-%d")
    meds = reminders.find({
        "user_id": session["user_id"],
        "date": today,
        "status": {"$in": ["pending", "missed"]}
    })

    formatted_meds = []
    for med in meds:
        time_24 = med["time"]
        time_12 = datetime.strptime(time_24, "%H:%M").strftime("%I:%M %p")
        med["time"] = time_12
        formatted_meds.append(med)

    return render_template("index.html", meds=formatted_meds, user_name=session["name"])

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = hash_password(request.form["password"])
        mobile = request.form["mobile"]

        # check if user already exists
        if users.find_one({"email": email}):
            return "⚠️ Email already registered. Please login."

        # Store mobile number in E.164 format (example for India)
        if not mobile.startswith("+"):
            mobile = "+91" + mobile  # change country code as needed

        user_id = users.insert_one({
            "name": name,
            "email": email,
            "password": password,
            "mobile": mobile
        }).inserted_id

        # auto login after register
        session["user_id"] = str(user_id)
        session["name"] = name
        return redirect("/")

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = hash_password(request.form["password"])
        user = users.find_one({"email": email, "password": password})

        if user:
            session["user_id"] = str(user["_id"])
            session["name"] = user["name"]
            return redirect("/")
        else:
            return "❌ Invalid email or password"

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

@app.route("/add", methods=["POST"])
def add_medicine():
    if "user_id" not in session:
        return redirect("/login")

    medicine_name = request.form["name"]
    dosage = request.form["dosage"]
    time = request.form["time"]

    data = {
        "user_id": session["user_id"],
        "medicine_name": medicine_name,
        "dosage": dosage,
        "time": time,
        "date": datetime.now().strftime("%Y-%m-%d"),
        "status": "pending"
    }
    med_id = reminders.insert_one(data).inserted_id
    data["_id"] = med_id

    # Schedule SMS reminder
    schedule_reminder(data)

    return redirect("/")

@app.route("/update/<id>/<status>")
def update_status(id, status):
    reminders.update_one({"_id": ObjectId(id)}, {"$set": {"status": status}})
    return redirect("/")

@app.route("/history")
def history():
    if "user_id" not in session:
        return redirect("/login")

    today = datetime.now().strftime("%Y-%m-%d")
    meds = reminders.find({"user_id": session["user_id"], "date": today})

    formatted_meds = []
    for med in meds:
        time_24 = med["time"]
        time_12 = datetime.strptime(time_24, "%H:%M").strftime("%I:%M %p")
        med["time"] = time_12
        formatted_meds.append(med)

    return render_template("history.html", meds=formatted_meds, user_name=session["name"])

if __name__ == "__main__":
    app.run(debug=True)
