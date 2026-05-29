import streamlit as st
import pandas as pd
import numpy as np
from streamlit_echarts import st_echarts
from ml_pipeline import aggregate_and_forecast

def render_forecasting(
    filtered_df: pd.DataFrame, 
    ml_model_type: str, 
    rf_estimators: int, 
    forecast_horizon: int
) -> None:
    """
    Renders the Predictive Forecasting view, detailing the active algorithm setup,
    R2 fit statistics, a large ECharts forecasting area chart, and a table of raw predictions.
    """
    st.markdown("Examine the details of the machine learning model, training fit quality, and raw future predictions.")
    
    # ---------------------------------------------------------
    # Interval and Scale Configuration
    # ---------------------------------------------------------
    st.markdown("<br>", unsafe_allow_html=True)
    col_sel1, _ = st.columns([1, 2])
    with col_sel1:
        interval_select = st.selectbox(
            "Forecasting Model Scale",
            options=["Daily", "Weekly", "Monthly"],
            index=0,
            help="Choose whether to view and model predictions on a daily, weekly, or monthly scale."
        )
    
    # Execute Model Training & Predictions
    hist_series, forecast_series, r2_score_val = aggregate_and_forecast(
        filtered_df, 
        interval=interval_select,
        model_type=ml_model_type,
        estimators=rf_estimators,
        periods=forecast_horizon
    )
    
    # ---------------------------------------------------------
    # Model Specification Metrics Display
    # ---------------------------------------------------------
    col_spec1, col_spec2, col_spec3 = st.columns(3)
    with col_spec1:
        st.metric("Active ML Algorithm", ml_model_type)
    with col_spec2:
        st.metric("Aggregated Data Samples", f"{len(hist_series)} periods")
    with col_spec3:
        st.metric("Model Quality (R² Fit)", f"{r2_score_val:.2%}" if r2_score_val >= 0 else "0.00% (Weak baseline)")
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    # ---------------------------------------------------------
    # Large Forecast Visual Chart Area (Apache ECharts Glow Line)
    # ---------------------------------------------------------
    with st.container(border=True):
        st.markdown(f"<h4>🔮 Outflow Projections ({forecast_horizon} Days Horizon)</h4>", unsafe_allow_html=True)
        
        hist_dates = [d.strftime('%Y-%m-%d') for d in hist_series['Date']]
        hist_vals = [float(v) for v in hist_series['Amount']]
        
        last_hist_row = hist_series.iloc[-1]
        connected_forecast = pd.concat([pd.DataFrame([last_hist_row]), forecast_series], ignore_index=True)
        connected_dates = [d.strftime('%Y-%m-%d') for d in connected_forecast['Date']]
        connected_vals = [float(v) for v in connected_forecast['Amount']]
        
        # Merge dates chronologically
        all_dates = sorted(list(set(hist_dates + connected_dates)))
        
        # Align timelines
        padded_hist = []
        padded_forecast = []
        for dt in all_dates:
            if dt in hist_dates:
                padded_hist.append(hist_vals[hist_dates.index(dt)])
            else:
                padded_hist.append(None)
                
            if dt in connected_dates:
                padded_forecast.append(connected_vals[connected_dates.index(dt)])
            else:
                padded_forecast.append(None)
                
        # ECharts large options configuration
        echarts_options = {
            "backgroundColor": "rgba(0,0,0,0)",
            "tooltip": {
                "trigger": "axis",
                "backgroundColor": "rgba(13, 14, 28, 0.9)",
                "borderColor": "rgba(255, 255, 255, 0.08)",
                "borderWidth": 1,
                "textStyle": {"color": "#f0f3f8", "fontFamily": "Plus Jakarta Sans"},
                "axisPointer": {"type": "line", "lineStyle": {"color": "rgba(255, 255, 255, 0.1)", "width": 1}}
            },
            "legend": {
                "data": ["Actual Spend", "ML Predictive Forecast"],
                "textStyle": {"color": "#8b9bb4", "fontFamily": "Plus Jakarta Sans", "fontWeight": 600},
                "right": "0%"
            },
            "grid": {"left": "3%", "right": "4%", "bottom": "3%", "containLabel": True},
            "xAxis": {
                "type": "category",
                "boundaryGap": False,
                "data": all_dates,
                "axisLine": {"lineStyle": {"color": "rgba(255, 255, 255, 0.08)"}},
                "axisLabel": {"color": "#8b9bb4", "fontFamily": "Plus Jakarta Sans"}
            },
            "yAxis": {
                "type": "value",
                "axisLine": {"lineStyle": {"color": "rgba(255, 255, 255, 0.08)"}},
                "axisLabel": {"color": "#8b9bb4", "fontFamily": "Plus Jakarta Sans", "formatter": "${value}"},
                "splitLine": {"lineStyle": {"color": "rgba(255, 255, 255, 0.04)"}}
            },
            "series": [
                {
                    "name": "Actual Spend",
                    "type": "line",
                    "smooth": True,
                    "symbol": "circle",
                    "symbolSize": 5,
                    "lineStyle": {
                        "color": "#4da3ff",
                        "width": 3.5,
                        "shadowColor": "rgba(77, 163, 255, 0.5)",
                        "shadowBlur": 10
                    },
                    "itemStyle": {"color": "#4da3ff"},
                    "areaStyle": {
                        "color": {
                            "type": "linear",
                            "x": 0, "y": 0, "x2": 0, "y2": 1,
                            "colorStops": [
                                {"offset": 0, "color": "rgba(77, 163, 255, 0.15)"},
                                {"offset": 1, "color": "rgba(77, 163, 255, 0.01)"}
                            ]
                        }
                    },
                    "data": padded_hist
                },
                {
                    "name": "ML Predictive Forecast",
                    "type": "line",
                    "smooth": True,
                    "symbol": "circle",
                    "symbolSize": 5,
                    "lineStyle": {
                        "color": "#a25eff",
                        "width": 3.5,
                        "type": "dashed",
                        "shadowColor": "rgba(162, 94, 255, 0.5)",
                        "shadowBlur": 10
                    },
                    "itemStyle": {"color": "#a25eff"},
                    "areaStyle": {
                        "color": {
                            "type": "linear",
                            "x": 0, "y": 0, "x2": 0, "y2": 1,
                            "colorStops": [
                                {"offset": 0, "color": "rgba(162, 94, 255, 0.1)"},
                                {"offset": 1, "color": "rgba(162, 94, 255, 0.01)"}
                            ]
                        }
                    },
                    "data": padded_forecast
                }
            ]
        }
        
        st_echarts(echarts_options, height="380px")
        
    st.markdown("---")
    
    # ---------------------------------------------------------
    # Predictions Table Outflow
    # ---------------------------------------------------------
    st.subheader("📋 Forecast Output Values")
    
    # Format predictions table for reporting
    forecast_table = forecast_series.copy()
    forecast_table['Date'] = forecast_table['Date'].dt.strftime('%b %d, %Y')
    forecast_table['Predicted Outflow'] = forecast_table['Amount'].map('${:,.2f}'.format)
    
    st.dataframe(
        forecast_table[['Date', 'Predicted Outflow']], 
        width="stretch", 
        hide_index=True
    )
