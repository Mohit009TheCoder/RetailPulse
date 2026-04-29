"""
Routes package - Contains all application blueprints
"""
from app.routes.main import main_bp
from app.routes.rfm import rfm_bp
from app.routes.churn import churn_bp
from app.routes.forecasting import forecasting_bp
from app.routes.model_comparison import model_comparison_bp

__all__ = [
    'main_bp',
    'rfm_bp',
    'churn_bp',
    'forecasting_bp',
    'model_comparison_bp'
]
