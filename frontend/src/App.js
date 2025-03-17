import React, { useState, useRef } from 'react';
import './App.css';
import { predictComfort, mapIntensityToNumber } from './api-service';

const ComfortPredictionForm = () => {
  const lastSubmittedData = useRef(null);
  const [formChanged, setFormChanged] = useState(false);

  // Remove predictionMode – we only support comfort prediction now.
  const [formData, setFormData] = useState({
    temp: 20,
    sun: false,
    headwind: false,
    snow: 'NONE',
    rain: 'NONE',
    fatigued: false,
    hr: 90,
    feels: 'COOL'
  });

  // Updated keys to match the new API schema.
  const [upperClothing, setUpperClothing] = useState({
    t_dress: false,
    t_poly: false,
    t_cot: false,
    sleeves: false,
    j_light: false,
    j_fleece: false,
    j_down: false
  });

  const [lowerClothing, setLowerClothing] = useState({
    shorts: false,
    p_thin: false,
    p_thick: false,
    p_fleece: false,
    p_down: false
  });

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => {
      const updated = {
        ...prev,
        [name]: type === 'checkbox' ? checked : value
      };
      if (lastSubmittedData.current) {
        const prevValue = prev[name];
        const newValue = type === 'checkbox' ? checked : value;
        if (prevValue !== newValue) {
          setFormChanged(true);
        }
      }
      return updated;
    });
  };

  const handleClothingChange = (category, item) => {
    if (category === 'upper') {
      setUpperClothing(prev => {
        const updated = {
          ...prev,
          [item]: !prev[item]
        };
        setFormChanged(true);
        return updated;
      });
    } else if (category === 'lower') {
      setLowerClothing(prev => {
        const updated = {
          ...prev,
          [item]: !prev[item]
        };
        setFormChanged(true);
        return updated;
      });
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    // Prepare one-hot encoded clothing data by merging upper and lower clothing selections.
    // (Here, the boolean values will be converted to 0/1 by the API service.)
    const clothingData = { ...upperClothing, ...lowerClothing };

    // Build the API payload using the updated raw schema:
    // t_dress, t_poly, t_cot, sleeves, j_light, j_fleece, j_down,
    // shorts, p_thin, p_thick, p_fleece, p_down, temp, sun, headwind, snow, rain, fatigued, hr, feels
    const apiData = {
      ...clothingData,
      temp: formData.temp,
      sun: formData.sun ? 1 : 0,
      headwind: formData.headwind ? 1 : 0,
      // Convert the intensity strings using the helper function
      snow: mapIntensityToNumber(formData.snow),
      rain: mapIntensityToNumber(formData.rain),
      fatigued: formData.fatigued ? 1 : 0,
      hr: formData.hr
    };

    if (formChanged || !lastSubmittedData.current) {
      console.log('Form submitted with:', apiData);
      try {
        const result = await predictComfort(apiData);
        if (result.prediction) {
          const feelsMapping = {
            cold: 'COLD',
            cool: 'COOL',
            warm: 'WARM',
            hot: 'HOT'
          };
          setFormData(prev => ({
            ...prev,
            feels: feelsMapping[result.prediction.toLowerCase()] || prev.feels
          }));
        }
        lastSubmittedData.current = { ...apiData };
        setFormChanged(false);
      } catch (error) {
        console.error('Error predicting comfort:', error);
      }
    } else {
      console.log('No changes since last submission, skipping API call');
    }
  };

  const handleReset = () => {
    setFormData({
      temp: 20,
      sun: false,
      headwind: false,
      snow: 'NONE',
      rain: 'NONE',
      fatigued: false,
      hr: 90,
      feels: 'COOL'
    });
    setUpperClothing({
      t_dress: false,
      t_poly: false,
      t_cot: false,
      sleeves: false,
      j_light: false,
      j_fleece: false,
      j_down: false
    });
    setLowerClothing({
      shorts: false,
      p_thin: false,
      p_thick: false,
      p_fleece: false,
      p_down: false
    });
    setFormChanged(true);
    lastSubmittedData.current = null;
  };

  // Update clothing labels to match new keys
  const clothingLabels = {
    t_dress: "Dress Shirt/T-Shirt",
    t_poly: "Polyester T-Shirt",
    t_cot: "Cotton T-Shirt",
    sleeves: "Long Sleeve Shirt",
    j_light: "Light Jacket",
    j_fleece: "Fleece Jacket",
    j_down: "Down Jacket",
    shorts: "Shorts",
    p_thin: "Thin Pants",
    p_thick: "Thick Pants",
    p_fleece: "Fleece Pants",
    p_down: "Insulated/Down Pants"
  };

  return (
    <div className="comfort-prediction-container">
      <h1>Comfort Prediction Tool</h1>

      <form onSubmit={handleSubmit}>
        <div className="form-sections">
          <div className="form-section clothing-section">
            <h2>Clothing Selection</h2>
            <div className="clothing-type">
              <h3>Upper Body</h3>
              <div className="clothing-options">
                {Object.keys(upperClothing).map(item => (
                  <div className="clothing-item" key={item}>
                    <label>
                      <input
                        type="checkbox"
                        checked={upperClothing[item]}
                        onChange={() => handleClothingChange('upper', item)}
                      />
                      {clothingLabels[item]}
                    </label>
                  </div>
                ))}
              </div>
            </div>

            <div className="clothing-type">
              <h3>Lower Body</h3>
              <div className="clothing-options">
                {Object.keys(lowerClothing).map(item => (
                  <div className="clothing-item" key={item}>
                    <label>
                      <input
                        type="checkbox"
                        checked={lowerClothing[item]}
                        onChange={() => handleClothingChange('lower', item)}
                      />
                      {clothingLabels[item]}
                    </label>
                  </div>
                ))}
              </div>
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
            Predict Comfort
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