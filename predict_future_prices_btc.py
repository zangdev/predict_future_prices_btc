import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
import requests
import time
import os


# Function to fetch real-time Bitcoin price data from CoinGecko API
def get_bitcoin_price():
    try:
        url = "https://bitcoinaverage-global-bitcoin-index-v1.p.rapidapi.com/indices/global/ticker/BTCUSD"
        headers = {
            "X-RapidAPI-Key": "*************************",
            "X-RapidAPI-Host": "bitcoinaverage-global-bitcoin-index-v1.p.rapidapi.com"
        }
        response = requests.get(url, headers=headers)
        data = response.json()
        bitcoin_price = data['last']
        return bitcoin_price
    except Exception as e:
        print("Error fetching Bitcoin price:", e)
        return None


# Function to predict future Bitcoin prices using linear regression
def predict_future_prices(bitcoin_data, num_days=1):
    X = bitcoin_data.index.values.reshape(-1, 1)
    y = bitcoin_data['Price']
    model = LinearRegression()
    model.fit(X, y)
    future_index = len(bitcoin_data) + num_days
    future_price = model.predict([[future_index]])[0]
    return future_price


# Function to determine buy, sell, or hold signal
def determine_signal(current_price, predicted_price):
    if predicted_price > current_price:
        return "Buy"
    elif predicted_price < current_price:
        return "Sell"
    else:
        return "Hold"


# Main function for real-time prediction
def real_time_prediction(initial_samples=10, retrain_threshold=20):
    historical_data = pd.DataFrame(columns=['Date', 'Price'])  # Initialize empty DataFrame
    prediction_count = 0

    while prediction_count < initial_samples:  # Fetch initial historical data for a certain number of samples
        real_time_price = get_bitcoin_price()
        if real_time_price is not None:
            historical_data = pd.concat(
                [historical_data, pd.DataFrame({'Date': [pd.Timestamp.now()], 'Price': [real_time_price]})],
                ignore_index=True)
            print("Fetched historical Bitcoin price:", real_time_price)
            prediction_count += 1
        time.sleep(1)  # Wait for 1 second before fetching next sample

    while True:
        #os.system('cls' if os.name == 'nt' else 'clear')  # Clear screen
        current_price = get_bitcoin_price()
        if current_price is not None:
            predicted_price = predict_future_prices(historical_data)
            signal = determine_signal(current_price, predicted_price)
            print("Current Bitcoin Price:", current_price)
            print("Predicted Price (10 seconds later):", predicted_price)
            print("Signal:", signal)

            # Check if we need to retrain the model
            if len(historical_data) >= retrain_threshold:
                print("\nRetraining the model with updated data...\n")
                historical_data = historical_data.iloc[-retrain_threshold:]  # Keep only the last 'retrain_threshold' samples
                predicted_price = predict_future_prices(historical_data)
                signal = determine_signal(current_price, predicted_price)
                print("New Prediction:", "| Predicted Price:", predicted_price, "| Signal:", signal)

            # Check for sell signal or price deviation
            if signal == "Sell" or abs(predicted_price - current_price) > 100:
                print("Sell signal detected or price deviation detected. Cancelling order.")
                # Add your logic here for cancelling the order or any other action you want to take
                print("Cancel")
                print("+++++++++++++++++++++++")

            # Check for successful profit-taking
            # Add your logic here for detecting successful profit-taking
            if current_price - predicted_price >= 1:
                print("Profit-taking opportunity detected. Taking profit.")
                # Add your logic here for taking profit or any other action you want to take
                print("Take Profit")
                print("+++++++++++++++++++++++")

            time.sleep(10)  # Wait for 10 seconds before fetching again
        else:
            print("Error fetching current Bitcoin price. Retrying in 10 seconds...")
            time.sleep(10)  # Wait for 10 seconds before retrying


# Start real-time prediction
real_time_prediction()
