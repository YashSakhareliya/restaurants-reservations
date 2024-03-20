import smtplib
from datetime import datetime
import json
import mysql.connector
from flask import Flask, render_template, request, redirect, url_for,session
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os,secrets
from werkzeug.security import generate_password_hash, check_password_hash

# Load configurations from JSON file
with open('templates/config.json', 'r') as c:
    params = json.load(c)["params"]

app = Flask(__name__)
# secret_key = secrets.token_hex(32)
# 9501d48e0af1bbfb07ca7b63676dc401b5908753854c1a5ce5f9de63f8333667

# print(secret_key)
# app.secret_key = '9501d48e0af1bbfb07ca7b63676dc401b5908753854c1a5ce5f9de63f8333667'
app.secret_key = os.environ.get('SECRET_KEY') or 'default_secret_key'

# MySQL configurations
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'root',
    'database': 'food',
}

# Email configurations
email_config = {
    'smtp_server': 'smtp.gmail.com',
    'smtp_port': 587,
    'sender_email': params['Gmail_username'],
    'sender_password': 'qptw phiy igkh iikr'
}


# Function to execute MySQL queries
def get_db_connection():
    return mysql.connector.connect(**db_config)


# Create contact table if not exists
def create_contact_table():
    conn = get_db_connection()
    cursor = conn.cursor()
    create_contact_table_query = ("""
    CREATE TABLE IF NOT EXISTS contact (
        id INT AUTO_INCREMENT PRIMARY KEY,
        Name VARCHAR(255) NOT NULL,
        Email VARCHAR(255) NOT NULL,
        Message VARCHAR(255) NOT NULL,
        Date DATETIME NOT NULL)
    """)
    cursor.execute(create_contact_table_query)
    conn.commit()
    cursor.close()
    conn.close()


# Create sign up table if not exists
def create_signup():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""create table if not exists signup (
        id INT AUTO_INCREMENT PRIMARY KEY,
        email VARCHAR(255) NOT NULL,
        password VARCHAR(255) NOT NULL,
        register_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""")
    conn.commit()
    cursor.close()
    conn.close()

def create_login_activity():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""create table if not exists Login_activity (
        id INT AUTO_INCREMENT PRIMARY KEY,
        email VARCHAR(255) NOT NULL,
        login_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""")
    conn.commit()
    cursor.close()
    conn.close()

create_login_activity()



# Create reservation table if not exists
def create_reserve_table():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS reservedtable(
    id INT AUTO_INCREMENT PRIMARY KEY,
    fname VARCHAR(255) NOT NULL,
    lname VARCHAR(255) NOT NULL,
    Email VARCHAR(255) NOT NULL,
    people INT NOT NULL,
    phone VARCHAR(255) NOT NULL,
    dates DATE NOT NULL,
    times VARCHAR(255) NOT NULL,
    msg VARCHAR(255) NOT NULL)
    """)
    conn.commit()
    cursor.close()
    conn.close()



create_contact_table()
create_signup()
create_reserve_table()


# Function to send email
def send_mail(recipient_email, subject, message):
    msg = MIMEMultipart()
    msg['From'] = email_config['sender_email']
    msg['To'] = recipient_email
    msg['Subject'] = subject
    msg.attach(MIMEText(message, 'plain'))

    # Connect to SMTP server
    server = smtplib.SMTP(email_config['smtp_server'], email_config['smtp_port'])
    server.starttls()
    server.login(email_config['sender_email'], email_config['sender_password'])

    # Send email
    text = msg.as_string()
    server.sendmail(email_config['sender_email'], recipient_email, text)

    # Quit server
    server.quit()


# Login page
@app.route('/')
def index1():
    return render_template('signup.html')


# Handle sign up form submission

@app.route('/new1', methods=['POST'])
def signup():
    mesage=''
    if request.method == 'POST'and 'email' in request.form and 'password' in request.form:
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirmpassword']
        con = get_db_connection()
        cur = con.cursor()
        cur.execute("select * from signup where email=%s", (email,))
        acc = cur.fetchone()
        if acc:
            mesage = 'Email Already Exist! '
            return render_template('login.html', mesage=mesage)
        elif password != confirm_password:
            mesage = 'Password Does Not Match!'
        else:
            try:
                hashed_password = generate_password_hash(password)
                cur.execute("INSERT INTO signup(email, password) VALUES (%s, %s)", (email, hashed_password))
                con.commit()
                cur.close()
                con.close()
                return redirect(url_for('login1'))
            except Exception as e:
                print("Error inserting values:", e)
                return 'Error inserting values'
        return render_template('signup.html', mesage=mesage)

@app.route('/new',methods=['GET','POST'])
def login1():
    mesage=''
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        email = request.form['email']
        password =request.form['password']
        con = get_db_connection()
        cur = con.cursor()
        cur.execute('select * from signup where email=%s', (email,))
        user=cur.fetchone()
        if user and check_password_hash(user[2], password):
            session['logged_in'] = True
            session['email'] = user[0]
            session['password'] =user[1]
            mesage='logged in successfully'

            cur.execute("INSERT INTO login_activity (email) VALUES (%s)", (email,))
            con.commit()
            cur.close()
            con.close()


            return render_template('index.html', params=params)
        else:
            mesage='Invalid email or password'
            return render_template('login.html', mesage=mesage)
    return render_template('login.html')

@app.route('/login')
def login():
    return render_template('login.html')



# Handle reservation form submission
@app.route('/reserved', methods=['POST'])
def submit_reserve():
    if request.method == 'POST':
        try:
            fname = request.form['fname']
            lname = request.form['lname']
            Email = request.form['emailR']
            people = request.form['people']
            phone = request.form['phoneR']

            # Date
            R_date_str = request.form['dates']
            R_date_obj = datetime.strptime(R_date_str, '%m/%d/%Y')
            R_date = R_date_obj.strftime('%Y-%m-%d')

            # Time
            R_time_str = request.form['times']
            R_time_obj = datetime.strptime(R_time_str, '%I:%M%p').strftime('%H:%M:%S')

            msg = request.form['msgR']

            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO reservedtable (fname, lname, Email, people, phone, dates, times, msg) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                (fname, lname, Email, people, phone, R_date, R_time_obj, msg)
            )
            conn.commit()
            cursor.close()
            conn.close()


            # Send mail to user to reserved your table
            # send mail to user
            subject = "congratulations!,Your reservation is conform"
            message = f"Dear {fname}, \n\n Thank you for Reservatin. Your table is reserved on {R_date} and Time {R_time_obj} for people:- {people}. \n For another query please contact us at Our Website Contact Us page. \n\n Have s nice day"
            send_mail(Email, subject, message)

            # Send mail to us any table is reserved to admin
            admin_subject = "New Table Reserved  "
            admin_message = f"EatWll table book by  {fname} for people {people},\n User Email:- ({Email}) \n DATE :- {R_date} \n Time :- {R_time_obj} \n Phone No:- {phone} \n Message :- {msg}\n\n Thank you."
            send_mail(email_config['sender_email'], admin_subject, admin_message)


            return 'Your table is reserved'
        except mysql.connector.Error as e:
            return 'Error inserting into database: {}'.format(str(e))
    return 'Error inserting values'


# Home page
@app.route('/home')
def home():
    return render_template('index.html', params=params)


# Handle contact form submission
@app.route('/contact', methods=['POST'])
def contact():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']

        # Get current date and time
        current_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO contact (name, email, message, date) VALUES (%s, %s, %s, %s)",
                           (name, email, message, current_datetime))
            conn.commit()
            cursor.close()
            conn.close()

            # send mail to user
            user_subject = "Thank you for contacting us!"
            user_message = f"Dear {name}, \n\n Thank you for contacting us. we have received your message and will get back to you as soon as possible."
            send_mail(email, user_subject, user_message)

            # send notification to admin
            admin_subject = "New Contact From Submittion  "
            admin_message = f"New message received from {name} ({email}) with subject: CONTACT ME \n\n Message: {message}"
            send_mail(email_config['sender_email'], admin_subject, admin_message)

            return 'Form submitted successfully!'
        except mysql.connector.Error as e:
            return 'Error submitting form: {}'.format(str(e))
    return "Method not allowed"


if __name__ == '__main__':
    app.run(debug=True)
