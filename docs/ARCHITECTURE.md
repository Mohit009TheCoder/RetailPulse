# RetailPulse Architecture Documentation

## System Overview

RetailPulse is a Flask-based web application that provides comprehensive customer analytics, churn prediction, and demand forecasting capabilities.

## Architecture Pattern

The application follows the **Blueprint Pattern** with a modular architecture:

```
┌─────────────────────────────────────────────────────────┐
│                     Flask Application                    │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │   Main BP    │  │   RFM BP     │  │  Churn BP    │ │
│  │  (Pages)     │  │  (API)       │  │  (API)       │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
│                                                          │
│  ┌──────────────┐  ┌──────────────┐                    │
│  │Forecasting BP│  │Model Comp BP │                    │
│  │  (API)       │  │  (API)       │                    │
│  └──────────────┘  └──────────────┘                    │
│                                                          │
├─────────────────────────────────────────────────────────┤
│                     Models Layer                         │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │ RFM Analysis │  │    Churn     │  │  Forecasting │ │
│  │              │  │  Prediction  │  │              │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
│                                                          │
│  ┌──────────────┐  ┌──────────────┐                    │
│  │  Advanced    │  │    Model     │                    │
│  │ Forecasting  │  │  Comparison  │                    │
│  └──────────────┘  └──────────────┘                    │
│                                                          │
├─────────────────────────────────────────────────────────┤
│                      Data Layer                          │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │              CSV Data Files                       │  │
│  │  - cleandataset.csv (processed)                  │  │
│  │  - Raw data files                                │  │
│  └──────────────────────────────────────────────────┘  │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

## Component Details

### 1. Application Factory (`app/__init__.py`)

- Creates and configures Flask application
- Registers all blueprints
- Sets up custom JSON encoder for numpy/pandas types
- Loads configuration

### 2. Blueprints (Routes)

#### Main Blueprint (`app/routes/main.py`)
- Serves HTML pages
- No business logic
- Routes: `/`, `/segments`, `/customers`, `/about`, etc.

#### RFM Blueprint (`app/routes/rfm.py`)
- RFM analysis endpoints
- Customer segmentation
- Prefix: `/api`

#### Churn Blueprint (`app/routes/churn.py`)
- Churn prediction endpoints
- Risk analysis
- Retention recommendations
- Prefix: `/api/churn`

#### Forecasting Blueprint (`app/routes/forecasting.py`)
- Demand forecasting
- Advanced ensemble forecasting
- Inventory recommendations
- Prefix: `/api/forecast`

#### Model Comparison Blueprint (`app/routes/model_comparison.py`)
- ML model comparison
- Performance metrics
- Feature importance
- Prefix: `/api/model-comparison`

### 3. Models Layer

#### RFM Analysis (`app/models/rfm_analysis.py`)
- Customer segmentation using RFM methodology
- Calculates Recency, Frequency, Monetary scores
- Assigns customers to segments

#### Churn Prediction (`app/models/churn_prediction.py`)
- Predicts customer churn probability
- Uses Random Forest, Gradient Boosting, Logistic Regression
- Provides risk levels and recommendations

#### Demand Forecasting (`app/models/demand_forecasting.py`)
- Time series forecasting
- Methods: Moving Average, Exponential Smoothing, ARIMA
- Product-level forecasts

#### Advanced Forecasting (`app/models/advanced_forecasting.py`)
- Ensemble forecasting
- Business recommendations
- Inventory optimization

#### Model Comparison (`app/models/model_comparison.py`)
- Compares multiple ML models
- Hyperparameter tuning
- Performance metrics (accuracy, precision, recall, F1, ROC-AUC)

### 4. Configuration (`config.py`)

- Environment-specific settings
- Development, Production, Testing configs
- Data paths and application settings

### 5. Entry Point (`run.py`)

- Application startup
- Model initialization
- Server configuration

## Data Flow

### Request Flow
```
Client Request
    ↓
Flask Router
    ↓
Blueprint Route Handler
    ↓
Model Method Call
    ↓
Data Processing
    ↓
JSON Response
    ↓
Client
```

### Model Initialization Flow
```
Application Start
    ↓
run.py
    ↓
Initialize Models
    ├─→ RFM Analyzer
    ├─→ Churn Predictor
    ├─→ Demand Forecaster
    └─→ Advanced Forecaster
    ↓
Load & Process Data
    ↓
Train ML Models
    ↓
Ready to Serve Requests
```

## Technology Stack

### Backend
- **Flask**: Web framework
- **Pandas**: Data manipulation
- **NumPy**: Numerical computing
- **Scikit-learn**: Machine learning
- **XGBoost**: Gradient boosting

### Frontend
- **HTML5/CSS3**: Structure and styling
- **JavaScript**: Interactivity
- **Chart.js**: Data visualization
- **Fetch API**: AJAX requests

## Design Patterns

1. **Application Factory Pattern**: Flexible app creation
2. **Blueprint Pattern**: Modular route organization
3. **Singleton Pattern**: Model instances
4. **Repository Pattern**: Data access abstraction

## Security Considerations

- Input validation on all endpoints
- Error handling with proper HTTP status codes
- No sensitive data in responses
- CORS configuration for production
- Environment-based configuration

## Performance Optimization

- Model initialization on startup (not per request)
- Efficient data processing with pandas
- Caching of computed results
- Lazy loading of large datasets

## Scalability

- Stateless API design
- Horizontal scaling capability
- Database-ready architecture (currently CSV-based)
- Microservices-ready blueprint structure

## Future Enhancements

1. Database integration (PostgreSQL/MongoDB)
2. User authentication and authorization
3. Real-time data updates with WebSockets
4. Caching layer (Redis)
5. API rate limiting
6. Containerization (Docker)
7. CI/CD pipeline
8. Comprehensive test coverage
