package main.api;

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
        private double upperClo; // required field
        private double lowerClo; // required field
        private byte temp; // required field
        private boolean sun = false; // default: false
        private boolean headwind = false; // default: false
        private Intensity snow = Intensity.NONE; // default: none
        private Intensity rain = Intensity.NONE; // default: none
        private boolean fatigued = false; // default: false
        private byte hr = 80; // default: 80
        private Feeling feels;

        protected void data() {  }

        private TempFeelConfig() {};

        // Provide copy method?

        public TempFeelConfig upperClo(double val) { this.upperClo = val; return this; }

        public TempFeelConfig lowerClo(double val) { this.lowerClo = val; return this; }

        // Sets temperature in celsius
        public TempFeelConfig temp(byte temp) { this.temp = temp; return this; }

        public TempFeelConfig sun() {this.sun = true; return this; }
        public TempFeelConfig noSun() {this.sun = false; return this; }

        public TempFeelConfig headwind(boolean b) { this.headwind = b; return this; }

        public TempFeelConfig snow(Intensity i) { this.snow = i; return this; }

        public TempFeelConfig rain(Intensity i) { this.rain = i; return this; }

        public TempFeelConfig fatigued(boolean b) { this.fatigued = b; return this; }

        public TempFeelConfig hr(byte hr) { this.hr = hr; return this; }

        public TempFeelConfig feeling(Feeling f) {this.feels = f; return this; }
    }

    // Static utility class: prevent instantiation
    private TempFeel() {}

    public static TempFeelConfig newConfig(){
        TempFeel x = new TempFeel();
        return x.new TempFeelConfig();
    }

    // Prediction retrievers

    public static Feeling getFeeling(TempFeelConfig c){
        return Feeling.COLD; // mock, should make a call to the python script
    }

    public static byte getHR(TempFeelConfig c) {
        return 80; // mock
    }

    public static double getUpperClo(TempFeelConfig c) {
        return 1.00; // mock, should make a call to the python script
    }
}