from flask import Flask, request, session, redirect, url_for, render_template
from flaskext.mysql import MySQL
import pymysql
import plotly
import plotly.express as px
import pandas as pd 
import re 
import json
import pickle
import numpy as np

C:\Users\Suyog\Downloads\db and bp prediction\db and bp\csv file
g1=pd.read_csv('C:/Users/Suyog/Downloads/db and bp prediction/db and bp/csv file/diabetes.csv')
g2=pd.read_csv('C:/Users/Suyog/Downloads/db and bp prediction/db and bp/csv file/data.csv')
g3=pd.read_csv('C:/Users/Suyog/Downloads/db and bp prediction/db and bp/csv file/aware.csv')
g4=pd.read_csv('C:/Users/Suyog/Downloads/db and bp prediction/db and bp/csv file/preval.csv')
g5=pd.read_csv('C:/Users/Suyog/Downloads/db and bp prediction/db and bp/csv file/prevalbp.csv')
g6=pd.read_csv('C:/Users/Suyog/Downloads/db and bp prediction/db and bp/csv file/AWAREBP.csv')
g7=pd.read_csv('C:/Users/Suyog/Downloads/db and bp prediction/db and bp/csv file/coviddata.csv')
               
filename = 'diabetes-prediction-lr-model.pkl'
regression = pickle.load(open(filename, 'rb'))

# Load the Random Forest CLassifier model
filename = 'bloodpressure-prediction-rfc-model.pkl'
classifier = pickle.load(open(filename, 'rb'))

app = Flask(__name__, template_folder='template')
 
# Change this to your secret key (can be anything, it's for extra protection)
app.secret_key = 'cairocoders-ednalan'
 
mysql = MySQL()
   
# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = ''
app.config['MYSQL_DATABASE_DB'] = 'prediction'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)
 
# http://localhost:5000/pythonlogin/ - this will be the login page
@app.route('/pythonlogin/', methods=['GET', 'POST'])
def login():
 # connect
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
  
    # Output message if something goes wrong...
    msg = ''
    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        # Check if account exists using MySQL
        cursor.execute('SELECT * FROM users WHERE username = %s AND password = %s', (username, password))
        # Fetch one record and return result
        users = cursor.fetchone()
   
    # If account exists in accounts table in out database
        if users:
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['id'] = users['id']
            session['username'] = users['username']
            # Redirect to home page
            #return 'Logged in successfully!'
            return redirect(url_for('home'))
        else:
            # Account doesnt exist or username/password incorrect
            msg = 'Incorrect username/password!'
    
    return render_template('index.html', msg=msg)
 
# http://localhost:5000/register - this will be the registration page
@app.route('/register', methods=['GET', 'POST'])
def register():
 # connect
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
  
    # Output message if something goes wrong...
    msg = ''
    # Check if "username", "password" and "email" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        # Create variables for easy access
        fullname = request.form['fullname']
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
   
  #Check if account exists using MySQL
        cursor.execute('SELECT * FROM users WHERE username = %s', (username))
        users = cursor.fetchone()
        # If account exists show error and validation checks
        if users:
            msg = 'users already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        elif not username or not password or not email:
            msg = 'Please fill out the form!'
        else:
            # Account doesnt exists and the form data is valid, now insert new account into accounts table
            cursor.execute('INSERT INTO users VALUES (NULL, %s, %s, %s, %s)', (fullname, username, password, email)) 
            conn.commit()
   
            msg = 'You have successfully registered!'
    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Please fill out the form!'
    # Show registration form with message (if any)
    return render_template('register.html', msg=msg)
  
# http://localhost:5000/home - this will be the home page, only accessible for loggedin users
@app.route('/')
def home():
    # Check if user is loggedin
    if 'loggedin' in session:
   
        # User is loggedin show them the home page
        return render_template('home.html', username=session['username'])
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

      
# http://localhost:5000/logout - this will be the logout page
@app.route('/logout')
def logout():
    # Remove session data, this will log the user out
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   # Redirect to login page
   return redirect(url_for('login'))

@app.route('/indexdb')
def indexdb():
	return render_template('indexdb.html')

@app.route('/predict', methods=['POST'])
def predict():
    if request.method == 'POST':
        preg = int(request.form['pregnancies'])
        glucose = int(request.form['glucose'])
        bp = int(request.form['bloodpressure'])
        st = int(request.form['skinthickness'])
        insulin = int(request.form['insulin'])
        bmi = float(request.form['bmi'])
        dpf = float(request.form['dpf'])
        age = int(request.form['age'])
        
        data = np.array([[preg, glucose, bp, st, insulin, bmi, dpf, age]])
        my_prediction = regression.predict(data)
        
        return render_template('resultdb.html', prediction=my_prediction)
    
@app.route('/indexbp')
def indexbp():
	return render_template('indexbp.html')

@app.route('/submit', methods=['POST'])
def submit():
    if request.method == 'POST':
        Patient_Number = int(request.form['Patient_Number'])
        LOHemoglobin = float(request.form['LOHemoglobin'])
        Age = int(request.form['Age'])
        BMI = int(request.form['BMI'])
        Sex = int(request.form['Sex'])
        Smoking = int(request.form['Smoking'])
        Physical_activity = int(request.form['Physical_activity'])
        salt_citd = int(request.form['salt_citd'])
        Level_of_Stress  = int(request.form['Level_of_Stress'])
        CKD  = int(request.form['CKD'])
        ATD  = int(request.form['ATD'])
        
        data = np.array([[Patient_Number, LOHemoglobin,Age,BMI,Sex,Smoking,Physical_activity,salt_citd,Level_of_Stress,CKD,ATD]])
        my_prediction = classifier.predict(data)
        
        return render_template('resultbp.html', prediction=my_prediction)


@app.route('/diabetes')
def diabetes(): 
    fig = px.bar(g1, x='Outcome' , y='Age', title='Number of Pregnancies as compared to age',width=1000,height=500)  
    graph1 = json.dumps(fig,cls=plotly.utils.PlotlyJSONEncoder) 
    return render_template('diabetes.html',graph1=graph1)


@app.route('/bp')
def bp(): 
    fig = px.bar(g2, x='Blood_Pressure' , y='Age', title='Number of age as compared to bp patient',width=1000,height=500)  
    graph1 = json.dumps(fig,cls=plotly.utils.PlotlyJSONEncoder) 
    return render_template('bp.html',graph1=graph1)

@app.route('/awareness')
def awareness(): 
    fig = px.bar(g3, x='State' , y='Awareness in %', title='Awareness Of Diabetes Prevalence Among Patients, By State',width=1000,height=500)  
    graph1 = json.dumps(fig,cls=plotly.utils.PlotlyJSONEncoder) 
    return render_template('awareness.html',graph1=graph1)

@app.route('/awarenessbp')
def awarenessbp(): 
    fig = px.bar(g6, x='AREA WISE' , y='AWERENESS IN  %', title='Awareness Of bp in patient in rural and urban',width=1000,height=500)  
    graph1 = json.dumps(fig,cls=plotly.utils.PlotlyJSONEncoder) 
    return render_template('awarenessbp.html',graph1=graph1)

@app.route('/dbpre')
def dbpre(): 
    fig = px.bar(g4, x='State' , y='Diabetes Prevalence in %', title='Diabetes Prevalence, By State',width=1000,height=500)  
    graph1 = json.dumps(fig,cls=plotly.utils.PlotlyJSONEncoder) 
    return render_template('dbpre.html',graph1=graph1)

@app.route('/bppre')
def bppre(): 
    fig = px.bar(g5, x='State' , y='bloodpressure Prevalence in %', title='bloodpressure Prevalence, By State',width=1000,height=500)  
    graph1 = json.dumps(fig,cls=plotly.utils.PlotlyJSONEncoder) 
    return render_template('bppre.html',graph1=graph1)

@app.route('/coviddata')
def coviddata(): 
    fig = px.bar(g7, x='covid-19 diabetes and blood pressure death rate' , y='death rate in %', title='Due to diabetes and bloodpressure death rate covid-19 in maharashtra',width=1000,height=500)  
    graph1 = json.dumps(fig,cls=plotly.utils.PlotlyJSONEncoder) 
    return render_template('coviddata.html',graph1=graph1)


@app.route('/info')
def info():
    return render_template('info.html')

@app.route('/abv')
def abv():
    return render_template('abv.html')

  
if __name__ == '__main__':
    app.run(debug=True)
