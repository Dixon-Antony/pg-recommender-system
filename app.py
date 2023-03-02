from flask import Flask, render_template, request
from flask import *
from flask_mysqldb import MySQL
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.secret_key = "abc123"  

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'pgpg'
 
mysql = MySQL(app)


#global_variables

UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route("/")
@app.route("/index")
def index():
    user_id = session['user_id']
    cursor = mysql.connection.cursor()
    #Executing SQL Statements
    cursor.execute(''' SELECT username FROM users WHERE userid=%s''',(user_id))
    data = cursor.fetchall()
    print(data)
    #Saving the Actions performed on the DB
    mysql.connection.commit()
    #Closing the cursor
    cursor.close()
    return render_template('index.html',name=data[0][0])

@app.route("/aindex")
def aindex():
    return render_template('aindex.html')

@app.route("/admindashboard")
def admindashboard():
    return render_template('admindashboard.html')

@app.route("/viewusers")
def viewusers():

    cursor = mysql.connection.cursor()
    #Executing SQL Statements
    cursor.execute(''' SELECT * FROM users ''')
    data = cursor.fetchall()
    #Saving the Actions performed on the DB
    mysql.connection.commit()
    #Closing the cursor
    cursor.close()

    return render_template('viewusers.html',data=data, len = len(data))

@app.route("/viewpgowners")
def viewpgowners():

    cursor = mysql.connection.cursor()
    #Executing SQL Statements
    cursor.execute(''' SELECT * FROM agents ''')
    data = cursor.fetchall()
    #Saving the Actions performed on the DB
    mysql.connection.commit()
    #Closing the cursor
    cursor.close()

    return render_template('viewpgowners.html',data=data, len = len(data))

@app.route("/viewqueries")
def viewqueries():
    return render_template('viewqueries.html')

@app.route("/userbooking")
def userbooking():
    return render_template('userbooking.html')

@app.route("/pgownerbooking")
def pgownerbooking():
    return render_template('pgownerbooking.html')

@app.route("/pgownerdashboard")
def pgownerdashboard():
    return render_template('pgownerdashboard.html')

@app.route("/managepg")
def managepg():
    pgid='1'
    cursor = mysql.connection.cursor()
    #Executing SQL Statements
    cursor.execute(''' SELECT * FROM pgs WHERE pgid=%s''',(pgid))
    data = cursor.fetchall()
    #Saving the Actions performed on the DB
    mysql.connection.commit()
    #Closing the cursor
    cursor.close()
    return render_template('managepg.html',data=data,len=len(data))

@app.route('/registerPG',methods=['POST'])
def registerPG():


    if request.method == 'POST':
        cursor = mysql.connection.cursor()
        files = request.files.getlist('pgimage[]')
        pgid=2
        for i in range(len(files)):
            if files[i]:
                columnName=str('pgimage'+str(i+1))
                filename = secure_filename(files[i].filename)
                files[i].save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

                if i==0:
                    cursor.execute('''INSERT INTO pgs (pgimage1) VALUES (%s)''',[filename])
                
                if i==1:
                    cursor.execute('''UPDATE pgs SET pgimage2=%s WHERE pgid=%s''',([filename],pgid))
                
                if i==2:
                    cursor.execute('''UPDATE pgs SET pgimage3=%s WHERE pgid=%s''',([filename],pgid))

                mysql.connection.commit()
        cursor.close()
   
        return redirect('/managepg')

@app.route("/pgownerprofile")
def pgownerprofile():
    return render_template('pgownerprofile.html')

@app.route("/listings")
def listings():

    pgdata = [{'name':'hello','img_src':'bg4','price':'5000','rating':'3'},
              {'name':'world','img_src':'bg2','price':'4500','rating':'4'},
              {'name':'Jg','img_src':'bg3','price':'5500','rating':'5'},
              {'name':'Dinesh','img_src':'bg4','price':'6000','rating':'2'}]
    

    return render_template('listings.html',pgdata=pgdata, len = len(pgdata))

@app.route("/viewListing")
def viewListing():
    return render_template('viewListing.html')

@app.route("/contact")
def contact():
    return render_template('contact.html')

@app.route("/favorites")
def favorites():
    return render_template('favorites.html')

@app.route("/profile")
def profile():

    user_id = session['user_id']

    cursor = mysql.connection.cursor()
    #Executing SQL Statements
    cursor.execute(''' SELECT * FROM users WHERE userid=%s''',(user_id))
    data = cursor.fetchall()
    #Saving the Actions performed on the DB
    mysql.connection.commit()
    #Closing the cursor
    cursor.close()

    return render_template('profile.html',data=data)

@app.route("/editProfile",methods=['GET','POST'])
def editProfile():

    user_id = session['user_id']

    if request.method=='GET':
        cursor = mysql.connection.cursor()
        #Executing SQL Statements
        cursor.execute(''' SELECT * FROM users WHERE userid=%s''',(user_id))
        data = cursor.fetchall()
        #Saving the Actions performed on the DB
        mysql.connection.commit()
        #Closing the cursor
        cursor.close()

        return render_template('editProfile.html',data=data)

    if request.method=='POST':
        username = request.form['username']
        password = request.form['password']
        phone = request.form['phone']

        cursor = mysql.connection.cursor()
        #Executing SQL Statements
        cursor.execute(''' UPDATE users SET username=%s,password=%s,phone=%s WHERE userid=%s''',(username,password,phone,user_id))
        #Saving the Actions performed on the DB
        mysql.connection.commit()
        #Closing the cursor
        cursor.close()

        return redirect('/profile')


    



@app.route("/login")
def login():
    return render_template('login.html')

@app.route("/plogin")
def plogin():
    return render_template('plogin.html')

@app.route('/loginVerify', methods=['POST'])
def loginVerify():
    #Creating a connection cursor

    if request.method == 'POST':
        lemail = request.form['lemail']
        lpassword = request.form['lpassword']

    if lemail == 'admin@gmail.com' and lpassword == 'admin123':
        return redirect('/aindex')

    cursor = mysql.connection.cursor()
    
    #Executing SQL Statements
    cursor.execute(''' SELECT * FROM users WHERE email=%s AND password=%s''',(lemail,lpassword))
    data = cursor.fetchall()
    #Saving the Actions performed on the DB
    mysql.connection.commit()
    
    #Closing the cursor
    cursor.close()

    if len(data)!=0:
        session['user_id'] = str(data[0][0])
        return redirect('/index')    
    else:
        return render_template ('login.html',res="invalid")
    

@app.route('/register', methods=['POST'])
def register():
    #Creating a connection cursor

    if request.method == 'POST':
        username = request.form['username']
        # print(username)
        phone = request.form['phone']
        # print(phone)
        email = request.form['email']
        # print(email)
        password = request.form['password']
        # print(password)
        cpassword = request.form['cpassword']
        # print(cpassword)
        aadhaar = request.form['aadhaar']
        # print(aadhaar)
        gender = request.form['gender']
        # print(gender)


        if password != cpassword:
            print('hi')
            return render_template('login.html',res='check_pass')

    cursor = mysql.connection.cursor()
    
    #Executing SQL Statements
    cursor.execute(''' INSERT into users (username,email,password,phone,aadhaar,gender) VALUES(%s,%s,%s,%s,%s,%s)''',(username,email,password,phone,aadhaar,gender))

    #Saving the Actions performed on the DB
    mysql.connection.commit()

    #Executing SQL Statements
    cursor.execute(''' SELECT userid FROM users WHERE username=%s''',(username))
    data = cursor.fetchall()
    session['user_id'] = data[0][0]
    #Saving the Actions performed on the DB
    mysql.connection.commit()
    
    #Closing the cursor
    cursor.close()

    return redirect('/index')



if __name__ == "__main__":
  app.run()