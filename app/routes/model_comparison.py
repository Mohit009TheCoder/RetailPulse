"""
Model Comparison routes
"""
from flask import Blueprint, request, jsonify
from app.routes.churn import get_churn_predictor

model_comparison_bp = Blueprint('model_comparison', __name__)


@model_comparison_bp.route('/baseline')
def get_baseline_comparison():
    """Get baseline model comparison"""
    try:
        predictor = get_churn_predictor()
        comparison = predictor.get_baseline_model_comparison()
        return jsonify({
            'success': True,
            'data': comparison
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@model_comparison_bp.route('/tuned')
def get_tuned_comparison():
    """Get tuned model comparison"""
    try:
        predictor = get_churn_predictor()
        comparison = predictor.get_tuned_model_comparison()
        return jsonify({
            'success': True,
            'data': comparison
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@model_comparison_bp.route('/full')
def get_full_comparison():
    """Get full model comparison (baseline and tuned)"""
    try:
        predictor = get_churn_predictor()
        comparison = predictor.get_full_model_comparison()
        return jsonify({
            'success': True,
            'data': comparison
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@model_comparison_bp.route('/summary')
def get_comparison_summary():
    """Get model comparison summary"""
    try:
        predictor = get_churn_predictor()
        summary = predictor.get_model_comparison_summary()
        return jsonify({
            'success': True,
            'data': summary
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@model_comparison_bp.route('/feature-importance')
def get_comparison_feature_importance():
    """Get feature importance from model comparison"""
    try:
        predictor = get_churn_predictor()
        model_name = request.args.get('model', 'xgboost')
        top_n = int(request.args.get('top_n', 15))
        
        importance = predictor.get_feature_importance_comparison(model_name, top_n)
        
        if importance is None:
            return jsonify({
                'success': False,
                'message': f'Model {model_name} not found or does not support feature importance'
            }), 404
        
        return jsonify({
            'success': True,
            'data': importance
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@model_comparison_bp.route('/confusion-matrices')
def get_comparison_confusion_matrices():
    """Get confusion matrices for all models"""
    try:
        predictor = get_churn_predictor()
        matrices = predictor.get_confusion_matrices_comparison()
        return jsonify({
            'success': True,
            'data': matrices
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@model_comparison_bp.route('/roc-curves')
def get_comparison_roc_curves():
    """Get ROC curve data for all models"""
    try:
        predictor = get_churn_predictor()
        roc_data = predictor.get_roc_curves_comparison()
        return jsonify({
            'success': True,
            'data': roc_data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500
