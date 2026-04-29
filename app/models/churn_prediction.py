import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from app.models.model_comparison import ModelComparison
import warnings
warnings.filterwarnings('ignore')

class ChurnPrediction:
    def __init__(self, data_path='cleandataset.csv'):
        """Initialize Churn Prediction System"""
        self.df = pd.read_csv(data_path)
        self.customer_features = None
        self.churn_labels = None
        self.models = {}
        self.scaler = StandardScaler()
        self.predictions = None
        self.feature_importance = None
        self.model_comparison = None
        self.prepare_data()
    
    def prepare_data(self):
        """Prepare and clean data for churn prediction"""
        # Convert InvoiceDate to datetime
        self.df['InvoiceDate'] = pd.to_datetime(self.df['InvoiceDate'], format='%m/%d/%Y %H:%M:%S')
        
        # Convert Quantity to numeric
        self.df['Quantity'] = pd.to_numeric(self.df['Quantity'], errors='coerce')
        
        # Calculate TotalAmount
        self.df['TotalAmount'] = self.df['Quantity'] * self.df['Price']
        
        # Filter positive quantities and amounts
        self.df = self.df[(self.df['Quantity'] > 0) & (self.df['TotalAmount'] > 0)]
        
        # Extract date
        self.df['Date'] = self.df['InvoiceDate'].dt.date
    
    def calculate_customer_features(self):
        """Calculate comprehensive customer features for churn prediction"""
        # Get the reference date (last date in dataset)
        reference_date = self.df['InvoiceDate'].max()
        
        # Calculate customer-level features
        customer_data = self.df.groupby('Customer ID').agg({
            'InvoiceDate': ['min', 'max', 'count'],
            'Invoice': 'nunique',
            'Quantity': ['sum', 'mean', 'std'],
            'TotalAmount': ['sum', 'mean', 'std', 'min', 'max'],
            'Description': 'nunique'
        }).reset_index()
        
        # Flatten column names
        customer_data.columns = ['Customer_ID', 'First_Purchase', 'Last_Purchase', 'Total_Transactions',
                                 'Unique_Invoices', 'Total_Quantity', 'Avg_Quantity', 'Std_Quantity',
                                 'Total_Spent', 'Avg_Transaction_Value', 'Std_Transaction_Value',
                                 'Min_Transaction', 'Max_Transaction', 'Unique_Products']
        
        # Calculate derived features
        customer_data['Recency_Days'] = (reference_date - customer_data['Last_Purchase']).dt.days
        customer_data['Customer_Lifetime_Days'] = (customer_data['Last_Purchase'] - customer_data['First_Purchase']).dt.days
        customer_data['Purchase_Frequency'] = customer_data['Total_Transactions'] / (customer_data['Customer_Lifetime_Days'] + 1)
        customer_data['Avg_Days_Between_Purchases'] = customer_data['Customer_Lifetime_Days'] / (customer_data['Unique_Invoices'] + 1)
        
        # Calculate RFM scores (using 5 quantiles creates 5 bins, need 5 labels)
        try:
            customer_data['R_Score'] = pd.qcut(customer_data['Recency_Days'], q=5, labels=False, duplicates='drop')
            customer_data['R_Score'] = 5 - customer_data['R_Score']  # Reverse so lower recency = higher score
        except:
            customer_data['R_Score'] = 3  # Default middle score if qcut fails
        
        try:
            customer_data['F_Score'] = pd.qcut(customer_data['Unique_Invoices'], q=5, labels=False, duplicates='drop')
        except:
            customer_data['F_Score'] = 3
        
        try:
            customer_data['M_Score'] = pd.qcut(customer_data['Total_Spent'], q=5, labels=False, duplicates='drop')
        except:
            customer_data['M_Score'] = 3
        
        # Convert scores to numeric (already done with astype above)
        customer_data['RFM_Score'] = customer_data['R_Score'] + customer_data['F_Score'] + customer_data['M_Score']
        
        # Calculate engagement metrics
        customer_data['Product_Diversity'] = customer_data['Unique_Products'] / customer_data['Total_Transactions']
        customer_data['Spending_Consistency'] = 1 - (customer_data['Std_Transaction_Value'] / (customer_data['Avg_Transaction_Value'] + 1))
        customer_data['Transaction_Size_Ratio'] = customer_data['Max_Transaction'] / (customer_data['Avg_Transaction_Value'] + 1)
        
        # Handle missing values
        customer_data = customer_data.fillna(0)
        
        # Define churn based on customer behavior patterns
        # A customer is considered churned if:
        # 1. Recency > 2x their average purchase interval, OR
        # 2. Recency > 60 days for frequent buyers (>10 purchases), OR
        # 3. Recency > 90 days for moderate buyers (5-10 purchases), OR
        # 4. Recency > 120 days for occasional buyers (<5 purchases)
        
        def determine_churn(row):
            recency = row['Recency_Days']
            frequency = row['Unique_Invoices']
            avg_days_between = row['Avg_Days_Between_Purchases']
            
            # Dynamic threshold based on customer behavior
            if frequency >= 10:  # Frequent buyers
                threshold = min(60, avg_days_between * 2)
            elif frequency >= 5:  # Moderate buyers
                threshold = min(90, avg_days_between * 2)
            else:  # Occasional buyers
                threshold = min(120, avg_days_between * 2)
            
            return 1 if recency > threshold else 0
        
        customer_data['Is_Churned'] = customer_data.apply(determine_churn, axis=1)
        
        self.customer_features = customer_data
        return customer_data
    
    def prepare_training_data(self):
        """Prepare features and labels for model training"""
        if self.customer_features is None:
            self.calculate_customer_features()
        
        # Select features for training
        feature_columns = [
            'Recency_Days', 'Unique_Invoices', 'Total_Spent', 'Avg_Transaction_Value',
            'Customer_Lifetime_Days', 'Purchase_Frequency', 'Avg_Days_Between_Purchases',
            'R_Score', 'F_Score', 'M_Score', 'RFM_Score',
            'Product_Diversity', 'Spending_Consistency', 'Transaction_Size_Ratio',
            'Total_Quantity', 'Avg_Quantity', 'Unique_Products'
        ]
        
        X = self.customer_features[feature_columns].copy()
        y = self.customer_features['Is_Churned'].copy()
        
        # Handle infinite values
        X = X.replace([np.inf, -np.inf], 0)
        
        return X, y, feature_columns
    
    def train_models(self):
        """Train multiple churn prediction models"""
        X, y, feature_columns = self.prepare_training_data()
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train Random Forest
        rf_model = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42, n_jobs=-1)
        rf_model.fit(X_train_scaled, y_train)
        rf_score = rf_model.score(X_test_scaled, y_test)
        
        # Train Gradient Boosting
        gb_model = GradientBoostingClassifier(n_estimators=100, max_depth=5, random_state=42)
        gb_model.fit(X_train_scaled, y_train)
        gb_score = gb_model.score(X_test_scaled, y_test)
        
        # Train Logistic Regression
        lr_model = LogisticRegression(max_iter=1000, random_state=42)
        lr_model.fit(X_train_scaled, y_train)
        lr_score = lr_model.score(X_test_scaled, y_test)
        
        # Store models and scores
        self.models = {
            'random_forest': {'model': rf_model, 'accuracy': rf_score},
            'gradient_boosting': {'model': gb_model, 'accuracy': gb_score},
            'logistic_regression': {'model': lr_model, 'accuracy': lr_score}
        }
        
        # Calculate feature importance from Random Forest
        self.feature_importance = pd.DataFrame({
            'Feature': feature_columns,
            'Importance': rf_model.feature_importances_
        }).sort_values('Importance', ascending=False)
        
        return self.models
    
    def predict_churn(self, model_name='random_forest'):
        """Predict churn probability for all customers"""
        if not self.models:
            self.train_models()
        
        X, y, feature_columns = self.prepare_training_data()
        X_scaled = self.scaler.transform(X)
        
        model = self.models[model_name]['model']
        
        # Predict probabilities
        churn_probabilities = model.predict_proba(X_scaled)[:, 1]
        churn_predictions = model.predict(X_scaled)
        
        # Create predictions dataframe
        predictions_df = self.customer_features[['Customer_ID', 'Recency_Days', 'Unique_Invoices', 
                                                   'Total_Spent', 'RFM_Score', 'Is_Churned',
                                                   'Avg_Days_Between_Purchases', 'Purchase_Frequency']].copy()
        predictions_df['Churn_Probability'] = churn_probabilities
        predictions_df['Predicted_Churn'] = churn_predictions
        
        # Classify risk levels with more granular thresholds
        def classify_risk(prob):
            if prob >= 0.7:
                return 'High Risk'
            elif prob >= 0.4:
                return 'Medium Risk'
            else:
                return 'Low Risk'
        
        predictions_df['Risk_Level'] = predictions_df['Churn_Probability'].apply(classify_risk)
        
        # Add customer value segment based on total spent
        predictions_df['Value_Segment'] = pd.qcut(
            predictions_df['Total_Spent'],
            q=4,
            labels=['Low Value', 'Medium Value', 'High Value', 'VIP'],
            duplicates='drop'
        )
        
        # Add days since last purchase category
        def categorize_recency(days):
            if days <= 30:
                return 'Active (0-30 days)'
            elif days <= 60:
                return 'Recent (31-60 days)'
            elif days <= 90:
                return 'At Risk (61-90 days)'
            else:
                return 'Inactive (90+ days)'
        
        predictions_df['Recency_Category'] = predictions_df['Recency_Days'].apply(categorize_recency)
        
        self.predictions = predictions_df
        return predictions_df
    
    def get_churn_summary(self):
        """Get summary statistics of churn predictions"""
        if self.predictions is None:
            self.predict_churn()
        
        # Calculate various metrics
        total_customers = int(len(self.predictions))
        churned_customers = int(self.predictions['Is_Churned'].sum())
        churn_rate = float(self.predictions['Is_Churned'].mean() * 100)
        
        high_risk = int((self.predictions['Risk_Level'] == 'High Risk').sum())
        medium_risk = int((self.predictions['Risk_Level'] == 'Medium Risk').sum())
        low_risk = int((self.predictions['Risk_Level'] == 'Low Risk').sum())
        
        avg_churn_prob = float(self.predictions['Churn_Probability'].mean() * 100)
        
        # VIP customers at risk (High Value or VIP segment with High or Medium risk)
        vip_at_risk = int(
            ((self.predictions['Value_Segment'].isin(['VIP', 'High Value'])) & 
             (self.predictions['Risk_Level'].isin(['High Risk', 'Medium Risk']))).sum()
        )
        
        # Active vs Inactive customers
        active_customers = int((self.predictions['Recency_Days'] <= 30).sum())
        inactive_customers = int((self.predictions['Recency_Days'] > 90).sum())
        
        # Average recency by risk level
        avg_recency_high_risk = float(
            self.predictions[self.predictions['Risk_Level'] == 'High Risk']['Recency_Days'].mean()
        ) if high_risk > 0 else 0
        
        summary = {
            'total_customers': total_customers,
            'churned_customers': churned_customers,
            'churn_rate': round(churn_rate, 2),
            'high_risk_customers': high_risk,
            'medium_risk_customers': medium_risk,
            'low_risk_customers': low_risk,
            'avg_churn_probability': round(avg_churn_prob, 2),
            'high_value_at_risk': vip_at_risk,
            'active_customers': active_customers,
            'inactive_customers': inactive_customers,
            'avg_recency_high_risk': round(avg_recency_high_risk, 1)
        }
        
        return summary
    
    def get_risk_distribution(self):
        """Get distribution of customers by risk level and value segment"""
        if self.predictions is None:
            self.predict_churn()
        
        distribution = self.predictions.groupby(['Risk_Level', 'Value_Segment']).size().reset_index(name='Count')
        
        # Convert to records and handle NaN values
        records = distribution.to_dict('records')
        for record in records:
            for key, value in record.items():
                if isinstance(value, (np.integer, np.int64)):
                    record[key] = int(value)
                elif isinstance(value, (np.floating, np.float64)):
                    if np.isnan(value) or np.isinf(value):
                        record[key] = 0
                    else:
                        record[key] = float(value)
                elif pd.isna(value):
                    record[key] = None
        
        return records
    
    def get_high_risk_customers(self, limit=100):
        """Get list of high-risk customers for intervention"""
        if self.predictions is None:
            self.predict_churn()
        
        high_risk = self.predictions[
            self.predictions['Risk_Level'] == 'High Risk'
        ].sort_values('Churn_Probability', ascending=False).head(limit)
        
        # Convert to records and handle NaN values
        records = high_risk.to_dict('records')
        for record in records:
            for key, value in record.items():
                if isinstance(value, (np.integer, np.int64)):
                    record[key] = int(value)
                elif isinstance(value, (np.floating, np.float64)):
                    if np.isnan(value) or np.isinf(value):
                        record[key] = 0
                    else:
                        record[key] = float(value)
                elif pd.isna(value):
                    record[key] = None
        
        return records
    
    def get_retention_recommendations(self):
        """Generate actionable retention recommendations"""
        if self.predictions is None:
            self.predict_churn()
        
        recommendations = []
        
        # High-value customers at risk
        high_value_risk = ((self.predictions['Value_Segment'].isin(['VIP', 'High Value'])) & 
                          (self.predictions['Risk_Level'] == 'High Risk')).sum()
        
        if high_value_risk > 0:
            recommendations.append({
                'priority': 'critical',
                'segment': 'High-Value at Risk',
                'count': int(high_value_risk),
                'title': 'Critical: High-Value Customers at Risk',
                'message': f'{high_value_risk} high-value customers are at high risk of churning.',
                'action': 'Immediate personalized outreach with exclusive offers and VIP treatment',
                'icon': '🚨'
            })
        
        # Medium risk customers
        medium_risk = (self.predictions['Risk_Level'] == 'Medium Risk').sum()
        if medium_risk > 0:
            recommendations.append({
                'priority': 'high',
                'segment': 'Medium Risk',
                'count': int(medium_risk),
                'title': 'Engagement Opportunity',
                'message': f'{medium_risk} customers showing signs of disengagement.',
                'action': 'Launch re-engagement campaign with targeted promotions',
                'icon': '⚠️'
            })
        
        # Recently churned high spenders
        recent_churn = self.predictions[
            (self.predictions['Is_Churned'] == 1) & 
            (self.predictions['Recency_Days'] < 120) &
            (self.predictions['Total_Spent'] > self.predictions['Total_Spent'].median())
        ]
        
        if len(recent_churn) > 0:
            recommendations.append({
                'priority': 'high',
                'segment': 'Win-Back',
                'count': int(len(recent_churn)),
                'title': 'Win-Back Opportunity',
                'message': f'{len(recent_churn)} valuable customers recently churned.',
                'action': 'Deploy win-back campaign with special incentives',
                'icon': '🎯'
            })
        
        # Low risk but low engagement
        low_engagement = self.predictions[
            (self.predictions['Risk_Level'] == 'Low Risk') & 
            (self.predictions['Unique_Invoices'] < 5)
        ]
        
        if len(low_engagement) > 0:
            recommendations.append({
                'priority': 'medium',
                'segment': 'Low Engagement',
                'count': int(len(low_engagement)),
                'title': 'Increase Engagement',
                'message': f'{len(low_engagement)} customers have low purchase frequency.',
                'action': 'Implement loyalty program and cross-sell campaigns',
                'icon': '📈'
            })
        
        return recommendations
    
    def get_model_performance(self):
        """Get performance metrics for all trained models"""
        if not self.models:
            self.train_models()
        
        performance = []
        for model_name, model_data in self.models.items():
            performance.append({
                'model': model_name.replace('_', ' ').title(),
                'accuracy': float(model_data['accuracy'] * 100)
            })
        
        return performance
    
    def get_feature_importance_data(self, top_n=10):
        """Get top N most important features"""
        if self.feature_importance is None:
            self.train_models()
        
        top_features = self.feature_importance.head(top_n).copy()
        top_features['Importance'] = top_features['Importance'] * 100
        
        # Convert to records and handle NaN values
        records = top_features.to_dict('records')
        for record in records:
            for key, value in record.items():
                if isinstance(value, (np.integer, np.int64)):
                    record[key] = int(value)
                elif isinstance(value, (np.floating, np.float64)):
                    if np.isnan(value) or np.isinf(value):
                        record[key] = 0
                    else:
                        record[key] = float(value)
                elif pd.isna(value):
                    record[key] = None
        
        return records
    
    def get_customer_churn_details(self, customer_id):
        """Get detailed churn prediction for specific customer"""
        if self.predictions is None:
            self.predict_churn()
        
        customer = self.predictions[self.predictions['Customer_ID'] == customer_id]
        
        if len(customer) == 0:
            return None
        
        customer_dict = customer.iloc[0].to_dict()
        
        # Convert numpy types to Python types
        for key, value in customer_dict.items():
            if isinstance(value, (np.integer, np.int64)):
                customer_dict[key] = int(value)
            elif isinstance(value, (np.floating, np.float64)):
                customer_dict[key] = float(value)
        
        return customer_dict

    def initialize_model_comparison(self):
        """Initialize and train model comparison system"""
        if self.customer_features is None:
            self.calculate_customer_features()
        
        X, y, feature_columns = self.prepare_training_data()
        
        # Create model comparison instance
        self.model_comparison = ModelComparison(X, y, feature_columns)
        
        # Train baseline models
        self.model_comparison.train_baseline_models()
        
        return self.model_comparison
    
    def get_baseline_model_comparison(self):
        """Get baseline model comparison results"""
        if self.model_comparison is None:
            self.initialize_model_comparison()
        
        return self.model_comparison.get_baseline_comparison()
    
    def get_tuned_model_comparison(self):
        """Get tuned model comparison results"""
        if self.model_comparison is None:
            self.initialize_model_comparison()
        
        return self.model_comparison.get_tuned_comparison()
    
    def get_full_model_comparison(self):
        """Get complete model comparison (baseline and tuned)"""
        if self.model_comparison is None:
            self.initialize_model_comparison()
        
        return self.model_comparison.get_full_comparison()
    
    def get_model_comparison_summary(self):
        """Get summary of model comparison"""
        if self.model_comparison is None:
            self.initialize_model_comparison()
        
        return self.model_comparison.get_model_comparison_summary()
    
    def get_feature_importance_comparison(self, model_name='xgboost', top_n=15):
        """Get feature importance from specific model"""
        if self.model_comparison is None:
            self.initialize_model_comparison()
        
        return self.model_comparison.get_feature_importance(model_name, top_n)
    
    def get_confusion_matrices_comparison(self):
        """Get confusion matrices for all models"""
        if self.model_comparison is None:
            self.initialize_model_comparison()
        
        return self.model_comparison.get_confusion_matrices()
    
    def get_roc_curves_comparison(self):
        """Get ROC curve data for all models"""
        if self.model_comparison is None:
            self.initialize_model_comparison()
        
        return self.model_comparison.get_roc_curves()
