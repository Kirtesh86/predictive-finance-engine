import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Set random seed for reproducibility
np.random.seed(42)

data = []

# Generate data for the last 180 days (6 months)
end_date = datetime.now()
start_date = end_date - timedelta(days=180)

current_date = start_date
while current_date <= end_date:
    # 1. Rent - Paid on the 1st of every month
    # Budget Limit: $1200.00 -> Rent spend: $1000.00
    if current_date.day == 1:
        data.append({
            'Date': current_date.strftime('%Y-%m-%d'),
            'Category': 'Rent',
            'Amount': 1000.00,
            'Account_Type': 'Checking Account',
            'Description': 'Nandanvan Heights Apartments (Rent)'
        })
        
    # 2. Utilities - Paid on the 10th and 20th of every month
    # Budget Limit: $200.00 -> Power: ~$75.00, Internet: $49.99 (Total: ~$125.00)
    if current_date.day == 10:
        data.append({
            'Date': current_date.strftime('%Y-%m-%d'),
            'Category': 'Utilities',
            'Amount': round(75.00 + np.random.uniform(-5, 5), 2),
            'Account_Type': 'Checking Account',
            'Description': 'State Electricity Board (Power/Water)'
        })
    if current_date.day == 20:
        data.append({
            'Date': current_date.strftime('%Y-%m-%d'),
            'Category': 'Utilities',
            'Amount': 49.99,
            'Account_Type': 'Credit Card',
            'Description': 'Comcast Broadband (Internet)'
        })
        
    # 3. Food - Groceries once a week (Thursday), small coffee runs (Tuesday/Friday)
    # Budget Limit: $300.00 -> Groceries: ~$30.00, Coffees: ~$4.00
    # Monthly Total: 4 * $30 + 8 * $4 = ~$152.00
    if current_date.weekday() == 3:  # Thursday
        data.append({
            'Date': current_date.strftime('%Y-%m-%d'),
            'Category': 'Food',
            'Amount': round(30.00 + np.random.uniform(-3, 3), 2),
            'Account_Type': 'Checking Account',
            'Description': 'Whole Foods Market (Nandanvan)'
        })
    if current_date.weekday() in [1, 4]:  # Tuesday, Friday
        data.append({
            'Date': current_date.strftime('%Y-%m-%d'),
            'Category': 'Food',
            'Amount': round(4.00 + np.random.uniform(-0.5, 0.5), 2),
            'Account_Type': 'Credit Card',
            'Description': 'Starbucks (Nandanvan)'
        })
        
    # 4. Entertainment - Weekend fun on Saturdays
    # Budget Limit: $150.00 -> Movies/Gaming: ~$15.00 (Total monthly: ~$60.00)
    if current_date.weekday() == 5:  # Saturday
        data.append({
            'Date': current_date.strftime('%Y-%m-%d'),
            'Category': 'Entertainment',
            'Amount': round(15.00 + np.random.uniform(-3, 3), 2),
            'Account_Type': 'Credit Card',
            'Description': 'PVR Cinemas (Nandanvan)'
        })

    current_date += timedelta(days=1)

# Compile into DataFrame
df = pd.DataFrame(data)
df.to_csv('expenses.csv', index=False)
print(f"Clean expenses dataset created successfully at expenses.csv with {len(df)} records.")
