package main.api;

import java.util.HashMap;

/**
 * A static utility class that allows clients to retrieve predictions from the trained classifier.
 * 
 * Example use:
 * TempFeelConfig c = TempFeel.newConfig();
 * c.upperClo(0.3).lowerClo(0.12).sun().headwind(false).fatigued(true);
 * Feeling f = TempFeel.getFeeling(c);
 * System.out.println("It will feel: "+f);
 * 
 */
public final class TempFeel {
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
        
        // Generate HashMap for serialization, excluding specified field (if any)
        public HashMap<Fields, String> toMap(Fields fieldToExclude) {
            HashMap<Fields, String> map = new HashMap<>();
            
            if (fieldToExclude != Fields.upperClo) map.put(Fields.upperClo, Double.valueOf(upperClo).toString());
            if (fieldToExclude != Fields.lowerClo) map.put(Fields.lowerClo, Double.valueOf(lowerClo).toString());
            if (fieldToExclude != Fields.temp) map.put(Fields.temp, Integer.valueOf(temp).toString());
            if (fieldToExclude != Fields.sun) map.put(Fields.sun, Boolean.valueOf(sun).toString());
            if (fieldToExclude != Fields.headwind) map.put(Fields.headwind, Boolean.valueOf(headwind).toString());
            if (fieldToExclude != Fields.snow) map.put(Fields.snow, snow.toString());
            if (fieldToExclude != Fields.rain) map.put(Fields.rain, rain.toString());
            if (fieldToExclude != Fields.fatigued) map.put(Fields.fatigued, Boolean.valueOf(fatigued).toString());
            if (fieldToExclude != Fields.hr) map.put(Fields.hr, Integer.valueOf(hr).toString());
            if (fieldToExclude != Fields.feels) map.put(Fields.feels, feels.toString());
            
            return map;
        }
        
        // Convenience method to get map with all fields
        public HashMap<Fields, String> toMap() {
            return toMap(null);
        }
    }

    // Static utility class: prevent instantiation
    private TempFeel() {}

    public static TempFeelConfig newConfig() {
        return TempFeelConfig.create();
    }

    public static Feeling getFeeling(TempFeelConfig c) {
        // Exclude the 'feels' field since that's what we're predicting
        HashMap<TempFeelConfig.Fields, String> data = c.toMap(TempFeelConfig.Fields.feels);
        
        // In a real implementation:
        // String json = convertToJson(data);
        // String result = callPythonScript(json);
        // return parseFeeling(result);
        
        return Feeling.COLD; // mock, should make a call to the python script
    }

    public static int getHR(TempFeelConfig c) {
        // Exclude the 'hr' field since that's what we're predicting
        HashMap<TempFeelConfig.Fields, String> data = c.toMap(TempFeelConfig.Fields.hr);
        
        // In a real implementation, similar to getFeeling
        
        return 80; // mock
    }

    public static double getUpperClo(TempFeelConfig c) {
        // Exclude the 'upperClo' field since that's what we're predicting
        HashMap<TempFeelConfig.Fields, String> data = c.toMap(TempFeelConfig.Fields.upperClo);
        
        // In a real implementation, similar to getFeeling
        
        return 1.00; // mock, should make a call to the python script
    }
    
    // Helper methods for when Python integration is implemented
    /*
    private static String convertToJson(HashMap<TempFeelConfig.Fields, String> data) {
        // Implementation to convert the map to JSON
        return "{}";
    }
    
    private static String callPythonScript(String jsonInput) {
        // Implementation to call Python script
        return "{}";
    }
    
    private static Feeling parseFeeling(String jsonResult) {
        // Implementation to parse feeling from result
        return Feeling.COLD;
    }
    */
}