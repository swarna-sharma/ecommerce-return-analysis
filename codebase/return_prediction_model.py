import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score
import matplotlib.pyplot as plt
import seaborn as sns
import config
import joblib

def prepare_features(df):
    """
    Prepare features for the prediction model
    """
    print("Preparing features for modeling...")
    
    # Select features for modeling
    feature_df = df.copy()
    
    # Encode categorical variables
    label_encoders = {}
    categorical_features = ['Category', 'Version_clean']
    
    for feature in categorical_features:
        le = LabelEncoder()
        feature_df[f'{feature}_encoded'] = le.fit_transform(feature_df[feature].astype(str))
        label_encoders[feature] = le
    
    # Select final features
    features = [
        'Category_encoded', 'Version_clean_encoded',
        'Total_Revenue_Abs', 'Price Reductions', 'Sales Tax',
        'Final_Revenue_Abs', 'Purchased Item Count'
    ]
    
    X = feature_df[features]
    y = feature_df['is_return']
    
    print(f"Feature matrix shape: {X.shape}")
    print(f"Target distribution:\n{y.value_counts()}")
    
    return X, y, label_encoders, features

def train_return_prediction_model(X, y):
    """
    Train logistic regression model to predict returns
    """
    print("\nTraining return prediction model...")
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=config.TEST_SIZE, random_state=config.RANDOM_STATE, stratify=y
    )
    
    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Train model
    model = LogisticRegression(random_state=config.RANDOM_STATE, class_weight='balanced')
    model.fit(X_train_scaled, y_train)
    
    # Make predictions
    y_pred = model.predict(X_test_scaled)
    y_pred_proba = model.predict_proba(X_test_scaled)[:, 1]
    
    # Evaluate model
    print("\n=== MODEL EVALUATION ===")
    print(classification_report(y_test, y_pred))
    print(f"ROC AUC Score: {roc_auc_score(y_test, y_pred_proba):.3f}")
    
    # Confusion Matrix
    cm = confusion_matrix(y_test, y_pred)
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
    plt.title('Confusion Matrix - Return Prediction')
    plt.ylabel('Actual')
    plt.xlabel('Predicted')
    plt.savefig('confusion_matrix.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    return model, scaler, X_test, y_test, y_pred_proba

def identify_high_risk_products(df, model, scaler, features, label_encoders):
    """
    Identify high-risk products using the trained model
    """
    print("\nIdentifying high-risk products...")
    
    # Prepare features for full dataset
    feature_df = df.copy()
    
    # Encode categorical variables using saved encoders
    for feature, le in label_encoders.items():
        feature_df[f'{feature}_encoded'] = le.transform(feature_df[feature].astype(str))
    
    X_full = feature_df[features]
    X_full_scaled = scaler.transform(X_full)
    
    # Predict return probabilities
    return_proba = model.predict_proba(X_full_scaled)[:, 1]
    
    # Add predictions to dataframe
    df_with_risk = df.copy()
    df_with_risk['return_probability'] = return_proba
    df_with_risk['risk_category'] = pd.cut(return_proba, 
                                        bins=[0, 0.3, 0.7, 1], 
                                        labels=['Low', 'Medium', 'High'])
    
    # High-risk products (probability > 0.7)
    high_risk_products = df_with_risk[df_with_risk['return_probability'] > 0.7]
    
    print(f"High-risk products identified: {len(high_risk_products)}")
    print(f"High-risk rate: {len(high_risk_products)/len(df_with_risk):.2%}")
    
    # Analyze high-risk products by category
    high_risk_by_category = high_risk_products.groupby('Category').agg({
        'Item Name': 'count',
        'return_probability': 'mean'
    }).sort_values('Item Name', ascending=False)
    
    print("\nHigh-risk products by category:")
    print(high_risk_by_category)
    
    return df_with_risk, high_risk_products

def save_high_risk_products(high_risk_products):
    """
    Save high-risk products to CSV for further analysis
    """
    # Select relevant columns
    output_columns = [
        'Item Name', 'Category', 'Version', 'Version_clean',
        'return_probability', 'risk_category', 'Final_Revenue_Abs',
        'is_return', 'Date'
    ]
    
    high_risk_output = high_risk_products[output_columns].sort_values('return_probability', ascending=False)
    
    # Save to CSV
    high_risk_output.to_csv(config.HIGH_RISK_PRODUCTS_PATH, index=False)
    print(f"\nHigh-risk products saved to: {config.HIGH_RISK_PRODUCTS_PATH}")
    
    return high_risk_output

if __name__ == "__main__":
    # Load enhanced data
    print("Loading analysis dataset...")
    df = pd.read_csv(config.ANALYSIS_DATA_PATH, parse_dates=['Date'])
    
    # Prepare features and train model
    X, y, label_encoders, features = prepare_features(df)
    model, scaler, X_test, y_test, y_pred_proba = train_return_prediction_model(X, y)
    
    # Identify high-risk products
    df_with_risk, high_risk_products = identify_high_risk_products(df, model, scaler, features, label_encoders)
    
    # Save results
    high_risk_output = save_high_risk_products(high_risk_products)
    
    print("\n=== PREDICTION MODEL COMPLETED ===")
    print(f"High-risk products identified: {len(high_risk_products)}")
    print(f"Model trained and high-risk products saved successfully!")