// api-service.js
const API_BASE_URL = 'http://localhost:8080/';

/**
 * Predicts comfort level based on clothing and environmental factors
 */
export const predictComfort = async (formData) => {
    try {
      // Extract only the fields needed by the model
      const modelInputData = {
        upperClo: formData.clo_upr,
        lowerClo: formData.clo_lwr,
        temp: formData.temp,
        sun: formData.sun ? 1 : 0,
        headwind: formData.headwind ? 1 : 0,
        snow: mapIntensityToNumber(formData.snow),
        rain: mapIntensityToNumber(formData.rain),
        fatigued: formData.fatigued ? 1 : 0,
        hr: formData.hr,
        feels: mapFeelsToNumber(formData.feels)
      };
  
      const response = await fetch(`${API_BASE_URL}/predict-feels`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ instances: [modelInputData] }),
      });
      
      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error predicting comfort:', error);
      throw error;
    }
  };

/**
 * Predicts recommended clothing based on environmental factors
 */
export const predictClothing = async (formData) => {
    try {
      // Extract only the fields needed by the model
      const modelInputData = {
        temp: formData.temp,
        sun: formData.sun ? 1 : 0,
        headwind: formData.headwind ? 1 : 0,
        snow: mapIntensityToNumber(formData.snow),
        rain: mapIntensityToNumber(formData.rain),
        fatigued: formData.fatigued ? 1 : 0,
        hr: formData.hr,
        feels: mapFeelsToNumber(formData.feels)
      };

      const response = await fetch(`${API_BASE_URL}/predict-clothing`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ instances: [modelInputData] }),
      });
      
      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error predicting clothing:', error);
      throw error;
    }
  };
  
  // Helper function to map feels values to numbers
  function mapFeelsToNumber(feels) {
    const feelsMap = {
      'COLD': 0,
      'COOL': 1,
      'WARM': 2,
      'HOT': 3
    };
    return feelsMap[feels] || 0;
  }
  
  // Helper function to map intensity to numbers (0-3)
  function mapIntensityToNumber(intensity) {
    const intensityMap = {
      'NONE': 0,
      'LIGHT': 1,
      'MODERATE': 2,
      'HEAVY': 3
    };
    return intensityMap[intensity] || 0;
  }