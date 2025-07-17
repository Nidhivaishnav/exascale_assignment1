import React, { useState, useEffect } from 'react';
import axios from 'axios';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js';
import { Line, Bar } from 'react-chartjs-2';
import './App.css';

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

function App() {
  const [forecastData, setForecastData] = useState(null);
  const [weatherData, setWeatherData] = useState(null);
  const [holidayData, setHolidayData] = useState(null);
  const [historicalData, setHistoricalData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [modelInfo, setModelInfo] = useState(null);

  const [formData, setFormData] = useState({
    temperature: '25',
    humidity: '60',
    wind_speed: '3',
    cloud_cover: '30',
    datetime: new Date().toISOString().slice(0, 16)
  });

  const [showHolidays, setShowHolidays] = useState(false);

  // Fetch initial data
  useEffect(() => {
    fetchWeatherData();
    fetchHolidayData();
    fetchHistoricalData();
    fetchModelInfo();
  }, []);

  const fetchWeatherData = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/weather?hours=24`);
      setWeatherData(response.data);
    } catch (error) {
      console.error('Error fetching weather data:', error);
    }
  };

  const fetchHolidayData = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/holidays`);
      setHolidayData(response.data);
    } catch (error) {
      console.error('Error fetching holiday data:', error);
    }
  };

  const fetchHistoricalData = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/historical-data?limit=24`);
      setHistoricalData(response.data.data);
    } catch (error) {
      console.error('Error fetching historical data:', error);
    }
  };

  const fetchModelInfo = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/model-info`);
      setModelInfo(response.data);
    } catch (error) {
      console.error('Error fetching model info:', error);
    }
  };

  const handleInputChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    
    try {
      const response = await axios.post(`${API_BASE_URL}/predict`, formData);
      setForecastData(response.data);
    } catch (error) {
      console.error('Error making prediction:', error);
      setError('Failed to generate forecast. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  // Create forecast chart data
  const createForecastChartData = () => {
    if (!forecastData) return null;

    const labels = forecastData.predictions.map((_, index) => {
      const date = new Date(formData.datetime);
      date.setHours(date.getHours() + index);
      return date.toLocaleString('en-US', { 
        hour: '2-digit', 
        minute: '2-digit',
        hour12: false 
      });
    });

    return {
      labels,
      datasets: [
        {
          label: 'Predicted Power Consumption (kW)',
          data: forecastData.predictions,
          borderColor: 'rgb(75, 192, 192)',
          backgroundColor: 'rgba(75, 192, 192, 0.2)',
          tension: 0.1,
          fill: true
        }
      ]
    };
  };

  // Create weather chart data
  const createWeatherChartData = () => {
    if (!weatherData) return null;

    const labels = weatherData.weather_data.map(item => {
      const date = new Date(item.datetime);
      return date.toLocaleString('en-US', { 
        hour: '2-digit', 
        minute: '2-digit',
        hour12: false 
      });
    });

    return {
      labels,
      datasets: [
        {
          label: 'Temperature (°C)',
          data: weatherData.weather_data.map(item => item.temperature),
          borderColor: 'rgb(255, 99, 132)',
          backgroundColor: 'rgba(255, 99, 132, 0.2)',
          yAxisID: 'y',
        },
        {
          label: 'Humidity (%)',
          data: weatherData.weather_data.map(item => item.humidity),
          borderColor: 'rgb(54, 162, 235)',
          backgroundColor: 'rgba(54, 162, 235, 0.2)',
          yAxisID: 'y1',
        },
        {
          label: 'Wind Speed (m/s)',
          data: weatherData.weather_data.map(item => item.wind_speed),
          borderColor: 'rgb(255, 206, 86)',
          backgroundColor: 'rgba(255, 206, 86, 0.2)',
          yAxisID: 'y2',
        },
        {
          label: 'Cloud Cover (%)',
          data: weatherData.weather_data.map(item => item.cloud_cover),
          borderColor: 'rgb(153, 102, 255)',
          backgroundColor: 'rgba(153, 102, 255, 0.2)',
          yAxisID: 'y1',
        }
      ]
    };
  };

  const chartOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top',
      },
      title: {
        display: true,
        text: '24-Hour Power Consumption Forecast'
      }
    },
    scales: {
      y: {
        beginAtZero: true,
        title: {
          display: true,
          text: 'Power Consumption (kW)'
        }
      },
      x: {
        title: {
          display: true,
          text: 'Time'
        }
      }
    }
  };

  const weatherChartOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top',
      },
      title: {
        display: true,
        text: '24-Hour Weather Forecast - Dhanbad, Jharkhand'
      }
    },
    scales: {
      y: {
        type: 'linear',
        display: true,
        position: 'left',
        title: {
          display: true,
          text: 'Temperature (°C)'
        }
      },
      y1: {
        type: 'linear',
        display: true,
        position: 'right',
        title: {
          display: true,
          text: 'Humidity / Cloud Cover (%)'
        },
        grid: {
          drawOnChartArea: false,
        },
      },
      y2: {
        type: 'linear',
        display: false,
        position: 'right',
      }
    }
  };

  // Get upcoming holidays
  const getUpcomingHolidays = () => {
    if (!holidayData) return [];
    const today = new Date();
    return holidayData.holidays.filter(holiday => {
      const holidayDate = new Date(holiday.date);
      return holidayDate >= today;
    }).slice(0, 5);
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>🔌 Utility Consumption Prediction System</h1>
        <p>Apex Power & Utilities (APU) - Dhanbad, Jharkhand, India</p>
        <div className="location-info">
          <span className="location">📍 Dhanbad, Jharkhand</span>
          <span className="model-status">
            {modelInfo?.model_loaded ? '✅ Model Loaded' : '⚠️ Mock Mode'}
          </span>
        </div>
      </header>

      <main className="App-main">
        <div className="dashboard-container">
          {/* Prediction Form */}
          <section className="prediction-section">
            <h2>🎯 Generate 24-Hour Forecast</h2>
            <form onSubmit={handleSubmit} className="prediction-form">
              <div className="form-row">
                <div className="form-group">
                  <label htmlFor="temperature">Temperature (°C):</label>
                  <input
                    type="number"
                    id="temperature"
                    name="temperature"
                    value={formData.temperature}
                    onChange={handleInputChange}
                    step="0.1"
                    min="-10"
                    max="50"
                    required
                  />
                </div>

                <div className="form-group">
                  <label htmlFor="humidity">Humidity (%):</label>
                  <input
                    type="number"
                    id="humidity"
                    name="humidity"
                    value={formData.humidity}
                    onChange={handleInputChange}
                    step="0.1"
                    min="0"
                    max="100"
                    required
                  />
                </div>

                <div className="form-group">
                  <label htmlFor="wind_speed">Wind Speed (m/s):</label>
                  <input
                    type="number"
                    id="wind_speed"
                    name="wind_speed"
                    value={formData.wind_speed}
                    onChange={handleInputChange}
                    step="0.1"
                    min="0"
                    max="20"
                    required
                  />
                </div>

                <div className="form-group">
                  <label htmlFor="cloud_cover">Cloud Cover (%):</label>
                  <input
                    type="number"
                    id="cloud_cover"
                    name="cloud_cover"
                    value={formData.cloud_cover}
                    onChange={handleInputChange}
                    step="0.1"
                    min="0"
                    max="100"
                    required
                  />
                </div>
              </div>

              <div className="form-group">
                <label htmlFor="datetime">Start Date & Time:</label>
                <input
                  type="datetime-local"
                  id="datetime"
                  name="datetime"
                  value={formData.datetime}
                  onChange={handleInputChange}
                  required
                />
              </div>

              <button type="submit" disabled={loading} className="predict-btn">
                {loading ? '🔄 Generating Forecast...' : '📊 Generate 24-Hour Forecast'}
              </button>
            </form>

            {error && (
              <div className="error-message">
                ❌ {error}
              </div>
            )}
          </section>

          {/* Forecast Chart */}
          {forecastData && (
            <section className="forecast-section">
              <h2>📈 24-Hour Power Consumption Forecast</h2>
              <div className="forecast-info">
                <div className="forecast-stats">
                  <span className="stat">
                    <strong>Confidence:</strong> {(forecastData.confidence * 100).toFixed(1)}%
                  </span>
                  <span className="stat">
                    <strong>Forecast Period:</strong> {forecastData.forecast_period}
                  </span>
                  <span className="stat">
                    <strong>Location:</strong> {forecastData.location}
                  </span>
                </div>
              </div>
              <div className="chart-container">
                <Line data={createForecastChartData()} options={chartOptions} />
              </div>
            </section>
          )}

          {/* Weather Data Visualization */}
          <section className="weather-section">
            <h2>🌤️ Weather Forecast</h2>
            {weatherData && (
              <>
                <div className="weather-info">
                  <span className="weather-location">📍 {weatherData.location}</span>
                  <span className="weather-period">⏰ {weatherData.forecast_period}</span>
                </div>
                <div className="chart-container">
                  <Line data={createWeatherChartData()} options={weatherChartOptions} />
                </div>
                
                {/* Weather Summary Cards */}
                <div className="weather-cards">
                  {weatherData.weather_data.slice(0, 6).map((weather, index) => (
                    <div key={index} className="weather-card">
                      <div className="weather-time">
                        {new Date(weather.datetime).toLocaleTimeString('en-US', { 
                          hour: '2-digit', 
                          minute: '2-digit',
                          hour12: false 
                        })}
                      </div>
                      <div className="weather-temp">{weather.temperature.toFixed(1)}°C</div>
                      <div className="weather-details">
                        <div>💧 {weather.humidity.toFixed(0)}%</div>
                        <div>💨 {weather.wind_speed.toFixed(1)} m/s</div>
                        <div>☁️ {weather.cloud_cover.toFixed(0)}%</div>
                      </div>
                    </div>
                  ))}
                </div>
              </>
            )}
          </section>

          {/* Holiday Information */}
          

          {/* Historical Data */}
          <section className="historical-section">
            <h2>📊 Recent Historical Data</h2>
            {historicalData.length > 0 ? (
              <div className="historical-table-container">
                <table className="historical-table">
                  <thead>
                    <tr>
                      <th>Date/Time</th>
                      <th>Temperature (°C)</th>
                      <th>Humidity (%)</th>
                      <th>Wind Speed (m/s)</th>
                      <th>F1 Power (kW)</th>
                      <th>F2 Power (kW)</th>
                      <th>F3 Power (kW)</th>
                    </tr>
                  </thead>
                  <tbody>
                    {historicalData.slice(0, 10).map((row, index) => (
                      <tr key={index}>
                        <td>{new Date(row.Datetime).toLocaleString()}</td>
                        <td>{row.Temperature?.toFixed(1) || 'N/A'}</td>
                        <td>{row.Humidity?.toFixed(1) || 'N/A'}</td>
                        <td>{row.WindSpeed?.toFixed(1) || 'N/A'}</td>
                        <td>{row.F1_132KV_PowerConsumption?.toFixed(0) || 'N/A'}</td>
                        <td>{row.F2_132KV_PowerConsumption?.toFixed(0) || 'N/A'}</td>
                        <td>{row.F3_132KV_PowerConsumption?.toFixed(0) || 'N/A'}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <p>Loading historical data...</p>
            )}
          </section>

          {/* Model Information */}
          {modelInfo && (
            <section className="model-info-section">
              <h2>🤖 Model Information</h2>
              <div className="model-cards">
                <div className="info-card">
                  <h3>Model Status</h3>
                  <p>{modelInfo.model_loaded ? '✅ Production Model' : '⚠️ Mock Mode'}</p>
                </div>
                <div className="info-card">
                  <h3>Assignment</h3>
                  <p>{modelInfo.assignment}</p>
                </div>
                <div className="info-card">
                  <h3>Location</h3>
                  <p>{modelInfo.location}</p>
                </div>
                {modelInfo.model_loaded && (
                  <div className="info-card">
                    <h3>Features</h3>
                    <p>{modelInfo.features_count} engineered features</p>
                  </div>
                )}
              </div>
            </section>
          )}
        </div>
      </main>

      <footer className="App-footer">
        <p>&copy; 2024 Apex Power & Utilities - Intelligent Power Demand Forecasting System</p>
        <p>Assignment: Data Developer Intern - Exascale Deeptech & AI Pvt. Ltd.</p>
      </footer>
    </div>
  );
}

export default App;