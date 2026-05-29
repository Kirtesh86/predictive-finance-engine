import streamlit as st
import pandas as pd
import numpy as np
from streamlit_echarts import st_echarts

def calculate_boxplot_statistics(series: pd.Series):
    """
    Calculates ECharts-compliant boxplot statistics (Min, Q1, Median, Q3, Max).
    """
    if series.empty:
        return [0.0, 0.0, 0.0, 0.0, 0.0]
    vals = series.dropna().tolist()
    vals.sort()
    
    min_val = float(np.min(vals))
    max_val = float(np.max(vals))
    q1 = float(np.percentile(vals, 25))
    median = float(np.percentile(vals, 50))
    q3 = float(np.percentile(vals, 75))
    
    return [min_val, q1, median, q3, max_val]

def render_analytics(filtered_df: pd.DataFrame) -> None:
    """
    Renders the Analytics view, structured with tabbed navigation:
    1. [ Category Breakdown ] - Account spend bars and statistics tables.
    2. [ Outlier Detection ] - Statistical distribution and boxplots.
    3. [ Merchant Trends ] - Coffee run metrics and merchant slices.
    """
    st.markdown("Detailed diagnostic dashboards exploring transaction distributions, account classes, and granular merchant tracking.")
    
    if filtered_df.empty:
        st.warning("⚠️ No matching data available to display analytics. Adjust your sidebar filters.")
        return
        
    # Tabbed Navigation
    tab_categories, tab_outliers, tab_merchants = st.tabs([
        "📊 Category Breakdown", 
        "🔍 Outlier Detection", 
        "☕ Merchant Trends"
    ])
    
    # ---------------------------------------------------------
    # TAB 1: Category Breakdown & Statistics
    # ---------------------------------------------------------
    with tab_categories:
        col_cat1, col_cat2 = st.columns([1.2, 1])
        
        with col_cat1:
            with st.container(border=True):
                st.markdown("<h5 style='margin-top:0;'>💳 Total Spend by Account Type</h5>", unsafe_allow_html=True)
                account_spend = filtered_df.groupby('Account_Type')['Amount'].sum().reset_index()
                
                # ECharts Bar Config
                bar_x = account_spend['Account_Type'].tolist()
                bar_y = [float(round(v, 2)) for v in account_spend['Amount']]
                
                bar_options = {
                    "backgroundColor": "rgba(0,0,0,0)",
                    "tooltip": {
                        "trigger": "axis",
                        "formatter": "<b>{b}</b>: ${c}",
                        "backgroundColor": "rgba(13, 14, 28, 0.9)",
                        "borderColor": "rgba(255, 255, 255, 0.08)",
                        "borderWidth": 1,
                        "textStyle": {"color": "#f0f3f8", "fontFamily": "Plus Jakarta Sans"}
                    },
                    "grid": {"left": "3%", "right": "4%", "bottom": "3%", "containLabel": True},
                    "xAxis": {
                        "type": "category",
                        "data": bar_x,
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
                            "name": "Spending",
                            "type": "bar",
                            "barWidth": "45%",
                            "itemStyle": {
                                "color": {
                                    "type": "linear",
                                    "x": 0, "y": 0, "x2": 0, "y2": 1,
                                    "colorStops": [
                                        {"offset": 0, "color": "#4da3ff"},
                                        {"offset": 1, "color": "#a25eff"}
                                    ]
                                },
                                "borderRadius": [5, 5, 0, 0]
                            },
                            "data": bar_y
                        }
                    ]
                }
                
                st_echarts(bar_options, height="260px")
                
        with col_cat2:
            with st.container(border=True):
                st.markdown("<h5 style='margin-top:0;'>🏷️ Share by Spending Category</h5>", unsafe_allow_html=True)
                category_spending = filtered_df.groupby('Category')['Amount'].sum().reset_index()
                
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
                            "type": "pie",
                            "radius": "70%",
                            "data": pie_data,
                            "color": ["#4da3ff", "#a25eff", "#ff5e97", "#00f2fe"],
                            "label": {
                                "color": "#8b9bb4",
                                "fontFamily": "Plus Jakarta Sans",
                                "fontSize": 10
                            },
                            "itemStyle": {
                                "borderRadius": 5,
                                "borderColor": "#06060c",
                                "borderWidth": 1
                            }
                        }
                    ]
                }
                st_echarts(pie_options, height="260px")
                
        st.markdown("<br>", unsafe_allow_html=True)
        st.subheader("🏷️ Category Statistical Summary")
        
        # Aggregate stats
        category_stats = filtered_df.groupby('Category').agg(
            Total_Spent=('Amount', 'sum'),
            Transaction_Count=('Amount', 'count'),
            Average_Transaction=('Amount', 'mean'),
            Max_Transaction=('Amount', 'max')
        ).reset_index()
        
        # Formats
        category_stats['Percentage Share'] = (category_stats['Total_Spent'] / category_stats['Total_Spent'].sum() * 100).round(1).map('{:.1f}%'.format)
        category_stats['Total Spent'] = category_stats['Total_Spent'].map('${:,.2f}'.format)
        category_stats['Average Transaction'] = category_stats['Average_Transaction'].map('${:,.2f}'.format)
        category_stats['Max Transaction'] = category_stats['Max_Transaction'].map('${:,.2f}'.format)
        
        category_summary_table = category_stats[['Category', 'Total Spent', 'Transaction_Count', 'Average Transaction', 'Max Transaction', 'Percentage Share']]
        st.dataframe(category_summary_table, width="stretch", hide_index=True)

    # ---------------------------------------------------------
    # TAB 2: Outlier Detection
    # ---------------------------------------------------------
    with tab_outliers:
        col_out1, col_out2 = st.columns([1, 1])
        
        with col_out1:
            with st.container(border=True):
                st.markdown("<h5 style='margin-top:0;'>📦 Outflow Distribution Boxplot</h5>", unsafe_allow_html=True)
                
                # Precompute boxplot figures
                box_values = calculate_boxplot_statistics(filtered_df['Amount'])
                
                boxplot_options = {
                    "backgroundColor": "rgba(0,0,0,0)",
                    "tooltip": {
                        "trigger": "item",
                        "backgroundColor": "rgba(13, 14, 28, 0.9)",
                        "borderColor": "rgba(255, 255, 255, 0.08)",
                        "borderWidth": 1,
                        "textStyle": {"color": "#f0f3f8", "fontFamily": "Plus Jakarta Sans"},
                        "formatter": "Max: ${c4}<br>Q3 (75%): ${c3}<br>Median (50%): ${c2}<br>Q1 (25%): ${c1}<br>Min: ${c0}"
                    },
                    "grid": {"left": "10%", "right": "10%", "bottom": "15%"},
                    "xAxis": {
                        "type": "category",
                        "data": ["All Transactions"],
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
                            "name": "boxplot",
                            "type": "boxplot",
                            "data": [box_values],
                            "itemStyle": {
                                "color": "rgba(77, 163, 255, 0.15)",
                                "borderColor": "#4da3ff",
                                "borderWidth": 2
                            }
                        }
                    ]
                }
                
                st_echarts(boxplot_options, height="260px")
                
        with col_out2:
            with st.container(border=True):
                st.markdown("<h5 style='margin-top:0;'>⚠️ Potential Spending Outliers</h5>", unsafe_allow_html=True)
                st.markdown("Transactions exceeding 1.5x the Interquartile Range (IQR) threshold are cataloged below as potential spending anomalies.")
                
                amounts = filtered_df['Amount']
                q1 = float(np.percentile(amounts, 25)) if not amounts.empty else 0.0
                q3 = float(np.percentile(amounts, 75)) if not amounts.empty else 0.0
                iqr = q3 - q1
                threshold = q3 + 1.5 * iqr
                
                outliers = filtered_df[filtered_df['Amount'] > threshold].sort_values(by="Amount", ascending=False)
                
                if not outliers.empty:
                    st.dataframe(
                        outliers[['Date', 'Category', 'Amount', 'Description']], 
                        width="stretch", 
                        hide_index=True
                    )
                else:
                    st.info("No transaction anomalies detected above the standard statistical outlier threshold.")

    # ---------------------------------------------------------
    # TAB 3: Merchant Trends
    # ---------------------------------------------------------
    with tab_merchants:
        food_df = filtered_df[filtered_df['Category'] == 'Food']
        if not food_df.empty:
            col_food1, col_food2 = st.columns([1.2, 1])
            
            with col_food1:
                with st.container(border=True):
                    st.markdown("<h5 style='margin-top:0;'>🍩 Food Budget Share by Merchant</h5>", unsafe_allow_html=True)
                    food_merchants = food_df.groupby('Description')['Amount'].sum().reset_index()
                    
                    food_pie_data = []
                    for _, r in food_merchants.iterrows():
                        food_pie_data.append({"name": str(r['Description']), "value": float(round(r['Amount'], 2))})
                        
                    food_pie_options = {
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
                                "type": "pie",
                                "radius": ["40%", "65%"],
                                "data": food_pie_data,
                                "color": ["#4da3ff", "#a25eff", "#ff5e97", "#00f2fe", "#ffd166"],
                                "label": {"color": "#8b9bb4", "fontFamily": "Plus Jakarta Sans", "fontSize": 10},
                                "itemStyle": {
                                    "borderRadius": 5,
                                    "borderColor": "#06060c",
                                    "borderWidth": 2
                                }
                            }
                        ]
                    }
                    st_echarts(food_pie_options, height="280px")
                    
            with col_food2:
                with st.container(border=True):
                    st.markdown("<h5 style='margin-top:0;'>☕ Cafe & Coffee Runs Analysis</h5>", unsafe_allow_html=True)
                    st.markdown("Detailed monitoring of expenditures at coffee shops (Starbucks, Owl Night Cafe, and Local Cafe spots).")
                    
                    # Filter specifically for cafe/coffee key phrases
                    coffee_df = food_df[food_df['Description'].str.contains("coffee|starbucks|owl|cafe", case=False, na=False)]
                    
                    total_food_spent = food_df['Amount'].sum()
                    total_coffee_spent = coffee_df['Amount'].sum()
                    coffee_count = len(coffee_df)
                    coffee_percentage = (total_coffee_spent / total_food_spent * 100) if total_food_spent > 0 else 0.0
                    
                    # Render metrics
                    col_c1, col_c2 = st.columns(2)
                    with col_c1:
                        st.metric("Total Coffee Spend", f"${total_coffee_spent:,.2f}")
                        st.metric("Coffee Runs Count", f"{coffee_count} Visited")
                    with col_c2:
                        st.metric("Share of Food Budget", f"{coffee_percentage:.1f}%")
                        avg_ticket = (total_coffee_spent / coffee_count) if coffee_count > 0 else 0.0
                        st.metric("Average Cost per Run", f"${avg_ticket:,.2f}")
                        
                    st.markdown("---")
                    
                    # Render a mini list of coffee records
                    st.markdown("##### 🕒 Recent Coffee Run Logs")
                    mini_coffee_list = coffee_df.sort_values(by="Date", ascending=False).head(5)[['Date', 'Description', 'Amount']]
                    st.dataframe(mini_coffee_list, width="stretch", hide_index=True)
        else:
            st.info("No Food transactions found in the filtered records to perform merchant analyses.")
