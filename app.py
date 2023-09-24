from flask import Flask, render_template, request, flash, session,jsonify,redirect
from flask_mysqldb import MySQL
from flask_session import Session
from werkzeug.security import generate_password_hash, check_password_hash
import random
from bs4 import BeautifulSoup
import smtplib
import pandas as pd

app = Flask(__name__)
app.secret_key = "bca_6th_sem"

# Configure MySQL connection
app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = "sree123sree"
app.config["MYSQL_DB"] = "carreira"
mysql = MySQL(app)

# Configure Session
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"

data=pd.read_excel('Carreira.xlsx')


@app.route("/")
def home():
    if not session.get("email"):
        return render_template("home.html",mail='')
    else:
        return render_template("home.html",mail=session['email'])

@app.route("/login")
def login():
    return render_template("login.html")


@app.route("/logout")
def logout():
    session['email']=None
    return redirect("/")


@app.route("/register")
def register():
    return render_template("register.html")


@app.route("/about")
def about():
    if not session.get("email"):
        return render_template("about.html",mail='')
    else:
        return render_template("about.html",mail=session['email'])
    


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
    return render_template("login.html",a=1)


# Define a function to handle the forget password form submission:
@app.route("/forgot_password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        session['email']=None
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
    if user:
        if check_password_hash(user[4], password):
            session["email"] = email
            return redirect("/activity")
         
        else:
            flash("Incorrect Password", "Error")
            return render_template("login.html", email=email)
    else:
        flash("This email is not registered", "Error")
        return render_template("login.html")


@app.route("/get_started")
def get_started():
    if not session.get("email"):
        return render_template("login.html")
    else:
        return redirect("/activity")


@app.route("/activity")
def activity():
    if not session.get("email"):
        return render_template("activity.html",mail="")
    else:
        return render_template("activity.html",mail=session['email'])


@app.route('/cources')
def cources():
    if not session.get("email"):
        return render_template("cources.html",mail='')
    else:
        return render_template("cources.html",mail=session['email'])


@app.route('/search')
def search():
   
    query = request.args.get('query', '')
    filtered_df = data[data['Course'].str.contains(query, case=False)]
    results = filtered_df['Course'].tolist()
    
    return jsonify(results)


@app.route('/search_query',methods=['POST'])
def search_query():
    query=request.form['search_query']
    filtered_df = data[data['Course'].str.contains(query, case=False)]
    results = filtered_df['Description'].tolist()
    results_course= filtered_df['Course'].tolist()

    if len(results) == 0:
        for i in range(data.shape[0]): 
            if query.lower() in data.loc[i][2].lower():
                results=[(data.loc[i][5])]
                results_course=[(data.loc[i][2])]
    details=[]
    for i in range(len(results)):
        details.append([results[i],results_course[i]])
    for i in details:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM course WHERE Course_name = %s", (i[1],))
        user = cur. fetchone()
        if user:
            cur.execute(
            "UPDATE course SET Views = %s WHERE Course_name = %s",
            (user[2]+1, i[1]),
            )
            mysql.connection.commit()
            cur.close()
        else:
            cur.execute(
            "INSERT INTO course (Course_name,Views) VALUES (%s, %s)",
            (i[1],1),
            )
            mysql.connection.commit()
            cur.close()
    if not session.get("email"):
        return render_template("cources.html",details=details,mail="")
    else:
        return render_template("cources.html",details=details,mail=session['email'])


@app.route("/arts_choice")
def arts_choice():
    session["stream"]="Arts"
    if not session.get("email"):
        return render_template("arts_choice.html",mail='')
    else:
        return render_template("arts_choice.html",mail=session['email'])


@app.route("/commerce_choice")
def commerce_choice():
    session["stream"]="Commerce"
    if not session.get("email"):
        return render_template("commerce_choice.html",mail='')
    else:
        return render_template("commerce_choice.html",mail=session['email'])


@app.route("/science_choice")
def science_choice():
    session["stream"]="Science"
    if not session.get("email"):
        return render_template("science_choice.html",mail='')
    else:
        return render_template("science_choice.html",mail=session['email'])
    

@app.route('/submit_images', methods=['POST'])
def submit_images():
    # Get the selected images from the request body
    selected_images = request.get_json()
    session['choice']=selected_images
    return "Success"
    

@app.route('/interest')
def interest():
    if session["stream"] =='Arts':
        new_data=data.loc[(data['Stream'] == 'Arts')]
        
    elif session["stream"] =='Commerce':
        new_data=data.loc[(data['Stream'] == 'Arts') | (data['Stream'] == 'Commerce')]
       
    elif session["stream"] =='Science':
        new_data=data
    new_data=new_data.reset_index(drop=True)
    
    
    new_result=[]
    for i in session['choice']:
        filtered_df = new_data[new_data['Key Word'].str.contains(i, case=False)]
        results = filtered_df['Interests'].tolist()
        new_result.append(results)
    result = [s for sublist in new_result for s in sublist if isinstance(sublist, list)]
    final_result = [item.strip() for s in result for item in s.split(",")]
    final_result=set(final_result)
    if not session.get("email"):
        return render_template("interest.html",result=final_result,mail='')
    else:  
        return render_template("interest.html",result=final_result,mail=session["email"])


@app.route("/final",methods=['POST'])
def final():
    interest=request.form.getlist("Course")
    if session["stream"] =='Arts':
        new_data=data.loc[(data['Stream'] == 'Arts')]
        
    elif session["stream"] =='Commerce':
        new_data=data.loc[(data['Stream'] == 'Arts') | (data['Stream'] == 'Commerce')]
       
    elif session["stream"] =='Science':
        new_data=data
    new_data=new_data.reset_index(drop=True)
    
    store=[]
    for i in range(new_data.shape[0]):
        for j in interest:
            if j.lower() in new_data.loc[i][3].lower():
                store.append([new_data.loc[i][2],new_data.loc[i][5]])
    store.reverse()
    for i in store:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM course WHERE Course_name = %s", (i[0],))
        user = cur. fetchone()
        if user:
            cur.execute(
            "UPDATE course SET Views = %s WHERE Course_name = %s",
            (user[2]+1, i[0]),
            )
            mysql.connection.commit()
            cur.close()
        else:
            cur.execute(
            "INSERT INTO course (Course_name,Views) VALUES (%s, %s)",
            (i[0],1),
            )
            mysql.connection.commit()
            cur.close()
    if not session.get("email"):
        return render_template("final.html",result=store,mail='')
    else:  
        return render_template("final.html",result=store,mail=session["email"])


    
if __name__ == "__main__":
    app.run(debug=True)
    # app.run(host='192.168.191.50',port='5000',debug=True)
   
