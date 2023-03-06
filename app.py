from flask import Flask, render_template, request, flash, url_for, session, redirect
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
import random
import smtplib


app = Flask(__name__)
app.secret_key = "bca_6th_sem"

# Configure MySQL connection
app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = "sree123sree"
app.config["MYSQL_DB"] = "carreira"
mysql = MySQL(app)


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/login")
def login():
    return render_template("login.html")


@app.route("/register")
def register():
    return render_template("register.html")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/forgotpassword")
def otp():
    return render_template("forgot_password.html")


@app.route("/register_validate", methods=["POST"])
def register_validate():
    # Get form data
    name = request.form["name"]
    email = request.form["email"]
    email = email.strip()
    phone = request.form["ph"]
    password = request.form["password"]
    password = password.strip()
    confirm_password = request.form["confirm_password"]

    # Validate form data
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM register WHERE email = %s", (email,))
    user = cur.fetchone()
    if user:
        flash("Email already registered!", "error")
        return render_template(
            "register.html",
            name=name,
            email=email,
            phone=phone,
            password=password,
            confirm_password=confirm_password,
        )
    if not phone.isnumeric() or len(phone) != 10:
        flash("Phone number must be a 10-digit number!", "error")
        return render_template(
            "register.html",
            name=name,
            email=email,
            phone=phone,
            password=password,
            confirm_password=confirm_password,
        )
    if len(password) < 8:
        flash("Password must be at least 8 characters long!", "error")
        return render_template(
            "register.html",
            name=name,
            email=email,
            phone=phone,
            password=password,
            confirm_password=confirm_password,
        )
    if password != confirm_password:
        flash("Confirm password must be same as password", "error")
        return render_template(
            "register.html",
            name=name,
            email=email,
            phone=phone,
            password=password,
            confirm_password=confirm_password,
        )
    hashed_password = generate_password_hash(password)
    cur.execute(
        "INSERT INTO register (name, email, phone, password) VALUES (%s, %s, %s, %s)",
        (name, email, phone, hashed_password),
    )
    mysql.connection.commit()
    cur.close()
    return render_template("login.html")


# Define a function to handle the forget password form submission:
@app.route("/forgot_password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email = request.form["email"]
        email = email.strip()
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM register WHERE email = %s", (email,))
        user = cur.fetchone()
        if user:
            session["email"] = email
            if email:
                otp = random.randint(100000, 999999)
                gmail_user = "carreiraofficial@gmail.com"
                gmail_password = "fafcmqnqlxrzedxw"
                session["otp"] = otp
                print(email)

                sent_from = gmail_user
                to = [email]
                subject = "OTP for Forget Password"
                body = "Your OTP is: " + str(otp)

                email_text = "Subject: {}\n\n{}".format(subject, body)

                smtp_server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
                smtp_server.ehlo()
                smtp_server.login(gmail_user, gmail_password)
                smtp_server.sendmail(sent_from, to, email_text)
                smtp_server.close()
                flash("Email sent successfully!", "Success")
                return render_template("forgot_password.html", email=email)
            else:
                return render_template(
                    "forgot_password.html", error="Please enter your email"
                )
        else:
            flash("This Email is not registered!", "Error")
            return render_template("forgot_password.html")

    else:
        return render_template("forgot_password.html")


# Define a function to handle OTP verification:
@app.route("/verify_otp", methods=["GET", "POST"])
def verify_otp():
    if request.method == "POST":
        # Retrieve the OTP for this email from the database
        otp = request.form["otp"]

        # Check if the user entered the correct OTP
        if session["otp"] == None:
            return render_template("forgot_password.html", otp="")
        ch_otp = session["otp"]
        if int(ch_otp) == int(otp):
            session["otp"] = None
            # OTP verification succeeded, redirect to reset password page
            return render_template("change_password.html")
        else:
            flash("Incorrect OTP!", "Error")
            return render_template("forgot_password.html", email=session["email"])


@app.route("/set_password", methods=["POST"])
def set_password():
    password = request.form["password"]
    if len(password) < 8:
        flash("Password must be at least 8 characters long!", "error")
        return render_template("change_password.html")
    else:
        new_password = generate_password_hash(password)
        cur = mysql.connection.cursor()
        cur.execute(
            "UPDATE register SET password = %s WHERE email = %s",
            (new_password, session["email"]),
        )
        mysql.connection.commit()
        cur.close()
        session["email"] = None
        return render_template("login.html")


@app.route("/login_validate", methods=["POST"])
def login_validate():
    email = request.form["email"]
    password = request.form["password"]
    email = email.strip()
    password = password.strip()
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM register WHERE email = %s", (email,))
    user = cur.fetchone()
    print(user)
    if user:
        if check_password_hash(user[4], password):
            session["email"] = email
            return render_template("activity.html")
        else:
            flash("Incorrect Password", "Error")
            return render_template("login.html", email=email)
    else:
        flash("This email not registered", "Error")
        return render_template("login.html")


@app.route("/get_started")
def get_started():
    if session == {}:
        return render_template("login.html")
    else:
        return render_template("activity.html")


if __name__ == "__main__":
    app.run(debug=True)
