package logging;

import java.io.IOException;
import java.util.logging.*;

public class LogConfig {


    public static void setup() {
        Logger LOG = Logger.getLogger("main");
        LOG.setLevel(Level.ALL);
        try {
            System.err.println("LogConfig begin");

            String logFileName =  "souffle.log";

            // 确保文件存在（没有就新建）
            java.io.File logFile = new java.io.File(logFileName);
            if (!logFile.exists()) {
                logFile.createNewFile();
            }


            FileHandler fileHandler = new FileHandler(logFile.getAbsolutePath(),true); // 追加模式
            fileHandler.setFormatter(new SimpleFormatter());
            fileHandler.setLevel(Level.ALL);
            LOG.addHandler(fileHandler);

            System.err.println("日志文件路径: " + logFile.getAbsolutePath());
            // 2. 输出到控制台（VS Code Output 面板）
            ConsoleHandler consoleHandler = new ConsoleHandler();
            consoleHandler.setFormatter(new SimpleFormatter());
            consoleHandler.setLevel(Level.INFO);
            LOG.addHandler(consoleHandler);

        } catch (IOException e) {
            e.printStackTrace();
        }
    }
}

