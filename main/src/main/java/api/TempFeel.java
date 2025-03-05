package api;

import java.io.IOException;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.util.HashMap;
import java.util.Map;
import java.util.List;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.fasterxml.jackson.databind.node.ArrayNode;

/**
 * A static utility class that allows clients to retrieve predictions from the trained classifier.
 * 
 * Example use:
 * TempFeelConfig c = TempFeel.newConfig().upperClo(0.3).lowerClo(0.12).sun().headwind(false).fatigued(true);
 * Feeling f = TempFeel.getFeeling(c);
 * System.out.println("It will feel: "+f);
 * 
 */
public final class TempFeel {
    // API configuration
    private static final String API_BASE_URL = "http://localhost:5000";
    private static final String PREDICT_ENDPOINT = "/predict";
    private static final HttpClient HTTP_CLIENT = HttpClient.newHttpClient();
    private static final ObjectMapper JSON_MAPPER = new ObjectMapper();

    public enum Intensity { NONE, LIGHT, MEDIUM, HEAVY };
    public enum Feeling { COLD, COOL, WARM, HOT };

    public static final class TempFeelConfig {
        private enum Fields {upperClo, lowerClo, temp, sun, headwind, snow, rain, fatigued, hr, feels}
        
        // All fields have default values
        private final double upperClo;
        private final double lowerClo;
        private final int temp;
        private final boolean sun;
        private final boolean headwind;
        private final Intensity snow;
        private final Intensity rain;
        private final boolean fatigued;
        private final int hr;
        private final Feeling feels;

        // Default values for all fields
        private static final double DEFAULT_UPPER_CLO = 0.08;
        private static final double DEFAULT_LOWER_CLO = 0.15;
        private static final int DEFAULT_TEMP = 20;
        private static final boolean DEFAULT_SUN = false;
        private static final boolean DEFAULT_HEADWIND = false;
        private static final Intensity DEFAULT_SNOW = Intensity.NONE;
        private static final Intensity DEFAULT_RAIN = Intensity.NONE;
        private static final boolean DEFAULT_FATIGUED = false;
        private static final int DEFAULT_HR = 80;
        private static final Feeling DEFAULT_FEELS = Feeling.COOL;

        // Private constructor with all parameters
        private TempFeelConfig(double upperClo, double lowerClo, int temp, 
                              boolean sun, boolean headwind, Intensity snow, 
                              Intensity rain, boolean fatigued, int hr, Feeling feels) {
            this.upperClo = upperClo;
            this.lowerClo = lowerClo;
            this.temp = temp;
            this.sun = sun;
            this.headwind = headwind;
            this.snow = snow;
            this.rain = rain;
            this.fatigued = fatigued;
            this.hr = hr;
            this.feels = feels;
        }
        
        // Factory method for initial config with defaults
        static TempFeelConfig create() {
            return new TempFeelConfig(
                DEFAULT_UPPER_CLO, DEFAULT_LOWER_CLO, DEFAULT_TEMP,
                DEFAULT_SUN, DEFAULT_HEADWIND, DEFAULT_SNOW,
                DEFAULT_RAIN, DEFAULT_FATIGUED, DEFAULT_HR, DEFAULT_FEELS);
        }
        
        // Each method returns a new instance with the updated value
        public TempFeelConfig upperClo(double val) {
            return new TempFeelConfig(val, lowerClo, temp, sun, headwind, snow, rain, fatigued, hr, feels);
        }

        public TempFeelConfig lowerClo(double val) {
            return new TempFeelConfig(upperClo, val, temp, sun, headwind, snow, rain, fatigued, hr, feels);
        }

        public TempFeelConfig temp(int val) {
            return new TempFeelConfig(upperClo, lowerClo, val, sun, headwind, snow, rain, fatigued, hr, feels);
        }

        public TempFeelConfig sun() {
            return new TempFeelConfig(upperClo, lowerClo, temp, true, headwind, snow, rain, fatigued, hr, feels);
        }

        public TempFeelConfig noSun() {
            return new TempFeelConfig(upperClo, lowerClo, temp, false, headwind, snow, rain, fatigued, hr, feels);
        }

        public TempFeelConfig headwind(boolean b) {
            return new TempFeelConfig(upperClo, lowerClo, temp, sun, b, snow, rain, fatigued, hr, feels);
        }

        public TempFeelConfig snow(Intensity i) {
            return new TempFeelConfig(upperClo, lowerClo, temp, sun, headwind, i, rain, fatigued, hr, feels);
        }

        public TempFeelConfig rain(Intensity i) {
            return new TempFeelConfig(upperClo, lowerClo, temp, sun, headwind, snow, i, fatigued, hr, feels);
        }

        public TempFeelConfig fatigued(boolean b) {
            return new TempFeelConfig(upperClo, lowerClo, temp, sun, headwind, snow, rain, b, hr, feels);
        }

        public TempFeelConfig hr(int val) {
            return new TempFeelConfig(upperClo, lowerClo, temp, sun, headwind, snow, rain, fatigued, val, feels);
        }

        public TempFeelConfig feeling(Feeling f) {
            return new TempFeelConfig(upperClo, lowerClo, temp, sun, headwind, snow, rain, fatigued, hr, f);
        }
        
        // Generate Map for API request, excluding specified field (if any)
        public Map<String, Object> toApiMap(Fields fieldToExclude) {
            Map<String, Object> map = new HashMap<>();
            
            // Convert to proper data types for API
            if (fieldToExclude != Fields.upperClo) map.put("upperClo", upperClo);
            if (fieldToExclude != Fields.lowerClo) map.put("lowerClo", lowerClo);
            if (fieldToExclude != Fields.temp) map.put("temp", temp);
            if (fieldToExclude != Fields.sun) map.put("sun", sun ? 1 : 0);  // Convert boolean to int
            if (fieldToExclude != Fields.headwind) map.put("headwind", headwind ? 1 : 0);
            
            // Convert enums to integers for API
            if (fieldToExclude != Fields.snow) map.put("snow", snow.ordinal());
            if (fieldToExclude != Fields.rain) map.put("rain", rain.ordinal());
            
            if (fieldToExclude != Fields.fatigued) map.put("fatigued", fatigued ? 1 : 0);
            if (fieldToExclude != Fields.hr) map.put("hr", hr);
            if (fieldToExclude != Fields.feels) map.put("feels", feels.ordinal());

            if (map.keySet().size() != 9) {
                throw new IllegalStateException("Missing fields in TempFeelConfig");
            }
            
            return map;
        }
        
        // Convenience method to get map with all fields
        public Map<String, Object> toApiMap() {
            return toApiMap(null);
        }
    }

    // Static utility class: prevent instantiation
    private TempFeel() {}

    public static TempFeelConfig newConfig() {
        return TempFeelConfig.create();
    }

    public static Feeling getFeeling(TempFeelConfig c) {
        try {
            // Exclude the 'feels' field since that's what we're predicting
            Map<String, Object> data = c.toApiMap(TempFeelConfig.Fields.feels);
            
            // Call Python API and get result
            Map<String, Object> result = callPredictionApi(data);
            
            // Parse the result
            if (result.containsKey("prediction_labels") && result.get("prediction_labels") instanceof List) {
                @SuppressWarnings("unchecked")
                List<String> labels = (List<String>) result.get("prediction_labels");
                if (!labels.isEmpty()) {
                    String label = labels.get(0);
                    return Feeling.valueOf(label.toUpperCase());
                }
            }
            
            // Fallback to using numeric prediction
            if (result.containsKey("predictions") && result.get("predictions") instanceof List) {
                @SuppressWarnings("unchecked")
                List<Integer> predictions = (List<Integer>) result.get("predictions");
                if (!predictions.isEmpty()) {
                    int prediction = predictions.get(0);
                    return intToFeeling(prediction);
                }
            }
            
            throw new RuntimeException("Unable to parse prediction result");
        } catch (Exception e) {
            System.err.println("Error getting feeling prediction: " + e.getMessage());
            e.printStackTrace();
            return Feeling.COOL; // Default as fallback
        }
    }

    public static int getHR(TempFeelConfig c) {
        // Since HR prediction isn't yet implemented in the Python API, return a mock value
        // In a real implementation, this would be similar to getFeeling but for HR
        return 80; // mock
    }

    public static double getUpperClo(TempFeelConfig c) {
        // Since upperClo prediction isn't yet implemented in the Python API, return a mock value
        // In a real implementation, this would be similar to getFeeling but for upperClo
        return 1.00; // mock
    }
    
    private static Map<String, Object> callPredictionApi(Map<String, Object> data) throws IOException, InterruptedException {
        // Create the request body
        ObjectNode requestBody = JSON_MAPPER.createObjectNode();
        ArrayNode instances = requestBody.putArray("instances");
        ObjectNode instance = instances.addObject();
        
        // Add all data fields to the instance
        for (Map.Entry<String, Object> entry : data.entrySet()) {
            String key = entry.getKey();
            Object value = entry.getValue();
            
            if (value instanceof Integer) {
                instance.put(key, (Integer) value);
            } else if (value instanceof Double) {
                instance.put(key, (Double) value);
            } else if (value instanceof Boolean) {
                instance.put(key, (Boolean) value);
            } else {
                instance.put(key, String.valueOf(value));
            }
        }
        
        // Convert to JSON string
        String requestJson = JSON_MAPPER.writeValueAsString(requestBody);
        
        // Build HTTP request
        HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create(API_BASE_URL + PREDICT_ENDPOINT))
                .header("Content-Type", "application/json")
                .POST(HttpRequest.BodyPublishers.ofString(requestJson))
                .build();
        
        // Send request and get response
        HttpResponse<String> response = HTTP_CLIENT.send(request, HttpResponse.BodyHandlers.ofString());
        
        // Check response status
        if (response.statusCode() != 200) {
            throw new IOException("API request failed with status code: " + response.statusCode() + 
                                 ", body: " + response.body());
        }
        
        // Parse response
        @SuppressWarnings("unchecked")
        Map<String, Object> result = JSON_MAPPER.readValue(response.body(), Map.class);
        return result;
    }
    
    private static Feeling intToFeeling(int feelingCode) {
        switch (feelingCode) {
            case 0: return Feeling.COLD;
            case 1: return Feeling.COOL;
            case 2: return Feeling.WARM;
            case 3: return Feeling.HOT;
            default: return Feeling.COOL; // Default
        }
    }
}