import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import config

def create_dashboard_summary():
    """
    Create summary files and visualizations for Power BI dashboard
    """
    print("Preparing Power BI dashboard materials...")
    
    # Load all datasets
    analysis_df = pd.read_csv(config.ANALYSIS_DATA_PATH, parse_dates=['Date'])
    high_risk_df = pd.read_csv(config.HIGH_RISK_PRODUCTS_PATH)
    
    # 1. Create summary statistics
    summary_stats = {
        'total_orders': len(analysis_df),
        'total_returns': analysis_df['is_return'].sum(),
        'overall_return_rate': analysis_df['is_return'].mean(),
        'total_revenue': analysis_df['Total_Revenue_Abs'].sum(),
        'revenue_lost_to_returns': analysis_df[analysis_df['is_return'] == 1]['Final_Revenue_Abs'].sum(),
        'high_risk_products_count': len(high_risk_df),
        'high_risk_revenue_exposure': high_risk_df['Final_Revenue_Abs'].sum()
    }
    
    # 2. Category performance summary
    category_summary = analysis_df.groupby('Category').agg({
        'is_return': ['count', 'sum', 'mean'],
        'Final_Revenue_Abs': 'sum',
        'Total_Revenue_Abs': 'sum'
    }).round(4)
    
    category_summary.columns = ['orders', 'returns', 'return_rate', 'final_revenue', 'total_revenue']
    category_summary['revenue_loss'] = category_summary['returns'] * category_summary['final_revenue'] / category_summary['orders']
    category_summary = category_summary.sort_values('return_rate', ascending=False)
    
    # 3. Monthly trends
    monthly_trends = analysis_df.groupby(pd.to_datetime(analysis_df['Date']).dt.to_period('M')).agg({
        'is_return': ['count', 'sum', 'mean'],
        'Final_Revenue_Abs': 'sum'
    }).round(4)
    monthly_trends.columns = ['orders', 'returns', 'return_rate', 'revenue']
    monthly_trends.index = monthly_trends.index.astype(str)
    
    # 4. High-risk analysis by category
    high_risk_summary = high_risk_df.groupby('Category').agg({
        'Item Name': 'count',
        'return_probability': 'mean',
        'Final_Revenue_Abs': 'sum'
    }).round(4)
    high_risk_summary.columns = ['high_risk_count', 'avg_risk_score', 'revenue_exposure']
    high_risk_summary = high_risk_summary.sort_values('high_risk_count', ascending=False)
    
    # 5. Save summary files
    summary_stats_df = pd.DataFrame([summary_stats])
    summary_stats_df.to_csv('dashboard_summary_stats.csv', index=False)
    category_summary.to_csv('dashboard_category_summary.csv')
    monthly_trends.to_csv('dashboard_monthly_trends.csv')
    high_risk_summary.to_csv('dashboard_high_risk_summary.csv')
    
    print("Dashboard summary files created:")
    print("✅ dashboard_summary_stats.csv")
    print("✅ dashboard_category_summary.csv") 
    print("✅ dashboard_monthly_trends.csv")
    print("✅ dashboard_high_risk_summary.csv")
    
    # 6. Create visualizations
    create_dashboard_visualizations(category_summary, monthly_trends, high_risk_summary, summary_stats)
    
    return summary_stats

def create_dashboard_visualizations(category_summary, monthly_trends, high_risk_summary, summary_stats):
    """
    Create key visualizations for the dashboard
    """
    print("Creating dashboard visualizations...")
    
    plt.style.use('seaborn-v0_8')
    
    # 1. Return Rate by Category
    plt.figure(figsize=(12, 6))
    top_categories = category_summary.head(10)
    plt.barh(top_categories.index, top_categories['return_rate'] * 100)
    plt.xlabel('Return Rate (%)')
    plt.title('Top 10 Categories by Return Rate')
    plt.tight_layout()
    plt.savefig('return_rate_by_category.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # 2. Monthly Return Trends
    plt.figure(figsize=(12, 6))
    plt.plot(monthly_trends.index, monthly_trends['return_rate'] * 100, marker='o')
    plt.xlabel('Month')
    plt.ylabel('Return Rate (%)')
    plt.title('Monthly Return Rate Trends')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('monthly_return_trends.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # 3. High-Risk Products by Category
    plt.figure(figsize=(12, 6))
    top_high_risk = high_risk_summary.head(10)
    plt.bar(top_high_risk.index, top_high_risk['high_risk_count'])
    plt.xlabel('Category')
    plt.ylabel('Number of High-Risk Products')
    plt.title('High-Risk Products by Category')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('high_risk_by_category.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print("Dashboard visualizations created:")
    print("✅ return_rate_by_category.png")
    print("✅ monthly_return_trends.png")
    print("✅ high_risk_by_category.png")

def generate_final_report():
    """
    Generate final project summary
    """
    print("\n" + "="*50)
    print("E-COMMERCE RETURN ANALYSIS - PROJECT COMPLETED")
    print("="*50)
    
    # Load summary
    summary_stats = pd.read_csv('dashboard_summary_stats.csv').iloc[0]
    
    print(f"\n📊 PROJECT DELIVERABLES:")
    print(f"✅ Python codebase for return prediction")
    print(f"✅ Cleaned datasets for analysis")
    print(f"✅ High-risk products identified: {int(summary_stats['high_risk_products_count'])}")
    print(f"✅ Dashboard-ready summary files")
    print(f"✅ Key visualizations for reporting")
    
    print(f"\n📈 KEY METRICS:")
    print(f"• Overall Return Rate: {summary_stats['overall_return_rate']:.2%}")
    print(f"• Total Orders Analyzed: {int(summary_stats['total_orders']):,}")
    print(f"• Revenue at Risk: ${summary_stats['high_risk_revenue_exposure']:,.2f}")
    print(f"• High-Risk Products: {int(summary_stats['high_risk_products_count'])}")
    
    print(f"\n🎯 NEXT STEPS:")
    print(f"1. Import CSV files into Power BI")
    print(f"2. Connect data sources in Power BI")
    print(f"3. Build interactive dashboard with filters")
    print(f"4. Share insights with stakeholders")
    
    print(f"\n📁 FILES FOR POWER BI:")
    print(f"• return_analysis_dataset.csv - Main dataset")
    print(f"• high_risk_products.csv - Risk predictions")
    print(f"• dashboard_*.csv - Summary tables")

if __name__ == "__main__":
    # Create dashboard materials
    summary_stats = create_dashboard_summary()
    
    # Generate final report
    generate_final_report()