import streamlit as st
import pandas as pd
import numpy as np
import requests
from streamlit_echarts import st_echarts
from streamlit_lottie import st_lottie
from ml_pipeline import aggregate_and_forecast, forecast_category_spending

def load_lottie_url(url: str):
    """
    Downloads Lottie JSON from URL with error handling for offline environments.
    """
    try:
        r = requests.get(url, timeout=3)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return None

def render_dashboard(
    filtered_df: pd.DataFrame,
    monthly_data: pd.Series,
    monthly_average: float,
    predicted_outflow: float,
    forecast_horizon: int,
    ml_model_type: str,
    rf_estimators: int
) -> None:
    """
    Renders the main dashboard page, including ML-driven budget alerts, KPI metric cards,
    the interactive ECharts trend area charts + ML forecasts, the category donut chart,
    and the recent transactions list.
    """
    col_head1, col_head2 = st.columns([3, 1])
    with col_head1:
        st.markdown("An intelligent financial analytics and predictive forecasting platform.")
    with col_head2:
        # Mini Lottie visual finance animation
        lottie_json = load_lottie_url("https://lottie.host/f8b9ec78-c0b7-4bde-8f81-f2f275990264/3sS7LqG9Xk.json")
        if lottie_json:
            st_lottie(lottie_json, height=60, key="dashboard_lottie")
            
    # ---------------------------------------------------------
    # Budget Limits Breach Checking (15-Day Predictive Alerts)
    # ---------------------------------------------------------
    budgets = st.session_state.get('budgets', {})
    alerts = []
    
    if budgets and not filtered_df.empty:
        # Determine the latest month in the dataset to calculate current month spend
        latest_date = filtered_df['Date'].max()
        current_month = latest_date.month
        current_year = latest_date.year
        
        for category, limit in budgets.items():
            if limit > 0:
                # 1. Calculate actual current month spend for this category
                cat_current_df = filtered_df[
                    (filtered_df['Category'] == category) & 
                    (filtered_df['Date'].dt.month == current_month) & 
                    (filtered_df['Date'].dt.year == current_year)
                ]
                current_month_spend = float(cat_current_df['Amount'].sum())
                
                # 2. Forecast next 15 days spend using category-specific RF model
                projected_15d_spend = forecast_category_spending(filtered_df, category, periods=15)
                
                total_projected_spend = current_month_spend + projected_15d_spend
                
                # 3. Check for budget limit breach
                if total_projected_spend > limit:
                    excess = total_projected_spend - limit
                    alerts.append({
                        "category": category,
                        "current_spend": current_month_spend,
                        "projected_15d": projected_15d_spend,
                        "projected": total_projected_spend,
                        "limit": limit,
                        "excess": excess
                    })
                    
    # Render warnings at the very top of the dashboard main page
    if alerts:
        for alert in alerts:
            alert_html = f"""
            <div class="budget-alert">
                ⚠️ <b>Projected Budget Breach ({alert['category']})</b>: 
                Your projected spend is <b>${alert['projected']:,.2f}</b> 
                (actual spend so far of <b>${alert['current_spend']:,.2f}</b> plus 15-day forecast of <b>${alert['projected_15d']:,.2f}</b>). 
                This exceeds your set budget limit of <b>${alert['limit']:,.2f}</b> by <b>${alert['excess']:,.2f}</b>!
            </div>
            """
            st.markdown(alert_html, unsafe_allow_html=True)
            
    total_spending = filtered_df['Amount'].sum()
    
    # ---------------------------------------------------------
    # HTML Branded Metric Cards Row with Glowing Deltas
    # ---------------------------------------------------------
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class="custom-card card-blue">
            <div class="card-label">Total Spending</div>
            <div class="card-value">${total_spending:,.2f}</div>
            <div class="badge-neutral">{len(filtered_df)} Transactions</div>
        </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown(f"""
        <div class="custom-card card-purple">
            <div class="card-label">Monthly Average Outflow</div>
            <div class="card-value">${monthly_average:,.2f}</div>
            <div class="badge-neutral">Based on {len(monthly_data)} Month(s)</div>
        </div>
        """, unsafe_allow_html=True)
        
    with col3:
        # Calculate comparison delta vs last month's actual value
        if len(monthly_data) >= 1:
            last_month_val = float(monthly_data.iloc[-1])
            pct = ((predicted_outflow - last_month_val) / last_month_val * 100) if last_month_val > 0 else 0.0
            
            # Setup glowing green or red pills
            if pct < 0:
                delta_pill = f"""
                <span class="badge-glow-green">
                    <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" style="vertical-align: middle;"><line x1="12" y1="5" x2="12" y2="19"></line><polyline points="19 12 12 19 5 12"></polyline></svg>
                    {abs(pct):.1f}% Down vs Last Month
                </span>
                """
            else:
                delta_pill = f"""
                <span class="badge-glow-red">
                    <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" style="vertical-align: middle;"><line x1="12" y1="19" x2="12" y2="5"></line><polyline points="5 12 12 5 19 12"></polyline></svg>
                    {abs(pct):.1f}% Up vs Last Month
                </span>
                """
        else:
            delta_pill = '<span class="badge-neutral">Insufficient history</span>'
            
        st.markdown(f"""
        <div class="custom-card card-pink">
            <div class="card-label">Predicted Outflow ({forecast_horizon}d)</div>
            <div class="card-value">${predicted_outflow:,.2f}</div>
            <div>{delta_pill}</div>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    # ---------------------------------------------------------
    # Visualizations Columns (Apache ECharts Area Spline & Donut)
    # ---------------------------------------------------------
    col_chart1, col_chart2 = st.columns([2, 1])
    
    with col_chart1:
        with st.container(border=True):
            st.markdown("<h4 style='margin-top:0; margin-bottom:1rem;'>📈 Spending Trajectory & ML Forecast</h4>", unsafe_allow_html=True)
            interval_select = st.selectbox(
                "Aggregation Interval",
                options=["Daily", "Weekly", "Monthly"],
                index=0,
                help="Choose whether to view and model spending trends on a daily, weekly, or monthly scale."
            )
            
            # Generate ML Forecast on selected interval
            hist_series, forecast_series, _ = aggregate_and_forecast(
                filtered_df, 
                interval=interval_select,
                model_type=ml_model_type,
                estimators=rf_estimators,
                periods=forecast_horizon
            )
            
            # Formulate coordinates
            hist_dates = [d.strftime('%Y-%m-%d') for d in hist_series['Date']]
            hist_vals = [float(v) for v in hist_series['Amount']]
            
            last_hist_row = hist_series.iloc[-1]
            connected_forecast = pd.concat([pd.DataFrame([last_hist_row]), forecast_series], ignore_index=True)
            connected_dates = [d.strftime('%Y-%m-%d') for d in connected_forecast['Date']]
            connected_vals = [float(v) for v in connected_forecast['Amount']]
            
            # Map full date range
            all_dates = sorted(list(set(hist_dates + connected_dates)))
            
            # Pad series matching timeline indexes
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
            
            # ECharts Options for Area Spline Chart
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
                "grid": {
                    "left": "3%",
                    "right": "4%",
                    "bottom": "3%",
                    "containLabel": True
                },
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
                        "symbolSize": 4,
                        "showSymbol": False,
                        "lineStyle": {
                            "color": "#4da3ff",
                            "width": 3,
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
                        "symbolSize": 4,
                        "showSymbol": False,
                        "lineStyle": {
                            "color": "#a25eff",
                            "width": 3,
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
            
            st_echarts(echarts_options, height="320px")
        
    with col_chart2:
        with st.container(border=True):
            st.markdown("<h4 style='margin-top:0; margin-bottom:1rem;'>🍩 Category Share</h4>", unsafe_allow_html=True)
            category_spending = filtered_df.groupby('Category')['Amount'].sum().reset_index()
            
            # ECharts Donut data construction
            pie_data = []
            for _, r in category_spending.iterrows():
                pie_data.append({"name": str(r['Category']), "value": float(round(r['Amount'], 2))})
                
            pie_options = {
                "backgroundColor": "rgba(0,0,0,0)",
                "tooltip": {
                    "trigger": "item",
                    "formatter": "<b>{b}</b>: ${c} ({d}%)",
                    "backgroundColor": "rgba(13, 14, 28, 0.9)",
                    "borderColor": "rgba(255, 255, 255, 0.08)",
                    "borderWidth": 1,
                    "textStyle": {"color": "#f0f3f8", "fontFamily": "Plus Jakarta Sans"}
                },
                "series": [
                    {
                        "name": "Categories",
                        "type": "pie",
                        "radius": ["45%", "65%"],
                        "avoidLabelOverlap": False,
                        "itemStyle": {
                            "borderRadius": 6,
                            "borderColor": "#06060c",
                            "borderWidth": 2
                        },
                        "label": {
                            "show": False,
                            "position": "center"
                        },
                        "emphasis": {
                            "label": {
                                "show": True,
                                "fontSize": "14",
                                "fontWeight": "bold",
                                "color": "#ffffff",
                                "formatter": "{b}\n${c}"
                            }
                        },
                        "labelLine": {
                            "show": False
                        },
                        "data": pie_data,
                        "color": ["#4da3ff", "#a25eff", "#ff5e97", "#00f2fe"]
                    }
                ]
            }
            
            st_echarts(pie_options, height="275px")
        
    st.markdown("---")
    
    # Recent Transactions List
    st.subheader("📊 Recent Transactions")
    st.dataframe(
        filtered_df.sort_values(by="Date", ascending=False),
        width="stretch",
        hide_index=True
    )
