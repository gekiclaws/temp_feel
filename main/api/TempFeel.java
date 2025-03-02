package main.api;

import java.util.HashMap;
import java.util.Set;
import java.lang.IllegalStateException;

/*
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

    public final class TempFeelConfig {
        private enum Fields {upperClo, lowerClo, temp, sun, headwind, snow, rain, fatigued, hr, feels}
        private HashMap<Fields, String> h = new HashMap<>();

        private double upperClo = -1; // required field
        private double lowerClo = -1; // required field
        private byte temp = -128; // required field
        private boolean sun = false; // default: false
        private boolean headwind = false; // default: false
        private Intensity snow = Intensity.NONE; // default: none
        private Intensity rain = Intensity.NONE; // default: none
        private boolean fatigued = false; // default: false
        private byte hr = 80; // default: 80
        private Feeling feels;

        private TempFeelConfig() {
            h.put(Fields.sun, Boolean.valueOf(this.sun).toString());
            h.put(Fields.headwind, Boolean.valueOf(this.headwind).toString());
            h.put(Fields.snow, this.snow.toString());
            h.put(Fields.rain, this.rain.toString());
            h.put(Fields.fatigued, Boolean.valueOf(this.fatigued).toString());
            h.put(Fields.hr, Byte.valueOf(this.hr).toString());
        };

        public TempFeelConfig upperClo(double val) {
            this.upperClo = val; h.put(Fields.upperClo, Double.valueOf(this.upperClo).toString()); return this; }

        public TempFeelConfig lowerClo(double val) { 
            this.lowerClo = val; h.put(Fields.lowerClo, Double.valueOf(this.lowerClo).toString()); return this; }

        /**
         * Updates the config temperature.
         * @param temp temperature in Celsius
         */
        public TempFeelConfig temp(byte temp) { 
            this.temp = temp; h.put(Fields.temp, Byte.valueOf(this.temp).toString()); return this; }

        public TempFeelConfig sun() {
            this.sun = true; h.put(Fields.sun, Boolean.valueOf(this.sun).toString()); return this; }

        public TempFeelConfig noSun() {
            this.sun = false; h.put(Fields.sun, Boolean.valueOf(this.sun).toString()); return this; }

        public TempFeelConfig headwind(boolean b) { 
            this.headwind = b; h.put(Fields.headwind, Boolean.valueOf(this.headwind).toString()); return this; }

        public TempFeelConfig snow(Intensity i) { 
            this.snow = i; h.put(Fields.snow, this.snow.toString()); return this; }

        public TempFeelConfig rain(Intensity i) { 
            this.rain = i; h.put(Fields.rain, this.rain.toString()); return this; }

        public TempFeelConfig fatigued(boolean b) { 
            this.fatigued = b; h.put(Fields.fatigued, Boolean.valueOf(this.fatigued).toString()); return this; }

        public TempFeelConfig hr(byte hr) { 
            this.hr = hr; h.put(Fields.hr, Byte.valueOf(this.hr).toString()); return this; }

        public TempFeelConfig feeling(Feeling f) {
            this.feels = f; h.put(Fields.feels, this.feels.toString()); return this; }
    }

    // Static utility class: prevent instantiation
    private TempFeel() {}

    public static TempFeelConfig newConfig(){
        TempFeel x = new TempFeel();
        return x.new TempFeelConfig();
    }

    // Prediction retrievers. All other fields in TempFeelConfig must be filled for these to work.
    private static boolean allOtherFieldsExist(TempFeelConfig c, TempFeelConfig.Fields field) {
        Set<TempFeelConfig.Fields> keys = c.h.keySet();
        keys.remove(field);
        return c.h.size() == 9;
    }

    public static Feeling getFeeling(TempFeelConfig c){
        if (!allOtherFieldsExist(c, TempFeelConfig.Fields.feels)) throw new IllegalStateException("All other fields must be initialized");
        return Feeling.COLD; // mock, should make a call to the python script
    }

    public static byte getHR(TempFeelConfig c) {
        if (!allOtherFieldsExist(c, TempFeelConfig.Fields.hr)) throw new IllegalStateException("All other fields must be initialized");
        return 80; // mock
    }

    public static double getUpperClo(TempFeelConfig c) {
        if (!allOtherFieldsExist(c, TempFeelConfig.Fields.upperClo)) throw new IllegalStateException("All other fields must be initialized");
        return 1.00; // mock, should make a call to the python script
    }

    public static void main(String[] args) {
        TempFeelConfig c = TempFeel.newConfig();
        c.upperClo(1).lowerClo(1).temp((byte)1);
        getFeeling(c);
    }
}