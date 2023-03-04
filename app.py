from flask import Flask,render_template,request,flash
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash,check_password_hash



app=Flask(__name__)
# Configure MySQL connection
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'sree123sree'
app.config['MYSQL_DB'] = 'carreira'

mysql = MySQL(app)
app.secret_key = 'bca_6th_sem'
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

@app.route("/register_validate",methods=['POST'])
def register_validate():
    # Get form data
    name = request.form['name']
    email = request.form['email']
    phone= request.form['ph']
    password = request.form['password']
    confirm_password = request.form['confirm_password']

    # Validate form data
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM register WHERE email = %s", (email,))
    user = cur.fetchone()
    if user:
        flash('Email already registered!', 'error')
        return render_template('register.html', name=name, email=email, phone=phone,password=password,confirm_password=confirm_password)
    if not phone.isnumeric() or len(phone) != 10:
        flash('Phone number must be a 10-digit number!', 'error')
        return render_template('register.html', name=name, email=email, phone=phone,password=password,confirm_password=confirm_password)
    if len(password) < 8:
        flash('Password must be at least 8 characters long!', 'error')
        return render_template('register.html', name=name, email=email, phone=phone,password=password,confirm_password=confirm_password)
    if password != confirm_password:
        flash('Confirm password must be same as password', 'error')
        return render_template('register.html', name=name, email=email, phone=phone,password=password,confirm_password=confirm_password)
    hashed_password = generate_password_hash(password)
    cur.execute("INSERT INTO register (name, email, phone, password) VALUES (%s, %s, %s, %s)", (name, email, phone, hashed_password))
    mysql.connection.commit()
    cur.close()
    return render_template('login.html')


    





if __name__=='__main__':
    app.run(debug=True)
#     entered_password = 'password123'
# if check_password_hash(hashed_password, entered_password):
#     # Password is correct
# else:
#     # Password is incorrect
