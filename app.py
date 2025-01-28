import numpy as np
import pandas as pd
import tensorflow as tf
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error, mean_absolute_percentage_error
from flask import Flask, request, jsonify
import os
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
from tensorflow.keras.optimizers import Adam
from datetime import datetime


# Initialize Flask app
app = Flask(__name__)

# Define file paths for each company
file_paths = {
    "RL": "RL_April18_March24.csv",
    "TCS": "TCS_April18_March24.csv",
    "HDFC": "HDFC_April18_March24.csv"
}

# Load and preprocess data
def load_and_preprocess_data(company_name, start_date, end_date):
    # Check if the company exists
    if company_name not in file_paths:
        raise ValueError("Invalid company name. Choose from RL, TCS, or HDFC.")

    # Load the CSV file for the selected company
    df = pd.read_csv(file_paths[company_name])

    # Log the columns in the DataFrame
    print("Columns in the CSV file:", df.columns)

    # Verify the 'Date' column name
    if 'Date' not in df.columns:
        raise ValueError("'Date' column not found. Please check the CSV file column names.")

    # Convert the 'Date' column to datetime, handling errors by coercing invalid dates to NaT
    df['Date'] = pd.to_datetime(df['Date'], format='%d-%b-%y', errors='coerce')

    # Drop rows with NaT (invalid dates)
    df = df.dropna(subset=['Date'])

    # Filter by the date range
    df = df[(df['Date'] >= start_date) & (df['Date'] <= end_date)]

    # Extract relevant columns and handle missing values
    columns = ['Open Price', 'High Price', 'Low Price', 'Close Price', 'Volume']
    data = df[columns].values

    # Handle missing values by replacing NaN values with the column means
    if np.any(np.isnan(data)):
        data = np.nan_to_num(data, nan=np.nanmean(data, axis=0))

    # Scale the data
    scaler = MinMaxScaler()
    data_scaled = scaler.fit_transform(data)
    
    return data_scaled, scaler

# Create rolling sequences
def create_rolling_sequences(data_scaled, window_size=10):
    X, y = [], []
    for i in range(len(data_scaled) - window_size):
        X.append(data_scaled[i:i + window_size])
        y.append(data_scaled[i + window_size, 0])  # Predicting 'Open Price' (first column)
    return np.array(X), np.array(y)

# Build and compile LSTM model
def build_model(input_shape):
    model = Sequential()
    model.add(LSTM(units=50, return_sequences=True, input_shape=input_shape))
    model.add(LSTM(units=50, return_sequences=False))
    model.add(Dense(units=1))  # Predicting the 'Open Price'
    model.compile(optimizer=Adam(learning_rate=0.001), loss='mean_squared_error')
    return model

@app.route('/predict', methods=['POST']) 
def predict():
    try:
        # Log the incoming data for debugging
        data = request.get_json()
        print("Received data:", data)

        # Validate the incoming data
        if not data or 'company_name' not in data or 'start_date' not in data or 'end_date' not in data:
            return jsonify({"error": "Missing required fields: company_name, start_date, end_date"}), 400

        company_name = data['company_name']
        start_date = datetime.strptime(data['start_date'], '%Y-%m-%d')
        end_date = datetime.strptime(data['end_date'], '%Y-%m-%d')

        # Step 1: Load and preprocess data
        processed_data, scaler = load_and_preprocess_data(company_name, start_date, end_date)

        # Step 2: Create rolling sequences
        window_size = 10
        X, y = create_rolling_sequences(processed_data, window_size)

        # Step 3: Build and train the LSTM model
        if len(X) == 0 or len(y) == 0:
            return jsonify({"error": "Not enough data points to create sequences"}), 400

        model = build_model(input_shape=(X.shape[1], X.shape[2]))
        model.fit(X, y, epochs=100, batch_size=32, verbose=1)

        # Step 4: Make predictions
        predictions = model.predict(X)
        predictions_inverse = scaler.inverse_transform(
            np.hstack((predictions, np.zeros((predictions.shape[0], processed_data.shape[1] - 1))))
        )[:, 0]  # Inverse scale predictions only for 'Open Price'

        # Step 5: Calculate evaluation metrics
        y_inverse = scaler.inverse_transform(
            np.hstack((y.reshape(-1, 1), np.zeros((y.shape[0], processed_data.shape[1] - 1))))
        )[:, 0]
        mae = mean_absolute_error(y_inverse, predictions_inverse)
        mse = mean_squared_error(y_inverse, predictions_inverse)
        mape = mean_absolute_percentage_error(y_inverse, predictions_inverse)

        # Step 6: Return results
        return jsonify({
            "message": "Prediction successful",
            "metrics": {
                "MAE": mae,
                "MSE": mse,
                "MAPE": mape
            },
            "predictions": predictions_inverse.tolist(),
            "actuals": y_inverse.tolist()
        })
    except Exception as e:
        # Log any error for debugging
        print(f"Error occurred: {e}")
        return jsonify({"error": str(e)}), 400


if __name__ == '__main__':
    # Ensure the required CSV files are present
    for file in file_paths.values():
        if not os.path.exists(file):
            raise FileNotFoundError(f"CSV file '{file}' not found.")

    # Run the Flask app
    app.run(debug=True)
