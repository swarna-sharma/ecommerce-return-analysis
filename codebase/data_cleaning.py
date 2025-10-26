import pandas as pd
import numpy as np
from datetime import datetime
import config

def load_and_clean_data():
    """
    Load the raw order dataset and perform cleaning operations
    """
    print("Loading raw data...")
    df = pd.read_csv(config.RAW_DATA_PATH)
    print(f"Original dataset shape: {df.shape}")
    
    # Create a clean copy
    df_clean = df.copy()
    
    # 1. Convert scientific notation to regular numbers for Transaction ID and Item ID
    print("Converting scientific notation...")
    df_clean['Transaction ID'] = df_clean['Transaction ID'].apply(lambda x: int(float(x)) if pd.notna(x) else x)
    df_clean['Item ID'] = df_clean['Item ID'].apply(lambda x: int(float(x)) if pd.notna(x) else x)
    
    # 2. Convert date to datetime format
    print("Converting dates...")
    df_clean['Date'] = pd.to_datetime(df_clean['Date'], format=config.DATE_FORMAT, errors='coerce')
    
    # 3. Create return flag (1 for return, 0 for purchase)
    df_clean['is_return'] = (df_clean['Final Quantity'] < config.RETURN_THRESHOLD).astype(int)
    
    # 4. Extract additional features from Version column
    print("Extracting features from Version...")
    df_clean['Version_clean'] = df_clean['Version'].astype(str).str.split('/').str[0].str.strip()
    
    # 5. Handle missing values
    print("Handling missing values...")
    numeric_cols = df_clean.select_dtypes(include=[np.number]).columns
    df_clean[numeric_cols] = df_clean[numeric_cols].fillna(0)
    
    # 6. Create absolute values for return analysis
    df_clean['Final_Revenue_Abs'] = df_clean['Final Revenue'].abs()
    df_clean['Total_Revenue_Abs'] = df_clean['Total Revenue'].abs()
    
    print(f"Cleaned dataset shape: {df_clean.shape}")
    print(f"Return rate: {df_clean['is_return'].mean():.2%}")
    
    return df_clean

def analyze_returns(df):
    """
    Perform basic return analysis
    """
    print("\n=== RETURN ANALYSIS ===")
    
    # Returns by category
    returns_by_category = df.groupby('Category')['is_return'].agg(['count', 'mean']).round(3)
    returns_by_category.columns = ['total_orders', 'return_rate']
    returns_by_category = returns_by_category.sort_values('return_rate', ascending=False)
    
    print("Return rates by category:")
    print(returns_by_category)
    
    return returns_by_category

if __name__ == "__main__":
    # Load and clean data
    cleaned_df = load_and_clean_data()
    
    # Perform initial analysis
    return_analysis = analyze_returns(cleaned_df)
    
    # Save cleaned data
    print(f"\nSaving cleaned data to {config.CLEANED_DATA_PATH}")
    cleaned_df.to_csv(config.CLEANED_DATA_PATH, index=False)
    
    print("Data cleaning completed successfully!")