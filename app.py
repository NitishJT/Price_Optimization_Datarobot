import streamlit as st
import pandas as pd
import numpy as np
import datetime
import requests
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Constants and API details loaded from .env
API_URL = os.getenv('API_URL')
API_KEY = os.getenv('API_KEY')
DEPLOYMENT_ID = os.getenv('DEPLOYMENT_ID')

# Function to make predictions
def make_datarobot_deployment_predictions(data, deployment_id, forecast_point):
    headers = {
        'Content-Type': 'text/plain; charset=UTF-8',
        'Authorization': f'Bearer {API_KEY}',
    }
    url = API_URL.format(deployment_id=deployment_id)
    params = {'forecastPoint': forecast_point}
    response = requests.post(url, data=data, headers=headers, params=params)
    response.raise_for_status()
    return response.json()

# Function to calculate and store max revenue
def calculate_and_store_max_revenue(results, date, details, final_results):
    max_revenue_row = results.loc[results['Revenue'].idxmax()]
    final_results.append({
        'Date': date,
        'DayOfWeek': details['day_of_week'],
        'IsWeekend': details['is_weekend'],
        'Event': details['event'],
        'CompetitorPrice': details['competitor_price'],
        'Occupancy': max_revenue_row['Predicted_Occupancy'],
        'Price': max_revenue_row['Price'],
        'Max_Revenue': max_revenue_row['Revenue']
    })

# Helper function to clean and normalize historical data
def clean_historical_data(df):
    if 'IsWeekend' not in df.columns:
        df['IsWeekend'] = df['DayOfWeek'].apply(lambda x: x in [5, 6])  # Saturday (5) and Sunday (6)
    df['Event'] = df['Event'].fillna(0).astype(int)
    df['CompetitorPrice'] = df['CompetitorPrice'].fillna(0).astype(float)
    df['Price'] = df['Price'].fillna(0).astype(float)
    return df

# Helper function to calculate `DayOfWeek` and `IsWeekend`
def get_day_details(date_str):
    date_obj = datetime.datetime.strptime(date_str, '%m/%d/%Y')
    day_of_week = date_obj.weekday()  # 0 = Monday, ..., 6 = Sunday
    is_weekend = day_of_week in [5, 6]
    return day_of_week, is_weekend

# Streamlit UI components
st.title('Hotel Revenue Optimization Dashboard')

# Upload historical data file
uploaded_file = st.file_uploader("Choose a CSV file containing historical data", type="csv")
if uploaded_file is not None:
    historical_data = pd.read_csv(uploaded_file)
    historical_data = clean_historical_data(historical_data)

    # Determine the last date in historical data as the forecast point
    last_date = pd.to_datetime(historical_data['Date']).max()
    max_selectable_date = last_date + pd.Timedelta(days=7)
    forecast_point = last_date.strftime("%Y-%m-%dT00:00:00Z")  # Format for forecast point

    st.write(f"The last date in the historical data is: {last_date.date()}")
    st.write(f"Forecast point is automatically set to: {forecast_point}")
    st.write(f"You can select prediction dates up to: {max_selectable_date.date()}")

    num_dates = st.slider("Select number of dates to predict", 1, 7, 1)
    date_details = {}
    for i in range(num_dates):
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            # User selects date within the allowed range
            selected_date = st.date_input(
                f"Date {i+1} (YYYY-MM-DD)",
                key=f"date_{i}",
                min_value=last_date + pd.Timedelta(days=1),
                max_value=max_selectable_date
            )
            if selected_date:
                date = selected_date.strftime("%m/%d/%Y")  # Convert to `MM/DD/YYYY`
        with col2:
            event = st.number_input(f"Event {i+1}", key=f"event_{i}", min_value=0, step=1)
        with col3:
            min_price = st.number_input(f"Min Price {i+1}", key=f"min_{i}", min_value=0.0, step=0.1)
        with col4:
            max_price = st.number_input(f"Max Price {i+1}", key=f"max_{i}", min_value=min_price, step=0.1)
        with col5:
            competitor_price = st.number_input(f"Competitor Price {i+1}", key=f"comp_{i}", min_value=0.0, step=0.1)

        if selected_date:
            day_of_week, is_weekend = get_day_details(date)
            date_details[date] = {
                "day_of_week": day_of_week,
                "is_weekend": is_weekend,
                "event": event,
                "min_price": min_price,
                "max_price": max_price,
                "competitor_price": competitor_price
            }

    # Button to calculate revenue
    if st.button("Calculate Max Revenue"):
        if not os.path.exists('input_files'):
            os.makedirs('input_files')

        final_results = []

        for date, details in date_details.items():
            price_points = np.linspace(details['min_price'], details['max_price'], num=10)
            price_revenue_predictions = []

            for price in price_points:
                future_data = pd.DataFrame([{
                    'Date': date,
                    'DayOfWeek': details['day_of_week'],
                    'IsWeekend': details['is_weekend'],
                    'Event': details['event'],
                    'CompetitorPrice': details['competitor_price'],
                    'Price': price,
                }])
                combined_data = pd.concat([historical_data, future_data], ignore_index=True)
                data = combined_data.to_csv(index=False)

                prediction = make_datarobot_deployment_predictions(data, DEPLOYMENT_ID, forecast_point)
                predicted_occupancy = prediction['data'][0]['prediction']
                revenue = price * predicted_occupancy
                price_revenue_predictions.append({
                    'Date': date,
                    'Price': price,
                    'Predicted_Occupancy': predicted_occupancy,
                    'Revenue': revenue
                })

            if price_revenue_predictions:
                results_df = pd.DataFrame(price_revenue_predictions)
                calculate_and_store_max_revenue(results_df, date, details, final_results)

        # Save the final results to a CSV
        final_results_df = pd.DataFrame(final_results)
        final_results_df.to_csv('final_max_revenue.csv', index=False)
        st.write("Final max revenue results saved to `final_max_revenue.csv`")
        st.write(final_results_df)
else:
    st.write("Please upload a CSV file to continue.")