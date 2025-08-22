package parsing;

import org.antlr.v4.runtime.tree.ParseTree;

public class NodeNumVisitor {
    public static int countNodes(ParseTree tree) {
        if (tree == null) return 0;
        int count = 1; // 当前节点
        for (int i = 0; i < tree.getChildCount(); i++) {
            count += countNodes(tree.getChild(i));
        }
        return count;
    }
}
