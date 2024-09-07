from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from tensorflow.keras.models import load_model
import yfinance as yf
from sklearn.preprocessing import MinMaxScaler
import numpy as np
import datetime as dt
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import os

app = Flask(__name__)
CORS(app)

# Function to fetch and prepare data for prediction
def fetch_and_prepare_data(company_name, look_back=100):
    end_date = dt.datetime.now().strftime('%Y-%m-%d')
    data = yf.download(company_name, start="2010-01-01", end=end_date)
    close_prices = data['Close'].values.reshape(-1, 1)

    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_data = scaler.fit_transform(close_prices)

    last_100_days = scaled_data[-look_back:]
    last_100_days = last_100_days.reshape(1, last_100_days.shape[0], 1)

    return last_100_days, scaler, data.index, close_prices

# Function to load the model and predict
def predict_for_company(company_name):
    model_path = f'models/{company_name}_model.h5'
    
    if not os.path.exists(model_path):
        return None, "Model not found"

    model = load_model(model_path)
    latest_data, scaler, dates, close_prices = fetch_and_prepare_data(company_name)
    
    prediction = model.predict(latest_data)
    prediction = scaler.inverse_transform(prediction)

    return prediction.flatten()[0]

# Predict endpoint
@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json(force=True)
    company_name = data['company'].upper()
    

    prediction = predict_for_company(company_name)
            

    print(prediction)
    
    return jsonify({
        'company': company_name,
        'prediction': float(prediction)
    })



# Plotting logic as an endpoint
@app.route('/plot', methods=['POST'])
def plot():
    try:
        data = request.get_json(force=True)
        company_name = data['company'].upper()

        # Load model and make prediction
        predicted_price, error = predict_for_company(company_name)

        if error:
            return jsonify({'error': error}), 404

        # Fetch stock data
        _, _, dates, actual_prices = fetch_and_prepare_data(company_name)

        # Create a plot
        plt.figure(figsize=(14, 7))
        plt.plot(dates, actual_prices, label='Actual Prices')

        # Plot the predicted price (as the next day's price)
        future_date = dates[-1] + pd.Timedelta(days=1)
        plt.plot(future_date, predicted_price, 'ro', label='Predicted Price (Next Day)')

        # Format the x-axis to show years
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
        plt.gca().xaxis.set_major_locator(mdates.YearLocator())

        plt.title(f'{company_name} Stock Price Prediction')
        plt.xlabel('Year')
        plt.ylabel('Price ($)')
        plt.legend()
        plt.grid(True)

        # Save the plot as an image
        plot_filename = f'plot_{company_name}.png'
        plt.savefig(plot_filename)
        plt.close()

        # Send the image file to the frontend
        return send_file(plot_filename, mimetype='image/png')

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
