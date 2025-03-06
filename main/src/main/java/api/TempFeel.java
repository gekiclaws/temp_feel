package api;

import java.io.IOException;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.util.ArrayList;
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
    private static final String API_BASE_URL = "http://localhost:8080";
    private static final ApiClient API_CLIENT = new ApiClient(API_BASE_URL);

    public enum Intensity { NONE, LIGHT, MEDIUM, HEAVY };
    public enum Feeling {
        COLD, COOL, WARM, HOT;

        // From string to feeling
        public static Feeling fromString(String s) {
            switch (s) {
                case "COLD": return COLD;
                case "COOL": return COOL;
                case "WARM": return WARM;
                case "HOT": return HOT;
                default: return COOL;  // Default
            }
        }
    };

    public static final class TempFeelConfig {
        private enum Fields {upperClo, lowerClo, temp, sun, headwind, snow, rain, fatigued, hr, feels}
        
        // All fields for the configuration
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

        // Flags for tracking explicitly set fields
        private final boolean upperCloSet;
        private final boolean lowerCloSet;
        private final boolean tempSet;
        private final boolean feelsSet;

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
                      Intensity rain, boolean fatigued, int hr, Feeling feels,
                      boolean upperCloSet, boolean lowerCloSet, boolean tempSet,
                      boolean feelsSet) {
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
            
            this.upperCloSet = upperCloSet;
            this.lowerCloSet = lowerCloSet;
            this.tempSet = tempSet;
            this.feelsSet = feelsSet;
        }

        // Factory method for initial config with defaults
        static TempFeelConfig create() {
            return new TempFeelConfig(
                DEFAULT_UPPER_CLO, DEFAULT_LOWER_CLO, DEFAULT_TEMP,
                DEFAULT_SUN, DEFAULT_HEADWIND, DEFAULT_SNOW,
                DEFAULT_RAIN, DEFAULT_FATIGUED, DEFAULT_HR, DEFAULT_FEELS,
                false, false, false, false);  // No fields set initially
        }
        
        // Each method returns a new instance with the updated value
        public TempFeelConfig upperClo(double val) {
            return new TempFeelConfig(val, lowerClo, temp, sun, headwind, snow, rain, fatigued, hr, feels,
                                    true, lowerCloSet, tempSet, feelsSet);
        }
        
        public TempFeelConfig lowerClo(double val) {
            return new TempFeelConfig(upperClo, val, temp, sun, headwind, snow, rain, fatigued, hr, feels,
                                    upperCloSet, true, tempSet, feelsSet);
        }
        
        public TempFeelConfig temp(int val) {
            return new TempFeelConfig(upperClo, lowerClo, temp, sun, headwind, snow, rain, fatigued, hr, feels,
                                    upperCloSet, lowerCloSet, true, feelsSet);
        }

        public TempFeelConfig sun() {
            return new TempFeelConfig(upperClo, lowerClo, temp, true, headwind, snow, rain, fatigued, hr, feels,
                                    upperCloSet, lowerCloSet, tempSet, feelsSet);
        }

        public TempFeelConfig noSun() {
            return new TempFeelConfig(upperClo, lowerClo, temp, false, headwind, snow, rain, fatigued, hr, feels,
            upperCloSet, lowerCloSet, tempSet, feelsSet);
        }

        public TempFeelConfig headwind(boolean b) {
            return new TempFeelConfig(upperClo, lowerClo, temp, sun, b, snow, rain, fatigued, hr, feels,
            upperCloSet, lowerCloSet, tempSet, feelsSet);
        }

        public TempFeelConfig snow(Intensity i) {
            return new TempFeelConfig(upperClo, lowerClo, temp, sun, headwind, i, rain, fatigued, hr, feels,
            upperCloSet, lowerCloSet, tempSet, feelsSet);
        }

        public TempFeelConfig rain(Intensity i) {
            return new TempFeelConfig(upperClo, lowerClo, temp, sun, headwind, snow, i, fatigued, hr, feels,
            upperCloSet, lowerCloSet, tempSet, feelsSet);
        }

        public TempFeelConfig fatigued(boolean b) {
            return new TempFeelConfig(upperClo, lowerClo, temp, sun, headwind, snow, rain, b, hr, feels,
            upperCloSet, lowerCloSet, tempSet, feelsSet);
        }

        public TempFeelConfig hr(int val) {
            return new TempFeelConfig(upperClo, lowerClo, temp, sun, headwind, snow, rain, fatigued, val, feels,
            upperCloSet, lowerCloSet, tempSet, feelsSet);
        }

        public TempFeelConfig feeling(Feeling f) {
            return new TempFeelConfig(upperClo, lowerClo, temp, sun, headwind, snow, rain, fatigued, hr, f,
            upperCloSet, lowerCloSet, tempSet, true);
        }
        
        // Generate complete Map for API request
        public Map<String, Object> toMap() {
            Map<String, Object> map = new HashMap<>();
            
            // Convert to proper data types for API
            map.put("upperClo", upperClo);
            map.put("lowerClo", lowerClo);
            map.put("temp", temp);
            map.put("sun", sun ? 1 : 0);  // Convert boolean to int
            map.put("headwind", headwind ? 1 : 0);
            map.put("snow", snow.ordinal());
            map.put("rain", rain.ordinal());
            map.put("fatigued", fatigued ? 1 : 0);
            map.put("hr", hr);
            map.put("feels", feels.ordinal());
            
            return map;
        }

        private void validate(Fields fieldToExclude) throws IllegalStateException {
            List<String> missingFields = new ArrayList<>();
            
            if (fieldToExclude != Fields.upperClo && !upperCloSet) missingFields.add("upperClo");
            if (fieldToExclude != Fields.lowerClo && !lowerCloSet) missingFields.add("lowerClo");
            if (fieldToExclude != Fields.temp && !tempSet) missingFields.add("temp");
            if (fieldToExclude != Fields.feels && !feelsSet) missingFields.add("feels");
            
            if (!missingFields.isEmpty()) {
                throw new IllegalStateException("Missing required parameters: " + 
                                            String.join(", ", missingFields));
            }
        }
    }

    // Static utility class: prevent instantiation
    private TempFeel() {}

    public static TempFeelConfig newConfig() {
        return TempFeelConfig.create();
    }

    public static Feeling getFeeling(TempFeelConfig c) {
        try {
            // Validate that all required fields are set
            c.validate(TempFeelConfig.Fields.feels);

            // Exclude the 'feels' field since that's what we're predicting
            Map<String, Object> data = c.toMap();
            
            // Call the API using the client
            Map<String, Object> result = API_CLIENT.predict("/predict", data);
            
            // Parse result
            String predictionLabel = result.get("prediction_label").toString();
            return Feeling.fromString(predictionLabel);
        } catch (Exception e) {
            throw new RuntimeException("Error getting feeling prediction: " + e.getMessage(), e);
        }
    }

    public static int getHR(TempFeelConfig c) {
        // Validate that all required fields are set
        c.validate(TempFeelConfig.Fields.hr);

        return 80; // mock
    }

    public static double getUpperClo(TempFeelConfig c) {
        // Validate that all required fields are set
        c.validate(TempFeelConfig.Fields.upperClo);

        return 1.00; // mock
    }
}