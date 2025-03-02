package clients;

import main.api.TempFeel;
import main.api.TempFeel.Feeling;
import main.api.TempFeel.TempFeelConfig;

public class CLI {
    public static void main(String[] args) {
        TempFeelConfig c = TempFeel.newConfig();
        c.upperClo(0.3).lowerClo(0.12).temp((byte)0);
        Feeling f = TempFeel.getFeeling(c);
        System.out.println("It will feel: "+f);
    }
}
