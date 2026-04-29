# RetailPulse - Customer Analytics & Demand Forecasting System

A comprehensive Flask-based web application for customer analytics, RFM segmentation, churn prediction, and demand forecasting using machine learning.

## 🚀 Features

- **RFM Analysis**: Customer segmentation based on Recency, Frequency, and Monetary value
- **Churn Prediction**: AI-powered prediction to identify at-risk customers
- **Demand Forecasting**: Multiple forecasting methods (Moving Average, Exponential Smoothing, ARIMA)
- **Advanced Forecasting**: Ensemble forecasting with business recommendations
- **Model Comparison**: Compare multiple ML models with detailed metrics
- **Interactive Dashboard**: Real-time visualizations and analytics

## 📁 Project Structure

```
retailpulse/
├── app/
│   ├── __init__.py              # Application factory
│   ├── models/                  # ML models and analytics
│   │   ├── __init__.py
│   │   ├── rfm_analysis.py
│   │   ├── churn_prediction.py
│   │   ├── demand_forecasting.py
│   │   ├── advanced_forecasting.py
│   │   └── model_comparison.py
│   ├── routes/                  # API endpoints (Blueprints)
│   │   ├── __init__.py
│   │   ├── main.py             # Main pages
│   │   ├── rfm.py              # RFM endpoints
│   │   ├── churn.py            # Churn prediction endpoints
│   │   ├── forecasting.py      # Forecasting endpoints
│   │   └── model_comparison.py # Model comparison endpoints
│   ├── static/                  # CSS, JS, images
│   │   ├── css/
│   │   └── js/
│   ├── templates/               # HTML templates
│   └── utils/                   # Helper functions
│       ├── __init__.py
│       └── helpers.py
├── data/
│   ├── raw/                     # Raw data files
│   └── processed/               # Processed datasets
│       └── cleandataset.csv
├── tests/                       # Unit tests
├── docs/                        # Documentation
├── config.py                    # Configuration settings
├── run.py                       # Application entry point
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

## 🛠️ Installation

### Prerequisites

- Python 3.8+
- pip

### Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd retailpulse
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Prepare data**
   - Place your dataset in `data/processed/cleandataset.csv`
   - Or update the `DATA_PATH` in `config.py`

## 🚀 Running the Application

### Development Mode

```bash
python run.py
```

The application will be available at `http://localhost:5001`

### Production Mode

```bash
export FLASK_ENV=production
python run.py
```

## 📊 API Endpoints

### RFM Analysis
- `POST /api/calculate-rfm` - Calculate RFM scores
- `GET /api/segment-summary` - Get segment statistics
- `GET /api/segment-distribution` - Get segment distribution
- `GET /api/customers` - Get customer details

### Churn Prediction
- `GET /api/churn/summary` - Get churn summary
- `GET /api/churn/predictions` - Get all predictions
- `GET /api/churn/high-risk` - Get high-risk customers
- `GET /api/churn/recommendations` - Get retention recommendations
- `GET /api/churn/risk-distribution` - Get risk distribution
- `GET /api/churn/model-performance` - Get model metrics
- `GET /api/churn/feature-importance` - Get feature importance

### Forecasting
- `POST /api/forecast/generate` - Generate forecasts
- `GET /api/forecast/historical` - Get historical data
- `GET /api/forecast/products` - Get top products
- `GET /api/forecast/accuracy` - Get accuracy metrics
- `POST /api/forecast/advanced/generate` - Advanced forecasting
- `GET /api/forecast/advanced/recommendations` - Business recommendations
- `GET /api/forecast/advanced/inventory` - Inventory recommendations

### Model Comparison
- `GET /api/model-comparison/baseline` - Baseline models
- `GET /api/model-comparison/tuned` - Tuned models
- `GET /api/model-comparison/full` - Full comparison
- `GET /api/model-comparison/summary` - Comparison summary
- `GET /api/model-comparison/feature-importance` - Feature importance
- `GET /api/model-comparison/confusion-matrices` - Confusion matrices
- `GET /api/model-comparison/roc-curves` - ROC curves

## 🧪 Testing

```bash
python -m pytest tests/
```

## 📝 Configuration

Edit `config.py` to customize:
- Data paths
- Debug mode
- Secret keys
- Other application settings

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

MIT License allows you to:
- ✅ Use commercially
- ✅ Modify
- ✅ Distribute
- ✅ Private use

## 👥 Authors

- RetailPulse Team

## 🙏 Acknowledgments

- Flask framework
- Scikit-learn
- Pandas & NumPy
- Chart.js for visualizations
# RetailPulse
