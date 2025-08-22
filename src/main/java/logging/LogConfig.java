package logging;

import java.io.IOException;
import java.util.logging.*;

public class LogConfig {
    private static final Logger LOG = Logger.getLogger("main");

    public static void setup() {
        try {
//            // 1. 移除默认的控制台 Handler（避免重复日志）
//            Logger rootLogger = Logger.getLogger("");
//            Handler[] handlers = rootLogger.getHandlers();
//            for (Handler h : handlers) {
//                rootLogger.removeHandler(h);
//            }
//
//            // 2. 控制台输出 Handler
//            ConsoleHandler consoleHandler = new ConsoleHandler();
//            consoleHandler.setLevel(Level.INFO); // 设置级别
//            consoleHandler.setFormatter(new SimpleFormatter()); // 默认格式化器
//
//            // 3. 文件输出 Handler
//            FileHandler fileHandler = new FileHandler("souffle.log", true); // 追加写入
//            fileHandler.setLevel(Level.ALL);
//            fileHandler.setFormatter(new SimpleFormatter());
//
//            // 4. 给 logger 添加 handler
//            LOG.addHandler(consoleHandler);
//            LOG.addHandler(fileHandler);
//
//            LOG.setLevel(Level.ALL); // 设置日志等级
//
//            // 5. 示例日志输出
//            LOG.severe("严重错误：服务崩溃！");
//            LOG.warning("警告：内存接近上限");
//            LOG.info("信息：服务已启动");
//            LOG.fine("调试信息：请求已接收");
//            LOG.finer("更详细的调试信息");
//            LOG.finest("最详细的调试信息");
            String logDir = "logs";
            String logFileName = logDir + java.io.File.separator + "souffle.log";

            // 确保目录存在
            java.io.File dir = new java.io.File(logDir);
            if (!dir.exists()) {
                dir.mkdirs(); // 创建目录
            }

            // 确保文件存在（没有就新建）
            java.io.File logFile = new java.io.File(logFileName);
            if (!logFile.exists()) {
                logFile.createNewFile();
            }

            LOG.setLevel(Level.ALL);
            FileHandler fileHandler = new FileHandler("souffle.log",true); // 追加模式
            fileHandler.setFormatter(new SimpleFormatter());
            LOG.addHandler(fileHandler);

            System.err.println("日志文件路径: " + logFile.getAbsolutePath());
            // 2. 输出到控制台（VS Code Output 面板）
            ConsoleHandler consoleHandler = new ConsoleHandler();
            consoleHandler.setFormatter(new SimpleFormatter());
            LOG.addHandler(consoleHandler);

        } catch (IOException e) {
            e.printStackTrace();
        }
    }
}

