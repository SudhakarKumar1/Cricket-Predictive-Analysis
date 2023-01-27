from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
import os
import mysql.connector



app = Flask(__name__)
app.secret_key =os.urandom(24)

#conn = mysql.connector.connect()



#database connection details below
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] ='admin123'
app.config['MYSQL_DB'] = 'login'

# Intialize MySQL
mysql= MySQL(app)


@app.route('/', methods=['GET','POST'])
def login():
    msg=''
    if request.method =='POST' and 'username' in request.form and 'password' in request.form :
        username = request.form['username']
        password = request.form ['password']
        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = % s AND password = % s',(username, password, ))
         # Fetch one record and return result
        accounts = cursor.fetchone()
        if accounts:
           #if accounts['role'] == 'admin':
                session['loggedin'] = True
                session['userid'] = accounts['userid']
                session['username'] = accounts['username']
                session['email'] = accounts['email']
                msg='Logged in successfully!'
                return render_template('home.html')

        else:    
             msg = 'Incorrect username/password!'
    return render_template('login.html', msg = msg)

@app.route('/home')
def home():
    # Check if user is loggedin
    if 'loggedin' in session:
        return render_template('home.html', username = session['username'])
    return redirect(url_for('login'))


@app.route('/profile')
def profile():
    # Check if user is loggedin
    if 'loggedin' in session:
        # account info for the user to display it on the profile page
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE id = %s', (session['id'],))
        account = cursor.fetchone()
        # Show the profile page with account info
        return render_template('profile.html', account=account)
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))



@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('userid', None)
    session.pop('username', None)
    session.pop('email', None)
    # Redirect to login page
    return redirect(url_for('login'))


app.route('/users', methods=['GET', 'POST'])
def users():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts')
        users = cursor.fetchall()
        return render_template("users.html", users=users)
    return redirect(url_for('login'))

app.route('/edit', methods=['GET', 'POST'])
def edit():
    msg=''
    if 'loggedin' in session:
        editUserId = request.args.get('userid')
        cursor=mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE userid= % s',(editUserId, ))
        editUser=cursor.fetchone()
        if request.method == 'POST' and 'username' in request.form and 'userid' in request.form and 'role' in request.form and 'country' in request.form:
            username=request.form['name']
            role = request.form['role']
            country = request.form['country']            
            userId = request.form['userid']
            if not re.match(r'^(?=[a-zA-Z0-9._]{8,20}$)(?!.*[_.]{2})[^_.].*[^_.]$', username):
                msg = 'username must be 8-20 characters long and contain only characters and numbers !'
            else:
                cursor.execute('UPDATE accounts SET username=% s, role =% s, country =% s WHERE userid =% s', (username, role, country, (userId, ), ))
                mysql.connection.commit()
                msg='User Updated'
                return redirect(url_for('users'))
        elif request.method=='POST':
            msg='Please fill out the form !'
            return render_template('edit.html', msg = msg, editUser=editUser)
    return redirect(url_for('login'))

@app.route ("/delete", methods =['GET'])
def delete():
    if 'loggedin' in session:
         deleteUserId == request.args.get('userid')
         cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
         deleteUserId= cursor.execute ('DELETE  FROM accounts WHERE userid = % s',(deleteUserId,))
         mysql.connection.commit()
         return redirect(url_for ('users'))
    return redirect (url_for('login'))


@app.route('/password_change', methods = ['GET','POST'])
def password_change():
    msg=''
    if 'loggedin' in session:
        changePassUserId=request.args.get('userid')
        if request.method=='POST' and 'password' in request.form and 'confirm_pass' in request.form and 'userid' in request.form:
            password = request.form['password']
            confirm_pass = request.form['confirm_pass']
            userId= request.form['userid']
            if not password or not confirm_pass:
                msg='Please fill out the form !'
            elif password != confirm_pass:
                msg='The passwords do not match'
            else:
                cursor=mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                cursor.execute('UPDATE accounts SET password = % s WHERE userid = % s',(password, (userId), ))
                mysql.connection.commit()
                msg='password updated !'
        elif request.method == 'POST':
            msg= 'Please fill out the form !'
        return render_template("password_change.html", msg = msg, changePassUserId=changePassUserId )
    return redirect(url_for('login'))


@app.route('/register', methods =['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form :
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        role = request.form['role']
        country= request.form['country']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = % s ', (username, ))
        cursor.execute('SELECT * FROM accounts WHERE email = % s ', (email, ))
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
            cursor.execute('INSERT INTO accounts VALUES (NULL, % s, % s, % s, % s, % s)', (username, password, email, role, country))
            mysql.connection.commit()
            msg = 'You have successfully registered !'
    elif request.method == 'POST':
        msg = 'Please fill out the form !'
    return render_template('register.html', msg = msg)

@app.route("/view", methods =['GET', 'POST'])
def view():
    if 'loggedin' in session:
        viewUserId = request.args.get('userid')   
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE userid = % s', (viewUserId, ))
        accounts = cursor.fetchone()   
        return render_template("view.html", accounts = accounts)
    return redirect(url_for('login'))

@app.route('/pwresetrq', methods =['GET', 'POST'])
def pwresetrq():
    return render_template ('pwresetrq.html')


if __name__ == "__main__":
    app.run(debug=True)
