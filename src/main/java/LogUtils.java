import java.net.URI;

public class LogUtils {
    public static String extractRelativeUri(String uri) {
        String prefix = "file:///d%3A/work24/";

        if (uri.startsWith(prefix)) {
            String newPath = uri.substring(prefix.length());
            return newPath;
        }
        return uri;
    }
}
