import React, { useState } from 'react';
import './App.css';

const ComfortPredictionForm = () => {
  const [formData, setFormData] = useState({
    clo_upr: 0.5, // Default upper body clothing insulation
    clo_lwr: 0.3, // Default lower body clothing insulation
    temp: 20, // Default temperature in °C
    sun: false,
    headwind: false,
    snow: 'NONE',
    rain: 'NONE',
    fatigued: false,
    hr: 75, // Default heart rate
    feels: 'COOL',
    predictionMode: 'comfort' // 'comfort' or 'clothing'
  });

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData({
      ...formData,
      [name]: type === 'checkbox' ? checked : value
    });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    // Here you would call your API with the form data
    console.log('Form submitted:', formData);
    // Call API: fetch('/api/predict-comfort', { method: 'POST', body: JSON.stringify(formData) })
  };

  const handleReset = () => {
    setFormData({
      clo_upr: 0.5,
      clo_lwr: 0.3,
      temp: 20,
      sun: false,
      headwind: false,
      snow: 'NONE',
      rain: 'NONE',
      fatigued: false,
      hr: 75,
      feels: 'COOL',
      predictionMode: 'comfort'
    });
  };

  return (
    <div className="comfort-prediction-container">
      <h1>Comfort Prediction Tool</h1>
      
      <div className="prediction-mode-selector">
        <label>
          <input
            type="radio"
            name="predictionMode"
            value="comfort"
            checked={formData.predictionMode === 'comfort'}
            onChange={handleChange}
          />
          Predict Comfort Level
        </label>
        <label>
          <input
            type="radio"
            name="predictionMode"
            value="clothing"
            checked={formData.predictionMode === 'clothing'}
            onChange={handleChange}
          />
          Recommend Clothing
        </label>
      </div>

      <form onSubmit={handleSubmit}>
        <div className="form-sections">
          <div className="form-section">
            <h2>Clothing Parameters</h2>
            
            <div className="form-group">
              <label htmlFor="clo_upr">Upper Body Clothing (Clo)</label>
              <input
                type="number"
                id="clo_upr"
                name="clo_upr"
                min="0"
                max="4"
                step="0.1"
                value={formData.clo_upr}
                onChange={handleChange}
                disabled={formData.predictionMode === 'clothing'}
                placeholder="Upper body insulation value"
              />
              <span className="helper-text">Range: 0-4 (T-shirt: 0.1, Heavy jacket: 2+)</span>
            </div>

            <div className="form-group">
              <label htmlFor="clo_lwr">Lower Body Clothing (Clo)</label>
              <input
                type="number"
                id="clo_lwr"
                name="clo_lwr"
                min="0"
                max="4"
                step="0.1"
                value={formData.clo_lwr}
                onChange={handleChange}
                disabled={formData.predictionMode === 'clothing'}
                placeholder="Lower body insulation value"
              />
              <span className="helper-text">Range: 0-4 (Shorts: 0.1, Insulated pants: 1.5+)</span>
            </div>
          </div>

          <div className="form-section">
            <h2>Environmental Conditions</h2>
            
            <div className="form-group">
              <label htmlFor="temp">Temperature (°C)</label>
              <input
                type="number"
                id="temp"
                name="temp"
                min="-50"
                max="50"
                value={formData.temp}
                onChange={handleChange}
                placeholder="Temperature in °C"
              />
            </div>

            <div className="form-group checkbox-group">
              <label>
                <input
                  type="checkbox"
                  name="sun"
                  checked={formData.sun}
                  onChange={handleChange}
                />
                Sunny
              </label>
            </div>

            <div className="form-group checkbox-group">
              <label>
                <input
                  type="checkbox"
                  name="headwind"
                  checked={formData.headwind}
                  onChange={handleChange}
                />
                Headwind
              </label>
            </div>

            <div className="form-group">
              <label htmlFor="snow">Snow</label>
              <select
                id="snow"
                name="snow"
                value={formData.snow}
                onChange={handleChange}
              >
                <option value="NONE">None</option>
                <option value="LIGHT">Light</option>
                <option value="MEDIUM">Medium</option>
                <option value="HEAVY">Heavy</option>
              </select>
            </div>

            <div className="form-group">
              <label htmlFor="rain">Rain</label>
              <select
                id="rain"
                name="rain"
                value={formData.rain}
                onChange={handleChange}
              >
                <option value="NONE">None</option>
                <option value="LIGHT">Light</option>
                <option value="MEDIUM">Medium</option>
                <option value="HEAVY">Heavy</option>
              </select>
            </div>
          </div>

          <div className="form-section">
            <h2>Physiological Data</h2>
            
            <div className="form-group checkbox-group">
              <label>
                <input
                  type="checkbox"
                  name="fatigued"
                  checked={formData.fatigued}
                  onChange={handleChange}
                />
                Fatigued
              </label>
            </div>

            <div className="form-group">
              <label htmlFor="hr">Heart Rate (BPM)</label>
              <input
                type="number"
                id="hr"
                name="hr"
                min="30"
                max="220"
                value={formData.hr}
                onChange={handleChange}
                placeholder="Heart rate in BPM"
              />
            </div>

            <div className="form-group">
              <label htmlFor="feels">Feels</label>
              <select
                id="feels"
                name="feels"
                value={formData.feels}
                onChange={handleChange}
                disabled={formData.predictionMode === 'comfort'}
              >
                <option value="COLD">Cold</option>
                <option value="COOL">Cool</option>
                <option value="WARM">Warm</option>
                <option value="HOT">Hot</option>
              </select>
            </div>
          </div>
        </div>

        <div className="form-buttons">
          <button type="submit" className="submit-button">
            {formData.predictionMode === 'comfort' 
              ? 'Predict Comfort' 
              : 'Recommend Clothing'}
          </button>
          <button type="button" className="reset-button" onClick={handleReset}>
            Reset
          </button>
        </div>
      </form>
    </div>
  );
};

export default ComfortPredictionForm;