import streamlit as st
import pandas as pd
import numpy as np
import os
from styles import get_custom_css
from database import init_db, SessionLocal, get_transactions_df
from ml_pipeline import aggregate_and_forecast
from components.dashboard import render_dashboard
from components.analytics import render_analytics
from components.forecasting import render_forecasting
from components.ai_agent import render_ai_agent
from components.settings import render_settings

# ---------------------------------------------------------
# Page Configuration
# ---------------------------------------------------------
st.set_page_config(
    page_title="Predictive Finance Engine",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Inject custom design stylesheet rules
st.markdown(get_custom_css(), unsafe_allow_html=True)

# ---------------------------------------------------------
# Database Initialization & Session Binding
# ---------------------------------------------------------
# Run schema creations and seeding on startup
init_db()
db_session = SessionLocal()

# ---------------------------------------------------------
# Initialize persistent Session State variables
# ---------------------------------------------------------
if "forecast_horizon" not in st.session_state:
    st.session_state.forecast_horizon = 30
if "ml_model_type" not in st.session_state:
    st.session_state.ml_model_type = "Random Forest Regressor"
if "rf_estimators" not in st.session_state:
    st.session_state.rf_estimators = 100
if "gemini_api_key" not in st.session_state:
    st.session_state.gemini_api_key = ""
if "budgets" not in st.session_state:
    st.session_state.budgets = {
        "Food": 300.0,
        "Rent": 1200.0,
        "Utilities": 200.0,
        "Entertainment": 150.0
    }

# ---------------------------------------------------------
# Sidebar Controls & File Upload
# ---------------------------------------------------------
with st.sidebar:
    st.markdown("### 🔮 Navigation")
    menu = st.radio(
        "Go to",
        ["Dashboard", "Analytics", "Predictive Forecasting", "AI Financial Agent", "Settings"],
        index=0,
        help="Switch between views to manage data, chat with AI, view charts, or configure parameters."
    )
    
    st.markdown("---")
    st.markdown("### 📂 Data Import")
    
    uploaded_file = st.sidebar.file_uploader(
        "Upload Transaction CSV", 
        type=["csv"],
        help="Upload a CSV with 'Date', 'Category', 'Amount', and 'Account_Type' columns."
    )
    
    # Load raw dataframe based on availability (Uploader overrides Database)
    raw_df = None
    if uploaded_file is not None:
        try:
            # File Uploader parsing helper
            raw_df = pd.read_csv(uploaded_file)
            raw_df['Date'] = pd.to_datetime(raw_df['Date'])
            raw_df['Amount'] = pd.to_numeric(raw_df['Amount'], errors='coerce')
            raw_df = raw_df.dropna(subset=['Date', 'Amount'])
            st.sidebar.success("Uploaded CSV loaded!")
        except Exception as e:
            st.sidebar.error(f"Error parsing CSV file: {e}")
    else:
        # Load directly from SQLite database
        try:
            raw_df = get_transactions_df(db_session)
            st.sidebar.info("Connected to SQLite backend.")
        except Exception as e:
            st.sidebar.error(f"Database read failed: {e}")
            
    # Set up filters if data is successfully loaded
    filtered_df = None
    if raw_df is not None:
        st.markdown("### 📅 Filters")
        
        # Date range filter setup
        min_date = raw_df['Date'].min().date() if not raw_df.empty else datetime.today().date()
        max_date = raw_df['Date'].max().date() if not raw_df.empty else datetime.today().date()
        
        # Date range input selection
        if not raw_df.empty:
            date_range = st.date_input(
                "Select Date Range",
                value=(min_date, max_date),
                min_value=min_date,
                max_value=max_date,
                help="Filter the analysis dashboard across specific transaction dates."
            )
        else:
            date_range = None
            
        # Category multiselect filter setup
        st.markdown("### 🏷️ Categories")
        available_categories = sorted(list(raw_df['Category'].unique())) if not raw_df.empty else []
        selected_categories = st.multiselect(
            "Filter Categories",
            options=available_categories,
            default=available_categories,
            help="Choose which spending categories to display on charts and cards."
        )
        
        # Apply Date Range filter first
        if date_range is not None:
            if isinstance(date_range, tuple) and len(date_range) == 2:
                start_date, end_date = date_range
                filtered_df = raw_df[(raw_df['Date'].dt.date >= start_date) & (raw_df['Date'].dt.date <= end_date)]
            elif isinstance(date_range, tuple) and len(date_range) == 1:
                start_date = date_range[0]
                filtered_df = raw_df[raw_df['Date'].dt.date >= start_date]
            else:
                filtered_df = raw_df
        else:
            filtered_df = raw_df
            
        # Apply Category filter
        if filtered_df is not None and not filtered_df.empty:
            filtered_df = filtered_df[filtered_df['Category'].isin(selected_categories)]
            
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.caption("Predictive Finance Engine v1.0.0")

# ---------------------------------------------------------
# Main Page View Router
# ---------------------------------------------------------
st.title("🔮 Predictive Finance Engine")

# Handle data rendering
if filtered_df is not None and not filtered_df.empty:
    
    # Check if there are enough data points for ML modeling
    if len(filtered_df) < 5:
        st.warning("⚠️ Insufficient data points selected. Please choose a broader date range or select more categories to run ML predictions.")
    else:
        # Precompute metrics used across views
        # Run default daily forecast for the Metric KPI card projection
        _, daily_forecast, _ = aggregate_and_forecast(
            filtered_df, 
            interval="Daily",
            model_type=st.session_state.ml_model_type,
            estimators=st.session_state.rf_estimators,
            periods=st.session_state.forecast_horizon
        )
        predicted_outflow = daily_forecast['Amount'].sum() # Forecasted horizon projection
        
        # Calculate monthly groups
        monthly_data = filtered_df.groupby(filtered_df['Date'].dt.to_period('M'))['Amount'].sum()
        monthly_average = monthly_data.mean() if not monthly_data.empty else 0.0

        # Dispatch navigation to specific rendering components
        if menu == "Dashboard":
            render_dashboard(
                filtered_df=filtered_df,
                monthly_data=monthly_data,
                monthly_average=monthly_average,
                predicted_outflow=predicted_outflow,
                forecast_horizon=st.session_state.forecast_horizon,
                ml_model_type=st.session_state.ml_model_type,
                rf_estimators=st.session_state.rf_estimators
            )
        elif menu == "Analytics":
            render_analytics(filtered_df=filtered_df)
        elif menu == "Predictive Forecasting":
            render_forecasting(
                filtered_df=filtered_df,
                ml_model_type=st.session_state.ml_model_type,
                rf_estimators=st.session_state.rf_estimators,
                forecast_horizon=st.session_state.forecast_horizon
            )
        elif menu == "AI Financial Agent":
            render_ai_agent(filtered_df=filtered_df)
        elif menu == "Settings":
            render_settings(
                filtered_df=filtered_df,
                db_session=db_session
            )

else:
    st.warning("⚠️ No matching transaction data found. Please adjust your sidebar filters or verify your CSV content.")

# ---------------------------------------------------------
# Clean Up Resource Sessions
# ---------------------------------------------------------
db_session.close()
