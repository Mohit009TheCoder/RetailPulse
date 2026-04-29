#!/usr/bin/env python3
"""
Test RFM Analysis Module
"""

from rfm_analysis import RFMAnalysis
import pandas as pd

def test_rfm_analysis():
    """Test the RFM analysis functionality"""
    print("=" * 60)
    print("Testing RFM Analysis Module")
    print("=" * 60)
    print()
    
    try:
        # Initialize RFM Analysis
        print("📊 Loading data...")
        rfm = RFMAnalysis('cleandataset.csv')
        print(f"✅ Data loaded: {len(rfm.df)} transactions")
        print()
        
        # Calculate RFM
        print("🔢 Calculating RFM scores...")
        rfm_df = rfm.calculate_rfm()
        print(f"✅ RFM calculated for {len(rfm_df)} customers")
        print()
        
        # Get segment summary
        print("📈 Generating segment summary...")
        summary = rfm.get_segment_summary()
        print("✅ Segment Summary:")
        print(summary.to_string(index=False))
        print()
        
        # Get segment distribution
        print("📊 Segment Distribution:")
        distribution = rfm.get_segment_distribution()
        for segment, count in sorted(distribution.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / len(rfm_df)) * 100
            print(f"  {segment:.<30} {count:>6} ({percentage:>5.1f}%)")
        print()
        
        # Sample customers from each segment
        print("👥 Sample Customers by Segment:")
        for segment in distribution.keys():
            customers = rfm.get_customer_details(segment=segment, limit=3)
            if customers:
                print(f"\n  {segment}:")
                for i, customer in enumerate(customers[:3], 1):
                    print(f"    {i}. Customer {int(customer['Customer ID'])} - "
                          f"R:{customer['R_Score']} F:{customer['F_Score']} M:{customer['M_Score']} "
                          f"(RFM: {customer['RFM_Score']})")
        print()
        
        # Statistics
        print("📊 Overall Statistics:")
        print(f"  Total Customers: {len(rfm_df):,}")
        print(f"  Total Segments: {len(distribution)}")
        print(f"  Avg Recency: {rfm_df['Recency'].mean():.1f} days")
        print(f"  Avg Frequency: {rfm_df['Frequency'].mean():.1f} purchases")
        print(f"  Avg Monetary: ${rfm_df['Monetary'].mean():,.2f}")
        print(f"  Avg RFM Score: {rfm_df['RFM_Score'].mean():.2f}")
        print()
        
        print("=" * 60)
        print("✅ All tests passed successfully!")
        print("=" * 60)
        print()
        print("🚀 Ready to run the Flask application!")
        print("   Run: python3 app.py")
        print("   Then open: http://localhost:5000")
        print()
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_rfm_analysis()
    exit(0 if success else 1)
