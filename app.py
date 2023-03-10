from flask import Flask, render_template, request
from flask import *
from flask_mysqldb import MySQL
from werkzeug.utils import secure_filename
import os
import random
import smtplib
from datetime import date

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

@app.route("/pgownerprofile")
def pgownerprofile():
    agent_id = session['agent_id']
    cursor = mysql.connection.cursor()
    #Executing SQL Statements
    cursor.execute(''' SELECT * FROM agents WHERE agentid=%s''',(agent_id))
    data = cursor.fetchall()
    #Saving the Actions performed on the DB
    mysql.connection.commit()
    #Closing the cursor
    cursor.close()
    return render_template('pgownerprofile.html',data=data)

@app.route("/pindex")
def pindex():
    agent_id = session['agent_id']
    cursor = mysql.connection.cursor()
    #Executing SQL Statements
    cursor.execute(''' SELECT aname FROM agents WHERE agentid=%s''',(agent_id))
    data = cursor.fetchall()
    print(data)
    #Saving the Actions performed on the DB
    mysql.connection.commit()
    #Closing the cursor
    cursor.close()
    return render_template('pindex.html',name=data[0][0])

@app.route("/managepg")
def managepg():
    agent_id=session['agent_id']
    print(agent_id)
    cursor = mysql.connection.cursor()
    #Executing SQL Statements
    cursor.execute(''' SELECT * FROM pgs WHERE pgownerid=%s''',(agent_id))
    data = cursor.fetchall()
    print(data)
    try:
        session['pgid'] = str(data[0][0])
        #Saving the Actions performed on the DB
        mysql.connection.commit()
        #Executing SQL Statements
        cursor.execute(''' SELECT * FROM rooms WHERE pgid=%s''',(session['pgid']))
        room_data = cursor.fetchall()
        #Saving the Actions performed on the DB
        mysql.connection.commit()
        #Closing the cursor
        cursor.close()
        return render_template('managepg.html',data=data,len=len(data),roomData =room_data)
    except:
        return redirect('addPG');

@app.route("/addPG")
def addPG():
    return render_template('addPG.html')

@app.route("/addRooms",methods=['POST'])
def addRooms():

    pgid = session['pgid']
    roomtype = 'standard'

    if request.method=='POST':
        s = request.form['single']
        sp = request.form['singlePrice']
        d = request.form['double']
        dp = request.form['doublePrice']
        t = request.form['triple']
        tp = request.form['triplePrice']
        q = request.form['quad']
        qp = request.form['quadPrice']
        cursor = mysql.connection.cursor()
        for i in range(4):
            if i==0:
                cursor.execute('''INSERT INTO rooms (pgid,roomtype,sharingtype,room_count,price) VALUES (%s,%s,%s,%s,%s)''',(pgid,roomtype,'single',s,sp))
                mysql.connection.commit()

            if i==1:
                cursor.execute('''INSERT INTO rooms (pgid,roomtype,sharingtype,room_count,price) VALUES (%s,%s,%s,%s,%s)''',(pgid,roomtype,'double',d,dp))
                mysql.connection.commit()
            
            if i==2:
                cursor.execute('''INSERT INTO rooms (pgid,roomtype,sharingtype,room_count,price) VALUES (%s,%s,%s,%s,%s)''',(pgid,roomtype,'triple',t,tp))
                mysql.connection.commit()
            
            if i==3:
                cursor.execute('''INSERT INTO rooms (pgid,roomtype,sharingtype,room_count,price) VALUES (%s,%s,%s,%s,%s)''',(pgid,roomtype,'quad',q,qp))
                mysql.connection.commit()

        cursor.close()

    return redirect('/managepg')

@app.route('/registerPG',methods=['POST'])
def registerPG():


    if request.method == 'POST':
        cursor = mysql.connection.cursor()
        pgname = request.form['pgname']
        pgdesc = request.form['pgdesc']
        pgtype = request.form['pgtype']
        pgownername = request.form['ownername']
        pgaddress = request.form['pgaddress']
        pgcity = request.form['pgcity']
        pgpincode = request.form['pgpincode']
        files = request.files.getlist('pgimage[]')


        cursor.execute('''SELECT agentid FROM agents WHERE aname = %s''',([pgownername]))
        pgownerid = cursor.fetchall()[0][0]
        mysql.connection.commit()

        cursor.execute('''INSERT INTO pgs (pgname,pgdesc,pgtype,pgownerid,pgaddress,pgcity,pgpincode) VALUES (%s,%s,%s,%s,%s,%s,%s)''',(pgname,pgdesc,pgtype,pgownerid,pgaddress,pgcity,pgpincode))
        mysql.connection.commit()

        cursor.execute('''SELECT pgid FROM pgs WHERE pgname = %s''',([pgname]))
        data = cursor.fetchall()
        mysql.connection.commit()
        
        session['pgid'] = str(data[0][0])

        for i in range(len(files)):
            if files[i]:
                filename = secure_filename(files[i].filename)
                files[i].save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            
                if i==0:
                    cursor.execute('''UPDATE pgs SET pgimage1=%s WHERE pgid=%s''',([filename],session['pgid']))
                
                if i==1:
                    cursor.execute('''UPDATE pgs SET pgimage2=%s WHERE pgid=%s''',([filename],session['pgid']))
                
                if i==2:
                    cursor.execute('''UPDATE pgs SET pgimage3=%s WHERE pgid=%s''',([filename],session['pgid']))

                mysql.connection.commit()
        cursor.close()
   
        return redirect('/managepg')


@app.route("/listings",methods=['POST','GET'])
def listings():

    # pgdata = [{'name':'hello','img_src':'bg4','price':'5000','rating':'3'},
    #         {'name':'world','img_src':'bg2','price':'4500','rating':'4'},
    #         {'name':'Jg','img_src':'bg3','price':'5500','rating':'5'},
    #         {'name':'Dinesh','img_src':'bg4','price':'6000','rating':'2'}]
    
    cursor = mysql.connection.cursor()
    #Executing SQL Statements
    cursor.execute(''' SELECT * FROM pgs''')
    data = cursor.fetchall()
    #Saving the Actions performed on the DB
    mysql.connection.commit()
    #Closing the cursor
    cursor.close()

    return render_template('listings.html',pgdata=data, len = len(data))
    

@app.route("/viewListing",methods=['POST'])
def viewListing():
    if request.method=='POST':
        pgId = request.form['pg-id'];
        cursor = mysql.connection.cursor()
        #Executing SQL Statements
        cursor.execute(''' SELECT * FROM pgs WHERE pgid=%s''',(pgId))
        data = cursor.fetchall()
        #Saving the Actions performed on the DB
        mysql.connection.commit()

        #Executing SQL Statements
        cursor.execute(''' SELECT * FROM rooms WHERE pgid=%s''',(pgId))
        room_data = cursor.fetchall()
        #Saving the Actions performed on the DB
        mysql.connection.commit()
        #Closing the cursor
        cursor.close()

    return render_template('viewListing.html',data=data,roomData=room_data)

@app.route("/contact")
def contact():
    return render_template('contact.html')

@app.route("/favorites")
def favorites():
    return render_template('favorites.html')

@app.route("/profile")
def profile():
    
    booking_status = 'not_boooked'
    try:
        booking_status = request.args['response']

    finally:
        user_id = session['user_id']

        cursor = mysql.connection.cursor()
        #Executing SQL Statements
        cursor.execute(''' SELECT * FROM users WHERE userid=%s''',(user_id))
        data = cursor.fetchall()
        #Saving the Actions performed on the DB
        mysql.connection.commit()
        #Closing the cursor
        cursor.close()

        return render_template('profile.html',data=data,status=booking_status)

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
    
@app.route('/ploginVerify', methods=['POST'])
def ploginVerify():
    #Creating a connection cursor

    if request.method == 'POST':
        lemail = request.form['lemail']
        lpassword = request.form['lpassword']

    if lemail == 'admin@gmail.com' and lpassword == 'admin123':
        return redirect('/aindex')

    cursor = mysql.connection.cursor()
    
    #Executing SQL Statements
    cursor.execute(''' SELECT * FROM agents WHERE aemail=%s AND apassword=%s''',(lemail,lpassword))
    data = cursor.fetchall()
    #Saving the Actions performed on the DB
    mysql.connection.commit()
    
    #Closing the cursor
    cursor.close()

    if len(data)!=0:
        session['agent_id'] = str(data[0][0])
        return redirect('/pindex')    
    else:
        return render_template ('plogin.html',res="invalid")


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
            return render_template('login.html',res='check_pass')

    cursor = mysql.connection.cursor()
    
    #Executing SQL Statements
    cursor.execute(''' INSERT into users (username,email,password,phone,aadhaar,gender) VALUES(%s,%s,%s,%s,%s,%s)''',(username,email,password,phone,aadhaar,gender))

    #Saving the Actions performed on the DB
    mysql.connection.commit()

    #Executing SQL Statements
    cursor.execute(''' SELECT userid FROM users WHERE username=%s''',([username]))
    data = cursor.fetchall()
    session['user_id'] = str(data[0][0])
    #Saving the Actions performed on the DB
    mysql.connection.commit()
    
    #Closing the cursor
    cursor.close()

    return redirect('/getOTP')

@app.route('/getOTP',methods=['GET','POST'])
def getOTP():
    if request.method=='GET':
        return render_template('getOTP.html')
    
    if request.method=='POST':
        emailid = request.form['email']
        msg = str(generateOTP())
        session['otp'] = str(msg)
        s = smtplib.SMTP('smtp.gmail.com', 587)
        s.starttls()
        s.login("pgrecc123@gmail.com", "dzdewdudmjshbbmh")
        s.sendmail('pgrecc123@gmail.com',emailid,msg)
        
        return render_template('valOTP.html')

def generateOTP():
    return random.randrange(100000,999999)         


@app.route('/valOTP',methods=['GET','POST'])
def valOTP():
    if request.method=='GET':
        return render_template('valOTP.html')
    
    if request.method=='POST':
        otp = request.form['otp']

        if otp == session['otp']:
            return redirect('/')
        else:
            return render_template('valOTP.html',error='invalid')

@app.route('/pregister', methods=['POST'])
def pregister():
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
            return render_template('plogin.html',res='check_pass')

    cursor = mysql.connection.cursor()
    
    #Executing SQL Statements
    cursor.execute(''' INSERT into agents (aname,aemail,apassword,aphone,aaadhaar,agender) VALUES(%s,%s,%s,%s,%s,%s)''',(username,email,password,phone,aadhaar,gender))

    #Saving the Actions performed on the DB
    mysql.connection.commit()

    #Executing SQL Statements
    cursor.execute(''' SELECT agentid FROM agents WHERE aname=%s''',([username]))
    data = cursor.fetchall()
    session['agent_id'] = str(data[0][0])
    #Saving the Actions performed on the DB
    mysql.connection.commit()
    
    #Closing the cursor
    cursor.close()

    return redirect('/pgetOTP')

@app.route('/pgetOTP',methods=['GET','POST'])
def pgetOTP():
    if request.method=='GET':
        return render_template('pgetOTP.html')
    
    if request.method=='POST':
        emailid = request.form['email']
        msg = str(pgenerateOTP())
        session['otp'] = str(msg)
        s = smtplib.SMTP('smtp.gmail.com', 587)
        s.starttls()
        s.login("pgrecc123@gmail.com", "dzdewdudmjshbbmh")
        s.sendmail('pgrecc123@gmail.com',emailid,msg)
        
        return render_template('pvalOTP.html')

def pgenerateOTP():
    return random.randrange(100000,999999)         


@app.route('/pvalOTP',methods=['GET','POST'])
def pvalOTP():
    if request.method=='GET':
        return render_template('pvalOTP.html')
    
    if request.method=='POST':
        otp = request.form['otp']

        if otp == session['otp']:
            return redirect('/pindex')
        else:
            return render_template('pvalOTP.html',error='invalid')


@app.route('/bookPG',methods=['GET','POST'])
def bookPG():

    if request.method == 'POST':
        [roomType,pgId,roomId] = request.form['bookBtn'].split('-')
        cursor = mysql.connection.cursor()
        
        #Executing SQL Statements
        cursor.execute(''' UPDATE rooms SET available = available - 1 WHERE pgid = %s AND sharingtype=%s;''',(pgId,roomType))
        #Saving the Actions performed on the DB
        mysql.connection.commit()

        #Executing SQL Statements
        print("user-id : ",session['user_id'])
        cursor.execute(''' INSERT into bookings (pgid,roomid,userid,bookingdate) VALUES(%s,%s,%s,%s)''',(pgId,roomId,session['user_id'],[date.today()]))
        #Saving the Actions performed on the DB
        mysql.connection.commit()

        return redirect(url_for('profile', response='booked'));


if __name__ == "__main__":
  app.run()