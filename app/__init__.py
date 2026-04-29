"""
RetailPulse - Customer Analytics & Demand Forecasting System
Main application factory
"""
from flask import Flask
import json
import numpy as np
import pandas as pd


class NumpyEncoder(json.JSONEncoder):
    """Custom JSON encoder to handle numpy/pandas types"""
    def default(self, obj):
        if isinstance(obj, (np.integer, np.int64)):
            return int(obj)
        elif isinstance(obj, (np.floating, np.float64)):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, pd.Timestamp):
            return obj.strftime('%Y-%m-%d')
        return super(NumpyEncoder, self).default(obj)


def create_app(config_name='default'):
    """Application factory pattern"""
    app = Flask(__name__)
    app.json_encoder = NumpyEncoder
    
    # Load configuration
    from config import config
    app.config.from_object(config[config_name])
    
    # Register blueprints
    from app.routes import main_bp, rfm_bp, churn_bp, forecasting_bp, model_comparison_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(rfm_bp, url_prefix='/api')
    app.register_blueprint(churn_bp, url_prefix='/api/churn')
    app.register_blueprint(forecasting_bp, url_prefix='/api/forecast')
    app.register_blueprint(model_comparison_bp, url_prefix='/api/model-comparison')
    
    return app
