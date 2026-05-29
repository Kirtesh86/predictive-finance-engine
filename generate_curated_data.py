import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Set random seed for reproducibility
np.random.seed(101)

data = []

# Generate data for the last 365 days (1 full year)
end_date = datetime.now()
start_date = end_date - timedelta(days=365)

current_date = start_date
while current_date <= end_date:
    # ---------------------------------------------------------
    # 1. FIXED MONTHLY RECURRING EXPENSES
    # ---------------------------------------------------------
    # Rent - Paid on the 1st of every month
    if current_date.day == 1:
        data.append({
            'Date': current_date.strftime('%Y-%m-%d'),
            'Category': 'Rent',
            'Amount': 1200.00,
            'Account_Type': 'Checking Account',
            'Description': 'Nandanvan Heights Apartments (Rent)'
        })
        
    # Utilities & Internet - Paid on the 10th of every month
    if current_date.day == 10:
        # Power & Water has seasonal variance (higher in summer: Apr-Jun)
        is_summer = current_date.month in [4, 5, 6]
        base_power = 185.00 if is_summer else 135.00
        
        data.append({
            'Date': current_date.strftime('%Y-%m-%d'),
            'Category': 'Utilities',
            'Amount': round(base_power + np.random.uniform(-15, 15), 2),
            'Account_Type': 'Checking Account',
            'Description': 'State Electricity Board (Power/Water)'
        })
        data.append({
            'Date': current_date.strftime('%Y-%m-%d'),
            'Category': 'Utilities',
            'Amount': 79.99,
            'Account_Type': 'Credit Card',
            'Description': 'Comcast Broadband (Internet)'
        })
        
    # Subscriptions - Netflix on 15th, Spotify on 20th
    if current_date.day == 15:
        data.append({
            'Date': current_date.strftime('%Y-%m-%d'),
            'Category': 'Entertainment',
            'Amount': 15.49,
            'Account_Type': 'Credit Card',
            'Description': 'Netflix Subscription'
        })
    if current_date.day == 20:
        data.append({
            'Date': current_date.strftime('%Y-%m-%d'),
            'Category': 'Entertainment',
            'Amount': 9.99,
            'Account_Type': 'Credit Card',
            'Description': 'Spotify Premium Family'
        })

    # ---------------------------------------------------------
    # 2. FREQUENT HABITS (Food & Groceries)
    # ---------------------------------------------------------
    # Weekday Coffee Runs (Mon-Fri)
    if current_date.weekday() < 5:
        # 65% probability of buying coffee on a workday
        if np.random.rand() < 0.65:
            coffee_spots = [
                ("Starbucks (Nandanvan)", 5.50, 8.50),
                ("Owl Night Cafe (Nandanvan)", 6.50, 9.50),
                ("Cafe Coffee Day (Nandanvan)", 5.00, 7.50),
                ("Nandanvan Cafe (Local)", 4.00, 6.50)
            ]
            # Owl Night Cafe is a favorite (weighted choice)
            chosen_idx = np.random.choice([0, 1, 2, 3], p=[0.25, 0.40, 0.15, 0.20])
            spot, min_p, max_p = coffee_spots[chosen_idx]
            
            data.append({
                'Date': current_date.strftime('%Y-%m-%d'),
                'Category': 'Food',
                'Amount': round(np.random.uniform(min_p, max_p), 2),
                'Account_Type': 'Credit Card',
                'Description': spot
            })
            
    # Thursday Weekly Groceries
    if current_date.weekday() == 3:  # Thursday
        grocery_spots = [
            ("Whole Foods Market (Nandanvan)", 90.00, 150.00),
            ("Local Kirana Shop (Nandanvan)", 60.00, 100.00)
        ]
        spot, min_g, max_g = grocery_spots[np.random.choice([0, 1], p=[0.7, 0.3])]
        data.append({
            'Date': current_date.strftime('%Y-%m-%d'),
            'Category': 'Food',
            'Amount': round(np.random.uniform(min_g, max_g), 2),
            'Account_Type': 'Checking Account',
            'Description': spot
        })
        
    # Weekend Dinners (Friday / Saturday)
    if current_date.weekday() in [4, 5]:
        # 80% probability of eating out on weekends
        if np.random.rand() < 0.80:
            restaurants = [
                ("Nandanvan Food Court", 25.00, 55.00),
                ("Haldiram's (Nandanvan)", 30.00, 65.00),
                ("The Grill House (Nandanvan)", 50.00, 110.00),
                ("Domino's Pizza (Local)", 20.00, 45.00)
            ]
            rest, min_r, max_r = restaurants[np.random.choice(len(restaurants))]
            data.append({
                'Date': current_date.strftime('%Y-%m-%d'),
                'Category': 'Food',
                'Amount': round(np.random.uniform(min_r, max_r), 2),
                'Account_Type': 'Credit Card',
                'Description': rest
            })

    # ---------------------------------------------------------
    # 3. ENTERTAINMENT & LEISURE (Saturdays)
    # ---------------------------------------------------------
    if current_date.weekday() == 5:  # Saturday
        # 50% probability of leisure outings
        if np.random.rand() < 0.50:
            # Lifestyle Inflation Factor: Spending climbs slightly as months pass
            months_elapsed = (current_date - start_date).days / 30.0
            inflation = months_elapsed * 10.0  # +$10/month creep
            
            activities = [
                ("PVR Cinemas (Nandanvan)", 15.00, 45.00),
                ("Sardar Patel Complex (Bowling)", 25.00, 55.00),
                ("Steam Games Store", 10.00, 60.00),
                ("Gaming Lounge (Nandanvan)", 15.00, 40.00)
            ]
            act, min_a, max_a = activities[np.random.choice(len(activities))]
            data.append({
                'Date': current_date.strftime('%Y-%m-%d'),
                'Category': 'Entertainment',
                'Amount': round(np.random.uniform(min_a, max_a) + inflation, 2),
                'Account_Type': 'Credit Card',
                'Description': act
            })

    # ---------------------------------------------------------
    # 4. RANDOM DISCRETIONARY SPENDS (Other)
    # ---------------------------------------------------------
    if np.random.rand() < 0.08:  # 8% daily chance
        other_items = [
            ("Pharmacy / Local Drugstore", 15.00, 65.00),
            ("Local Fuel / Petrol Station", 30.00, 55.00),
            ("Amazon online purchase", 20.00, 150.00),
            ("Uber Ride (Local)", 8.00, 25.00)
        ]
        item, min_o, max_o = other_items[np.random.choice(len(other_items))]
        data.append({
            'Date': current_date.strftime('%Y-%m-%d'),
            'Category': 'Other',
            'Amount': round(np.random.uniform(min_o, max_o), 2),
            'Account_Type': 'Credit Card',
            'Description': item
        })

    # ---------------------------------------------------------
    # 5. LARGE SPENDING ANOMALIES (Outliers for Analytics)
    # ---------------------------------------------------------
    # Anomaly 1: A major trip in the fall (October 12)
    if current_date.month == 10 and current_date.day == 12:
        data.append({
            'Date': current_date.strftime('%Y-%m-%d'),
            'Category': 'Entertainment',
            'Amount': 850.00,
            'Account_Type': 'Credit Card',
            'Description': 'Weekend Vacation Booking (Goa Trip)'
        })
        
    # Anomaly 2: Christmas tech purchase (December 24)
    if current_date.month == 12 and current_date.day == 24:
        data.append({
            'Date': current_date.strftime('%Y-%m-%d'),
            'Category': 'Other',
            'Amount': 2499.00,
            'Account_Type': 'Credit Card',
            'Description': 'Apple MacBook Pro 16" (Work/Study)'
        })

    current_date += timedelta(days=1)

# Compile into DataFrame
df = pd.DataFrame(data)
df.to_csv('expenses.csv', index=False)
print(f"Curated explanatory dataset created successfully at expenses.csv with {len(df)} records.")
