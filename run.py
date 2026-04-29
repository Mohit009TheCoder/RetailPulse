"""
RetailPulse - Customer Analytics & Demand Forecasting System
Main application entry point
"""
import os
from app import create_app
from app.routes.rfm import init_rfm_analyzer
from app.routes.churn import init_churn_predictor
from app.routes.forecasting import init_forecasters

# Create application instance
app = create_app(os.getenv('FLASK_ENV', 'development'))


def initialize_models():
    """Initialize all ML models on startup"""
    with app.app_context():
        print("=" * 60)
        print("RetailPulse - Initializing Analytics Models")
        print("=" * 60)
        
        print("\n[1/4] Calculating RFM scores...")
        rfm_analyzer = init_rfm_analyzer()
        print(f"✓ RFM analysis complete! Analyzed {len(rfm_analyzer.rfm_df)} customers")
        
        print("\n[2/4] Preparing forecasting data...")
        demand_forecaster, advanced_forecaster = init_forecasters()
        print("✓ Forecasting data ready!")
        
        print("\n[3/4] Training churn prediction models...")
        churn_predictor = init_churn_predictor()
        print("✓ Churn prediction models trained!")
        
        print("\n[4/4] Initializing ML model comparison system...")
        print("✓ Model comparison ready!")
        
        print("\n" + "=" * 60)
        print("All systems initialized successfully!")
        print("=" * 60)
        print(f"\n🚀 Server starting on http://0.0.0.0:5001")
        print("=" * 60 + "\n")


if __name__ == '__main__':
    # Initialize models before starting server
    initialize_models()
    
    # Run the application
    app.run(
        debug=app.config['DEBUG'],
        host='0.0.0.0',
        port=5001
    )
