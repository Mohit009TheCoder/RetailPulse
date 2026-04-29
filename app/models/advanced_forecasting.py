import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

class AdvancedEnsembleForecasting:
    def __init__(self, data_path='cleandataset.csv'):
        """Initialize Advanced Ensemble Forecasting System"""
        self.df = pd.read_csv(data_path)
        self.daily_sales = None
        self.product_sales = None
        self.forecast_results = {}
        self.confidence_intervals = {}
        self.recommendations = []
        self.prepare_data()
    
    def prepare_data(self):
        """Prepare and clean data for forecasting"""
        # Convert InvoiceDate to datetime
        self.df['InvoiceDate'] = pd.to_datetime(self.df['InvoiceDate'], format='%m/%d/%Y %H:%M:%S')
        
        # Convert Quantity to numeric
        self.df['Quantity'] = pd.to_numeric(self.df['Quantity'], errors='coerce')
        
        # Calculate TotalAmount
        self.df['TotalAmount'] = self.df['Quantity'] * self.df['Price']
        
        # Filter positive quantities and amounts
        self.df = self.df[(self.df['Quantity'] > 0) & (self.df['TotalAmount'] > 0)]
        
        # Extract date
        self.df['Date'] = self.df['InvoiceDate'].dt.date
    
    def aggregate_daily_sales(self):
        """Aggregate sales by day with additional metrics"""
        daily = self.df.groupby('Date').agg({
            'Quantity': 'sum',
            'TotalAmount': 'sum',
            'Invoice': 'nunique',
            'Customer ID': 'nunique'
        }).reset_index()
        
        daily.columns = ['Date', 'Total_Quantity', 'Total_Revenue', 'Total_Orders', 'Unique_Customers']
        daily['Date'] = pd.to_datetime(daily['Date'])
        daily = daily.sort_values('Date')
        
        # Fill missing dates
        date_range = pd.date_range(start=daily['Date'].min(), end=daily['Date'].max(), freq='D')
        daily = daily.set_index('Date').reindex(date_range, fill_value=0).reset_index()
        daily.columns = ['Date', 'Total_Quantity', 'Total_Revenue', 'Total_Orders', 'Unique_Customers']
        
        # Add derived features
        daily['Day_of_Week'] = daily['Date'].dt.dayofweek
        daily['Day_Name'] = daily['Date'].dt.day_name()
        daily['Month'] = daily['Date'].dt.month
        daily['Quarter'] = daily['Date'].dt.quarter
        daily['Is_Weekend'] = daily['Day_of_Week'].isin([5, 6]).astype(int)
        
        # Calculate moving averages
        daily['MA_7'] = daily['Total_Quantity'].rolling(window=7, min_periods=1).mean()
        daily['MA_30'] = daily['Total_Quantity'].rolling(window=30, min_periods=1).mean()
        
        # Calculate volatility
        daily['Volatility'] = daily['Total_Quantity'].rolling(window=7, min_periods=1).std()
        
        self.daily_sales = daily
        return daily
    
    def moving_average_forecast(self, data, window=7, periods=30):
        """Enhanced Moving Average with confidence intervals"""
        ma = data['Total_Quantity'].rolling(window=window).mean()
        std = data['Total_Quantity'].rolling(window=window).std()
        
        last_ma = ma.iloc[-1]
        last_std = std.iloc[-1]
        
        forecast_dates = pd.date_range(
            start=data['Date'].max() + timedelta(days=1),
            periods=periods,
            freq='D'
        )
        
        forecast_values = [last_ma] * periods
        lower_bound = [last_ma - 1.96 * last_std] * periods
        upper_bound = [last_ma + 1.96 * last_std] * periods
        
        return pd.DataFrame({
            'Date': forecast_dates,
            'Forecast': forecast_values,
            'Lower_Bound': lower_bound,
            'Upper_Bound': upper_bound,
            'Method': 'Moving Average'
        })
    
    def exponential_smoothing_forecast(self, data, alpha=0.3, periods=30):
        """Enhanced Exponential Smoothing with trend"""
        values = data['Total_Quantity'].values
        
        # Double exponential smoothing (Holt's method)
        level = [values[0]]
        trend = [values[1] - values[0]]
        
        beta = 0.1  # Trend smoothing parameter
        
        for i in range(1, len(values)):
            level.append(alpha * values[i] + (1 - alpha) * (level[i-1] + trend[i-1]))
            trend.append(beta * (level[i] - level[i-1]) + (1 - beta) * trend[i-1])
        
        last_level = level[-1]
        last_trend = trend[-1]
        
        forecast_dates = pd.date_range(
            start=data['Date'].max() + timedelta(days=1),
            periods=periods,
            freq='D'
        )
        
        forecast_values = [last_level + (i + 1) * last_trend for i in range(periods)]
        
        # Calculate confidence intervals
        residuals = values - np.array([level[i] + trend[i] for i in range(len(values))])
        std_error = np.std(residuals)
        
        lower_bound = [f - 1.96 * std_error for f in forecast_values]
        upper_bound = [f + 1.96 * std_error for f in forecast_values]
        
        return pd.DataFrame({
            'Date': forecast_dates,
            'Forecast': forecast_values,
            'Lower_Bound': lower_bound,
            'Upper_Bound': upper_bound,
            'Method': 'Exponential Smoothing'
        })
    
    def linear_trend_forecast(self, data, periods=30):
        """Enhanced Linear Trend with confidence intervals"""
        data_copy = data.copy()
        data_copy['Days'] = (data_copy['Date'] - data_copy['Date'].min()).dt.days
        
        X = data_copy['Days'].values
        y = data_copy['Total_Quantity'].values
        
        # Linear regression
        n = len(X)
        sum_x = np.sum(X)
        sum_y = np.sum(y)
        sum_xy = np.sum(X * y)
        sum_x2 = np.sum(X ** 2)
        
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x ** 2)
        intercept = (sum_y - slope * sum_x) / n
        
        # Calculate R-squared and standard error
        y_pred = slope * X + intercept
        ss_res = np.sum((y - y_pred) ** 2)
        ss_tot = np.sum((y - np.mean(y)) ** 2)
        r_squared = 1 - (ss_res / ss_tot)
        
        std_error = np.sqrt(ss_res / (n - 2))
        
        # Generate forecast
        last_day = X[-1]
        forecast_days = np.arange(last_day + 1, last_day + periods + 1)
        forecast_values = slope * forecast_days + intercept
        forecast_values = np.maximum(forecast_values, 0)
        
        # Confidence intervals
        lower_bound = forecast_values - 1.96 * std_error
        upper_bound = forecast_values + 1.96 * std_error
        
        forecast_dates = pd.date_range(
            start=data['Date'].max() + timedelta(days=1),
            periods=periods,
            freq='D'
        )
        
        return pd.DataFrame({
            'Date': forecast_dates,
            'Forecast': forecast_values,
            'Lower_Bound': lower_bound,
            'Upper_Bound': upper_bound,
            'Method': 'Linear Trend',
            'R_Squared': r_squared
        })
    
    def seasonal_forecast(self, data, periods=30):
        """Enhanced Seasonal forecast with trend adjustment"""
        data_copy = data.copy()
        data_copy['DayOfWeek'] = data_copy['Date'].dt.dayofweek
        
        # Calculate seasonal pattern
        seasonal_pattern = data_copy.groupby('DayOfWeek')['Total_Quantity'].agg(['mean', 'std']).to_dict()
        
        # Calculate overall trend
        recent_avg = data_copy['Total_Quantity'].tail(30).mean()
        overall_avg = data_copy['Total_Quantity'].mean()
        trend_factor = recent_avg / overall_avg if overall_avg > 0 else 1
        
        forecast_dates = pd.date_range(
            start=data['Date'].max() + timedelta(days=1),
            periods=periods,
            freq='D'
        )
        
        forecast_values = []
        lower_bound = []
        upper_bound = []
        
        for date in forecast_dates:
            dow = date.dayofweek
            base_value = seasonal_pattern['mean'][dow] * trend_factor
            std_value = seasonal_pattern['std'][dow]
            
            forecast_values.append(base_value)
            lower_bound.append(base_value - 1.96 * std_value)
            upper_bound.append(base_value + 1.96 * std_value)
        
        return pd.DataFrame({
            'Date': forecast_dates,
            'Forecast': forecast_values,
            'Lower_Bound': lower_bound,
            'Upper_Bound': upper_bound,
            'Method': 'Seasonal'
        })
    
    def weighted_ensemble_forecast(self, data, periods=30):
        """Advanced Weighted Ensemble with dynamic weights"""
        # Generate individual forecasts
        ma_forecast = self.moving_average_forecast(data, periods=periods)
        es_forecast = self.exponential_smoothing_forecast(data, periods=periods)
        lt_forecast = self.linear_trend_forecast(data, periods=periods)
        seasonal_forecast = self.seasonal_forecast(data, periods=periods)
        
        # Calculate weights based on recent performance
        recent_data = data.tail(30)
        weights = self.calculate_model_weights(recent_data)
        
        # Weighted average
        ensemble_values = (
            weights['ma'] * ma_forecast['Forecast'].values +
            weights['es'] * es_forecast['Forecast'].values +
            weights['lt'] * lt_forecast['Forecast'].values +
            weights['seasonal'] * seasonal_forecast['Forecast'].values
        )
        
        # Ensemble confidence intervals
        lower_bound = (
            weights['ma'] * ma_forecast['Lower_Bound'].values +
            weights['es'] * es_forecast['Lower_Bound'].values +
            weights['lt'] * lt_forecast['Lower_Bound'].values +
            weights['seasonal'] * seasonal_forecast['Lower_Bound'].values
        )
        
        upper_bound = (
            weights['ma'] * ma_forecast['Upper_Bound'].values +
            weights['es'] * es_forecast['Upper_Bound'].values +
            weights['lt'] * lt_forecast['Upper_Bound'].values +
            weights['seasonal'] * seasonal_forecast['Upper_Bound'].values
        )
        
        return pd.DataFrame({
            'Date': ma_forecast['Date'],
            'Forecast': ensemble_values,
            'Lower_Bound': lower_bound,
            'Upper_Bound': upper_bound,
            'Method': 'Weighted Ensemble',
            'Weights': [weights] * periods
        })
    
    def calculate_model_weights(self, recent_data):
        """Calculate dynamic weights based on recent performance"""
        if len(recent_data) < 14:
            # Default equal weights
            return {'ma': 0.25, 'es': 0.25, 'lt': 0.25, 'seasonal': 0.25}
        
        # Calculate errors for each model on recent data
        test_size = 7
        train_data = recent_data.iloc[:-test_size]
        test_data = recent_data.iloc[-test_size:]
        
        errors = {}
        
        # Moving Average error
        ma_pred = train_data['Total_Quantity'].tail(7).mean()
        errors['ma'] = np.mean(np.abs(test_data['Total_Quantity'].values - ma_pred))
        
        # Exponential Smoothing error
        es_pred = train_data['Total_Quantity'].ewm(alpha=0.3).mean().iloc[-1]
        errors['es'] = np.mean(np.abs(test_data['Total_Quantity'].values - es_pred))
        
        # Linear Trend error
        X = np.arange(len(train_data))
        y = train_data['Total_Quantity'].values
        slope = np.polyfit(X, y, 1)[0]
        lt_pred = y[-1] + slope * np.arange(1, test_size + 1)
        errors['lt'] = np.mean(np.abs(test_data['Total_Quantity'].values - lt_pred))
        
        # Seasonal error
        seasonal_avg = train_data.groupby(train_data['Date'].dt.dayofweek)['Total_Quantity'].mean()
        seasonal_pred = [seasonal_avg.get(d.dayofweek, seasonal_avg.mean()) for d in test_data['Date']]
        errors['seasonal'] = np.mean(np.abs(test_data['Total_Quantity'].values - seasonal_pred))
        
        # Convert errors to weights (inverse of error)
        total_inverse_error = sum(1 / (e + 1) for e in errors.values())
        weights = {k: (1 / (v + 1)) / total_inverse_error for k, v in errors.items()}
        
        return weights
    
    def generate_comprehensive_forecast(self, periods=30):
        """Generate comprehensive forecast with all analytics"""
        if self.daily_sales is None:
            self.aggregate_daily_sales()
        
        data = self.daily_sales
        
        # Generate weighted ensemble forecast
        ensemble = self.weighted_ensemble_forecast(data, periods=periods)
        
        # Store results
        self.forecast_results = {
            'ensemble': ensemble,
            'historical': data,
            'periods': periods
        }
        
        # Generate recommendations
        self.generate_recommendations(ensemble, data)
        
        return ensemble
    
    def generate_recommendations(self, forecast, historical):
        """Generate actionable business recommendations"""
        self.recommendations = []
        
        # Analyze trend
        forecast_avg = forecast['Forecast'].mean()
        historical_avg = historical['Total_Quantity'].tail(30).mean()
        trend_change = ((forecast_avg - historical_avg) / historical_avg) * 100
        
        if trend_change > 10:
            self.recommendations.append({
                'type': 'growth',
                'priority': 'high',
                'title': 'Demand Increasing',
                'message': f'Forecasted demand is {trend_change:.1f}% higher than recent average. Consider increasing inventory levels.',
                'action': 'Increase stock by 15-20%'
            })
        elif trend_change < -10:
            self.recommendations.append({
                'type': 'decline',
                'priority': 'high',
                'title': 'Demand Decreasing',
                'message': f'Forecasted demand is {abs(trend_change):.1f}% lower than recent average. Consider reducing inventory to avoid overstock.',
                'action': 'Reduce stock by 10-15%'
            })
        else:
            self.recommendations.append({
                'type': 'stable',
                'priority': 'medium',
                'title': 'Stable Demand',
                'message': 'Demand is expected to remain stable. Maintain current inventory levels.',
                'action': 'Continue current strategy'
            })
        
        # Analyze volatility
        forecast_std = forecast['Forecast'].std()
        if forecast_std > forecast_avg * 0.3:
            self.recommendations.append({
                'type': 'volatility',
                'priority': 'medium',
                'title': 'High Demand Variability',
                'message': 'Significant fluctuations expected. Maintain safety stock buffer.',
                'action': 'Add 20% safety stock'
            })
        
        # Peak day analysis
        forecast_with_dow = forecast.copy()
        forecast_with_dow['DayOfWeek'] = forecast_with_dow['Date'].dt.day_name()
        peak_day = forecast_with_dow.groupby('DayOfWeek')['Forecast'].mean().idxmax()
        
        self.recommendations.append({
            'type': 'scheduling',
            'priority': 'medium',
            'title': 'Peak Demand Day',
            'message': f'{peak_day} shows highest forecasted demand. Plan staffing and inventory accordingly.',
            'action': f'Increase resources on {peak_day}s'
        })
        
        # Confidence analysis
        avg_confidence_width = (forecast['Upper_Bound'] - forecast['Lower_Bound']).mean()
        if avg_confidence_width > forecast_avg * 0.5:
            self.recommendations.append({
                'type': 'uncertainty',
                'priority': 'low',
                'title': 'Forecast Uncertainty',
                'message': 'Wide confidence intervals indicate uncertainty. Monitor actual sales closely.',
                'action': 'Review forecast weekly'
            })
    
    def get_forecast_summary(self):
        """Get comprehensive forecast summary"""
        if not self.forecast_results:
            return None
        
        ensemble = self.forecast_results['ensemble']
        historical = self.forecast_results['historical']
        
        summary = {
            'forecast_period': int(self.forecast_results['periods']),
            'avg_daily_forecast': float(ensemble['Forecast'].mean()),
            'total_forecast': float(ensemble['Forecast'].sum()),
            'min_forecast': float(ensemble['Forecast'].min()),
            'max_forecast': float(ensemble['Forecast'].max()),
            'confidence_range': float((ensemble['Upper_Bound'] - ensemble['Lower_Bound']).mean()),
            'historical_avg': float(historical['Total_Quantity'].tail(30).mean()),
            'trend_direction': 'increasing' if ensemble['Forecast'].mean() > historical['Total_Quantity'].tail(30).mean() else 'decreasing',
            'recommendations': self.recommendations
        }
        
        return summary
    
    def get_forecast_by_day(self):
        """Get detailed day-by-day forecast"""
        if not self.forecast_results:
            return None
        
        ensemble = self.forecast_results['ensemble']
        
        forecast_by_day = ensemble.copy()
        forecast_by_day['Day_Name'] = forecast_by_day['Date'].dt.day_name()
        forecast_by_day['Week'] = ((forecast_by_day['Date'] - forecast_by_day['Date'].min()).dt.days // 7) + 1
        
        return forecast_by_day.to_dict('records')
    
    def get_inventory_recommendations(self, safety_stock_days=7):
        """Calculate inventory recommendations"""
        if not self.forecast_results:
            return None
        
        ensemble = self.forecast_results['ensemble']
        
        # Calculate recommended order quantity
        avg_daily_demand = float(ensemble['Forecast'].mean())
        max_daily_demand = float(ensemble['Upper_Bound'].max())
        
        # Safety stock calculation
        safety_stock = max_daily_demand * safety_stock_days
        
        # Reorder point
        lead_time_days = 7  # Assume 7 days lead time
        reorder_point = (avg_daily_demand * lead_time_days) + safety_stock
        
        # Economic order quantity (simplified)
        total_forecast = float(ensemble['Forecast'].sum())
        
        recommendations = {
            'avg_daily_demand': round(avg_daily_demand, 2),
            'max_daily_demand': round(max_daily_demand, 2),
            'safety_stock': round(safety_stock, 2),
            'reorder_point': round(reorder_point, 2),
            'recommended_order_quantity': round(total_forecast * 1.1, 2),  # 10% buffer
            'lead_time_days': int(lead_time_days),
            'safety_stock_days': int(safety_stock_days)
        }
        
        return recommendations
