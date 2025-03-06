package api;

import java.util.HashMap;
import java.util.Map;

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
        // Required fields that need validation use wrapper types
        private final Double upperClo;  // Using wrapper types allows null
        private final Double lowerClo;
        private final Integer temp;
        private final Feeling feels;  // Could be null if not predicting
        
        // Optional fields use primitives with defaults
        private final boolean sun;
        private final boolean headwind;
        private final Intensity snow;
        private final Intensity rain;
        private final boolean fatigued;
        private final int hr;
    
        private TempFeelConfig(Builder builder) {
            // Copy all values directly - no defaults applied during construction
            this.upperClo = builder.upperClo;
            this.lowerClo = builder.lowerClo;
            this.temp = builder.temp;
            this.sun = builder.sun;
            this.headwind = builder.headwind;
            this.snow = builder.snow;
            this.rain = builder.rain;
            this.fatigued = builder.fatigued;
            this.hr = builder.hr;
            this.feels = builder.feels;
        }
    
        public Builder toBuilder() {
            return new Builder(this);
        }
    
        // Domain-specific validation methods
        public boolean canPredictFeeling() {
            return upperClo != null && lowerClo != null && temp != null;
        }
    
        // Getters with appropriate default handling
        public double getUpperClo() { 
            return upperClo != null ? upperClo : 0.08; 
        }
        
        public double getLowerClo() { 
            return lowerClo != null ? lowerClo : 0.15; 
        }
        
        public int getTemp() { 
            return temp != null ? temp : 20; 
        }
        
        public boolean isSun() { return sun; }
        public boolean isHeadwind() { return headwind; }
        public Intensity getSnow() { return snow; }
        public Intensity getRain() { return rain; }
        public boolean isFatigued() { return fatigued; }
        public int getHr() { return hr; }
        public Feeling getFeels() { return feels; }
    
        // Map generation provides defaults for null values
        public Map<String, Object> toMap() {
            Map<String, Object> map = new HashMap<>();
            
            map.put("upperClo", getUpperClo());
            map.put("lowerClo", getLowerClo());
            map.put("temp", getTemp());
            map.put("sun", sun ? 1 : 0);
            map.put("headwind", headwind ? 1 : 0);
            map.put("snow", snow.ordinal());
            map.put("rain", rain.ordinal());
            map.put("fatigued", fatigued ? 1 : 0);
            map.put("hr", hr);
            if (feels != null) {
                map.put("feels", feels.ordinal());
            }
            
            return map;
        }
    
        public static class Builder {
            // Required fields start as null
            private Double upperClo = null;
            private Double lowerClo = null;
            private Integer temp = null;
            
            // Optional fields have defaults
            private boolean sun = false;
            private boolean headwind = false;
            private Intensity snow = Intensity.NONE;
            private Intensity rain = Intensity.NONE;
            private boolean fatigued = false;
            private int hr = 80;
            private Feeling feels = null;
    
            public Builder() {}
            
            private Builder(TempFeelConfig config) {
                this.upperClo = config.upperClo;
                this.lowerClo = config.lowerClo;
                this.temp = config.temp;
                this.sun = config.sun;
                this.headwind = config.headwind;
                this.snow = config.snow;
                this.rain = config.rain;
                this.fatigued = config.fatigued;
                this.hr = config.hr;
                this.feels = config.feels;
            }
            
            public Builder upperClo(double val) {
                this.upperClo = val;
                return this;
            }
            
            public Builder lowerClo(double val) {
                this.lowerClo = val;
                return this;
            }
            
            public Builder clo(double val) {
                return upperClo(val).lowerClo(val);
            }
            
            public Builder temp(int val) {
                this.temp = val;
                return this;
            }
            
            public Builder sun() {
                this.sun = true;
                return this;
            }
            
            public Builder noSun() {
                this.sun = false;
                return this;
            }
            
            public Builder headwind(boolean val) {
                this.headwind = val;
                return this;
            }
            
            public Builder snow(Intensity val) {
                this.snow = val;
                return this;
            }
            
            public Builder rain(Intensity val) {
                this.rain = val;
                return this;
            }
            
            public Builder fatigued(boolean val) {
                this.fatigued = val;
                return this;
            }
            
            public Builder hr(int val) {
                this.hr = val;
                return this;
            }
            
            public Builder feeling(Feeling val) {
                this.feels = val;
                return this;
            }
            
            public TempFeelConfig build() {
                return new TempFeelConfig(this);
            }
        }
    }

    // Static utility class: prevent instantiation
    private TempFeel() {}

    public static TempFeelConfig.Builder builder() {
        return new TempFeelConfig.Builder();
    }

    public static Feeling getFeeling(TempFeelConfig c) {
        if (!c.canPredictFeeling()) {
            throw new IllegalArgumentException("Config is missing required fields for predicting feeling");
        }

        try {
            // Convert config to map
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


        return 80; // mock
    }

    public static double getUpperClo(TempFeelConfig c) {
        // Validate that all required fields are set


        return 1.00; // mock
    }
}