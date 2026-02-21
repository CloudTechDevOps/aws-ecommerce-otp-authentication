import os
import random
from datetime import datetime, timedelta
from flask import Flask, request, jsonify
import pymysql
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mail import Mail, Message

app = Flask(__name__)
CORS(app)

# ---------------- CONFIGURATION ----------------
db_config = {
    "host": "dev.c8h8simk8khk.us-east-1.rds.amazonaws.com",
    "user": "admin",
    "password": "Cloud123",
    "database": "cloud"
}

# GMAIL CONFIG - Use a Google App Password here!
app.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT=587,
    MAIL_USE_TLS=True,
    MAIL_USERNAME='vvardhan2211@gmail.com', 
    MAIL_PASSWORD='czvk tjjz kiea qrbu' 
)
mail = Mail(app)

# Temp storage for registrations waiting for OTP verification
pending_users = {}

def get_db_connection():
    return pymysql.connect(
        host=db_config["host"],
        user=db_config["user"],
        password=db_config["password"],
        database=db_config["database"],
        cursorclass=pymysql.cursors.DictCursor
    )
# ---------------- HEALTH CHECK ----------------
@app.route('/api/health', methods=['GET'])
def health_check():
    # ALB calls this every 30 seconds to verify the app is running
    return jsonify({'status': 'healthy'}), 200

# ---------------- SIGNUP LOGIC (2 STEPS) ----------------

@app.route("/api/signup/request", methods=["POST"])
def signup_request():
    data = request.get_json()
    email = data.get("email")
    username = data.get("username")
    
    # Generate 6-digit OTP
    otp = str(random.randint(100000, 999999))
    
    # Store user data temporarily
    pending_users[email] = {
        "username": username,
        "password": generate_password_hash(data.get("password")),
        "otp": otp,
        "expiry": datetime.now() + timedelta(minutes=10)
    }

    try:
        msg = Message("Google Store - Verify Registration", sender=app.config['MAIL_USERNAME'], recipients=[email])
        msg.body = f"Hello {username}, your registration  from veera sir naresh itOTP is {otp}. It expires in 10 minutes."
        mail.send(msg)
        return jsonify({"message": "OTP sent to email!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/signup/verify", methods=["POST"])
def signup_verify():
    data = request.get_json()
    email = data.get("email")
    user_otp = data.get("otp")

    user = pending_users.get(email)
    if user and user['otp'] == user_otp and datetime.now() < user['expiry']:
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            sql = "INSERT INTO users (username, email, password) VALUES (%s, %s, %s)"
            cursor.execute(sql, (user['username'], email, user['password']))
            conn.commit()
            del pending_users[email]
            return jsonify({"message": "Account created successfully!"}), 201
        except Exception as e:
            return jsonify({"error": "User already exists"}), 400
    return jsonify({"error": "Invalid or expired OTP"}), 401

# ---------------- LOGIN LOGIC (2 STEPS) ----------------

@app.route("/api/login/request", methods=["POST"])
def login_request():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
    user = cursor.fetchone()

    if user and check_password_hash(user["password"], password):
        otp = str(random.randint(100000, 999999))
        expiry = datetime.now() + timedelta(minutes=5)
        
        # Store OTP in DB for existing user
        cursor.execute("UPDATE users SET otp_code = %s, otp_expiry = %s WHERE email = %s", 
                       (otp, expiry, email))
        conn.commit()
        
        msg = Message("Google Store - Login OTP", sender=app.config['MAIL_USERNAME'], recipients=[email])
        msg.body = f"Your login OTP from veera sir naresh it is {otp}. It expires in 5 minutes."
        mail.send(msg)
        
        return jsonify({"message": "OTP sent to email"}), 200
    
    return jsonify({"error": "Invalid credentials"}), 401

@app.route("/api/login/verify", methods=["POST"])
def login_verify():
    data = request.get_json()
    email = data.get("email")
    user_otp = data.get("otp")

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email = %s AND otp_code = %s", (email, user_otp))
    user = cursor.fetchone()

    if user and datetime.now() < user["otp_expiry"]:
        return jsonify({
            "message": "Login successful",
            "user": {"username": user["username"], "email": user["email"]}
        }), 200
    
    return jsonify({"error": "Invalid or expired OTP"}), 401

if __name__ == "__main__":

    app.run(host="0.0.0.0", port=5000, debug=True)
