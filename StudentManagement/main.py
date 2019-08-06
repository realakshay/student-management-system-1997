from flask import render_template, url_for, request, session, redirect,flash, jsonify
from app import app
from app.database import DB
import pymongo, csv, json, codecs
import pandas as pd
from werkzeug.security import generate_password_hash, check_password_hash

@app.route('/')
def index():
    return render_template('index.html', username=session.get('user'))

@app.route('/loginpage')
def loginpage():
    return render_template('Login.html', username=session.get('user'))

@app.route('/registration', methods=['GET','POST'])
def registration():
    if request.method=='POST':
        name=request.form['fullname']
        dob=request.form['birthdate']
        email=request.form['email']
        mobile=request.form['mobile']
        gender=request.form['gender']
        prn=request.form['prn']
        lastedu=request.form['lastedu']
        marks=request.form['marks']
        address=request.form['address']
        current=request.form['currentyear']
        password=generate_password_hash(request.form['password1'])

        data1={'Name':name,'DOB':dob,'Email':email,'Mobile':mobile,'Gender':gender, 'Address':address}
        collection1="PersonalInfo"

        data2={'Email':email, 'Password':password}
        collection2="LoginInfo"

        data3={'Email':email, 'PRN':prn, 'Current Year':current, lastedu:marks,'SSC':'N/A','HSC':'N/A','SE':'N/A','TE':'N/A','BE':'N/A','CGPA':'N/A'}
        collection3="AcademicInfo"

        data4={'Email':email, 'certificates':[]}
        collection4="Certifications"

        try:
            DB.insert(collection1,data1)
            DB.insert(collection2,data2)
            DB.insert(collection3,data3)
            DB.insert(collection4,data4)
            flash("Registration Successful")
            return render_template('Login.html', username=session.get('user'))

        except pymongo.errors.DuplicateKeyError:
            flash("Record already exist.")
            return redirect(url_for('registration'))

    return render_template('register.html', username=session.get('user'))

@app.route('/checklogin', methods=['POST','GET'])
def checklogin():
    if request.method=='POST':
        username=request.form['email']
        password=request.form['password']
        query={'Email':username}
        collection="LoginInfo"
        data=DB.find_one(collection,query)
        password2=data['Password']
        if check_password_hash(password2,password):
            session['user']=username
            return redirect(url_for('success'))
        else:
            flash("Invalid username or password")
            return redirect(url_for('loginpage'))

@app.route('/success', methods=['GET','POST'])
def success():
    name=session.get('user')
    return render_template('home.html', username=name, personal=None, academic=None)

@app.route('/searchpersonalprofile', methods=['GET','POST'])
def searchpersonalprofile():
    username=session.get('user')
    collection='PersonalInfo'
    query={'Email':username}
    personal=DB.find_one(collection,query)
    print(personal['Name'])
    return render_template('home.html', username=session.get('user'), personal=personal)


@app.route('/searchacademicprofile', methods=['GET','POST'])
def searchacademicprofile():
    username=session.get('user')
    collection='AcademicInfo'
    query=({'Email':username})
    academic=DB.find_one(collection,query)
    k=list(academic.keys())
    v=list(academic.values())
    newdict={}
    for i in range(2,len(k)):
        newdict[k[i]]=v[i]
    print(newdict)
    return render_template('home.html', username=session.get('user'), personal=None, academic=newdict)


@app.route('/searchcertificatesprofile', methods=['GET','POST'])
def searchcertificatesprofile():
    username=session.get('user')
    collection='Certifications'
    query=({'Email':username})
    academic=DB.find_one(collection,query)
    k=list(academic.keys())
    v=list(academic.values())
    newdict={}
    for i in range(2,len(k)):
        newdict[k[i]]=v[i]
    print(newdict)
    return render_template('home.html', username=session.get('user'), personal=None, academic=None, certificate=newdict)


@app.route('/updatepersonalpage', methods=['GET'])
def updatepersonalpage():
    print(session.get('user'))
    if session.get('user'):
        return render_template('profilepage.html', username=session.get('user'))
    else:
        flash("Please Login")
        return redirect(url_for('loginpage'))

@app.route('/updatepersonal', methods=['POST','PUT'])
def updatepersonal():
    if request.method=='POST':
        print(session.get('user'))
        username=session.get('user')
        updatecol=request.form['updateinfo']
        updatetext=request.form['updatetxt']
        collection='PersonalInfo'
        query={'Email':username}
        newvalues = { "$set": {updatecol: updatetext} }
        print(updatecol,updatetext)
        DB.update_one(collection,query,newvalues)
        flash(updatecol + " Successfully Updated")
        return render_template('home.html', username=session.get('user'), personal=None, academic=None)


@app.route('/updateacademicpage', methods=['GET'])
def updateacademicpage():
    print(session.get('user'))
    if session.get('user'):
        return render_template('academicprofilepage.html', username=session.get('user'))
    else:
        flash("Please Login")
        return redirect(url_for('loginpage'))

@app.route('/updateacademic', methods=['POST','PUT'])
def updateacademic():
    if request.method=='POST':
        print(session.get('user'))
        username=session.get('user')
        updatecol=request.form['updateinfo']
        updatetext=request.form['updatetxt']
        collection='AcademicInfo'
        query={'Email':username}
        newvalues = { "$set": {updatecol: updatetext} }
        print(updatecol,updatetext)
        DB.update_one(collection,query,newvalues)
        flash(updatecol + " Successfully Updated")
        return render_template('home.html', username=session.get('user'), personal=None, academic=None)


@app.route('/updatecertificatepage')
def updatecertificatepage():
    if session.get('user'):
        return render_template('certificateprofilepage.html', username=session.get('user'))
    else:
        flash("Please Login")
        return redirect(url_for('loginpage'))

@app.route('/updatecertificate', methods=['POST','PUT'])
def updatecertificate():
    if request.method=='POST':
        username=session.get('user')
        updatetext=request.form['updatetxt']
        collection='Certifications'
        query={'Email':username}
        newvalues = { "$push": {'certificates': updatetext}}
        DB.update_one(collection,query,newvalues)
        flash("Certificate Successfully Updated")
        return render_template('home.html', username=session.get('user'), personal=None, academic=None)

@app.route('/profilehomepage')
def profilehomepage():
    if session.get('user'):
        return redirect(url_for('success'))
    else:
        flash("Please login first")
        return redirect(url_for('loginpage'))

'''
###########################
#    It is for admin      #
###########################
'''

@app.route('/adminindex')
def adminindex():
    return render_template('adminindex.html', username=session.get('user'))

@app.route('/adminloginpage')
def adminloginpage():
    return render_template('adminlogin.html', username=session.get('user'))

@app.route('/checkadmin', methods=['POST'])
def checkadmin():
    if request.method=='POST':
        username=request.form['email']
        password=request.form['password']
        query={'Email':username}
        collection="LoginInfo"
        data=DB.find_one(collection,query)
        password2=data['Password']
        if check_password_hash(password2,password):
            session['user']=username
            return redirect(url_for('adminsuccess'))
        else:
            flash("Invalid username or password")
            return redirect(url_for('loginpage'))

@app.route('/adminsuccess', methods=['GET','POST'])
def adminsuccess():
    name=session.get('user')
    return render_template('adminhome.html', username=name, personal=None, academic=None)

@app.route('/searchallstudent')
def searchallstudent():
    collection='AcademicInfo'
    mydoc=DB.showall(collection)
    x=[]
    for doc in mydoc:
        doc.pop('_id')
        x.append(doc)

    with open('a.json','w') as fp:
        for i in range(0,len(x)):
            json.dump(x[i],fp)
            fp.write(',')
    fp.close()

    json_data=jsonify(x)
    return json_data


@app.route('/searchsecondyear')
def searchsecondyear():
    collection='PersonalInfo'
    query={}
    personal=DB.find_many(collection,query)
    return render_template('adminhome.html', username=session.get('user'), personal=personal)


@app.route('/searchthirdyear')
def searchthirdyear():
    data = pd.read_json(codecs.open('a.json','r','utf-8'))
    return data

@app.route('/searchfinalyear')
def searchfinalyear():
    return "Final Year"

@app.route('/adminlogout')
def adminlogout():
    if session.get('user'):
        session.pop('user')
        flash('You were successfully logged out')
        return redirect(url_for('adminloginpage'))

@app.route('/studentlogout')
def studentlogout():
    if session.get('user'):
        session.pop('user')
        flash('You were successfully logged out')
        return redirect(url_for('loginpage'))

if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5000, debug=True)
