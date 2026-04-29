import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class RFMAnalysis:
    def __init__(self, data_path='cleandataset.csv'):
        """Initialize RFM Analysis with data"""
        self.df = pd.read_csv(data_path)
        self.rfm_df = None
        self.prepare_data()
    
    def prepare_data(self):
        """Prepare and clean data for RFM analysis"""
        # Convert InvoiceDate to datetime
        self.df['InvoiceDate'] = pd.to_datetime(self.df['InvoiceDate'], format='%m/%d/%Y %H:%M:%S')
        
        # Convert Customer ID to numeric
        self.df['Customer ID'] = pd.to_numeric(self.df['Customer ID'], errors='coerce')
        
        # Remove rows with missing Customer ID
        self.df = self.df.dropna(subset=['Customer ID'])
        
        # Convert Quantity to numeric
        self.df['Quantity'] = pd.to_numeric(self.df['Quantity'], errors='coerce')
        
        # Calculate TotalAmount
        self.df['TotalAmount'] = self.df['Quantity'] * self.df['Price']
        
        # Filter positive quantities and amounts
        self.df = self.df[(self.df['Quantity'] > 0) & (self.df['TotalAmount'] > 0)]
    
    def calculate_rfm(self):
        """Calculate RFM metrics for each customer"""
        # Get the most recent date in the dataset
        snapshot_date = self.df['InvoiceDate'].max() + timedelta(days=1)
        
        # Calculate RFM metrics
        rfm = self.df.groupby('Customer ID').agg({
            'InvoiceDate': lambda x: (snapshot_date - x.max()).days,  # Recency
            'Invoice': 'nunique',  # Frequency
            'TotalAmount': 'sum'  # Monetary
        })
        
        # Rename columns
        rfm.columns = ['Recency', 'Frequency', 'Monetary']
        
        # Calculate RFM scores (1-5, where 5 is best)
        # Use rank-based scoring to handle duplicates better
        rfm['R_Score'] = pd.cut(rfm['Recency'].rank(method='first', pct=True), 
                                bins=5, labels=[5, 4, 3, 2, 1]).astype(int)
        rfm['F_Score'] = pd.cut(rfm['Frequency'].rank(method='first', pct=True), 
                                bins=5, labels=[1, 2, 3, 4, 5]).astype(int)
        rfm['M_Score'] = pd.cut(rfm['Monetary'].rank(method='first', pct=True), 
                                bins=5, labels=[1, 2, 3, 4, 5]).astype(int)
        
        # Calculate RFM Score
        rfm['RFM_Score'] = rfm['R_Score'] + rfm['F_Score'] + rfm['M_Score']
        
        # Assign customer segments
        rfm['Segment'] = rfm.apply(self.assign_segment, axis=1)
        
        # Reset index to make Customer ID a column
        rfm = rfm.reset_index()
        
        self.rfm_df = rfm
        return rfm
    
    def assign_segment(self, row):
        """Assign customer segment based on RFM scores"""
        r, f, m = row['R_Score'], row['F_Score'], row['M_Score']
        
        # Champions: High value, frequent buyers, recent purchases
        if r >= 4 and f >= 4 and m >= 4:
            return 'Champions'
        
        # Loyal Customers: Frequent buyers with good monetary value
        elif r >= 3 and f >= 4:
            return 'Loyal Customers'
        
        # Potential Loyalists: Recent customers with average frequency
        elif r >= 4 and f >= 2 and f <= 3:
            return 'Potential Loyalists'
        
        # New Customers: Recent buyers with low frequency
        elif r >= 4 and f == 1:
            return 'New Customers'
        
        # At Risk: Used to be frequent buyers but haven't purchased recently
        elif r <= 2 and f >= 3:
            return 'At Risk'
        
        # Can't Lose Them: High monetary value but low recency
        elif r <= 2 and m >= 4:
            return "Can't Lose Them"
        
        # Hibernating: Low recency, frequency, and monetary value
        elif r <= 2 and f <= 2:
            return 'Hibernating'
        
        # Promising: Recent buyers with potential
        elif r >= 3 and f >= 2 and m >= 2:
            return 'Promising'
        
        # Need Attention: Below average in all metrics
        else:
            return 'Need Attention'
    
    def get_segment_summary(self):
        """Get summary statistics for each segment"""
        if self.rfm_df is None:
            self.calculate_rfm()
        
        summary = self.rfm_df.groupby('Segment').agg({
            'Customer ID': 'count',
            'Recency': 'mean',
            'Frequency': 'mean',
            'Monetary': 'mean',
            'RFM_Score': 'mean'
        }).round(2)
        
        summary.columns = ['Customer Count', 'Avg Recency', 'Avg Frequency', 'Avg Monetary', 'Avg RFM Score']
        summary = summary.sort_values('Customer Count', ascending=False)
        
        return summary.reset_index()
    
    def get_customer_details(self, customer_id=None, segment=None, limit=100):
        """Get detailed customer information"""
        if self.rfm_df is None:
            self.calculate_rfm()
        
        result = self.rfm_df.copy()
        
        if customer_id:
            result = result[result['Customer ID'] == float(customer_id)]
        
        if segment:
            result = result[result['Segment'] == segment]
        
        return result.head(limit).to_dict('records')
    
    def get_segment_distribution(self):
        """Get segment distribution for visualization"""
        if self.rfm_df is None:
            self.calculate_rfm()
        
        distribution = self.rfm_df['Segment'].value_counts().to_dict()
        return distribution
