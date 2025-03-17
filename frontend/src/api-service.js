// const API_BASE_URL = 'http://localhost:8080';
const API_BASE_URL = 'https://temp-feel-api.vercel.app';

export const predictComfort = async (formData) => {
  try {
    // Build model input data using the updated raw schema order:
    // t_dress, t_poly, t_cot, sleeves, j_light, j_fleece, j_down,
    // shorts, p_thin, p_thick, p_fleece, p_down, temp, sun, headwind, snow, rain, fatigued, hr, feels
    const modelInputData = {
      t_dress: formData.t_dress ? 1 : 0,
      t_poly: formData.t_poly ? 1 : 0,
      t_cot: formData.t_cot ? 1 : 0,
      sleeves: formData.sleeves ? 1 : 0,
      j_light: formData.j_light ? 1 : 0,
      j_fleece: formData.j_fleece ? 1 : 0,
      j_down: formData.j_down ? 1 : 0,
      shorts: formData.shorts ? 1 : 0,
      p_thin: formData.p_thin ? 1 : 0,
      p_thick: formData.p_thick ? 1 : 0,
      p_fleece: formData.p_fleece ? 1 : 0,
      p_down: formData.p_down ? 1 : 0,
      temp: formData.temp,
      sun: formData.sun ? 1 : 0,
      headwind: formData.headwind ? 1 : 0,
      snow: formData.snow,
      rain: formData.rain,
      fatigued: formData.fatigued ? 1 : 0,
      hr: formData.hr
    };

    const response = await fetch(`${API_BASE_URL}/predict/feels`, {
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

export const mapIntensityToNumber = (intensity) => {
  const intensityMap = {
    'NONE': 0,
    'LIGHT': 1,
    'MEDIUM': 2,
    'HEAVY': 3
  };
  return intensityMap[intensity] || 0;
};