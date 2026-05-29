import pandas as pd
import numpy as np
import re
from typing import Optional

def analyze_spending_query(df: pd.DataFrame, query: str, api_key: str = "") -> str:
    """
    Analyzes the user's transaction data to answer natural language queries.
    If a Gemini API key is provided, it uses the Gemini LLM for analysis.
    Otherwise, it falls back to a smart, mathematically precise local rules-based engine.

    Parameters:
        df (pd.DataFrame): The filtered transaction DataFrame.
        query (str): The user's query text.
        api_key (str): Optional Google Gemini API key.

    Returns:
        str: Analytical text answer to the query.
    """
    query_lower = query.lower().strip()
    
    # ---------------------------------------------------------
    # Case A: Live Gemini API Key Available
    # ---------------------------------------------------------
    if api_key.strip():
        try:
            import google.generativeai as genai
            genai.configure(api_key=api_key.strip())
            
            # Precompute high-impact stats to feed into context to avoid large payload sizes
            total_spend = df['Amount'].sum()
            category_totals = df.groupby('Category')['Amount'].sum().to_dict()
            merchant_totals = df.groupby('Description')['Amount'].sum().sort_values(ascending=False).head(8).to_dict()
            monthly_totals = df.groupby(df['Date'].dt.to_period('M'))['Amount'].sum().to_dict()
            monthly_totals_str = {str(k): v for k, v in monthly_totals.items()}
            
            # Format a compact sample table
            sample_tx = df.sort_values(by='Date', ascending=False).head(10)[['Date', 'Category', 'Amount', 'Description']].to_string(index=False)
            
            prompt = f"""You are a professional, highly insightful AI Financial Agent for the "Predictive Finance Engine" dashboard.
Analyze the user's spending data and answer the query: "{query}"

Here is the analytical summary of their transaction dataset:
- Total Outflow: ${total_spend:,.2f} across {len(df)} transactions.
- Spending by Category: {category_totals}
- Top Merchants/Descriptions: {merchant_totals}
- Outflow by Months: {monthly_totals_str}

Recent transaction samples:
{sample_tx}

Provide a conversational, direct, and numerically accurate response. Keep it concise, highlighting actionable insights or trends (e.g. coffee runs, rent ratios). Format your response in clean markdown.
"""
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"⚠️ **AI Agent Error**: Failed to execute LLM API request. Falling back to local rules-based engine.\n\n*Error details: {e}*\n\n---\n" + _local_nlp_engine(df, query_lower)
            
    # ---------------------------------------------------------
    # Case B: Local Rule-Based NLP Fallback
    # ---------------------------------------------------------
    return _local_nlp_engine(df, query_lower)


def _local_nlp_engine(df: pd.DataFrame, query: str) -> str:
    """
    Local analytical parsing engine that processes user questions using
    pandas aggregations and regular expressions, ensuring zero-dependency accuracy.
    """
    total_spend = df['Amount'].sum()
    
    # 1. Total Spending Queries
    if any(k in query for k in ["total", "how much did i spend", "sum", "expenditure"]):
        # Check if they are asking about a specific category
        for cat in df['Category'].unique():
            if cat.lower() in query:
                cat_spend = df[df['Category'] == cat]['Amount'].sum()
                pct = (cat_spend / total_spend * 100) if total_spend > 0 else 0
                return f"💰 **Total Spend on {cat}**: You spent a total of **${cat_spend:,.2f}** on **{cat}** (representing **{pct:.1f}%** of your total spending)."
        
        # Check if they are asking about coffee
        if "coffee" in query or "owl" in query or "starbucks" in query:
            coffee_df = df[df['Description'].str.contains("coffee|starbucks|owl|cafe", case=False, na=False)]
            coffee_spend = coffee_df['Amount'].sum()
            return f"☕ **Coffee Spending**: You spent a total of **${coffee_spend:,.2f}** on coffee runs across **{len(coffee_df)}** visits (including Starbucks and Owl Night Cafe)."

        return f"📊 **Total Outflow**: Your total spending is **${total_spend:,.2f}** across **{len(df)}** transactions in the selected filter range."

    # 2. Maximum / Highest Outflow Queries
    if any(k in query for k in ["highest", "largest", "maximum", "most expensive", "big ticket", "biggest"]):
        # Check for category
        if "category" in query or "categories" in query:
            cat_totals = df.groupby('Category')['Amount'].sum()
            if not cat_totals.empty:
                max_cat = cat_totals.idxmax()
                max_cat_val = cat_totals.max()
                pct = (max_cat_val / total_spend * 100) if total_spend > 0 else 0
                return f"📈 **Highest Spending Category**: Your top expenditure category is **{max_cat}** with a total of **${max_cat_val:,.2f}** (**{pct:.1f}%** of total outflow)."
        
        # Max individual transaction
        idx_max = df['Amount'].idxmax()
        row = df.loc[idx_max]
        return f"🛍️ **Largest Individual Outflow**: Your highest single transaction was **${row['Amount']:,.2f}** on **{row['Date'].strftime('%b %d, %Y')}** for *\"{row['Description']}\"* ({row['Category']})."

    # 3. Minimum / Cheapest Queries
    if any(k in query for k in ["lowest", "cheapest", "smallest", "minimum"]):
        idx_min = df['Amount'].idxmin()
        row = df.loc[idx_min]
        return f"🏷️ **Smallest Outflow**: Your lowest transaction recorded was **${row['Amount']:,.2f}** on **{row['Date'].strftime('%b %d, %Y')}** for *\"{row['Description']}\"* ({row['Category']})."

    # 4. Coffee / Late-Night Habits Specific Query (Granular Merchant Analytics)
    if any(k in query for k in ["coffee", "owl", "starbucks", "nandanvan", "cafe"]):
        coffee_df = df[df['Description'].str.contains("coffee|starbucks|owl|cafe", case=False, na=False)]
        if not coffee_df.empty:
            coffee_spend = coffee_df['Amount'].sum()
            counts = coffee_df['Description'].value_counts()
            
            # Break down spots
            spots_str = ""
            for spot, count in counts.items():
                spot_spend = coffee_df[coffee_df['Description'] == spot]['Amount'].sum()
                spots_str += f"\n- **{spot}**: {count} visit(s) totaling **${spot_spend:,.2f}**"
                
            return f"☕ **Coffee & Cafe Tracker**: You spent a total of **${coffee_spend:,.2f}** on coffee runs. Here is the merchant breakdown:{spots_str}"
        return "☕ **Coffee Tracker**: No coffee or cafe transaction entries found in the selected date range."

    # 5. Average Outflow Queries
    if any(k in query for k in ["average", "mean"]):
        avg_spend = df['Amount'].mean()
        # Monthly average
        monthly_data = df.groupby(df['Date'].dt.to_period('M'))['Amount'].sum()
        avg_monthly = monthly_data.mean() if not monthly_data.empty else 0.0
        return f"📐 **Average Expenditures**:\n- **Per Transaction**: **${avg_spend:,.2f}**\n- **Per Calendar Month**: **${avg_monthly:,.2f}** (based on {len(monthly_data)} month(s))"

    # 6. Categories Breakdown
    if any(k in query for k in ["category", "categories", "breakdown"]):
        cat_totals = df.groupby('Category')['Amount'].sum().sort_values(ascending=False)
        cat_str = ""
        for cat, val in cat_totals.items():
            pct = (val / total_spend * 100) if total_spend > 0 else 0
            cat_str += f"\n- **{cat}**: **${val:,.2f}** ({pct:.1f}%)"
        return f"🍩 **Outflow Category Breakdown**:{cat_str}"

    # Default fallback response
    return f"""🤖 **AI Assistant**: I analyzed your dataset of **{len(df)} transactions** totaling **${total_spend:,.2f}**. 
To get a precise analysis, try asking specific questions like:
- *What is my highest spend category?*
- *How much did I spend on rent?*
- *How much do I spend on coffee at Starbucks and Owl Night Cafe?*
- *Show me my category breakdown.*
- *What is my average transaction size?*

*(Tip: To get open-ended cognitive answers, paste your Gemini API Key in the **Settings** page!)*"""
