import React, { useState, useEffect, useRef } from 'react';
import './App.css';
import { predictComfort, predictClothing } from './api-service';

const ComfortPredictionForm = () => {
  // Add a ref to store the last submitted form data
  const lastSubmittedData = useRef(null);
  // Add state to track if form has changed since last submission
  const [formChanged, setFormChanged] = useState(false);
  // Add state to store predicted clo values
  const [predictedClo, setPredictedClo] = useState(null);

  const [formData, setFormData] = useState({
    temp: 20,
    sun: false,
    headwind: false,
    snow: 'NONE',
    rain: 'NONE',
    fatigued: false,
    hr: 90,
    feels: 'COOL',
    predictionMode: 'comfort'
  });

  const [upperClothing, setUpperClothing] = useState({
    t_polo: false,
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

  const clothingValues = {
    // Upper body
    t_polo: 0.05,
    t_poly: 0.08,
    t_cot: 0.09,
    sleeves: 0.2,
    j_light: 0.5,
    j_fleece: 0.7,
    j_down: 0.9,
    
    // Lower body
    shorts: 0.06,
    p_thin: 0.15,
    p_thick: 0.24,
    p_fleece: 0.8,
    p_down: 0.9
  };

  // Calculate clo values whenever clothing selections change
  useEffect(() => {
    let clo_upr = Object.entries(upperClothing)
      .filter(([_, selected]) => selected)
      .reduce((sum, [item, _]) => sum + clothingValues[item], 0);
    
    let clo_lwr = Object.entries(lowerClothing)
      .filter(([_, selected]) => selected)
      .reduce((sum, [item, _]) => sum + clothingValues[item], 0);
    
    setFormData(prev => {
      const updated = {
        ...prev,
        clo_upr,
        clo_lwr
      };
      
      // Mark form as changed if clothing changed
      if (lastSubmittedData.current && 
          (lastSubmittedData.current.clo_upr !== clo_upr || 
           lastSubmittedData.current.clo_lwr !== clo_lwr)) {
        setFormChanged(true);
      }
      
      return updated;
    });
  }, [upperClothing, lowerClothing]);

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    
    setFormData(prev => {
      const updated = {
        ...prev,
        [name]: type === 'checkbox' ? checked : value
      };
      
      // Clear predicted clo values when switching modes
      if (name === 'predictionMode') {
        setPredictedClo(null);
      }
      
      // Mark form as changed
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
    
    // Prepare API call with complete data
    const apiData = {
      ...formData,
      upper_clothing: Object.keys(upperClothing).filter(item => upperClothing[item]),
      lower_clothing: Object.keys(lowerClothing).filter(item => lowerClothing[item])
    };
    
    // Only make API call if form has changed since last submission (but don't show this to user)
    if (formChanged || !lastSubmittedData.current) {
      console.log('Form submitted with changes:', apiData);
      
      try {
        let result;
        if (formData.predictionMode === 'comfort') {
          // Call comfort prediction API
          result = await predictComfort(apiData);
          
          if (result.prediction) {
            // Map the prediction label to the corresponding feels value
            const feelsMapping = {
              'cold': 'COLD',
              'cool': 'COOL',
              'warm': 'WARM',
              'hot': 'HOT'
            };
            
            // Update the feels value based on the prediction
            setFormData(prev => ({
              ...prev,
              feels: feelsMapping[result.prediction.toLowerCase()] || prev.feels
            }));
          }
        } else {
          // Call clothing prediction API
          result = await predictClothing(apiData);
          
          if (result.predictions) {
            // Store predicted clo values
            setPredictedClo(result.predictions);
            
            // Get recommended clothing based on clo values
            const recommendedUpper = Object.entries(clothingValues)
              .filter(([key]) => key.startsWith('t_') || key.startsWith('j_'))
              .reduce((closest, [item, value]) => {
                return Math.abs(value - result.predictions.upr_clo) < Math.abs(closest.value - result.predictions.upr_clo)
                  ? { item, value }
                  : closest;
              }, { item: '', value: Infinity });

            const recommendedLower = Object.entries(clothingValues)
              .filter(([key]) => !key.startsWith('t_') && !key.startsWith('j_'))
              .reduce((closest, [item, value]) => {
                return Math.abs(value - result.predictions.lwr_clo) < Math.abs(closest.value - result.predictions.lwr_clo)
                  ? { item, value }
                  : closest;
              }, { item: '', value: Infinity });

            // Update clothing selections
            setUpperClothing(prev => {
              const updated = {};
              Object.keys(prev).forEach(key => {
                updated[key] = key === recommendedUpper.item;
              });
              return updated;
            });

            setLowerClothing(prev => {
              const updated = {};
              Object.keys(prev).forEach(key => {
                updated[key] = key === recommendedLower.item;
              });
              return updated;
            });
          }
        }
        
        // Store the current data as last submitted
        lastSubmittedData.current = {...apiData};
        
        // Reset the changed flag
        setFormChanged(false);
      } catch (error) {
        console.error('Error predicting comfort:', error);
        // Handle error (could add an error state here if needed)
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
      feels: 'COOL',
      predictionMode: 'comfort'
    });
    
    setUpperClothing({
      t_polo: false,
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
    
    // Clear predicted clo values
    setPredictedClo(null);
    
    // Mark as changed after reset
    setFormChanged(true);
    
    // Clear the last submitted data
    lastSubmittedData.current = null;
  };

  const clothingLabels = {
    t_polo: "Polo Shirt",
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
          {formData.predictionMode === 'comfort' && (
            <div className="form-section clothing-section">
              <h2>Clothing</h2>
              
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
                          disabled={formData.predictionMode === 'clothing'}
                        />
                        {clothingLabels[item]}
                      </label>
                    </div>
                  ))}
                </div>
                <div className="calculated-value">
                  Insulation value: <strong>{formData.clo_upr?.toFixed(2) || 0}</strong> clo
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
                          disabled={formData.predictionMode === 'clothing'}
                        />
                        {clothingLabels[item]}
                      </label>
                    </div>
                  ))}
                </div>
                <div className="calculated-value">
                  Insulation value: <strong>{formData.clo_lwr?.toFixed(2) || 0}</strong> clo
                </div>
              </div>
            </div>
          )}

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
                className={formData.predictionMode === 'comfort' ? 'highlight-feels' : ''}
              >
                <option value="COLD">Cold</option>
                <option value="COOL">Cool</option>
                <option value="WARM">Warm</option>
                <option value="HOT">Hot</option>
              </select>
            </div>
          </div>
        </div>

        {formData.predictionMode === 'clothing' && predictedClo && (
          <div className="predicted-clo-values">
            <h3>Clothing Insulation you need</h3>
            <div>Upper body: <strong>{predictedClo.upr_clo.toFixed(2)}</strong> clo</div>
            <div>Lower body: <strong>{predictedClo.lwr_clo.toFixed(2)}</strong> clo</div>
          </div>
        )}

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