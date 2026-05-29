import pandas as pd
import numpy as np
import streamlit as st
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
from typing import Tuple

@st.cache_data
def aggregate_and_forecast(
    df: pd.DataFrame, 
    interval: str = "Daily", 
    model_type: str = "Random Forest Regressor", 
    estimators: int = 100, 
    periods: int = 30
) -> Tuple[pd.DataFrame, pd.DataFrame, float]:
    """
    Aggregates historical daily spending into weekly or monthly totals, performs 
    feature engineering, trains a machine learning model, and forecasts spending 
    for the upcoming configured days. Cached using st.cache_data.

    Parameters:
        df (pd.DataFrame): Input transactions DataFrame containing 'Date' and 'Amount' columns.
        interval (str): Aggregation level - 'Daily', 'Weekly', or 'Monthly'. Defaults to 'Daily'.
        model_type (str): ML algorithm - 'Random Forest Regressor' or 'Linear Regression'. Defaults to 'Random Forest Regressor'.
        estimators (int): Number of trees in the Random Forest ensemble. Defaults to 100.
        periods (int): Forecast horizon in days. Defaults to 30.

    Returns:
        Tuple[pd.DataFrame, pd.DataFrame, float]: A tuple containing:
            - hist_series (pd.DataFrame): Aggregated historical totals (Date, Amount).
            - future_df (pd.DataFrame): Forecasted values for future dates (Date, Amount).
            - r2_val (float): R-squared goodness-of-fit statistic on the training set.
    """
    # Resilience check for empty dataframes
    if df is None or df.empty:
        empty_hist = pd.DataFrame(columns=['Date', 'Amount'])
        empty_future = pd.DataFrame(columns=['Date', 'Amount'])
        return empty_hist, empty_future, 0.0

    # Ensure transactions are sorted chronologically
    df_sorted = df.copy().sort_values(by='Date')
    min_date = df_sorted['Date'].min()
    max_date = df_sorted['Date'].max()
    
    # Scale forecasting periods according to aggregation type
    if interval == "Weekly":
        freq = 'W'
        periods_scaled = max(1, int(periods / 7))
    elif interval == "Monthly":
        freq = 'MS'
        periods_scaled = max(1, int(periods / 30))
    else:
        freq = 'D'
        periods_scaled = periods
        
    # Generate continuous date range to fill missing intervals with 0
    full_range = pd.date_range(start=min_date, end=max_date, freq=freq)
    
    # Aggregate spending inside the target frequency
    grouped = df_sorted.groupby(pd.Grouper(key='Date', freq=freq))['Amount'].sum()
    aggregated = grouped.reindex(full_range, fill_value=0.0).reset_index()
    aggregated.columns = ['Date', 'Amount']
    
    # Feature engineering for the ML model
    aggregated['TimeIndex'] = np.arange(len(aggregated))
    aggregated['MonthOfYear'] = aggregated['Date'].dt.month
    
    features = ['TimeIndex', 'MonthOfYear']
    if freq == 'D':
        aggregated['DayOfWeek'] = aggregated['Date'].dt.dayofweek
        features.append('DayOfWeek')
        
    X = aggregated[features]
    y = aggregated['Amount']
    
    # Select and train the Predictive Model
    if model_type == "Linear Regression":
        model = LinearRegression()
    else:
        model = RandomForestRegressor(n_estimators=estimators, random_state=42)
        
    model.fit(X, y)
    
    # Predict future intervals
    future_dates = pd.date_range(start=aggregated['Date'].max(), periods=periods_scaled + 1, freq=freq)[1:]
    future_df = pd.DataFrame({'Date': future_dates})
    future_df['TimeIndex'] = np.arange(len(aggregated), len(aggregated) + periods_scaled)
    future_df['MonthOfYear'] = future_df['Date'].dt.month
    
    if freq == 'D':
        future_df['DayOfWeek'] = future_df['Date'].dt.dayofweek
        
    # Predict future expenditures
    X_future = future_df[features]
    future_df['Amount'] = model.predict(X_future)
    future_df['Amount'] = future_df['Amount'].clip(lower=0.0) # Ensure spending is positive
    
    # Calculate training fit quality (R² score)
    train_pred = model.predict(X)
    r2_val = float(r2_score(y, train_pred))
    
    return aggregated, future_df, r2_val

@st.cache_data
def forecast_category_spending(df: pd.DataFrame, category: str, periods: int = 15) -> float:
    """
    Trains a category-specific Random Forest model on historical daily spend
    to forecast the total expenditure for this category over the upcoming period.
    Cached using st.cache_data.

    Parameters:
        df (pd.DataFrame): The full transaction database.
        category (str): The specific spending category to forecast.
        periods (int): Forecast horizon in days. Defaults to 15.

    Returns:
        float: The sum of forecasted spending over the horizon.
    """
    category_data = df[df['Category'] == category]
    if category_data.empty:
        return 0.0
        
    category_data = category_data.sort_values(by='Date')
    min_date = df['Date'].min() # Align with the overall timeline bounds
    max_date = df['Date'].max()
    
    # Complete daily range
    full_range = pd.date_range(start=min_date, end=max_date, freq='D')
    
    grouped = category_data.groupby('Date')['Amount'].sum()
    aggregated = grouped.reindex(full_range, fill_value=0.0).reset_index()
    aggregated.columns = ['Date', 'Amount']
    
    aggregated['TimeIndex'] = np.arange(len(aggregated))
    aggregated['MonthOfYear'] = aggregated['Date'].dt.month
    aggregated['DayOfWeek'] = aggregated['Date'].dt.dayofweek
    
    features = ['TimeIndex', 'MonthOfYear', 'DayOfWeek']
    X = aggregated[features]
    y = aggregated['Amount']
    
    # Train Random Forest Regressor
    model = RandomForestRegressor(n_estimators=50, random_state=42) # Smaller tree count for speed
    model.fit(X, y)
    
    # Predict future 15 days
    future_dates = pd.date_range(start=aggregated['Date'].max(), periods=periods + 1, freq='D')[1:]
    future_df = pd.DataFrame({'Date': future_dates})
    future_df['TimeIndex'] = np.arange(len(aggregated), len(aggregated) + periods)
    future_df['MonthOfYear'] = future_df['Date'].dt.month
    future_df['DayOfWeek'] = future_df['Date'].dt.dayofweek
    
    X_future = future_df[features]
    predictions = model.predict(X_future)
    predictions = np.clip(predictions, a_min=0.0, a_max=None)
    
    return float(np.sum(predictions))
