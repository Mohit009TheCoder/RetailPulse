# Project Structure Documentation

## Complete Directory Tree

```
retailpulse/
│
├── app/                          # Main application package
│   ├── __init__.py              # Application factory
│   │
│   ├── models/                  # Business logic & ML models
│   │   ├── __init__.py
│   │   ├── rfm_analysis.py      # RFM segmentation
│   │   ├── churn_prediction.py  # Churn prediction models
│   │   ├── demand_forecasting.py # Demand forecasting
│   │   ├── advanced_forecasting.py # Advanced ensemble forecasting
│   │   └── model_comparison.py  # ML model comparison
│   │
│   ├── routes/                  # API endpoints (Blueprints)
│   │   ├── __init__.py
│   │   ├── main.py             # Main page routes
│   │   ├── rfm.py              # RFM API endpoints
│   │   ├── churn.py            # Churn prediction endpoints
│   │   ├── forecasting.py      # Forecasting endpoints
│   │   └── model_comparison.py # Model comparison endpoints
│   │
│   ├── static/                  # Static assets
│   │   ├── css/
│   │   │   └── style.css       # Main stylesheet
│   │   └── js/
│   │       ├── main.js         # Common utilities
│   │       ├── dashboard.js    # Dashboard functionality
│   │       ├── segments.js     # Segments page
│   │       ├── customers.js    # Customers page
│   │       ├── churn_prediction.js # Churn page
│   │       ├── forecasting.js  # Forecasting page
│   │       ├── advanced_forecasting.js # Advanced forecasting
│   │       └── model_comparison.js # Model comparison
│   │
│   ├── templates/               # HTML templates
│   │   ├── base.html           # Base template
│   │   ├── index.html          # Dashboard
│   │   ├── segments.html       # Customer segments
│   │   ├── customers.html      # Customer details
│   │   ├── churn_prediction.html # Churn prediction
│   │   ├── forecasting.html    # Demand forecasting
│   │   ├── advanced_forecasting.html # Advanced forecasting
│   │   ├── model_comparison.html # Model comparison
│   │   └── about.html          # About page
│   │
│   └── utils/                   # Utility functions
│       ├── __init__.py
│       └── helpers.py          # Helper functions
│
├── data/                        # Data directory
│   ├── raw/                    # Raw data files
│   │   ├── 1.csv
│   │   └── 2.csv
│   └── processed/              # Processed datasets
│       └── cleandataset.csv    # Main dataset
│
├── tests/                       # Test suite
│   ├── __init__.py
│   ├── test_rfm.py            # RFM tests
│   └── verify_setup.py        # Setup verification
│
├── docs/                        # Documentation
│   ├── ARCHITECTURE.md         # System architecture
│   ├── DEPLOYMENT.md           # Deployment guide
│   ├── PROJECT_STRUCTURE.md    # This file
│   ├── data.ipynb             # Data exploration notebook
│   └── LOADER_DEMO.html       # Loader demo (archived)
│
├── config.py                    # Configuration settings
├── run.py                       # Application entry point
├── start.sh                     # Startup script
├── requirements.txt             # Python dependencies
├── .gitignore                  # Git ignore rules
└── README.md                    # Project documentation
```

## Directory Purposes

### `/app` - Application Package
The main application code organized by function.

**Key Files:**
- `__init__.py`: Application factory that creates and configures Flask app
- Imports and registers all blueprints
- Sets up custom JSON encoder

### `/app/models` - Business Logic Layer
Contains all ML models and analytics logic.

**Responsibilities:**
- Data processing and transformation
- ML model training and prediction
- Business calculations (RFM, churn, forecasting)
- No HTTP/request handling

**Files:**
- `rfm_analysis.py`: Customer segmentation using RFM methodology
- `churn_prediction.py`: Churn prediction with multiple ML models
- `demand_forecasting.py`: Time series forecasting
- `advanced_forecasting.py`: Ensemble forecasting with recommendations
- `model_comparison.py`: ML model comparison and tuning

### `/app/routes` - API Layer
Flask blueprints that handle HTTP requests/responses.

**Responsibilities:**
- Route definitions
- Request validation
- Response formatting
- Calling model methods
- Error handling

**Files:**
- `main.py`: Page rendering routes
- `rfm.py`: RFM analysis API
- `churn.py`: Churn prediction API
- `forecasting.py`: Forecasting API
- `model_comparison.py`: Model comparison API

### `/app/static` - Static Assets
Frontend resources served directly by Flask.

**Structure:**
- `/css`: Stylesheets
- `/js`: JavaScript files

**JavaScript Organization:**
- `main.js`: Common utilities (API calls, formatting, notifications)
- Page-specific JS files for each feature

### `/app/templates` - HTML Templates
Jinja2 templates for rendering pages.

**Structure:**
- `base.html`: Base template with navbar, footer
- Feature-specific templates extend base

### `/app/utils` - Utility Functions
Reusable helper functions.

**Current:**
- `helpers.py`: Formatting functions

**Future:**
- Validation functions
- Data transformation utilities
- Common calculations

### `/data` - Data Storage
Organized data files.

**Structure:**
- `/raw`: Original, unprocessed data
- `/processed`: Cleaned, ready-to-use data

### `/tests` - Test Suite
Unit and integration tests.

**Organization:**
- Test files mirror app structure
- `test_*.py` naming convention

### `/docs` - Documentation
Project documentation and guides.

**Files:**
- `ARCHITECTURE.md`: System design
- `DEPLOYMENT.md`: Deployment instructions
- `PROJECT_STRUCTURE.md`: This file
- Jupyter notebooks for analysis

## File Naming Conventions

### Python Files
- `snake_case.py` for all Python files
- `test_*.py` for test files
- `__init__.py` for package initialization

### JavaScript Files
- `snake_case.js` for all JS files
- Match corresponding Python module names

### HTML Templates
- `snake_case.html` for all templates
- Match route names

### CSS Files
- `style.css` for main stylesheet
- `component_name.css` for component-specific styles

## Import Patterns

### Within App Package
```python
# Absolute imports from app root
from app.models import RFMAnalysis
from app.utils import format_currency
```

### In Routes
```python
# Import models
from app.models import ChurnPrediction

# Import Flask utilities
from flask import Blueprint, jsonify, request
```

### In Models
```python
# Standard library
import pandas as pd
import numpy as np

# Third-party
from sklearn.ensemble import RandomForestClassifier

# Local (if needed)
from app.utils import helpers
```

## Configuration Management

### Environment-Based Config
```python
# config.py
class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False
```

### Usage
```python
# run.py
app = create_app(os.getenv('FLASK_ENV', 'development'))
```

## Blueprint Registration

### In `app/__init__.py`
```python
from app.routes import main_bp, rfm_bp, churn_bp

app.register_blueprint(main_bp)
app.register_blueprint(rfm_bp, url_prefix='/api')
app.register_blueprint(churn_bp, url_prefix='/api/churn')
```

## Static File URLs

### In Templates
```html
<link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
<script src="{{ url_for('static', filename='js/main.js') }}"></script>
```

### In JavaScript
```javascript
// Relative paths work fine
fetch('/api/churn/summary')
```

## Data Flow Example

### Request: Get Churn Summary

1. **Client**: `GET /api/churn/summary`
2. **Flask Router**: Routes to `churn_bp`
3. **Route Handler**: `app/routes/churn.py::get_churn_summary()`
4. **Model Call**: `churn_predictor.get_churn_summary()`
5. **Model Logic**: `app/models/churn_prediction.py::get_churn_summary()`
6. **Data Processing**: Calculate metrics from predictions
7. **Response**: JSON with summary data
8. **Client**: Receives and displays data

## Best Practices

### 1. Separation of Concerns
- Routes handle HTTP, not business logic
- Models handle business logic, not HTTP
- Utils are pure functions

### 2. Single Responsibility
- Each file has one clear purpose
- Each function does one thing well

### 3. DRY (Don't Repeat Yourself)
- Common code in utils
- Shared templates extend base
- Reusable components

### 4. Explicit is Better Than Implicit
- Clear import statements
- Descriptive variable names
- Type hints where helpful

### 5. Error Handling
- Try-except in route handlers
- Proper HTTP status codes
- Meaningful error messages

## Adding New Features

### 1. Create Model
```python
# app/models/new_feature.py
class NewFeature:
    def __init__(self, data_path):
        # Initialize
        pass
    
    def analyze(self):
        # Business logic
        pass
```

### 2. Create Routes
```python
# app/routes/new_feature.py
from flask import Blueprint
from app.models import NewFeature

new_feature_bp = Blueprint('new_feature', __name__)

@new_feature_bp.route('/analyze')
def analyze():
    # Handle request
    pass
```

### 3. Register Blueprint
```python
# app/__init__.py
from app.routes import new_feature_bp
app.register_blueprint(new_feature_bp, url_prefix='/api/new-feature')
```

### 4. Create Frontend
```javascript
// app/static/js/new_feature.js
async function loadData() {
    const data = await apiCall('/api/new-feature/analyze');
    // Handle data
}
```

### 5. Create Template
```html
<!-- app/templates/new_feature.html -->
{% extends "base.html" %}
{% block content %}
<!-- Page content -->
{% endblock %}
```

## Migration from Old Structure

### Old Structure Issues
- All code in root directory
- No separation of concerns
- Hard to maintain and scale
- Difficult to test

### New Structure Benefits
- Clear organization
- Easy to find code
- Scalable architecture
- Testable components
- Professional structure
