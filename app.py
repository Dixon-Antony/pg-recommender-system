from flask import Flask, render_template, request
from flask import *
from flask_mysqldb import MySQL
from werkzeug.utils import secure_filename
import os
import random
import smtplib
from datetime import date

import pandas as pd
import numpy as np
from scipy.sparse import csr_matrix
from sklearn.neighbors import NearestNeighbors



app = Flask(__name__)
app.secret_key = "abc123"  

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'pgrs'
 
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
    cursor.execute(''' SELECT username FROM users WHERE userid=%s''',([user_id]))
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

    cursor = mysql.connection.cursor()
    #Executing SQL Statements
    cursor.execute(''' SELECT * FROM queries WHERE status='negative' AND pg_id=%s''',([session['pgid']]))
    data = cursor.fetchall()
    print(data)
    #Saving the Actions performed on the DB
    mysql.connection.commit()
    #Closing the cursor
    cursor.close()

    return render_template('viewqueries.html',data=data, len = len(data))

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
    cursor.execute(''' SELECT * FROM agents WHERE agentid=%s''',([agent_id]))
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
    cursor.execute(''' SELECT aname FROM agents WHERE agentid=%s''',([agent_id]))
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
    cursor.execute(''' SELECT * FROM pgs WHERE pgownerid=%s''',([agent_id]))
    data = cursor.fetchall()
    print(data)
    if len(data)==0:
        session['pgid'] = 'none'
    else:    
        session['pgid'] = str(data[0][0])
    #Saving the Actions performed on the DB
    mysql.connection.commit()
    #Executing SQL Statements
    cursor.execute(''' SELECT * FROM rooms WHERE pgid=%s''',[session['pgid']])
    room_data = cursor.fetchall()
    #Saving the Actions performed on the DB
    mysql.connection.commit()
    #Closing the cursor
    cursor.close()
    return render_template('managepg.html',data=data,len=len(data),roomData =room_data)

@app.route("/addPG")
def addPG():
    return render_template('addPG.html')
    

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
   
        return redirect('/addRooms')

@app.route("/addRooms",methods=['POST','GET'])
def addRooms():

    pgid = session['pgid']
    roomtype = 'standard'
    
    if request.method=='GET':
        return render_template('addRooms.html')

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
                cursor.execute('''INSERT INTO rooms (pgid,roomtype,sharingtype,room_count,available,price) VALUES (%s,%s,%s,%s,%s,%s)''',(pgid,roomtype,'single',s,s,sp))
                mysql.connection.commit()

            if i==1:
                cursor.execute('''INSERT INTO rooms (pgid,roomtype,sharingtype,room_count,available,price) VALUES (%s,%s,%s,%s,%s,%s)''',(pgid,roomtype,'double',d,d,dp))
                mysql.connection.commit()
            
            if i==2:
                cursor.execute('''INSERT INTO rooms (pgid,roomtype,sharingtype,room_count,available,price) VALUES (%s,%s,%s,%s,%s,%s)''',(pgid,roomtype,'triple',t,t,tp))
                mysql.connection.commit()
            
            if i==3:
                cursor.execute('''INSERT INTO rooms (pgid,roomtype,sharingtype,room_count,available,price) VALUES (%s,%s,%s,%s,%s,%s)''',(pgid,roomtype,'quad',q,q,qp))
                mysql.connection.commit()

        

        cursor.execute(''' SELECT * FROM  pgs WHERE pgid=%s''',([pgid]))
        emailPgData = cursor.fetchall()
        print(emailPgData)
        mysql.connection.commit()

        cursor.execute(''' SELECT email FROM  users WHERE subscription="subscribed" ''')
        receiverData = cursor.fetchall()
        receivers = []
        for i in range(len(receiverData)):
            receivers.append(receiverData[i][0])
        print(receivers)
        mysql.connection.commit()
        
        # msg = MIMEMultipart()
        # msg['From'] = "me@gmail.com"
        # msg['To'] = "you@gmail.com"
        # msg['Subject'] = "Email using Python"

        welcome="A New Paying Guest property has arrived !!! Check it out at the website\n\n"
        pgName = "Name : "+emailPgData[0][1]
        pgType = "Type : "+emailPgData[0][6]
        pgAddress = "Address : "+emailPgData[0][8]
        note = "This email has been sent to you because you're subscribed to the messaging service."
        msg = "From : PGReccMessageEngine\n"+"Subject : New PG Added !\n \n"+welcome+"\n"+pgName + "\n"+pgType+"\n"+pgAddress+"\n\n\n"+note
         
        s = smtplib.SMTP('smtp.gmail.com', 587)
        s.ehlo()
        s.starttls()
        s.ehlo()
        s.login("PGReccMessageEngine", "pliuttlzepratzho")
        s.sendmail('PGReccMessageEngine',receivers,msg)
        s.quit()
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
    

    if request.method=='POST':
        search = cari = "%" + request.form['search'] +"%"

        cursor.execute(''' SELECT * FROM pgs WHERE pgname LIKE %s OR pgaddress LIKE %s  OR pgtype LIKE %s OR pgpincode LIKE %s  ''',([search],[search],[search],[search]))
        data = cursor.fetchall()
        # print(data)
        #Saving the Actions performed on the DB
        mysql.connection.commit()

    #Executing SQL Statements
    cursor.execute(''' SELECT pg_id,AVG(rating) FROM ratings GROUP BY pg_id''')
    rating_data = cursor.fetchall()
    # print(rating_data)
    #Saving the Actions performed on the DB
    mysql.connection.commit()

    for i in range(len(rating_data)):
        #Executing SQL Statements
        cursor.execute(''' UPDATE pgs SET pgrating=%s WHERE pgid=%s''',(round(rating_data[i][1],1),[rating_data[i][0]]))
        # Saving the Actions performed on the DB
        mysql.connection.commit()

    #Closing the cursor
    cursor.close()

    return render_template('listings.html',pgdata=data, len = len(data))

      

@app.route("/viewListing",methods=['POST'])

def viewListing():
    if request.method=='POST':
        pgId = request.form['pg-id'];
        session['pgid'] = pgId
        cursor = mysql.connection.cursor()
        #Executing SQL Statements
        cursor.execute(''' SELECT * FROM pgs WHERE pgid=%s''',([pgId]))
        data = cursor.fetchall()
        pg_name = data[0][1]
        recommendations = get_pg_recommendation(pg_name)
        #Saving the Actions performed on the DB
        mysql.connection.commit()

        cursor.execute(''' SELECT aname FROM agents WHERE agentid=%s''',([data[0][7]]))
        agentName = cursor.fetchall()[0][0]
        mysql.connection.commit()

        #Executing SQL Statements
        cursor.execute(''' SELECT * FROM rooms WHERE pgid=%s''',([pgId]))
        room_data = cursor.fetchall()
        #Saving the Actions performed on the DB
        mysql.connection.commit()
        
        recommended_data=[]
        for i in range(len(recommendations)):
            #Executing SQL Statements
            cursor.execute(''' SELECT * FROM pgs WHERE pgname=%s ''',([recommendations[i][1]]))
            rec_data = cursor.fetchall()
            recommended_data.append(rec_data[0])
            #Saving the Actions performed on the DB
            mysql.connection.commit()

        # print(recommended_data)

        #Closing the cursor
        cursor.close()
            


        return render_template('viewListing.html',data=data,roomData=room_data, recommendation_data=recommended_data, rlen = len(recommended_data),agentName = agentName)

def get_pg_recommendation(pg_name):
        #recommendation

    cursor = mysql.connection.cursor()
    #Executing SQL Statements
    cursor.execute(''' SELECT pgid,pgname FROM pgs''')
    pgdata = list(cursor.fetchall())

    df = pd.DataFrame(pgdata,columns=['pgId','title'])
    # print(df)
    # print(type(df))

    #Saving the Actions performed on the DB
    mysql.connection.commit()

    cursor.execute(''' SELECT * FROM ratings WHERE pg_id=%s''',([session['pgid']]))
    newPgdata = cursor.fetchall()
    if len(newPgdata)==0:
        return []
    #Saving the Actions performed on the DB
    mysql.connection.commit()

    #Executing SQL Statements
    cursor.execute(''' SELECT user_id,pg_id,rating FROM ratings''')
    ratingdata = list(cursor.fetchall())

    rdf = pd.DataFrame(ratingdata,columns=['userId','pgId','rating'])
    # print(rdf.head())

    #Saving the Actions performed on the DB
    mysql.connection.commit()
    #Closing the cursor
    cursor.close()

    pgs = df
    ratings = rdf


    final_dataset = ratings.pivot_table(index='pgId',columns='userId',values='rating')
    final_dataset.fillna(0,inplace=True)

    no_user_voted = ratings.groupby('pgId')['rating'].agg('count')
    no_pgs_voted = ratings.groupby('userId')['rating'].agg('count')

    final_dataset = final_dataset.loc[no_user_voted[no_user_voted > 10].index,:]

    final_dataset=final_dataset.loc[:,no_pgs_voted[no_pgs_voted > 50].index]

    csr_data = csr_matrix(final_dataset.values)
    final_dataset.reset_index(inplace=True)

    knn = NearestNeighbors(metric='cosine', algorithm='brute', n_neighbors=20, n_jobs=-1)
    knn.fit(csr_data)

    n_pgs_to_recommend = 10
    pg_list = pgs[pgs['title'].str.contains(pg_name)]  
    if len(pg_list):        
        pg_idx= pg_list.iloc[0]['pgId']
        pg_idx = final_dataset[final_dataset['pgId'] == pg_idx].index[0]
        distances , indices = knn.kneighbors(csr_data[pg_idx],n_neighbors=n_pgs_to_recommend+1)    
        rec_pg_indices = sorted(list(zip(indices.squeeze().tolist(),distances.squeeze().tolist())),key=lambda x: x[1])[:0:-1]
        recommend_frame = []
        for val in rec_pg_indices:
            pg_idx = final_dataset.iloc[val[0]]['pgId']
            idx = pgs[pgs['pgId'] == pg_idx].index
            recommend_frame.append({'Title':pgs.iloc[idx]['title'].values[0],'Distance':val[1]})
        df = pd.DataFrame(recommend_frame,index=range(1,n_pgs_to_recommend+1))
        return df.to_records()
    else:
        return "No pgs found. Please check your input"



    

@app.route("/contact")
def contact():
    user_id = session['user_id']
    session['pgid']=str(0)
    cursor = mysql.connection.cursor()
    #Executing SQL Statements
    cursor.execute(''' SELECT * FROM queries WHERE user_id=%s AND pg_id=%s''',(user_id,[session['pgid']]))
    data = cursor.fetchall()
    #Saving the Actions performed on the DB
    mysql.connection.commit()
    #Closing the cursor
    cursor.close()

    return render_template('contact.html',data=data,len=len(data))

@app.route("/booking")
def booking():
        
        booking_status = 'not_boooked'
        try:
            booking_status = request.args['response']
            print(booking_status)
            
        finally:
            cursor = mysql.connection.cursor()
            #Executing SQL Statements
            cursor.execute(''' SELECT bookingid,pgid,bookingdate,rating FROM bookings WHERE userid=%s''',(session['user_id']))
            booking_details = cursor.fetchall()
            #Saving the Actions performed on the DB
            mysql.connection.commit()

            pg_data = []
            for i in range(len(booking_details)):
                pg_id = str(booking_details[i][1])
                #Executing SQL Statements
                cursor.execute(''' SELECT * FROM pgs WHERE pgid=%s''',([pg_id]))
                data = cursor.fetchall()
                pg_data.append(data[0])
                #Saving the Actions performed on the DB
                mysql.connection.commit()
            cursor.close()

            return render_template('booking.html',status=booking_status,booking_details=booking_details,len=len(booking_details),pg_data=pg_data)

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
    
@app.route("/editAgentProfile",methods=['GET','POST'])
def editAgentProfile():

    agent_id = session['agent_id']

    if request.method=='GET':
        cursor = mysql.connection.cursor()
        #Executing SQL Statements
        cursor.execute(''' SELECT * FROM agents WHERE agentid=%s''',([agent_id]))
        data = cursor.fetchall()
        #Saving the Actions performed on the DB
        mysql.connection.commit()
        #Closing the cursor
        cursor.close()

        return render_template('editAgentProfile.html',data=data)

    if request.method=='POST':
        username = request.form['username']
        password = request.form['password']
        phone = request.form['phone']

        cursor = mysql.connection.cursor()
        #Executing SQL Statements
        cursor.execute(''' UPDATE agents SET aname=%s,apassword=%s,aphone=%s WHERE agentid=%s''',(username,password,phone,agent_id))
        #Saving the Actions performed on the DB
        mysql.connection.commit()
        #Closing the cursor
        cursor.close()

        return redirect('/pgownerprofile')

@app.route("/editRooms",methods=['GET','POST'])
def editRooms():

    pg_id = session['pgid']
    print("PG ID",pg_id)
    if request.method=='GET':
        cursor = mysql.connection.cursor()
        #Executing SQL Statements
        cursor.execute(''' SELECT * FROM rooms WHERE pgid=%s''',([pg_id]))
        data = cursor.fetchall()
        print(data)
        #Saving the Actions performed on the DB
        mysql.connection.commit()
        #Closing the cursor
        cursor.close()

        return render_template('editRooms.html',data=data)

    if request.method=='POST':
        savailable = request.form['savailable']

        sroomcount = request.form['sroomcount']

        sprice = request.form['sprice']

        davailable = request.form['davailable']
 
        droomcount = request.form['droomcount']

        dprice = request.form['dprice']

        tavailable = request.form['tavailable']

        troomcount = request.form['troomcount']

        tprice = request.form['tprice']

        qavailable = request.form['qavailable']

        qroomcount = request.form['qroomcount']

        qprice = request.form['qprice']


        cursor = mysql.connection.cursor()
        #Executing SQL Statements
        cursor.execute(''' UPDATE rooms SET available=%s,room_count=%s,price=%s WHERE pgid=%s AND sharingtype=%s''',(savailable,sroomcount,sprice,[pg_id],'single'))
        #Saving the Actions performed on the DB
        mysql.connection.commit()
        #Executing SQL Statements
        cursor.execute(''' UPDATE rooms SET available=%s,room_count=%s,price=%s WHERE pgid=%s AND sharingtype=%s''',(davailable,droomcount,dprice,[pg_id],'double'))
        #Saving the Actions performed on the DB
        mysql.connection.commit()
        #Executing SQL Statements
        cursor.execute(''' UPDATE rooms SET available=%s,room_count=%s,price=%s WHERE pgid=%s AND sharingtype=%s''',(tavailable,troomcount,tprice,[pg_id],'triple'))
        #Saving the Actions performed on the DB
        mysql.connection.commit()
        #Executing SQL Statements
        cursor.execute(''' UPDATE rooms SET available=%s,room_count=%s,price=%s WHERE pgid=%s AND sharingtype=%s''',(qavailable,qroomcount,qprice,[pg_id],'quad'))
        #Saving the Actions performed on the DB
        mysql.connection.commit()
        #Closing the cursor
        cursor.close()

        return redirect('/managepg')
    
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


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
        session['pgid']=str(0)
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
        s.ehlo()
        s.starttls()
        s.ehlo()
        s.login("PGReccMessageEngine", "pliuttlzepratzho")
        s.sendmail('PGReccMessageEngine',emailid,msg)
        s.quit()

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
        # if otp == '123456':
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
        s.ehlo()
        s.starttls()
        s.ehlo()
        s.login("PGReccMessageEngine", "pliuttlzepratzho")
        s.sendmail('PGReccMessageEngine',emailid,msg)
        s.quit()

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
        # if otp == '123456':
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
        cursor.execute(''' INSERT into bookings (pgid,roomid,userid,bookingdate) VALUES(%s,%s,%s,%s)''',(pgId,roomId,session['user_id'],[date.today()]))
        #Saving the Actions performed on the DB
        mysql.connection.commit()

        cursor.execute('''SELECT bookingid FROM bookings ORDER BY bookingid DESC LIMIT 1''',)
        booking_id = cursor.fetchall()[0][0]
        #Saving the Actions performed on the DB
        mysql.connection.commit()
        
        cursor.close()

        return render_template('payment.html',booking_id=booking_id)

@app.route('/ratePG',methods=['POST'])
def ratePG():
    
    if request.method=='POST':
        rating = request.form['rate']
        pg_id = request.form['pg-id']
        user_id = session['user_id']
        cursor = mysql.connection.cursor()
        cursor.execute(''' INSERT INTO ratings (user_id,pg_id,rating) VALUES(%s,%s,%s);''',(user_id,pg_id,rating))
        #Saving the Actions performed on the DB
        mysql.connection.commit()

        cursor.execute(''' UPDATE bookings SET rating=%s WHERE userid=%s AND pgid=%s''',(rating,user_id,pg_id))
        #Saving the Actions performed on the DB
        mysql.connection.commit()

        cursor.close()

    return redirect('booking');

@app.route('/userqueries')
def userqueries():
    user_id = session['user_id']

    cursor = mysql.connection.cursor()
    #Executing SQL Statements
    cursor.execute(''' SELECT queries.qrid,queries.user_id,pgs.pgname,queries.name,queries.email,queries.queries,queries.replies,queries.status FROM queries INNER JOIN pgs on queries.pg_id=pgs.pgid WHERE user_id=%s''',([user_id]))
    data = cursor.fetchall()
    print(data)
    #Saving the Actions performed on the DB
    mysql.connection.commit()
    #Closing the cursor
    cursor.close()
    return render_template("userqueries.html",data=data,len=len(data))

@app.route('/postQuery',methods=['POST'])
def postQuery():
    if request.method == 'POST':
        name = request.form['name']
        email= request.form['email']
        queries = request.form['queries']
        user_id = session['user_id']
        pg_id = session['pgid']

        cursor = mysql.connection.cursor()
        cursor.execute(''' INSERT INTO queries (name,email,queries,user_id,pg_id) VALUES(%s,%s,%s,%s,%s);''',(name,email,queries,user_id,[pg_id]))
        #Saving the Actions performed on the DB
        mysql.connection.commit()
        cursor.close()

        if session['pgid'] == str(0):
            return redirect('/contact')

    return redirect('/userqueries')

@app.route('/reply',methods=['POST'])
def reply():
    if request.method=='POST':
        reply = request.form['reply']
        qrid = request.form['queryId']
        cursor = mysql.connection.cursor()
        cursor.execute(''' UPDATE queries SET replies=%s,status='positive' WHERE qrid=%s''',(reply,qrid))
        #Saving the Actions performed on the DB
        mysql.connection.commit()
        cursor.close()

        if session['pgid'] == str(0):
            return redirect('/viewqueries')

    return redirect('/guests')


@app.route("/popularPgs")
def popularPgs():
    cursor = mysql.connection.cursor()
    cursor.execute('''SELECT * FROM pgs ORDER BY pgrating DESC LIMIT 10''')
    data = cursor.fetchall()
    # print(data)
    #Saving the Actions performed on the DB
    mysql.connection.commit()
    cursor.close()

    return render_template('popularPgs.html',pgdata=data, len = len(data))

@app.route("/guests")
def guests():
    pg_id = session['pgid']
    cursor = mysql.connection.cursor()
    cursor.execute('''SELECT bookings.bookingid,bookings.roomid,bookings.bookingdate,users.username,users.phone FROM bookings INNER JOIN users ON bookings.userid = users.userid WHERE pgid=%s''',([pg_id]))
    data = cursor.fetchall()
    mysql.connection.commit()
    print(data)
    cursor.execute('''SELECT pgname from pgs WHERE pgid=%s''',([pg_id]))
    pg_name = cursor.fetchall()[0][0]
    mysql.connection.commit()
    #Saving the Actions performed on the DB

    cursor.execute(''' SELECT * FROM queries WHERE pg_id=%s AND status=%s ''',([pg_id],'negative'))
    qdata = cursor.fetchall()
    cursor.close()
    mysql.connection.commit()
    return render_template('guests.html',data=data, len = len(data),qdata=qdata,qlen=len(qdata),pgName = pg_name)

@app.route('/subscribe',methods=['POST'])
def subscribe():
    if request.method=='POST':
        subscription_data = request.form['subscribe'].split('-')
        cursor = mysql.connection.cursor()
        cursor.execute(''' UPDATE users SET subscription=%s WHERE userid=%s ''',([subscription_data[1]],[subscription_data[0]]))
        mysql.connection.commit()
        cursor.close()

        return redirect('/profile')
    
@app.route('/askQueries')
def askQueries():
    pg_id = session['pgid']
    cursor = mysql.connection.cursor()
    cursor.execute(''' SELECT pgname FROM pgs WHERE pgid=%s ''',([pg_id]))
    pgName = cursor.fetchall()[0][0]
    mysql.connection.commit()
    cursor.close()
    return render_template('/askQueries.html',pgName=pgName)

@app.route("/payment",methods=['POST'])
def payment():

    if request.method == 'POST':
        booking_id = request.form['payment-btn']
        print(booking_id)
        cursor = mysql.connection.cursor()
        cursor.execute('''UPDATE bookings SET payment='paid' WHERE bookingid=%s''',([booking_id]))
        mysql.connection.commit()
        cursor.close()
        return redirect(url_for('booking', response='booked'))
    




if __name__ == "__main__":
  app.run()


