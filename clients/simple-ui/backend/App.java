
import main.api.TempFeel;
import main.api.TempFeel.TempFeelConfig;

public final class App {
    private TempFeelConfig config;

    public App() {
        this.config = TempFeel.newConfig();
    }

    public static void main(String[] args) {
        new App();
    }
}