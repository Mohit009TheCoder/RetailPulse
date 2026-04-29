"""
Main routes - Dashboard and general pages
"""
from flask import Blueprint, render_template

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html')


@main_bp.route('/segments')
def segments():
    """Segments analysis page"""
    return render_template('segments.html')


@main_bp.route('/customers')
def customers():
    """Customer details page"""
    return render_template('customers.html')


@main_bp.route('/about')
def about():
    """About RFM page"""
    return render_template('about.html')


@main_bp.route('/forecasting')
def forecasting():
    """Demand forecasting page"""
    return render_template('forecasting.html')


@main_bp.route('/advanced-forecasting')
def advanced_forecasting_page():
    """Advanced forecasting page"""
    return render_template('advanced_forecasting.html')


@main_bp.route('/churn-prediction')
def churn_prediction_page():
    """Churn prediction page"""
    return render_template('churn_prediction.html')


@main_bp.route('/model-comparison')
def model_comparison_page():
    """Model comparison page"""
    return render_template('model_comparison.html')
