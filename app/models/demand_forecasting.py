import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

class DemandForecasting:
    def __init__(self, data_path='cleandataset.csv'):
        """Initialize Demand Forecasting with data"""
        self.df = pd.read_csv(data_path)
        self.daily_sales = None
        self.product_sales = None
        self.forecasts = {}
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
        """Aggregate sales by day"""
        daily = self.df.groupby('Date').agg({
            'Quantity': 'sum',
            'TotalAmount': 'sum',
            'Invoice': 'nunique'
        }).reset_index()
        
        daily.columns = ['Date', 'Total_Quantity', 'Total_Revenue', 'Total_Orders']
        daily['Date'] = pd.to_datetime(daily['Date'])
        daily = daily.sort_values('Date')
        
        # Fill missing dates
        date_range = pd.date_range(start=daily['Date'].min(), end=daily['Date'].max(), freq='D')
        daily = daily.set_index('Date').reindex(date_range, fill_value=0).reset_index()
        daily.columns = ['Date', 'Total_Quantity', 'Total_Revenue', 'Total_Orders']
        
        self.daily_sales = daily
        return daily
    
    def aggregate_product_sales(self, top_n=20):
        """Aggregate sales by product"""
        product = self.df.groupby('Description').agg({
            'Quantity': 'sum',
            'TotalAmount': 'sum',
            'Invoice': 'nunique'
        }).reset_index()
        
        product.columns = ['Product', 'Total_Quantity', 'Total_Revenue', 'Total_Orders']
        product = product.sort_values('Total_Revenue', ascending=False).head(top_n)
        
        self.product_sales = product
        return product
    
    def moving_average_forecast(self, data, window=7, periods=30):
        """Simple Moving Average forecast"""
        ma = data['Total_Quantity'].rolling(window=window).mean()
        last_ma = ma.iloc[-1]
        
        forecast_dates = pd.date_range(
            start=data['Date'].max() + timedelta(days=1),
            periods=periods,
            freq='D'
        )
        
        forecast_values = [last_ma] * periods
        
        return pd.DataFrame({
            'Date': forecast_dates,
            'Forecast_Quantity': forecast_values,
            'Method': 'Moving Average'
        })
    
    def exponential_smoothing_forecast(self, data, alpha=0.3, periods=30):
        """Exponential Smoothing forecast"""
        values = data['Total_Quantity'].values
        
        # Calculate exponential smoothing
        smoothed = [values[0]]
        for i in range(1, len(values)):
            smoothed.append(alpha * values[i] + (1 - alpha) * smoothed[i-1])
        
        last_smoothed = smoothed[-1]
        
        forecast_dates = pd.date_range(
            start=data['Date'].max() + timedelta(days=1),
            periods=periods,
            freq='D'
        )
        
        forecast_values = [last_smoothed] * periods
        
        return pd.DataFrame({
            'Date': forecast_dates,
            'Forecast_Quantity': forecast_values,
            'Method': 'Exponential Smoothing'
        })
    
    def linear_trend_forecast(self, data, periods=30):
        """Linear Trend forecast"""
        # Prepare data for linear regression
        data_copy = data.copy()
        data_copy['Days'] = (data_copy['Date'] - data_copy['Date'].min()).dt.days
        
        X = data_copy['Days'].values
        y = data_copy['Total_Quantity'].values
        
        # Calculate linear regression coefficients
        n = len(X)
        sum_x = np.sum(X)
        sum_y = np.sum(y)
        sum_xy = np.sum(X * y)
        sum_x2 = np.sum(X ** 2)
        
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x ** 2)
        intercept = (sum_y - slope * sum_x) / n
        
        # Generate forecast
        last_day = X[-1]
        forecast_days = np.arange(last_day + 1, last_day + periods + 1)
        forecast_values = slope * forecast_days + intercept
        forecast_values = np.maximum(forecast_values, 0)  # No negative forecasts
        
        forecast_dates = pd.date_range(
            start=data['Date'].max() + timedelta(days=1),
            periods=periods,
            freq='D'
        )
        
        return pd.DataFrame({
            'Date': forecast_dates,
            'Forecast_Quantity': forecast_values,
            'Method': 'Linear Trend'
        })
    
    def seasonal_forecast(self, data, periods=30):
        """Seasonal forecast based on day of week patterns"""
        data_copy = data.copy()
        data_copy['DayOfWeek'] = data_copy['Date'].dt.dayofweek
        
        # Calculate average by day of week
        seasonal_pattern = data_copy.groupby('DayOfWeek')['Total_Quantity'].mean().to_dict()
        
        forecast_dates = pd.date_range(
            start=data['Date'].max() + timedelta(days=1),
            periods=periods,
            freq='D'
        )
        
        forecast_values = [seasonal_pattern[date.dayofweek] for date in forecast_dates]
        
        return pd.DataFrame({
            'Date': forecast_dates,
            'Forecast_Quantity': forecast_values,
            'Method': 'Seasonal'
        })
    
    def ensemble_forecast(self, data, periods=30):
        """Ensemble forecast combining multiple methods"""
        ma_forecast = self.moving_average_forecast(data, periods=periods)
        es_forecast = self.exponential_smoothing_forecast(data, periods=periods)
        lt_forecast = self.linear_trend_forecast(data, periods=periods)
        seasonal_forecast = self.seasonal_forecast(data, periods=periods)
        
        # Average all forecasts
        ensemble_values = (
            ma_forecast['Forecast_Quantity'].values +
            es_forecast['Forecast_Quantity'].values +
            lt_forecast['Forecast_Quantity'].values +
            seasonal_forecast['Forecast_Quantity'].values
        ) / 4
        
        return pd.DataFrame({
            'Date': ma_forecast['Date'],
            'Forecast_Quantity': ensemble_values,
            'Method': 'Ensemble'
        })
    
    def generate_all_forecasts(self, periods=30):
        """Generate all forecasts"""
        if self.daily_sales is None:
            self.aggregate_daily_sales()
        
        data = self.daily_sales
        
        self.forecasts = {
            'moving_average': self.moving_average_forecast(data, periods=periods),
            'exponential_smoothing': self.exponential_smoothing_forecast(data, periods=periods),
            'linear_trend': self.linear_trend_forecast(data, periods=periods),
            'seasonal': self.seasonal_forecast(data, periods=periods),
            'ensemble': self.ensemble_forecast(data, periods=periods)
        }
        
        return self.forecasts
    
    def get_forecast_summary(self, periods=30):
        """Get summary of all forecasts"""
        if not self.forecasts:
            self.generate_all_forecasts(periods=periods)
        
        summary = []
        for method, forecast_df in self.forecasts.items():
            summary.append({
                'Method': method.replace('_', ' ').title(),
                'Avg_Daily_Forecast': forecast_df['Forecast_Quantity'].mean(),
                'Total_Forecast': forecast_df['Forecast_Quantity'].sum(),
                'Min_Forecast': forecast_df['Forecast_Quantity'].min(),
                'Max_Forecast': forecast_df['Forecast_Quantity'].max()
            })
        
        return pd.DataFrame(summary)
    
    def get_historical_stats(self):
        """Get historical statistics"""
        if self.daily_sales is None:
            self.aggregate_daily_sales()
        
        stats = {
            'total_days': int(len(self.daily_sales)),
            'avg_daily_quantity': float(self.daily_sales['Total_Quantity'].mean()),
            'avg_daily_revenue': float(self.daily_sales['Total_Revenue'].mean()),
            'avg_daily_orders': float(self.daily_sales['Total_Orders'].mean()),
            'total_quantity': float(self.daily_sales['Total_Quantity'].sum()),
            'total_revenue': float(self.daily_sales['Total_Revenue'].sum()),
            'total_orders': float(self.daily_sales['Total_Orders'].sum()),
            'start_date': self.daily_sales['Date'].min().strftime('%Y-%m-%d'),
            'end_date': self.daily_sales['Date'].max().strftime('%Y-%m-%d')
        }
        
        return stats
    
    def get_product_forecast(self, product_name, periods=30):
        """Get forecast for specific product"""
        product_data = self.df[self.df['Description'] == product_name].copy()
        
        if len(product_data) == 0:
            return None
        
        # Aggregate by date
        daily_product = product_data.groupby('Date').agg({
            'Quantity': 'sum'
        }).reset_index()
        
        daily_product.columns = ['Date', 'Total_Quantity']
        daily_product['Date'] = pd.to_datetime(daily_product['Date'])
        daily_product = daily_product.sort_values('Date')
        
        # Fill missing dates
        date_range = pd.date_range(
            start=daily_product['Date'].min(),
            end=daily_product['Date'].max(),
            freq='D'
        )
        daily_product = daily_product.set_index('Date').reindex(date_range, fill_value=0).reset_index()
        daily_product.columns = ['Date', 'Total_Quantity']
        
        # Generate forecast
        forecast = self.ensemble_forecast(daily_product, periods=periods)
        
        return {
            'product': product_name,
            'historical': daily_product.to_dict('records'),
            'forecast': forecast.to_dict('records')
        }
    
    def get_accuracy_metrics(self, test_size=30):
        """Calculate forecast accuracy on historical data"""
        if self.daily_sales is None:
            self.aggregate_daily_sales()
        
        # Split data
        train_data = self.daily_sales.iloc[:-test_size].copy()
        test_data = self.daily_sales.iloc[-test_size:].copy()
        
        if len(train_data) < 30:
            return None
        
        # Generate forecasts on training data
        ma_forecast = self.moving_average_forecast(train_data, periods=test_size)
        es_forecast = self.exponential_smoothing_forecast(train_data, periods=test_size)
        lt_forecast = self.linear_trend_forecast(train_data, periods=test_size)
        
        actual = test_data['Total_Quantity'].values
        
        metrics = []
        for name, forecast in [
            ('Moving Average', ma_forecast),
            ('Exponential Smoothing', es_forecast),
            ('Linear Trend', lt_forecast)
        ]:
            predicted = forecast['Forecast_Quantity'].values
            
            # Calculate metrics
            mae = np.mean(np.abs(actual - predicted))
            rmse = np.sqrt(np.mean((actual - predicted) ** 2))
            mape = np.mean(np.abs((actual - predicted) / (actual + 1))) * 100
            
            metrics.append({
                'Method': name,
                'MAE': mae,
                'RMSE': rmse,
                'MAPE': mape
            })
        
        return pd.DataFrame(metrics)
