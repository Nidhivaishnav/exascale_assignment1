import pandas as pd
import numpy as np
import joblib
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import os
from datetime import datetime

class ModelService:
    def __init__(self):
        self.model = None
        self.scaler = None
        self.is_trained = False
        
    def load_model(self, model_path: str):
        """Load a trained model from file"""
        try:
            self.model = joblib.load(model_path)
            self.is_trained = True
            return True
        except Exception as e:
            print(f"Error loading model: {e}")
            return False
    
    def save_model(self, model_path: str):
        """Save the current model to file"""
        try:
            joblib.dump(self.model, model_path)
            return True
        except Exception as e:
            print(f"Error saving model: {e}")
            return False
    
    def train_model(self, data_path: str):
        """Train a new model using the provided data"""
        try:
            # Load data
            df = pd.read_csv(data_path)
            
            # Prepare features and target
            feature_columns = ['Temperature', 'Humidity', 'WindSpeed']
            target_column = 'F1_132KV_PowerConsumption'
            
            X = df[feature_columns]
            y = df[target_column]
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
            
            # Scale features
            self.scaler = StandardScaler()
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            # Train model
            self.model = RandomForestRegressor(n_estimators=100, random_state=42)
            self.model.fit(X_train_scaled, y_train)
            
            # Evaluate model
            y_pred = self.model.predict(X_test_scaled)
            mse = mean_squared_error(y_test, y_pred)
            r2 = r2_score(y_test, y_pred)
            
            self.is_trained = True
            
            return {
                'success': True,
                'mse': mse,
                'r2': r2,
                'trained_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def predict(self, features: dict):
        """Make prediction using the trained model"""
        if not self.is_trained:
            raise ValueError("Model is not trained or loaded")
        
        try:
            # Convert features to numpy array
            feature_array = np.array([[
                features['temperature'],
                features['humidity'],
                features['wind_speed']
            ]])
            
            # Scale features if scaler is available
            if self.scaler:
                feature_array = self.scaler.transform(feature_array)
            
            # Make prediction
            prediction = self.model.predict(feature_array)[0]
            
            return {
                'prediction': prediction,
                'success': True
            }
            
        except Exception as e:
            return {
                'prediction': None,
                'success': False,
                'error': str(e)
            }
    
    def get_model_info(self):
        """Get information about the current model"""
        if not self.is_trained:
            return {'trained': False}
        
        return {
            'trained': True,
            'model_type': type(self.model).__name__,
            'features': ['Temperature', 'Humidity', 'WindSpeed'],
            'target': 'F1_132KV_PowerConsumption'
        } 