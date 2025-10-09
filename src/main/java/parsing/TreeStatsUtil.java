package parsing;

import org.antlr.v4.runtime.*;
import org.antlr.v4.runtime.tree.*;
import parsing.souffle.SouffleLexer;
import parsing.souffle.SouffleParser;

import java.io.IOException;

public class TreeStatsUtil {

    public static class TreeStats {
        public int maxDegree;
        public int maxDepth;

        @Override
        public String toString() {
            return "maxDegree=" + maxDegree + ", maxDepth=" + maxDepth;
        }
    }

    // 递归DFS
    private static void dfs(ParseTree node, int depth, TreeStats stats) {
        int childCount = node.getChildCount();
        stats.maxDegree = Math.max(stats.maxDegree, childCount);
        stats.maxDepth = Math.max(stats.maxDepth, depth);

        for (int i = 0; i < childCount; i++) {
            dfs(node.getChild(i), depth + 1, stats);
        }
    }

    /**
     * 从文件解析，返回语法树的最大度数与深度
     * @param filePath 文件路径
     * @return TreeStats 对象
     */
    public static TreeStats computeStatsFromFile(String filePath) throws IOException {
        CharStream input = CharStreams.fromFileName(filePath);

        SouffleLexer lexer = new SouffleLexer(input);
        CommonTokenStream tokens = new CommonTokenStream(lexer);
        SouffleParser parser = new SouffleParser(tokens);


        ParseTree tree = parser.program();

        TreeStats stats = new TreeStats();
        dfs(tree, 1, stats);
        return stats;
    }
}

