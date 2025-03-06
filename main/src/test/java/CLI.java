
import api.TempFeel;

import api.TempFeel.Feeling;
import api.TempFeel.Intensity;
import api.TempFeel.TempFeelConfig;

public class CLI {
    public static void main(String[] args) {
        // Successful call
        TempFeelConfig c = TempFeel.newConfig().upperClo(0.3).lowerClo(0.12).temp(0);
        Feeling f = TempFeel.getFeeling(c);
        System.out.println("It will feel: "+f);
    }
}
