# Medicine_Remainder
🏥 Medicine Reminder System with SMS Notifications

📌 Project Description
The Medicine Reminder System is a web-based application designed to help patients manage and track their medicines easily. It allows users to register, log in, and add their medicines with a simple interface. The system ensures that medicines are taken on time by sending SMS notifications to the registered mobile number.
This project solves a real-world problem — people often forget to take their medicines on time, which can affect their health. With this system, users get notified instantly whenever they add a medicine or if they miss it, helping them stay consistent with their prescriptions.

🎯 Key Features:-

1.User Authentication

💠Patients can register with name, email, mobile number, and password.

💠Secure login system for accessing their dashboard.

2.Medicine Management

💠Patients can add medicines from their dashboard.

💠All medicines are linked to the logged-in user only.

💠Medicines marked as taken disappear automatically.

If marked as missed, they remain visible under "missed medicines".

3.SMS Notifications (via Twilio API)

💠Sends SMS to the patient’s registered mobile number when a medicine is added.

💠Sends SMS alerts if a medicine is marked as missed.

4.Personalized Dashboard

💠Displays only the current user’s medicines.

💠Shows pending and missed medicines, hides those already taken.

4.MongoDB Integration

💠Stores patient details and medicine records.

💠Each medicine entry is linked to the corresponding user (by email).

⚙️ Tech Stack

✓Frontend: HTML, CSS (for dashboard and forms)

✓Backend: Python (Flask Framework)

✓Database: MongoDB (for storing users and medicines)

✓Notifications: Twilio SMS API

✓Template Engine: Jinja2 (Flask’s default)

📌 Usefulness in Day-to-Day Life

⁕Helps patients remember their medicines.

⁕Reduces chances of missed or wrong doses.

⁕Can be expanded to include email reminders, doctor’s notes, or scheduling.

⁕Useful for elderly patients or chronic disease management.
