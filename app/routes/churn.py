"""
Churn Prediction routes
"""
from flask import Blueprint, request, jsonify, current_app
import numpy as np
import pandas as pd
from app.models import ChurnPrediction

churn_bp = Blueprint('churn', __name__)

# Initialize churn predictor (will be set in run.py)
churn_predictor = None


def init_churn_predictor():
    """Initialize churn predictor with data path from config"""
    global churn_predictor
    data_path = current_app.config.get('DATA_PATH')
    churn_predictor = ChurnPrediction(data_path)
    churn_predictor.calculate_customer_features()
    churn_predictor.train_models()
    churn_predictor.initialize_model_comparison()
    return churn_predictor


def get_churn_predictor():
    """Get the churn predictor instance, initializing if needed"""
    global churn_predictor
    if churn_predictor is None:
        init_churn_predictor()
    return churn_predictor

@churn_bp.route('/summary')
def get_churn_summary():
    """Get churn prediction summary"""
    try:
        if churn_predictor is None:
            init_churn_predictor()
        
        summary = churn_predictor.get_churn_summary()
        return jsonify({
            'success': True,
            'data': summary
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@churn_bp.route('/predictions')
def get_churn_predictions():
    """Get churn predictions for all customers"""
    try:
        if churn_predictor is None:
            init_churn_predictor()
        
        limit = int(request.args.get('limit', 1000))
        predictions = churn_predictor.predict_churn()
        
        # Convert to records and limit
        records = predictions.head(limit).to_dict('records')
        
        # Convert numpy types and handle NaN
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
        
        return jsonify({
            'success': True,
            'data': records,
            'total': len(predictions)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@churn_bp.route('/high-risk')
def get_high_risk_customers():
    """Get high-risk customers"""
    try:
        if churn_predictor is None:
            init_churn_predictor()
        
        limit = int(request.args.get('limit', 100))
        high_risk = churn_predictor.get_high_risk_customers(limit=limit)
        
        return jsonify({
            'success': True,
            'data': high_risk
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@churn_bp.route('/recommendations')
def get_churn_recommendations():
    """Get retention recommendations"""
    try:
        if churn_predictor is None:
            init_churn_predictor()
        
        recommendations = churn_predictor.get_retention_recommendations()
        
        return jsonify({
            'success': True,
            'data': recommendations
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@churn_bp.route('/risk-distribution')
def get_risk_distribution():
    """Get risk distribution by value segment"""
    try:
        if churn_predictor is None:
            init_churn_predictor()
        
        distribution = churn_predictor.get_risk_distribution()
        
        return jsonify({
            'success': True,
            'data': distribution
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@churn_bp.route('/model-performance')
def get_churn_model_performance():
    """Get model performance metrics"""
    try:
        if churn_predictor is None:
            init_churn_predictor()
        
        performance = churn_predictor.get_model_performance()
        
        return jsonify({
            'success': True,
            'data': performance
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@churn_bp.route('/feature-importance')
def get_churn_feature_importance():
    """Get feature importance"""
    try:
        if churn_predictor is None:
            init_churn_predictor()
        
        top_n = int(request.args.get('top_n', 10))
        features = churn_predictor.get_feature_importance_data(top_n=top_n)
        
        return jsonify({
            'success': True,
            'data': features
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@churn_bp.route('/customer/<customer_id>')
def get_customer_churn_details(customer_id):
    """Get churn details for specific customer"""
    try:
        if churn_predictor is None:
            init_churn_predictor()
        
        details = churn_predictor.get_customer_churn_details(float(customer_id))
        
        if details is None:
            return jsonify({
                'success': False,
                'message': 'Customer not found'
            }), 404
        
        return jsonify({
            'success': True,
            'data': details
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500
