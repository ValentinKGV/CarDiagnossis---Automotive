from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import math
import obd

app = Flask(__name__)
app.secret_key = 'super_secret_key'

# conexiune globala OBD
obd_connection = None

def init_obd():
    global obd_connection
    try:
        obd_connection = obd.OBD("COM8", fast=False, timeout=1)
        print("OBD connected")
    except Exception as e:
        print("OBD connection failed:", e)

init_obd()

# initializare baza de date
def init_db():
    conn = sqlite3.connect("obd_data.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        power_kw REAL NOT NULL
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS date_extinse (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        timestamp TEXT,
        rpm INTEGER,
        speed INTEGER,
        torque REAL,
        coolant_temp INTEGER,
        intake_pressure INTEGER,
        battery_voltage REAL
    )''')
    conn.commit()
    conn.close()

init_db()

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("obd_data.db")
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=?", (username,))
        user = c.fetchone()
        conn.close()

        if user and check_password_hash(user[2], password):
            session["logged_in"] = True
            session["username"] = username
            session["user_id"] = user[0]
            session["power_kw"] = user[3]
            return redirect(url_for("dashboard"))
        else:
            return render_template("login.html", error="Invalid credentials.")
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        power_kw = request.form["power_kw"]

        if not power_kw.replace('.', '', 1).isdigit():
            return render_template("register.html", error="Invalid power (kW).")

        hashed = generate_password_hash(password)

        try:
            conn = sqlite3.connect("obd_data.db")
            c = conn.cursor()
            c.execute("INSERT INTO users (username, password, power_kw) VALUES (?, ?, ?)",
                      (username, hashed, float(power_kw)))
            conn.commit()
            conn.close()
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            return render_template("register.html", error="Username already exists.")
    return render_template("register.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/dashboard")
def dashboard():
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    return render_template("dashboard.html", username=session["username"])

@app.route("/extended")
def extended():
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    return render_template("extended.html")

@app.route("/extended/data")
def extended_data():
    if not session.get("logged_in") or not obd_connection or not obd_connection.is_connected():
        return jsonify([])

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def get_value(cmd):
        try:
            response = obd_connection.query(cmd)
            return response.value.magnitude if response and response.value is not None else None
        except:
            return None

    rpm = get_value(obd.commands.RPM)
    speed = get_value(obd.commands.SPEED)
    coolant_temp = get_value(obd.commands.COOLANT_TEMP)
    intake_pressure = get_value(obd.commands.INTAKE_PRESSURE)
    battery_voltage = get_value(obd.commands.CONTROL_MODULE_VOLTAGE)
    engine_load = get_value(obd.commands.ENGINE_LOAD)

    if battery_voltage is not None:
        battery_voltage = round(battery_voltage, 2)

    power_kw = session.get("power_kw", 0)
    torque = None
    if rpm and engine_load:
        try:
            torque = ((60000 / (2 * math.pi)) * (`power_kw` * (engine_load / 100))) / rpm
            torque = round(torque, 2)
        except:
            torque = None

    user_id = session["user_id"]

    conn = sqlite3.connect("obd_data.db")
    c = conn.cursor()
    c.execute('''INSERT INTO date_extinse (user_id, timestamp, rpm, speed, torque, coolant_temp,
                 intake_pressure, battery_voltage)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
              (user_id, timestamp, rpm, speed, torque, coolant_temp,
               intake_pressure, battery_voltage))
    conn.commit()

    c.execute("SELECT timestamp, rpm, speed, torque, coolant_temp, intake_pressure, battery_voltage FROM date_extinse WHERE user_id = ? ORDER BY timestamp DESC LIMIT 10", (user_id,))
    data = c.fetchall()
    conn.close()

    return jsonify(data)

@app.route("/istoric")
def istoric():
    if not session.get("logged_in"):
        return redirect(url_for("login"))

    user_id = session["user_id"]
    conn = sqlite3.connect("obd_data.db")
    c = conn.cursor()
    c.execute("SELECT * FROM date_extinse WHERE user_id = ? ORDER BY timestamp DESC LIMIT 50", (user_id,))
    data = c.fetchall()
    conn.close()

    return render_template("istoric.html", data=data)

# ✅ Verificare parametri optimali
@app.route("/check")
def check():
    if not session.get("logged_in"):
        return redirect(url_for("login"))

    conn = sqlite3.connect("obd_data.db")
    c = conn.cursor()
    c.execute('''
        SELECT coolant_temp, battery_voltage, intake_pressure
        FROM date_extinse
        WHERE user_id = ?
        ORDER BY timestamp DESC
        LIMIT 1
    ''', (session["user_id"],))
    row = c.fetchone()
    conn.close()

    if not row:
        verdict = "No data available."
    else:
        coolant, voltage, intake = row
        if 70 <= coolant <= 110 and 12.0 <= voltage <= 14.5 and 90 <= intake <= 110:
            verdict = "Your car is running fine."
        else:
            verdict = "Your car should be checked by a specialist."

    return render_template("check.html", verdict=verdict)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
