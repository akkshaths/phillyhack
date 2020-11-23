from flask import Flask, request, session, g, redirect, \
    url_for, abort, render_template, flash

from database import update_emission_from_users
from database import select_emission_from_usertable

from database import addUser
from database import checkUser
import datetime
from urllib.request import urlopen as urlopen
import os, sys, json

app = Flask(__name__)
app.config.from_object(__name__)

app.config.from_envvar('APP_CONFIG_FILE', silent=True)

MAPBOX_ACCESS_KEY = app.config['MAPBOX_ACCESS_KEY']

app.secret_key = 'Bob'

@app.route('/')
def hello():
    return render_template("homepage.html")

@app.route('/login')
def login():
    return render_template("login.html", errorMessage='')

@app.route('/check', methods = ['POST'])
def check():
    userList = [request.form['username'], request.form['password']]
    checkMark = checkUser(userList[0], userList[1])
    if checkMark == 1:
        session['ID'] = userList
        return redirect('/dashboard')
    else:
        return render_template("login.html", errorMessage='Invalid username or password.')

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/checkS', methods = ['POST'])
def check2():
    userList = request.form['Submit']
    checkMark = addUser(userList[0], userList[1])
    if checkMark == 1:
        session['ID'] = userList
        return redirect('/dashboard')
    else:
        return render_template("login.html", errorMessage='This username already exists. Please try a new one')

@app.route('/dashboard')
def dash():
    userData = select_emission_from_usertable(session['ID'][0])
    daysPassed = datetime.date.today() - userData[3]

    if daysPassed == 0:
        return render_template('dashboard.html', Day=0, Month=0, Year=0)
    day = int(userData[4]/(daysPassed.days))

    month = int(day * 30)

    year = int(month *12)
    return render_template('dashboard.html', Day=str(day) + "\n", Month=str(month)+"\n", Year=str(year)+"\n")

@app.route('/goBack', methods = ['POST'])
def look():
    userList = request.form['Submit2']
    query = userList[0]
    resp1 = urlopen('https://api.tiles.mapbox.com/geocoding/v5/mapbox.places/{query}.json?access_token={token}'.format(query=query, token=MAPBOX_ACCESS_KEY))
    coord1 = json.loads(resp1.read().decode('utf-8'))["u'features"]["u'center"]
    print("done")
    query = userList[1]
    resp2 = urlopen('https://api.tiles.mapbox.com/geocoding/v5/mapbox.places/{query}.json?access_token={token}'.format(query=query, token=MAPBOX_ACCESS_KEY))
    coord2 = json.loads(resp2.read().decode('utf-8'))["u'features"]["u'center"]
    print("done")
    newT = urlopen("https://api.mapbox.com/directions/v5/mapbox/cycling/-122.42,37.78;-77.03,38.91?access_token=pk.eyJ1IjoiYWtrc2hhdGhzIiwiYSI6ImNraGN2dWp4YzBjdG4yeXMydWpkM2poZzkifQ.GekNoGm7gaC9qxAPWN-7Cw")
    addToCurrent = json.loads(newT.read().decode('utf-8'))["legs"]["distance"] *0.000621371
    print("done")
    if userList[2] == "Diesel under 20K lbs":
        addToCurrent *= .3
    elif userList[2] == "Diesel 20-30K lbs":
        addToCurrent *= .188
    elif userList[2] == "Diesel above 33K lbs":
        addToCurrent *= .2
    elif userList[2] == "Gas under 20K lbs":
        addToCurrent *= .33
    elif userList[2] == "Gas 20-30K lbs":
        addToCurrent *= .203
    elif userList[2] == "Gas above 33K lbs":
        addToCurrent *= .210
    else:
        addToCurrent = 0
    
    

    update_emission_from_users(session['ID'][0], select_emission_from_usertable(session['ID'][4]+int(addToCurrent)))
    return redirect('/dashboard')
    



@app.route('/addRoute')
def mapbox_js():
    return render_template(
        'addRoute.html', 
        ACCESS_KEY=MAPBOX_ACCESS_KEY
    )

