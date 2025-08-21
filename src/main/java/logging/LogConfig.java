package logging;

import java.io.IOException;
import java.util.logging.*;

public class LogConfig {
    private static final Logger LOG = Logger.getLogger("main");

    public static void setup() {
        try {
            // 1. 移除默认的控制台 Handler（避免重复日志）
            Logger rootLogger = Logger.getLogger("");
            Handler[] handlers = rootLogger.getHandlers();
            for (Handler h : handlers) {
                rootLogger.removeHandler(h);
            }

            // 2. 控制台输出 Handler
            ConsoleHandler consoleHandler = new ConsoleHandler();
            consoleHandler.setLevel(Level.INFO); // 设置级别
            consoleHandler.setFormatter(new SimpleFormatter()); // 默认格式化器

            // 3. 文件输出 Handler
            FileHandler fileHandler = new FileHandler("server.log", true); // 追加写入
            fileHandler.setLevel(Level.ALL);
            fileHandler.setFormatter(new SimpleFormatter());

            // 4. 给 logger 添加 handler
            LOG.addHandler(consoleHandler);
            LOG.addHandler(fileHandler);

            LOG.setLevel(Level.ALL); // 设置日志等级

            // 5. 示例日志输出
            LOG.severe("严重错误：服务崩溃！");
            LOG.warning("警告：内存接近上限");
            LOG.info("信息：服务已启动");
            LOG.fine("调试信息：请求已接收");
            LOG.finer("更详细的调试信息");
            LOG.finest("最详细的调试信息");

        } catch (IOException e) {
            e.printStackTrace();
        }
    }
}

