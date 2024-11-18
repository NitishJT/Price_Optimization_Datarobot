
# Hotel Revenue Optimization Dashboard

A Streamlit-based web application that integrates with **DataRobot's Prediction API** to optimize hotel revenue. It forecasts occupancy rates, recommends price points, and calculates maximum possible revenue for future dates based on historical data.

---

## Features

- **Upload Historical Data**: Upload historical hotel data in CSV format.
- **Automatic Forecast Point**: Determines the last date in the uploaded data as the forecast point for predictions.
- **Revenue Optimization**: Predicts future occupancy and calculates the optimal price point for maximum revenue.
- **Date Selection**: Choose up to 7 future dates for prediction beyond the forecast point.
- **Dynamic Price Range**: Define minimum and maximum price points for exploring different pricing strategies.
- **DataRobot Integration**: Uses **DataRobot's Deployment API** for predictions.

---

## Installation

### Prerequisites
- Python 3.7 or later.
- **Streamlit** for the web application.
- A **DataRobot** account with a deployed model and API access.

### Install Required Libraries
Run the following command:

```bash
pip install -r requirements.txt
```

---

### Setting Up

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/NitishJT/Price_Optimization_Datarobot.git
   cd Price_Optimization_Datarobot
   ```

2. **Set Up a Virtual Environment (Optional but Recommended)**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use venv\Scripts\activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set Up Environment Variables**:
   - Create a `.env` file in the root directory.
   - Add the following:
     ```plaintext
     API_URL=https://app.datarobot.com/api/v2/deployments/{deployment_id}/predictions
     API_KEY=<your-datarobot-api-key>
     DEPLOYMENT_ID=<your-datarobot-deployment-id>
     ```
     Replace `<your-datarobot-api-key>` and `<your-datarobot-deployment-id>` with your DataRobot credentials.

5. **Update `.gitignore`**:
   Add sensitive files and directories to `.gitignore`:
   ```plaintext
   .env
   venv/
   input_files/
   ```

---

## How It Works

### Workflow

1. **Upload Historical Data**:
   - Users upload a CSV file containing historical hotel data.
   - Required columns: `Date`, `DayOfWeek`, `IsWeekend`, `Event`, `CompetitorPrice`, `Price`, and other relevant features.
   - Application preprocesses the data (e.g., filling missing values).

2. **Set Forecast Point**:
   - Automatically determines the last date in the uploaded data as the forecast point.
   - Predicts for up to 7 days beyond the forecast point.

3. **Select Prediction Dates**:
   - Users select future dates (up to 7) for prediction.

4. **Define Pricing Strategy**:
   For each selected date:
   - Specify **Event Indicator** (0 for no event, 1 for an event).
   - Provide **Minimum and Maximum Price Points**.
   - Add **Competitor Prices**.

5. **Predict and Optimize**:
   - Uses DataRobot's Deployment API to predict occupancy for each price point.
   - Calculates revenue as:
     ```plaintext
     Max_Revenue = Predicted_Occupancy × Price
     ```
   - Identifies the optimal price point (maximizing revenue) for each date.

6. **Output Results**:
   - Displays results, including optimal price and revenue for each date, in the application.
   - Saves results to a local CSV file (`final_max_revenue.csv`).

---

## Usage

### Run the Streamlit Application
```bash
streamlit run app.py
```

### Using the Application
1. Upload a historical data CSV file.
2. Review the **Forecast Point** (last date in the historical data).
3. Select future dates, define pricing ranges, and provide competitor prices.
4. Click "Calculate Max Revenue" to view results.
5. Download results from the saved CSV file (`final_max_revenue.csv`).

---

## Example CSV Format

The historical data file should have the following columns:

| Date       | DayOfWeek | IsWeekend | Event | CompetitorPrice | Price  |
|------------|-----------|-----------|-------|-----------------|--------|
| 2024-11-10 | 0         | 0         | 1     | 120.0           | 100.0  |
| 2024-11-11 | 1         | 0         | 0     | 110.0           | 105.0  |

---

## Key Files

- **app.py**: Main application code.
- **.env**: Stores API credentials (ignored in version control).
- **requirements.txt**: Lists Python dependencies.

---

## Requirements

Ensure the following libraries are in `requirements.txt`:

```plaintext
streamlit
pandas
numpy
requests
python-dotenv
```

---

## DataRobot API Details

- **API URL**:  
  `https://app.datarobot.com/api/v2/deployments/{deployment_id}/predictions`
- **Authorization**:  
  Use the API key as a **Bearer token**.
- **Request Format**:  
  - Historical and future data are combined and sent in CSV format.
  - The forecast point is specified as a query parameter (`forecastPoint`).

---

## Troubleshooting

1. **403: Permission Denied**:  
   Ensure the correct API key and deployment ID are set in `.env`.

2. **FileNotFoundError**:  
   Ensure the `input_files` directory exists or is created dynamically by the application.

3. **Prediction Errors**:  
   Verify the uploaded CSV matches the required format.

---

## Future Enhancements

- Add support for visualizations (e.g., revenue trends, price-occupancy heatmaps).
- Improve error handling for API failures.
- Extend support for multivariate models using additional features.

