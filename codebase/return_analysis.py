import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import config

def load_cleaned_data():
    """Load the cleaned dataset"""
    print("Loading cleaned data...")
    df = pd.read_csv(config.CLEANED_DATA_PATH, parse_dates=['Date'])
    return df

def comprehensive_return_analysis(df):
    """
    Perform comprehensive return analysis
    """
    print("\n=== COMPREHENSIVE RETURN ANALYSIS ===")
    
    # 1. Overall metrics
    total_orders = len(df)
    total_returns = df['is_return'].sum()
    overall_return_rate = total_returns / total_orders
    
    print(f"Total Orders: {total_orders:,}")
    print(f"Total Returns: {total_returns:,}")
    print(f"Overall Return Rate: {overall_return_rate:.2%}")
    
    # 2. Return analysis by category
    category_analysis = df.groupby('Category').agg({
        'is_return': ['count', 'sum', 'mean'],
        'Final_Revenue_Abs': 'sum',
        'Total_Revenue_Abs': 'sum'
    }).round(3)
    
    # Flatten column names
    category_analysis.columns = ['total_orders', 'returns', 'return_rate', 'final_revenue', 'total_revenue']
    category_analysis = category_analysis.sort_values('return_rate', ascending=False)
    
    print("\nReturn Analysis by Category:")
    print(category_analysis)
    
    # 3. Monthly return trends
    df['year_month'] = df['Date'].dt.to_period('M')
    monthly_trends = df.groupby('year_month').agg({
        'is_return': ['count', 'sum', 'mean'],
        'Final_Revenue_Abs': 'sum'
    }).round(3)
    
    monthly_trends.columns = ['total_orders', 'returns', 'return_rate', 'revenue']
    print("\nMonthly Return Trends:")
    print(monthly_trends.tail(6))  # Last 6 months
    
    # 4. Version analysis (sizes/colors)
    version_analysis = df.groupby('Version_clean').agg({
        'is_return': ['count', 'mean']
    }).round(3)
    version_analysis.columns = ['total_orders', 'return_rate']
    version_analysis = version_analysis[version_analysis['total_orders'] > 10].sort_values('return_rate', ascending=False)
    
    print("\nTop 10 Versions with Highest Return Rates (min 10 orders):")
    print(version_analysis.head(10))
    
    return {
        'category_analysis': category_analysis,
        'monthly_trends': monthly_trends,
        'version_analysis': version_analysis,
        'overall_metrics': {
            'total_orders': total_orders,
            'total_returns': total_returns,
            'overall_return_rate': overall_return_rate
        }
    }

def create_analysis_dataset(df, analysis_results):
    """
    Create enhanced dataset for further analysis and Power BI
    """
    print("\nCreating enhanced analysis dataset...")
    
    # Add derived features
    df_enhanced = df.copy()
    
    # Time-based features
    df_enhanced['order_month'] = df_enhanced['Date'].dt.to_period('M')
    df_enhanced['order_week'] = df_enhanced['Date'].dt.isocalendar().week
    df_enhanced['order_day'] = df_enhanced['Date'].dt.day_name()
    
    # Revenue impact features
    df_enhanced['revenue_loss'] = df_enhanced['is_return'] * df_enhanced['Final_Revenue_Abs']
    
    # Save enhanced dataset
    df_enhanced.to_csv(config.ANALYSIS_DATA_PATH, index=False)
    print(f"Enhanced dataset saved to: {config.ANALYSIS_DATA_PATH}")
    
    return df_enhanced

if __name__ == "__main__":
    # Load cleaned data
    df = load_cleaned_data()
    
    # Perform comprehensive analysis
    analysis_results = comprehensive_return_analysis(df)
    
    # Create enhanced dataset for Power BI
    enhanced_df = create_analysis_dataset(df, analysis_results)
    
    print("\nReturn analysis completed successfully!")
    print(f"Enhanced dataset ready for Power BI: {config.ANALYSIS_DATA_PATH}")