from flask import Flask, request, render_template, flash, redirect, url_for
import numpy as np
import pickle
import secrets
app = Flask(__name__)
app.secret_key = secrets.token_hex(16)



model = pickle.load(open("Model.pkl", "rb"))

# Dictionary mapping pollutant names to their index values

pollutants = {
    "PM2.5": 0,
    "PM10": 1,
    "NO2": 2,
    "NH3": 3,
    "SO2": 4,
    "CO": 5,
    "O3": 6,
}

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/predict', methods=['POST'])
def predict():
    float_values = []

    # Check if PM2.5 or PM10 is greater than zero
    if float(request.form['input1']) <= 0 and float(request.form['input2']) <= 0:
        flash('Either PM2.5 or PM10 must have a value greater than zero.', 'error')
        return redirect(url_for('home'))

    # Check if at least three pollutants have values greater than zero
    valid_pollutant_count = 0
    for key, value in request.form.items():
        # Check if the value is not empty and is a valid float
        if isinstance(value, str) and value and value.replace('.', '', 1).isdigit():
            float_value = float(value)
            float_values.append(float_value)
            # Count the valid pollutant values greater than zero
            if float_value > 0:
                valid_pollutant_count += 1

    # Print the number of valid pollutant values for debugging
    print(f"Valid pollutant count: {valid_pollutant_count}")

    if valid_pollutant_count < 3:
        flash('At least three valid pollutant values greater than zero are required to predict AQI', 'error')
        return redirect(url_for('home'))

    Values = [np.array(float_values)]
    prediction = model.predict(Values)
    
    # Calculate AQI sub-indices
    pmsi, pmli, NOi, NHi, SOi, COi, Oi = float_values
    sub_indices = {
        "PM2.5": pmsi,
        "PM10": pmli,
        "NO2": NOi,
        "NH3": NHi,
        "SO2": SOi,
        "CO": COi,
        "O3": Oi,
    }

    
    # Find the pollutant name with the maximum sub-index
    max_pollutant = max(sub_indices, key=lambda x: sub_indices[x])

    return render_template("index.html",
                           prediction_text=str(prediction[0]),
                           prominent_pollutant=max_pollutant,
                           prediction_css_class=get_css_class(prediction[0]))



    
    

def get_css_class(prediction):
    # Determine the CSS class based on prediction range
    if 0 <= prediction <= 50:
        return "parrot-green"
    elif 51 <= prediction <= 100:
        return "light-green"
    elif 101 <= prediction <= 200:
        return "yellow"
    elif 201 <= prediction <= 300:
        return "orange"
    elif 301 <= prediction <= 400:
        return "red"
    else:
        return "dark-red"

if __name__ == '__main__':
    app.run(debug=True)
