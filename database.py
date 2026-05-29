import os
import pandas as pd
import streamlit as st
from datetime import datetime, date
from typing import Optional
from sqlalchemy import create_engine, Column, Integer, Float, String, Date
from sqlalchemy.orm import declarative_base, sessionmaker, Session

# Database SQLite Location Setup
DATABASE_URL = "sqlite:///finance.db"

# Base class for ORM schema declarations
Base = declarative_base()

class Transaction(Base):
    """
    SQLAlchemy ORM model representing a financial transaction record in SQLite database.
    """
    __tablename__ = 'transactions'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(Date, nullable=False)
    category = Column(String(50), nullable=False)
    amount = Column(Float, nullable=False)
    account_type = Column(String(50), nullable=False)
    description = Column(String(200), nullable=True)

# ---------------------------------------------------------
# Connection Caching Optimization
# ---------------------------------------------------------
@st.cache_resource
def get_db_engine():
    """
    Creates and caches the SQLAlchemy database engine instance.
    """
    return create_engine(
        DATABASE_URL, 
        connect_args={"check_same_thread": False} # SQLite specific for Streamlit multi-threading
    )

@st.cache_resource
def get_sessionmaker():
    """
    Creates and caches the local session factory bound to the cached engine.
    """
    engine = get_db_engine()
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)

def SessionLocal() -> Session:
    """
    Returns an active database session instance.
    """
    session_factory = get_sessionmaker()
    return session_factory()

# ---------------------------------------------------------
# Database Lifecycle & Transaction Seeding
# ---------------------------------------------------------
def init_db() -> None:
    """
    Initializes the database schema tables. If the transactions table is empty,
    it automatically seeds the database with transaction history from expenses.csv.
    """
    engine = get_db_engine()
    Base.metadata.create_all(bind=engine)
    
    session = SessionLocal()
    try:
        # Check if the database table is currently unseeded
        if session.query(Transaction).count() == 0:
            csv_path = "expenses.csv"
            
            # Generate the CSV if missing
            if not os.path.exists(csv_path):
                import subprocess
                subprocess.run(["python", "generate_clean_data.py"], check=True)
                
            if os.path.exists(csv_path):
                df = pd.read_csv(csv_path)
                transactions_to_seed = []
                
                for _, row in df.iterrows():
                    # Parse date formatting
                    date_obj = datetime.strptime(str(row['Date']), '%Y-%m-%d').date()
                    tx = Transaction(
                        date=date_obj,
                        category=str(row['Category']),
                        amount=float(row['Amount']),
                        account_type=str(row['Account_Type']),
                        description=str(row['Description']) if pd.notna(row.get('Description')) else ""
                    )
                    transactions_to_seed.append(tx)
                
                # Bulk insert for efficiency
                session.bulk_save_objects(transactions_to_seed)
                session.commit()
                print(f"[Database] Success: Seeded database with {len(transactions_to_seed)} records from {csv_path}.")
    except Exception as e:
        session.rollback()
        print(f"[Database] Error seeding database: {e}")
    finally:
        session.close()


def get_transactions_df(session: Session) -> pd.DataFrame:
    """
    Queries all Transaction entries and returns them in a Pandas DataFrame.

    Parameters:
        session (Session): The active SQLAlchemy DB session.

    Returns:
        pd.DataFrame: A formatted pandas DataFrame of the transactions dataset.
    """
    query = session.query(Transaction).statement
    df = pd.read_sql(query, session.bind)
    
    if df.empty:
        return pd.DataFrame(columns=['Date', 'Category', 'Amount', 'Account_Type', 'Description'])
    
    # Map lowercase database schema columns to matching uppercase dashboard columns
    df['Date'] = pd.to_datetime(df['date'])
    df['Amount'] = df['amount']
    df['Category'] = df['category']
    df['Account_Type'] = df['account_type']
    df['Description'] = df['description'].fillna("")
    
    return df[['Date', 'Category', 'Amount', 'Account_Type', 'Description']]


def add_transaction(
    session: Session, 
    transaction_date: date, 
    category: str, 
    amount: float, 
    account_type: str, 
    description: str = ""
) -> None:
    """
    Saves a manual transaction record into the database.

    Parameters:
        session (Session): The active SQLAlchemy DB session.
        transaction_date (date): Calendar date of the event.
        category (str): Financial category.
        amount (float): Outflow volume in dollars.
        account_type (str): Origin account type.
        description (str): Memo detail description.
    """
    try:
        tx = Transaction(
            date=transaction_date,
            category=category,
            amount=amount,
            account_type=account_type,
            description=description
        )
        session.add(tx)
        session.commit()
        print(f"[Database] Success: Added transaction: {category} of ${amount:.2f}")
    except Exception as e:
        session.rollback()
        print(f"[Database] Error adding transaction: {e}")
        raise e
