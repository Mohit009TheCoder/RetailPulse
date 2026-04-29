"""
RFM Analysis routes
"""
from flask import Blueprint, request, jsonify, current_app
from app.models import RFMAnalysis

rfm_bp = Blueprint('rfm', __name__)

# Initialize RFM analyzer (will be set in run.py)
rfm_analyzer = None


def init_rfm_analyzer():
    """Initialize RFM analyzer with data path from config"""
    global rfm_analyzer
    data_path = current_app.config.get('DATA_PATH')
    rfm_analyzer = RFMAnalysis(data_path)
    rfm_analyzer.calculate_rfm()
    return rfm_analyzer


@rfm_bp.route('/calculate-rfm', methods=['POST'])
def calculate_rfm():
    """Calculate RFM scores"""
    try:
        if rfm_analyzer is None:
            init_rfm_analyzer()
        
        rfm_df = rfm_analyzer.calculate_rfm()
        return jsonify({
            'success': True,
            'message': 'RFM analysis completed successfully',
            'total_customers': len(rfm_df)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@rfm_bp.route('/segment-summary')
def segment_summary():
    """Get segment summary statistics"""
    try:
        if rfm_analyzer is None:
            init_rfm_analyzer()
        
        summary = rfm_analyzer.get_segment_summary()
        return jsonify({
            'success': True,
            'data': summary.to_dict('records')
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@rfm_bp.route('/segment-distribution')
def segment_distribution():
    """Get segment distribution for charts"""
    try:
        if rfm_analyzer is None:
            init_rfm_analyzer()
        
        distribution = rfm_analyzer.get_segment_distribution()
        return jsonify({
            'success': True,
            'data': distribution
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@rfm_bp.route('/customers')
def get_customers():
    """Get customer details with optional filters"""
    try:
        if rfm_analyzer is None:
            init_rfm_analyzer()
        
        customer_id = request.args.get('customer_id')
        segment = request.args.get('segment')
        limit = int(request.args.get('limit', 100))
        
        customers = rfm_analyzer.get_customer_details(
            customer_id=customer_id,
            segment=segment,
            limit=limit
        )
        
        return jsonify({
            'success': True,
            'data': customers,
            'count': len(customers)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500
