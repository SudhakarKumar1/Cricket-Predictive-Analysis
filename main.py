from flask import Flask, render_template, request, redirect, url_for, session
from flask_bcrypt import Bcrypt
from flask_mail import Mail, Message
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
import os
import mysql.connector
import uuid


app = Flask(__name__)
mail= Mail(app)


app.secret_key =os.urandom(24)
bcrypt = Bcrypt(app)


#database connection details below
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] ='admin123'
app.config['MYSQL_DB'] = 'profile'


app.config['MAIL_SERVER'] = 'smtp.mail.yahoo.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = "sudhakarkumar80@yahoo.com"
app.config['MAIL_PASSWORD'] = "faqusromkvsrvnyg"
mail = Mail(app)



#mySQL object
mysql= MySQL(app)

@app.route('/')
@app.route('/login', methods=['GET','POST'])
def login():
    msg=''
    if request.method =='POST' and 'username' in request.form and 'password' in request.form :
        username = request.form['username']
        password = request.form ['password']
        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE username = %s',(username,))
         # Fetch one record and return result
        user = cursor.fetchone()
        try:
            check = bcrypt.check_password_hash(user['password'], password)
            session['loggedin'] = True
            session['id'] = user['id']
            session['username'] = user['username']
            session['email'] = user['email']
            msg='Logged in successfully!'
            return render_template('index.html')
        except:
             msg = 'Incorrect username/password!'

    return render_template('login.html', msg = msg)

@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('userid', None)
    session.pop('username', None)
    session.pop('email', None)
    # Redirect to login page
    return redirect(url_for('login'))

@app.route('/register', methods =['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form and 'country' in request.form :
        username = request.form['username']
        password = request.form['password']
        #password = bcrypt.generate_password_hash(password)
        email = request.form['email']
        country= request.form['country']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE username = % s ', (username, ))
        cursor.execute('SELECT * FROM users WHERE email = % s ', (email, ))
        account = cursor.fetchall()
        if account:
            msg = 'Username already taken or Account already exists !'
        elif not re.fullmatch(r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+', email):
            msg = 'Invalid email address !'
        elif not re.fullmatch(r'^(?=[a-zA-Z0-9._]{8,20}$)(?!.*[_.]{2})[^_.].*[^_.]$', username):
            msg = 'Username must contain only characters and numbers !'
        elif not re.fullmatch(r'[A-Za-z0-9@#$%^&+=]{8,}', password):
            msg="Password must contain atleast 8 characters"
        elif not username or not password or not email:
            msg = 'Please fill out the form !'
        else:
            cursor.execute('INSERT INTO users VALUES (NULL, %s, %s, %s, NULL, %s)', (username, password, email, country))
            mysql.connection.commit()
            msg = 'You have successfully registered !'
    elif request.method == 'POST':
        msg = 'Please fill out the form !'
    return render_template('register.html', msg = msg)

@app.route("/index")
def index():
    if 'loggedin' in session:
        return render_template("index.html")
    return redirect(url_for('login'))


@app.route("/display")
def display():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE id = % s', (session['id'], ))
        account = cursor.fetchone()   
        return render_template("display.html", account = account)
    return redirect(url_for('login'))



@app.route("/update", methods =['GET', 'POST'])
def update():
    msg = ''
    if 'loggedin' in session:
        if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form and 'country' in request.form :
            username = request.form['username']
            password = request.form['password']
            email = request.form['email']
            country = request.form['country']   
            
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT * FROM users WHERE username = % s', (username, ))
            cursor.execute('SELECT * FROM users WHERE email = % s ', (email, ))
            account = cursor.fetchall()
            if account:
                msg = 'Username already taken or Account already exists !'
            elif not re.fullmatch(r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+', email):
                msg = 'Invalid email address !'
            elif not re.fullmatch(r'^(?=[a-zA-Z0-9._]{8,20}$)(?!.*[_.]{2})[^_.].*[^_.]$', username):
                msg = 'Username must contain only characters and numbers !'
            elif not re.fullmatch(r'[A-Za-z0-9@#$%^&+=]{8,}', password):
                msg="Password must contain atleast 8 characters"
            elif not username or not password or not email:
                msg = 'Please fill out the form !'
            else:
                cursor.execute('UPDATE users SET  username =%s, password =%s, email =%s, country =%s WHERE id =%s', (username, password, email, country, (session['id'], ), ))
                mysql.connection.commit()
                msg = 'You have successfully updated !'
        elif request.method == 'POST':
            msg = 'Please fill out the form !'
        return render_template("update.html", msg = msg)
    return redirect(url_for('login'))


@app.route('/forgot', methods=('POST','GET'))
def forgot():
    if 'loggedin' in session:
        return redirect('/')
    if request.method == 'POST':
        email = request.form['email']
        token = str(uuid.uuid4())
        cursor = mysql.connection.cursor()
        result = cursor.execute("SELECT * FROM users WHERE email=%s",(email,))
        if result > 0:
            data = cursor.fetchone()
            msg= Message(subject="forgot password request", sender="sudhakarkumar80@yahoo.com", recipients=[email])
            msg.body = render_template("sent.html", token=token, data=data)
            mail.send(msg) 
            cursor = mysql.connection.cursor()
            cursor.execute("UPDATE users SET token= %s WHERE email=%s",(token,email))
            mysql.connection.commit()
            cursor.close()
            msg='Email sent to your inbox'
            return redirect('/forgot')
        else:
           msg='Email does not match'
            

    return render_template('forgot.html')

@app.route('/reset/<token>',methods=['POST', 'GET'])
def reset(token):
    msg=''
    # TODO Understand if this needs be here
    if 'loggedin' in session:
        return redirect('/')
    if request.method == 'POST':
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        if password != confirm_password:
            msg = 'password donot match'
            return redirect('reset')
        password = bcrypt.generate_password_hash(password)
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE token=%s",(token,))
        user = cursor.fetchone()
        newToken = str(uuid.uuid4())
        if user:
            cursor = mysql.connection.cursor()
            cursor.execute('UPDATE users SET password =%s, token =%s WHERE token =%s', ( password, newToken, token ))
            mysql.connection.commit()
            cursor.close()
            msg = 'password successfully updated'
            return redirect('/login')
            # TODO :: how to pass msg to redirect , msg = msg)
        else:
            cursor.execute('UPDATE users SET token =%s WHERE token =%s', ( newToken, token ))
            msg='Your token is invalid'
            return redirect('/')

    return render_template('/reset.html', msg = msg)



if __name__ == "__main__":
    app.run(debug=True)
