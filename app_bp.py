# Importing essential libraries
from flask import Flask, render_template, request
import pickle
import numpy as np

# Load the Random Forest CLassifier model
filename = 'bloodpressure-prediction-rfc-model.pkl'
classifier = pickle.load(open(filename, 'rb'))

app = Flask(__name__)

@app.route('/')
def home():
	return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    if request.method == 'POST':
        Patient_Number = int(request.form['Patient_Number'])
        LOHemoglobin = int(request.form['LOHemoglobin'])
        Age = int(request.form['Age'])
        BMI = int(request.form['BMI'])
        Sex = int(request.form['Sex'])
        Smoking = float(request.form['Smoking'])
        Physical_activity = float(request.form['Physical_activity'])
        salt_citd = int(request.form['salt_citd'])
        Level_of_Stress  = int(request.form['Level_of_Stress'])
        CKD  = int(request.form['CKD'])
        ATD  = int(request.form['ATD'])
        
        data = np.array([[Patient_Number, LOHemoglobin,Age,BMI,Sex,Smoking,Physical_activity,salt_citd,Level_of_Stress,CKD,ATD]])
        my_prediction = classifier.predict(data)
        
        return render_template('result.html', prediction=my_prediction)

if __name__ == '__main__':
	app.run(debug=True)

