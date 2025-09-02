import java.net.URI;
import java.net.URLDecoder;
import java.nio.charset.StandardCharsets;

public class LogUtils {
    public static String extractRelativeUri(String uri) {
        String prefix = "file:///";
        if (uri.startsWith(prefix)) {
            // 去掉 "file:///"
            String path = uri.substring(prefix.length());
            // URL 解码（把 %3A 转换为 : 等）
            path = URLDecoder.decode(path, StandardCharsets.UTF_8);
            return path;
        }
        return uri;
    }
}


