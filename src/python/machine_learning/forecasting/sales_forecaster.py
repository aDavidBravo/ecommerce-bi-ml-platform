"""
Sales Forecasting Module
Implementa múltiples algoritmos de forecasting: LSTM, Prophet, XGBoost, ARIMA
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

# Time series libraries
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.statespace.sarimax import SARIMAX
from prophet import Prophet
import xgboost as xgb
from lightgbm import LGBMRegressor

# Deep Learning
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout, Bidirectional
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint

# PyTorch
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader

# ML utilities
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import mlflow
import mlflow.sklearn
import mlflow.tensorflow
import mlflow.pytorch

class SalesForecaster:
    """
    Clase unificada para forecasting de ventas con múltiples algoritmos
    """
    
    def __init__(self, data: pd.DataFrame, target_col: str = 'sales'):
        """
        Args:
            data: DataFrame con series temporales
            target_col: Nombre de la columna objetivo
        """
        self.data = data
        self.target_col = target_col
        self.models = {}
        self.predictions = {}
        self.metrics = {}
        
    def prepare_data(self, test_size: float = 0.2):
        """Prepara datos para entrenamiento y validación"""
        split_idx = int(len(self.data) * (1 - test_size))
        
        self.train_data = self.data[:split_idx]
        self.test_data = self.data[split_idx:]
        
        return self.train_data, self.test_data
    
    # ========================================
    # ARIMA / SARIMA
    # ========================================
    
    def train_arima(self, order: Tuple[int, int, int] = (5, 1, 2)) -> Dict:
        """
        Entrena modelo ARIMA
        
        Args:
            order: Parámetros (p, d, q) del modelo ARIMA
        """
        with mlflow.start_run(run_name="ARIMA_Forecasting"):
            mlflow.log_params({
                "model_type": "ARIMA",
                "p": order[0],
                "d": order[1],
                "q": order[2]
            })
            
            # Entrenar modelo
            model = ARIMA(self.train_data[self.target_col], order=order)
            fitted_model = model.fit()
            
            # Predicciones
            forecast = fitted_model.forecast(steps=len(self.test_data))
            
            # Métricas
            mae = mean_absolute_error(self.test_data[self.target_col], forecast)
            rmse = np.sqrt(mean_squared_error(self.test_data[self.target_col], forecast))
            mape = np.mean(np.abs((self.test_data[self.target_col] - forecast) / 
                                   self.test_data[self.target_col])) * 100
            
            mlflow.log_metrics({
                "MAE": mae,
                "RMSE": rmse,
                "MAPE": mape
            })
            
            # Guardar modelo
            mlflow.sklearn.log_model(fitted_model, "arima_model")
            
            self.models['ARIMA'] = fitted_model
            self.predictions['ARIMA'] = forecast
            self.metrics['ARIMA'] = {"MAE": mae, "RMSE": rmse, "MAPE": mape}
            
            return self.metrics['ARIMA']
    
    def train_sarima(self, order: Tuple = (1, 1, 1), 
                     seasonal_order: Tuple = (1, 1, 1, 12)) -> Dict:
        """
        Entrena modelo SARIMA con estacionalidad
        """
        with mlflow.start_run(run_name="SARIMA_Forecasting"):
            mlflow.log_params({
                "model_type": "SARIMA",
                "order": str(order),
                "seasonal_order": str(seasonal_order)
            })
            
            model = SARIMAX(self.train_data[self.target_col], 
                           order=order,
                           seasonal_order=seasonal_order)
            fitted_model = model.fit(disp=False)
            
            forecast = fitted_model.forecast(steps=len(self.test_data))
            
            mae = mean_absolute_error(self.test_data[self.target_col], forecast)
            rmse = np.sqrt(mean_squared_error(self.test_data[self.target_col], forecast))
            mape = np.mean(np.abs((self.test_data[self.target_col] - forecast) / 
                                   self.test_data[self.target_col])) * 100
            
            mlflow.log_metrics({"MAE": mae, "RMSE": rmse, "MAPE": mape})
            
            self.models['SARIMA'] = fitted_model
            self.predictions['SARIMA'] = forecast
            self.metrics['SARIMA'] = {"MAE": mae, "RMSE": rmse, "MAPE": mape}
            
            return self.metrics['SARIMA']
    
    # ========================================
    # PROPHET
    # ========================================
    
    def train_prophet(self, changepoint_prior_scale: float = 0.05,
                     seasonality_prior_scale: float = 10.0) -> Dict:
        """
        Entrena modelo Prophet de Facebook
        """
        with mlflow.start_run(run_name="Prophet_Forecasting"):
            mlflow.log_params({
                "model_type": "Prophet",
                "changepoint_prior_scale": changepoint_prior_scale,
                "seasonality_prior_scale": seasonality_prior_scale
            })
            
            # Preparar datos para Prophet
            df_prophet = self.train_data.reset_index()
            df_prophet.columns = ['ds', 'y']
            
            # Entrenar modelo
            model = Prophet(
                changepoint_prior_scale=changepoint_prior_scale,
                seasonality_prior_scale=seasonality_prior_scale,
                daily_seasonality=True,
                weekly_seasonality=True,
                yearly_seasonality=True
            )
            model.fit(df_prophet)
            
            # Hacer predicciones
            future = model.make_future_dataframe(periods=len(self.test_data))
            forecast = model.predict(future)
            
            # Extraer predicciones
            predictions = forecast.tail(len(self.test_data))['yhat'].values
            
            # Métricas
            mae = mean_absolute_error(self.test_data[self.target_col], predictions)
            rmse = np.sqrt(mean_squared_error(self.test_data[self.target_col], predictions))
            mape = np.mean(np.abs((self.test_data[self.target_col] - predictions) / 
                                   self.test_data[self.target_col])) * 100
            
            mlflow.log_metrics({"MAE": mae, "RMSE": rmse, "MAPE": mape})
            
            self.models['Prophet'] = model
            self.predictions['Prophet'] = predictions
            self.metrics['Prophet'] = {"MAE": mae, "RMSE": rmse, "MAPE": mape}
            
            return self.metrics['Prophet']
    
    # ========================================
    # XGBOOST
    # ========================================
    
    def create_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Crea features para modelos ML"""
        df = df.copy()
        df['dayofweek'] = df.index.dayofweek
        df['quarter'] = df.index.quarter
        df['month'] = df.index.month
        df['year'] = df.index.year
        df['dayofyear'] = df.index.dayofyear
        df['weekofyear'] = df.index.isocalendar().week
        
        # Lags
        for lag in [1, 7, 14, 30]:
            df[f'lag_{lag}'] = df[self.target_col].shift(lag)
        
        # Rolling statistics
        for window in [7, 14, 30]:
            df[f'rolling_mean_{window}'] = df[self.target_col].rolling(window).mean()
            df[f'rolling_std_{window}'] = df[self.target_col].rolling(window).std()
        
        return df.dropna()
    
    def train_xgboost(self, params: Optional[Dict] = None) -> Dict:
        """
        Entrena modelo XGBoost para forecasting
        """
        if params is None:
            params = {
                'objective': 'reg:squarederror',
                'max_depth': 6,
                'learning_rate': 0.1,
                'n_estimators': 1000,
                'subsample': 0.8,
                'colsample_bytree': 0.8
            }
        
        with mlflow.start_run(run_name="XGBoost_Forecasting"):
            mlflow.log_params({**params, "model_type": "XGBoost"})
            
            # Crear features
            train_features = self.create_features(self.train_data)
            test_features = self.create_features(self.test_data)
            
            feature_cols = [col for col in train_features.columns if col != self.target_col]
            
            X_train = train_features[feature_cols]
            y_train = train_features[self.target_col]
            X_test = test_features[feature_cols]
            y_test = test_features[self.target_col]
            
            # Entrenar modelo
            model = xgb.XGBRegressor(**params, random_state=42)
            model.fit(
                X_train, y_train,
                eval_set=[(X_test, y_test)],
                early_stopping_rounds=50,
                verbose=False
            )
            
            # Predicciones
            predictions = model.predict(X_test)
            
            # Métricas
            mae = mean_absolute_error(y_test, predictions)
            rmse = np.sqrt(mean_squared_error(y_test, predictions))
            mape = np.mean(np.abs((y_test - predictions) / y_test)) * 100
            r2 = r2_score(y_test, predictions)
            
            mlflow.log_metrics({
                "MAE": mae,
                "RMSE": rmse,
                "MAPE": mape,
                "R2": r2
            })
            
            # Guardar modelo
            mlflow.sklearn.log_model(model, "xgboost_model")
            
            # Feature importance
            feature_importance = pd.DataFrame({
                'feature': feature_cols,
                'importance': model.feature_importances_
            }).sort_values('importance', ascending=False)
            
            mlflow.log_dict(feature_importance.to_dict(), "feature_importance.json")
            
            self.models['XGBoost'] = model
            self.predictions['XGBoost'] = predictions
            self.metrics['XGBoost'] = {
                "MAE": mae, "RMSE": rmse, "MAPE": mape, "R2": r2
            }
            
            return self.metrics['XGBoost']
    
    # ========================================
    # LSTM (TensorFlow)
    # ========================================
    
    def prepare_lstm_data(self, sequence_length: int = 30) -> Tuple:
        """Prepara datos para LSTM"""
        # Normalizar datos
        scaler = MinMaxScaler()
        scaled_data = scaler.fit_transform(
            self.train_data[[self.target_col]].values
        )
        
        # Crear secuencias
        X, y = [], []
        for i in range(sequence_length, len(scaled_data)):
            X.append(scaled_data[i-sequence_length:i, 0])
            y.append(scaled_data[i, 0])
        
        X, y = np.array(X), np.array(y)
        X = np.reshape(X, (X.shape[0], X.shape[1], 1))
        
        return X, y, scaler
    
    def train_lstm(self, sequence_length: int = 30, epochs: int = 100) -> Dict:
        """
        Entrena modelo LSTM para forecasting
        """
        with mlflow.start_run(run_name="LSTM_Forecasting"):
            mlflow.log_params({
                "model_type": "LSTM",
                "sequence_length": sequence_length,
                "epochs": epochs
            })
            
            # Preparar datos
            X_train, y_train, scaler = self.prepare_lstm_data(sequence_length)
            
            # Construir modelo
            model = Sequential([
                LSTM(100, return_sequences=True, input_shape=(sequence_length, 1)),
                Dropout(0.2),
                LSTM(100, return_sequences=True),
                Dropout(0.2),
                LSTM(50, return_sequences=False),
                Dropout(0.2),
                Dense(25),
                Dense(1)
            ])
            
            model.compile(optimizer='adam', loss='mse', metrics=['mae'])
            
            # Callbacks
            early_stop = EarlyStopping(monitor='loss', patience=10, 
                                      restore_best_weights=True)
            
            # Entrenar
            history = model.fit(
                X_train, y_train,
                epochs=epochs,
                batch_size=32,
                verbose=0,
                callbacks=[early_stop]
            )
            
            # Predicciones para test set
            test_scaled = scaler.transform(self.test_data[[self.target_col]].values)
            X_test = []
            
            for i in range(sequence_length, len(test_scaled)):
                X_test.append(test_scaled[i-sequence_length:i, 0])
            
            X_test = np.array(X_test)
            X_test = np.reshape(X_test, (X_test.shape[0], X_test.shape[1], 1))
            
            predictions_scaled = model.predict(X_test, verbose=0)
            predictions = scaler.inverse_transform(predictions_scaled)
            
            # Métricas
            y_test_actual = self.test_data[self.target_col].values[sequence_length:]
            mae = mean_absolute_error(y_test_actual, predictions)
            rmse = np.sqrt(mean_squared_error(y_test_actual, predictions))
            mape = np.mean(np.abs((y_test_actual - predictions.flatten()) / 
                                   y_test_actual)) * 100
            
            mlflow.log_metrics({"MAE": mae, "RMSE": rmse, "MAPE": mape})
            
            # Guardar modelo
            mlflow.tensorflow.log_model(model, "lstm_model")
            
            self.models['LSTM'] = model
            self.predictions['LSTM'] = predictions.flatten()
            self.metrics['LSTM'] = {"MAE": mae, "RMSE": rmse, "MAPE": mape}
            
            return self.metrics['LSTM']
    
    # ========================================
    # ENSEMBLE
    # ========================================
    
    def ensemble_forecast(self, weights: Optional[Dict] = None) -> Dict:
        """
        Crea predicción ensemble combinando todos los modelos
        """
        if not self.predictions:
            raise ValueError("No hay modelos entrenados. Entrena modelos primero.")
        
        if weights is None:
            # Pesos iguales por defecto
            weights = {model: 1/len(self.predictions) 
                      for model in self.predictions.keys()}
        
        with mlflow.start_run(run_name="Ensemble_Forecasting"):
            mlflow.log_params({"model_type": "Ensemble", "weights": str(weights)})
            
            # Combinar predicciones
            ensemble_pred = np.zeros(len(self.test_data))
            
            for model_name, pred in self.predictions.items():
                if len(pred) == len(ensemble_pred):
                    ensemble_pred += weights.get(model_name, 0) * pred
            
            # Métricas
            mae = mean_absolute_error(self.test_data[self.target_col], ensemble_pred)
            rmse = np.sqrt(mean_squared_error(self.test_data[self.target_col], 
                                              ensemble_pred))
            mape = np.mean(np.abs((self.test_data[self.target_col] - ensemble_pred) / 
                                   self.test_data[self.target_col])) * 100
            
            mlflow.log_metrics({"MAE": mae, "RMSE": rmse, "MAPE": mape})
            
            self.predictions['Ensemble'] = ensemble_pred
            self.metrics['Ensemble'] = {"MAE": mae, "RMSE": rmse, "MAPE": mape}
            
            return self.metrics['Ensemble']
    
    def get_best_model(self) -> Tuple[str, Dict]:
        """Retorna el mejor modelo basado en MAPE"""
        if not self.metrics:
            raise ValueError("No hay métricas disponibles. Entrena modelos primero.")
        
        best_model = min(self.metrics.items(), 
                        key=lambda x: x[1].get('MAPE', float('inf')))
        
        return best_model
    
    def plot_predictions(self):
        """Visualiza predicciones de todos los modelos"""
        import matplotlib.pyplot as plt
        
        plt.figure(figsize=(15, 8))
        plt.plot(self.test_data.index, self.test_data[self.target_col], 
                label='Actual', linewidth=2, color='black')
        
        colors = ['blue', 'red', 'green', 'orange', 'purple', 'brown']
        
        for i, (model_name, pred) in enumerate(self.predictions.items()):
            if len(pred) == len(self.test_data):
                plt.plot(self.test_data.index, pred, 
                        label=f'{model_name} (MAPE: {self.metrics[model_name]["MAPE"]:.2f}%)',
                        linewidth=1.5, alpha=0.7, color=colors[i % len(colors)])
        
        plt.title('Sales Forecasting - Model Comparison', fontsize=16, fontweight='bold')
        plt.xlabel('Date', fontsize=12)
        plt.ylabel('Sales', fontsize=12)
        plt.legend(loc='best', fontsize=10)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        return plt.gcf()


# ========================================
# EJEMPLO DE USO
# ========================================

if __name__ == "__main__":
    # Generar datos de ejemplo
    dates = pd.date_range('2020-01-01', periods=1000, freq='D')
    sales = np.cumsum(np.random.randn(1000)) + 100 + \
            10 * np.sin(np.arange(1000) * 2 * np.pi / 365)  # Estacionalidad anual
    
    df = pd.DataFrame({'sales': sales}, index=dates)
    
    # Inicializar forecaster
    forecaster = SalesForecaster(df, target_col='sales')
    forecaster.prepare_data(test_size=0.2)
    
    # Entrenar modelos
    print("Training ARIMA...")
    forecaster.train_arima()
    
    print("Training SARIMA...")
    forecaster.train_sarima()
    
    print("Training Prophet...")
    forecaster.train_prophet()
    
    print("Training XGBoost...")
    forecaster.train_xgboost()
    
    print("Training LSTM...")
    forecaster.train_lstm()
    
    # Ensemble
    print("Creating Ensemble...")
    forecaster.ensemble_forecast()
    
    # Mejor modelo
    best_model_name, best_metrics = forecaster.get_best_model()
    print(f"\nBest Model: {best_model_name}")
    print(f"Metrics: {best_metrics}")
    
    # Visualizar
    fig = forecaster.plot_predictions()
    fig.savefig('/tmp/forecasting_comparison.png', dpi=300, bbox_inches='tight')
    print("\nPlot saved!")
