import yfinance as yf
import numpy as np
import datetime as dt
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, LSTM
import os

# List of banks and tech companies
companies = [
    'JPM', 'BAC', 'WFC', 'C', 'GS', 'MS', 'HSBC', 'BCS', 'DB', 'BNPQY', 'UBS',
    'RY', 'TD', 'MUFG', 'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'TSLA', 'NVDA',
    'ORCL', 'INTC', 'CSCO', 'IBM', 'CRM', 'ADBE', 'NFLX', 'AMD'
]

# Fetch and prepare data from Yahoo Finance
def fetch_data_for_companies(companies):
    end_date = dt.datetime.now().strftime('%Y-%m-%d')  # Current date
    data = {}
    
    for company in companies:
        print(f"Fetching data for {company}...")
        company_data = yf.download(company, start="2010-01-01", end=end_date)
        data[company] = company_data

    return data

# Function to train model for a specific company
def train_model(company_data, company_name, look_back=100):
    # Prepare the data for training
    close_prices = company_data['Close'].values.reshape(-1, 1)
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_data = scaler.fit_transform(close_prices)

    # Create input-output sequences for the LSTM
    def create_dataset(data, look_back=100):
        X, Y = [], []
        for i in range(len(data) - look_back - 1):
            X.append(data[i:(i + look_back), 0])
            Y.append(data[i + look_back, 0])
        return np.array(X), np.array(Y)

    X, Y = create_dataset(scaled_data, look_back)
    X = X.reshape((X.shape[0], X.shape[1], 1)) 

    # Build the LSTM model
    model = Sequential([
        LSTM(50, return_sequences=True, input_shape=(X.shape[1], 1)),
        LSTM(50),
        Dense(1)
    ])
    
    model.compile(optimizer='adam', loss='mean_squared_error')

    
    print(f"Training model for {company_name}...")
    model.fit(X, Y, epochs=50, batch_size=32, verbose=1)
    
    # Save the model
    if not os.path.exists('models'):
        os.makedirs('models')
    model.save(f'models/{company_name}_model.h5')
    print(f"Model for {company_name} saved.")

# Fetch data for the list of companies
data = fetch_data_for_companies(companies)

company = 'AAPL'
train_model(data[company],company)
'''
# Train and save models for each company
for company in companies:
    if company in data:
        train_model(data[company], company)
'''