"""
Forecasting routes - Demand forecasting and advanced forecasting
"""
from flask import Blueprint, request, jsonify, current_app
import numpy as np
import pandas as pd
from app.models import DemandForecasting, AdvancedEnsembleForecasting

forecasting_bp = Blueprint('forecasting', __name__)

# Initialize forecasters (will be set in run.py)
demand_forecaster = None
advanced_forecaster = None


def init_forecasters():
    """Initialize forecasters with data path from config"""
    global demand_forecaster, advanced_forecaster
    data_path = current_app.config.get('DATA_PATH')
    
    demand_forecaster = DemandForecasting(data_path)
    demand_forecaster.aggregate_daily_sales()
    demand_forecaster.aggregate_product_sales()
    
    advanced_forecaster = AdvancedEnsembleForecasting(data_path)
    advanced_forecaster.aggregate_daily_sales()
    
    return demand_forecaster, advanced_forecaster


@forecasting_bp.route('/generate', methods=['POST'])
def generate_forecast():
    """Generate demand forecasts"""
    try:
        if demand_forecaster is None:
            init_forecasters()
        
        data = request.get_json() or {}
        periods = int(data.get('periods', 30))
        
        forecasts = demand_forecaster.generate_all_forecasts(periods=periods)
        summary = demand_forecaster.get_forecast_summary(periods=periods)
        
        # Convert forecasts to serializable format
        forecast_data = {}
        for method, df in forecasts.items():
            records = df.to_dict('records')
            for record in records:
                if 'Date' in record and isinstance(record['Date'], pd.Timestamp):
                    record['Date'] = record['Date'].strftime('%Y-%m-%d')
                for key, value in record.items():
                    if isinstance(value, (np.integer, np.int64)):
                        record[key] = int(value)
                    elif isinstance(value, (np.floating, np.float64)):
                        record[key] = float(value)
            forecast_data[method] = records
        
        # Convert summary
        summary_records = summary.to_dict('records')
        for record in summary_records:
            for key, value in record.items():
                if isinstance(value, (np.integer, np.int64)):
                    record[key] = int(value)
                elif isinstance(value, (np.floating, np.float64)):
                    record[key] = float(value)
        
        return jsonify({
            'success': True,
            'forecasts': forecast_data,
            'summary': summary_records
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@forecasting_bp.route('/historical')
def get_historical():
    """Get historical sales data"""
    try:
        if demand_forecaster is None:
            init_forecasters()
        
        daily_sales = demand_forecaster.aggregate_daily_sales()
        stats = demand_forecaster.get_historical_stats()
        
        # Convert DataFrame to dict with proper type conversion
        data_records = daily_sales.to_dict('records')
        for record in data_records:
            if 'Date' in record and isinstance(record['Date'], pd.Timestamp):
                record['Date'] = record['Date'].strftime('%Y-%m-%d')
            for key, value in record.items():
                if isinstance(value, (np.integer, np.int64)):
                    record[key] = int(value)
                elif isinstance(value, (np.floating, np.float64)):
                    record[key] = float(value)
        
        return jsonify({
            'success': True,
            'data': data_records,
            'stats': stats
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@forecasting_bp.route('/products')
def get_top_products():
    """Get top products by revenue"""
    try:
        if demand_forecaster is None:
            init_forecasters()
        
        top_n = int(request.args.get('limit', 20))
        products = demand_forecaster.aggregate_product_sales(top_n=top_n)
        
        return jsonify({
            'success': True,
            'data': products.to_dict('records')
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@forecasting_bp.route('/product/<path:product_name>')
def get_product_forecast(product_name):
    """Get forecast for specific product"""
    try:
        if demand_forecaster is None:
            init_forecasters()
        
        periods = int(request.args.get('periods', 30))
        forecast = demand_forecaster.get_product_forecast(product_name, periods=periods)
        
        if forecast is None:
            return jsonify({
                'success': False,
                'message': 'Product not found'
            }), 404
        
        return jsonify({
            'success': True,
            'data': forecast
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@forecasting_bp.route('/accuracy')
def get_forecast_accuracy():
    """Get forecast accuracy metrics"""
    try:
        if demand_forecaster is None:
            init_forecasters()
        
        test_size = int(request.args.get('test_size', 30))
        metrics = demand_forecaster.get_accuracy_metrics(test_size=test_size)
        
        if metrics is None:
            return jsonify({
                'success': False,
                'message': 'Not enough data for accuracy calculation'
            }), 400
        
        return jsonify({
            'success': True,
            'data': metrics.to_dict('records')
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


# Advanced Forecasting Routes
@forecasting_bp.route('/advanced/generate', methods=['POST'])
def generate_advanced_forecast():
    """Generate advanced ensemble forecast"""
    try:
        if advanced_forecaster is None:
            init_forecasters()
        
        data = request.get_json() or {}
        periods = int(data.get('periods', 30))
        
        # Generate comprehensive forecast
        forecast = advanced_forecaster.generate_comprehensive_forecast(periods=periods)
        summary = advanced_forecaster.get_forecast_summary()
        forecast_by_day = advanced_forecaster.get_forecast_by_day()
        
        # Convert forecast DataFrame
        forecast_records = forecast.to_dict('records')
        for record in forecast_records:
            if 'Date' in record and isinstance(record['Date'], pd.Timestamp):
                record['Date'] = record['Date'].strftime('%Y-%m-%d')
            for key, value in record.items():
                if isinstance(value, (np.integer, np.int64)):
                    record[key] = int(value)
                elif isinstance(value, (np.floating, np.float64)):
                    record[key] = float(value)
                elif isinstance(value, dict):
                    for k, v in value.items():
                        if isinstance(v, (np.integer, np.int64)):
                            value[k] = int(v)
                        elif isinstance(v, (np.floating, np.float64)):
                            value[k] = float(v)
        
        # Convert daily forecast
        for record in forecast_by_day:
            if 'Date' in record and isinstance(record['Date'], pd.Timestamp):
                record['Date'] = record['Date'].strftime('%Y-%m-%d')
            for key, value in record.items():
                if isinstance(value, (np.integer, np.int64)):
                    record[key] = int(value)
                elif isinstance(value, (np.floating, np.float64)):
                    record[key] = float(value)
        
        return jsonify({
            'success': True,
            'forecast': forecast_records,
            'summary': summary,
            'daily_forecast': forecast_by_day
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@forecasting_bp.route('/advanced/recommendations')
def get_recommendations():
    """Get business recommendations"""
    try:
        if advanced_forecaster is None:
            init_forecasters()
        
        if not advanced_forecaster.recommendations:
            return jsonify({
                'success': False,
                'message': 'Generate forecast first'
            }), 400
        
        return jsonify({
            'success': True,
            'recommendations': advanced_forecaster.recommendations
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@forecasting_bp.route('/advanced/inventory')
def get_inventory_recommendations():
    """Get inventory recommendations"""
    try:
        if advanced_forecaster is None:
            init_forecasters()
        
        safety_days = int(request.args.get('safety_days', 7))
        recommendations = advanced_forecaster.get_inventory_recommendations(safety_stock_days=safety_days)
        
        if recommendations is None:
            return jsonify({
                'success': False,
                'message': 'Generate forecast first'
            }), 400
        
        return jsonify({
            'success': True,
            'data': recommendations
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500
