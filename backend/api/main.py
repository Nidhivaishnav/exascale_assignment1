from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict
import pandas as pd
import numpy as np
import joblib
from datetime import datetime, timedelta
import uvicorn
import json
import os
from pathlib import Path
import requests
import traceback

app = FastAPI(title="Utility Consumption Prediction API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables for model artifacts
model = None
scaler_X = None
scaler_y = None
selected_features = None
model_metadata = None

# Load model artifacts on startup
def load_model_artifacts():
    global model, scaler_X, scaler_y, selected_features, model_metadata
    try:
        # Use absolute path for model file
        model_path = Path(r'D:\\New folder\\assignment\\assignment\\ml\\models\\power_demand_rf_model.pkl')
        print(f"Checking for model at: {model_path}")
        if model_path.exists():
            model = joblib.load(model_path)
            print("✅ Model loaded from D:\\New folder\\assignment\\assignment\\ml\\models\\power_demand_rf_model.pkl")
            return True
        else:
            print(f"⚠️ Model artifact not found at {model_path} - using mock predictions")
            return False
    except Exception as e:
        print(f"❌ Error loading model artifact: {e}")
        return False

# Pydantic models
class PredictionRequest(BaseModel):
    temperature: float
    humidity: float
    wind_speed: float
    cloud_cover: Optional[float] = None
    datetime: str

class PredictionResponse(BaseModel):
    predictions: List[float]
    confidence: float
    timestamp: str
    forecast_period: str
    location: str

class WeatherData(BaseModel):
    temperature: float
    humidity: float
    wind_speed: float
    cloud_cover: float
    datetime: str

class WeatherResponse(BaseModel):
    weather_data: List[WeatherData]
    location: str
    forecast_period: str

class HolidayData(BaseModel):
    date: str
    name: str
    category: str
    is_holiday: bool

class HolidayResponse(BaseModel):
    holidays: List[HolidayData]
    location: str
    total_holidays: int

class HistoricalDataResponse(BaseModel):
    data: List[dict]
    total_records: int

# Utility functions
def get_dhanbad_holidays():
    """Get localized holidays for Dhanbad, Jharkhand"""
    holidays_2024 = [
        {'date': '2024-01-01', 'name': 'New Year Day', 'category': 'National'},
        {'date': '2024-01-26', 'name': 'Republic Day', 'category': 'National'},
        {'date': '2024-03-08', 'name': 'Holi', 'category': 'Religious'},
        {'date': '2024-04-17', 'name': 'Ram Navami', 'category': 'Religious'},
        {'date': '2024-05-01', 'name': 'Labour Day', 'category': 'Industrial'},
        {'date': '2024-06-17', 'name': 'Eid ul-Fitr', 'category': 'Religious'},
        {'date': '2024-06-30', 'name': 'Hul Diwas (Tribal Heroes Day)', 'category': 'State'},
        {'date': '2024-07-15', 'name': 'Coal Miners Day', 'category': 'Industrial'},
        {'date': '2024-08-15', 'name': 'Independence Day', 'category': 'National'},
        {'date': '2024-08-26', 'name': 'Janmashtami', 'category': 'Religious'},
        {'date': '2024-09-16', 'name': 'Eid al-Adha', 'category': 'Religious'},
        {'date': '2024-10-02', 'name': 'Gandhi Jayanti', 'category': 'National'},
        {'date': '2024-10-12', 'name': 'Dussehra', 'category': 'Religious'},
        {'date': '2024-11-01', 'name': 'Diwali', 'category': 'Religious'},
        {'date': '2024-11-15', 'name': 'Jharkhand Foundation Day', 'category': 'State'},
        {'date': '2024-11-20', 'name': 'Sohrai Festival', 'category': 'Local_Tribal'},
        {'date': '2024-12-04', 'name': 'Miners Safety Day', 'category': 'Industrial'},
        {'date': '2024-12-15', 'name': 'Tusu Festival', 'category': 'Local_Tribal'},
        {'date': '2024-12-25', 'name': 'Christmas', 'category': 'Religious'},
        {'date': '2024-09-24', 'name': 'Karam Puja', 'category': 'Local_Tribal'},
    ]
    return holidays_2024

def generate_weather_forecast(start_date: datetime, hours: int = 24):
    """Generate weather forecast for Dhanbad, Jharkhand"""
    weather_data = []
    
    for i in range(hours):
        forecast_time = start_date + timedelta(hours=i)
        hour = forecast_time.hour
        month = forecast_time.month
        
        # Temperature patterns based on Dhanbad climate
        if month in [12, 1, 2]:  # Winter
            base_temp = 15 + 5 * np.sin(2 * np.pi * hour / 24) + np.random.normal(0, 1)
        elif month in [3, 4, 5]:  # Summer
            base_temp = 35 + 8 * np.sin(2 * np.pi * hour / 24) + np.random.normal(0, 2)
        elif month in [6, 7, 8, 9]:  # Monsoon
            base_temp = 28 + 6 * np.sin(2 * np.pi * hour / 24) + np.random.normal(0, 1)
        else:  # Post-monsoon
            base_temp = 25 + 7 * np.sin(2 * np.pi * hour / 24) + np.random.normal(0, 1)
        
        # Humidity patterns
        if month in [6, 7, 8, 9]:  # Monsoon
            humidity = 70 + 20 * np.sin(2 * np.pi * hour / 24) + np.random.normal(0, 3)
        else:
            humidity = 50 + 15 * np.sin(2 * np.pi * hour / 24) + np.random.normal(0, 3)
        
        # Wind speed patterns
        wind_speed = 2 + 1.5 * np.sin(2 * np.pi * hour / 24) + np.random.normal(0, 0.3)
        
        # Cloud cover
        if month in [6, 7, 8, 9]:  # Monsoon
            cloud_cover = 60 + 30 * np.sin(2 * np.pi * hour / 24) + np.random.normal(0, 5)
        else:
            cloud_cover = 30 + 25 * np.sin(2 * np.pi * hour / 24) + np.random.normal(0, 5)
        
        # Ensure realistic bounds
        temperature = max(5, min(45, base_temp))
        humidity = max(10, min(95, humidity))
        wind_speed = max(0, min(20, wind_speed))
        cloud_cover = max(0, min(100, cloud_cover))
        
        weather_data.append(WeatherData(
            temperature=temperature,
            humidity=humidity,
            wind_speed=wind_speed,
            cloud_cover=cloud_cover,
            datetime=forecast_time.isoformat()
        ))
    
    return weather_data

def create_features_for_prediction(weather_data: List[WeatherData], base_datetime: datetime):
    """Create features for prediction based on weather data"""
    features_list = []
    
    for i, weather in enumerate(weather_data):
        dt = base_datetime + timedelta(hours=i)
        
        # Basic temporal features
        features = {
            'Temperature': weather.temperature,
            'Humidity': weather.humidity,
            'WindSpeed': weather.wind_speed,
            'CloudCover': weather.cloud_cover,
            'hour': dt.hour,
            'dayofweek': dt.weekday(),
            'month': dt.month,
            'is_weekend': 1 if dt.weekday() >= 5 else 0,
            'is_business_hours': 1 if 9 <= dt.hour <= 17 else 0,
            'is_peak_hours': 1 if 18 <= dt.hour <= 22 else 0,
            'heat_index': weather.temperature + 0.5 * (weather.humidity - 50) / 10,
            'temp_humidity_interaction': weather.temperature * weather.humidity,
            'is_holiday': 0  # Simplified for demo
        }
        
        # Add cyclical features
        features['hour_sin'] = np.sin(2 * np.pi * dt.hour / 24)
        features['hour_cos'] = np.cos(2 * np.pi * dt.hour / 24)
        features['month_sin'] = np.sin(2 * np.pi * dt.month / 12)
        features['month_cos'] = np.cos(2 * np.pi * dt.month / 12)
        
        features_list.append(features)
    
    return features_list

# Load model artifacts on startup
load_model_artifacts()

# API Routes
@app.get("/")
async def root():
    return {
        "message": "Utility Consumption Prediction API",
        "version": "1.0.0",
        "location": "Dhanbad, Jharkhand, India",
        "assignment": "Apex Power & Utilities (APU)",
        "model_loaded": model is not None
    }

@app.post("/predict", response_model=PredictionResponse)
async def predict_24_hour_consumption(request: PredictionRequest):
    """Generate 24-hour forecast (96 blocks of 10 minutes each)"""
    try:
        base_datetime = datetime.fromisoformat(request.datetime.replace('Z', '+00:00'))
        blocks = 96  # 24 hours * 6 blocks of 10 minutes
        predictions = []
        times = []
        for i in range(blocks):
            block_time = base_datetime + timedelta(minutes=10 * i)
            times.append(block_time.isoformat())
            # Create feature vector for each block
            features = {
                'Temperature': request.temperature,
                'Humidity': request.humidity,
                'WindSpeed': request.wind_speed,
                'is_holiday': 0,
                'hour': block_time.hour,
                'dayofweek': block_time.weekday(),
                'month': block_time.month,
                'is_weekend': 1 if block_time.weekday() >= 5 else 0
            }
            # Pass only the features used during model training
            feature_vector = pd.DataFrame([features], columns=['Temperature', 'Humidity', 'WindSpeed', 'is_holiday', 'hour', 'dayofweek', 'month', 'is_weekend'])
            if model is not None:
                prediction = model.predict(feature_vector)[0]
                predictions.append(max(0, prediction))
            else:
                # Fallback mock prediction
                base_consumption = 25000.0
                temp_effect = (features['Temperature'] - 25) * 100
                humidity_effect = (features['Humidity'] - 50) * 50
                hour_effect = 2000 * np.sin(2 * np.pi * features['hour'] / 24)
                prediction = base_consumption + temp_effect + humidity_effect + hour_effect
                predictions.append(max(15000, prediction))
        confidence = 0.85 if model is not None else 0.60
        return PredictionResponse(
            predictions=predictions,
            confidence=confidence,
            timestamp=datetime.now().isoformat(),
            forecast_period="24 hours (96 blocks of 10 minutes)",
            location="Dhanbad, Jharkhand, India"
        )
    except Exception as e:
        print("Exception in /predict endpoint:")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/weather", response_model=WeatherResponse)
async def get_weather_forecast(hours: int = 24):
    """Get weather forecast for Dhanbad, Jharkhand"""
    try:
        base_datetime = datetime.now()
        weather_forecast = generate_weather_forecast(base_datetime, hours=hours)
        
        return WeatherResponse(
            weather_data=weather_forecast,
            location="Dhanbad, Jharkhand, India",
            forecast_period=f"{hours} hours"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/holidays", response_model=HolidayResponse)
async def get_localized_holidays(year: int = 2024):
    """Get localized holidays for Dhanbad, Jharkhand"""
    try:
        holidays_data = get_dhanbad_holidays()
        
        # Convert to HolidayData objects
        holidays = []
        for holiday in holidays_data:
            holidays.append(HolidayData(
                date=holiday['date'],
                name=holiday['name'],
                category=holiday['category'],
                is_holiday=True
            ))
        
        return HolidayResponse(
            holidays=holidays,
            location="Dhanbad, Jharkhand, India",
            total_holidays=len(holidays)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/historical-data", response_model=HistoricalDataResponse)
async def get_historical_data(limit: int = 100, offset: int = 0):
    """Get historical consumption data"""
    try:
        # Try to load actual historical data
        try:
            df = pd.read_csv('../../data/raw/Utility_consumption.csv')
            total_records = len(df)
            data = df.iloc[offset:offset+limit].to_dict('records')
        except:
            # Fallback to mock data
            mock_data = []
            base_datetime = datetime.now() - timedelta(days=30)
            
            for i in range(limit):
                dt = base_datetime + timedelta(minutes=i*10)
                mock_data.append({
                    'Datetime': dt.isoformat(),
                    'Temperature': 25 + 5 * np.sin(2 * np.pi * dt.hour / 24) + np.random.normal(0, 2),
                    'Humidity': 60 + 15 * np.sin(2 * np.pi * dt.hour / 24) + np.random.normal(0, 5),
                    'WindSpeed': 3 + np.random.normal(0, 1),
                    'F1_132KV_PowerConsumption': 25000 + 5000 * np.sin(2 * np.pi * dt.hour / 24) + np.random.normal(0, 1000),
                    'F2_132KV_PowerConsumption': 18000 + 3000 * np.sin(2 * np.pi * dt.hour / 24) + np.random.normal(0, 800),
                    'F3_132KV_PowerConsumption': 22000 + 4000 * np.sin(2 * np.pi * dt.hour / 24) + np.random.normal(0, 900)
                })
            
            data = mock_data
            total_records = 50000  # Mock total
        
        return HistoricalDataResponse(
            data=data,
            total_records=total_records
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/model-info")
async def get_model_info():
    """Get model information and performance metrics"""
    global model, selected_features, model_metadata
    if model is not None:
        return {
            "model_loaded": True,
            "model_metadata": model_metadata,
            "features_count": len(selected_features) if selected_features else 0,
            "location": "Dhanbad, Jharkhand, India",
            "assignment": "Apex Power & Utilities (APU)"
        }
    else:
        return {
            "model_loaded": False,
            "message": "Model not loaded - using mock predictions",
            "location": "Dhanbad, Jharkhand, India",
            "assignment": "Apex Power & Utilities (APU)"
        }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "model_loaded": model is not None,
        "location": "Dhanbad, Jharkhand, India",
        "services": {
            "prediction": "operational",
            "weather": "operational",
            "holidays": "operational",
            "historical_data": "operational"
        }
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)