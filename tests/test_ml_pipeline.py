import pytest
import pandas as pd
import numpy as np
from datetime import datetime
from ml_pipeline import aggregate_and_forecast, forecast_category_spending

def test_aggregate_and_forecast_basic():
    """
    Tests that aggregate_and_forecast runs successfully on basic dataframe input,
    returning structured historical and forecast dataframes along with an R2 score.
    """
    # Create standard mock dataset
    dates = pd.date_range(start="2026-01-01", periods=10, freq="D")
    df = pd.DataFrame({
        'Date': dates,
        'Amount': [10.0, 15.0, 20.0, 10.0, 5.0, 30.0, 25.0, 15.0, 10.0, 20.0],
        'Category': ['Food'] * 10
    })
    
    # Disable Streamlit caching for tests to avoid session state errors
    # (By calling it directly)
    hist, forecast, r2 = aggregate_and_forecast.__wrapped__(
        df,
        interval="Daily",
        model_type="Linear Regression",
        periods=5
    )
    
    # Assertions
    assert isinstance(hist, pd.DataFrame)
    assert isinstance(forecast, pd.DataFrame)
    assert isinstance(r2, float)
    
    assert not hist.empty
    assert len(forecast) == 5
    assert 'Date' in hist.columns and 'Amount' in hist.columns
    assert 'Date' in forecast.columns and 'Amount' in forecast.columns
    assert all(forecast['Amount'] >= 0) # Ensure values are clipped

def test_aggregate_and_forecast_empty():
    """
    Tests that aggregate_and_forecast handles empty inputs gracefully without raising errors.
    """
    df = pd.DataFrame(columns=['Date', 'Amount', 'Category'])
    hist, forecast, r2 = aggregate_and_forecast.__wrapped__(df)
    
    assert hist.empty
    assert forecast.empty
    assert r2 == 0.0

def test_aggregate_and_forecast_leap_year():
    """
    Tests that dates near leap years (e.g. Feb 2024) are handled cleanly.
    """
    dates = pd.to_datetime(["2024-02-27", "2024-02-28", "2024-02-29", "2024-03-01"])
    df = pd.DataFrame({
        'Date': dates,
        'Amount': [100.0, 150.0, 120.0, 200.0],
        'Category': ['Rent'] * 4
    })
    
    hist, forecast, r2 = aggregate_and_forecast.__wrapped__(
        df,
        interval="Daily",
        model_type="Linear Regression",
        periods=3
    )
    
    assert not hist.empty
    # The aggregated dates should match start to end including leap day
    assert "2024-02-29" in hist['Date'].dt.strftime('%Y-%m-%d').values
    assert len(forecast) == 3

def test_forecast_category_spending_empty():
    """
    Tests forecast_category_spending returns 0.0 if the category is missing.
    """
    df = pd.DataFrame({
        'Date': pd.date_range("2026-01-01", periods=5),
        'Amount': [10, 20, 30, 40, 50],
        'Category': ['Rent'] * 5
    })
    
    # Forecast category "Food" which does not exist in df
    val = forecast_category_spending.__wrapped__(df, "Food", periods=10)
    assert val == 0.0
