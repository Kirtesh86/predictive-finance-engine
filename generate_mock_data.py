import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Set random seed for reproducibility
np.random.seed(42)

# Number of mock expense records to generate
num_records = 200

# Generate random dates over the past 6 months
start_date = datetime.now() - timedelta(days=180)
date_range = [start_date + timedelta(days=int(x)) for x in np.random.randint(0, 180, num_records)]
date_range.sort()

# Categories and their probability weights
categories = ['Food', 'Rent', 'Entertainment', 'Utilities']
category_weights = [0.4, 0.1, 0.25, 0.25]
selected_categories = np.random.choice(categories, size=num_records, p=category_weights)

# Account types and their probability weights
account_types = ['Credit Card', 'Checking Account', 'Savings Account', 'Cash']
account_weights = [0.5, 0.3, 0.1, 0.1]
selected_accounts = np.random.choice(account_types, size=num_records, p=account_weights)

# Generate amounts depending on category to look somewhat realistic
amounts = []
for cat in selected_categories:
    if cat == 'Rent':
        # Rent is usually a fixed large amount
        amounts.append(round(np.random.normal(1200, 50), 2))
    elif cat == 'Utilities':
        # Utilities are moderate
        amounts.append(round(np.random.normal(150, 30), 2))
    elif cat == 'Food':
        # Food is lower but frequent
        amounts.append(round(np.random.exponential(35) + 5, 2))
    else:  # Entertainment
        # Entertainment has high variance
        amounts.append(round(np.random.uniform(10, 150), 2))

# Create DataFrame
df = pd.DataFrame({
    'Date': [d.strftime('%Y-%m-%d') for d in date_range],
    'Category': selected_categories,
    'Amount': amounts,
    'Account_Type': selected_accounts
})

# Save to CSV
output_path = 'expenses.csv'
df.to_csv(output_path, index=False)
print(f"Mock expenses data successfully written to {output_path}")
print(df.head())
