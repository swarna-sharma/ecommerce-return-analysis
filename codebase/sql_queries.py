import sqlite3
import pandas as pd
import config

def create_database_from_csv():
    """
    Create SQLite database from your CSV (simulating real database)
    """
    print("Creating SQL database from CSV...")
    
    # Read CSV
    df = pd.read_csv(config.RAW_DATA_PATH)
    
    # Create SQLite database
    conn = sqlite3.connect('ecommerce_returns.db')
    
    # Save to SQL table
    df.to_sql('orders', conn, if_exists='replace', index=False)
    
    print("Database created: ecommerce_returns.db")
    return conn

def run_sql_analysis():
    """
    Run SQL queries for return analysis
    """
    conn = create_database_from_csv()
    
    print("\n=== SQL RETURN ANALYSIS QUERIES ===")
    
    # Query 1: Return rates by category (SQL)
    query1 = """
    SELECT 
        Category,
        COUNT(*) as total_orders,
        SUM(CASE WHEN "Final Quantity" < 0 THEN 1 ELSE 0 END) as returns,
        ROUND(SUM(CASE WHEN "Final Quantity" < 0 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as return_rate_percent,
        ROUND(SUM("Final Revenue"), 2) as total_revenue
    FROM orders
    GROUP BY Category
    ORDER BY return_rate_percent DESC
    """
    
    print("1. Return Rates by Category (SQL):")
    category_returns = pd.read_sql_query(query1, conn)
    print(category_returns.head())
    
    # Query 2: Monthly return trends (SQL)
    query2 = """
    SELECT 
        strftime('%Y-%m', Date) as month,
        COUNT(*) as total_orders,
        SUM(CASE WHEN "Final Quantity" < 0 THEN 1 ELSE 0 END) as returns,
        ROUND(SUM(CASE WHEN "Final Quantity" < 0 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as return_rate_percent,
        ROUND(SUM("Final Revenue"), 2) as monthly_revenue
    FROM orders
    GROUP BY strftime('%Y-%m', Date)
    ORDER BY month
    """
    
    print("\n2. Monthly Return Trends (SQL):")
    monthly_trends = pd.read_sql_query(query2, conn)
    print(monthly_trends.head())
    
    # Query 3: High-value returns (SQL)
    query3 = """
    SELECT 
        "Item Name",
        Category,
        "Final Revenue",
        "Final Quantity"
    FROM orders
    WHERE "Final Quantity" < 0 
    AND ABS("Final Revenue") > 50
    ORDER BY ABS("Final Revenue") DESC
    LIMIT 10
    """
    
    print("\n3. High-Value Returns (SQL):")
    high_value_returns = pd.read_sql_query(query3, conn)
    print(high_value_returns)
    
    # Query 4: Customer return patterns (SQL)
    query4 = """
    SELECT 
        "Buyer ID",
        COUNT(*) as total_orders,
        SUM(CASE WHEN "Final Quantity" < 0 THEN 1 ELSE 0 END) as return_count,
        ROUND(SUM(CASE WHEN "Final Quantity" < 0 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as customer_return_rate,
        ROUND(SUM("Final Revenue"), 2) as total_spent
    FROM orders
    GROUP BY "Buyer ID"
    HAVING total_orders > 1
    ORDER BY customer_return_rate DESC
    LIMIT 10
    """
    
    print("\n4. Customers with Highest Return Rates (SQL):")
    customer_returns = pd.read_sql_query(query4, conn)
    print(customer_returns)
    
    # Save SQL results
    category_returns.to_csv('sql_category_returns.csv', index=False)
    monthly_trends.to_csv('sql_monthly_trends.csv', index=False)
    high_value_returns.to_csv('sql_high_value_returns.csv', index=False)
    customer_returns.to_csv('sql_customer_returns.csv', index=False)
    
    conn.close()
    
    print("\n✅ SQL analysis completed! Files saved:")
    print("   - sql_category_returns.csv")
    print("   - sql_monthly_trends.csv") 
    print("   - sql_high_value_returns.csv")
    print("   - sql_customer_returns.csv")
    
    return category_returns

def advanced_sql_analysis():
    """
    More complex SQL queries for deeper insights
    """
    conn = sqlite3.connect('ecommerce_returns.db')
    
    print("\n=== ADVANCED SQL ANALYSIS ===")
    
    # Query: Products with both high sales and high returns
    query = """
    WITH product_stats AS (
        SELECT 
            "Item Name",
            Category,
            COUNT(*) as total_orders,
            SUM(CASE WHEN "Final Quantity" < 0 THEN 1 ELSE 0 END) as returns,
            ROUND(SUM(CASE WHEN "Final Quantity" < 0 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as return_rate,
            ROUND(SUM("Final Revenue"), 2) as total_revenue,
            ROUND(AVG("Final Revenue"), 2) as avg_order_value
        FROM orders
        GROUP BY "Item Name", Category
        HAVING total_orders >= 5
    )
    SELECT *
    FROM product_stats
    WHERE return_rate > 20 AND total_revenue > 100
    ORDER BY return_rate DESC, total_revenue DESC
    """
    
    problem_products = pd.read_sql_query(query, conn)
    print("Problem Products (High Sales + High Returns):")
    print(problem_products)
    
    problem_products.to_csv('sql_problem_products.csv', index=False)
    conn.close()
    
    return problem_products

if __name__ == "__main__":
    # Run SQL analysis
    category_returns = run_sql_analysis()
    
    # Advanced SQL analysis
    problem_products = advanced_sql_analysis()
    
    print("\n🎯 SQL INTEGRATION COMPLETED!")
    print("SQL provided: Data extraction, complex aggregations, and customer-level analysis")
    print("Python provided: Machine learning, visualization, and predictive modeling")