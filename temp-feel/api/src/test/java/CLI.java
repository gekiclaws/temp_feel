
import api.TempFeel;

import api.TempFeel.Feeling;
import api.TempFeel.TempFeelConfig;

public class CLI {
    public static void main(String[] args) {
        // Successful call
        TempFeelConfig c = TempFeel.builder().upperClo(0.08).lowerClo(0.15).temp(19).sun().hr(120).build();
        Feeling f = TempFeel.getFeeling(c);
        System.out.println("It will feel: "+f);
    }
}
