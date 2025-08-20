import org.eclipse.lsp4j.*;
import parsing.Utils;
import parsing.symbols.SouffleContext;
import parsing.symbols.SouffleProjectContext;
import parsing.symbols.SouffleSymbol;
import parsing.symbols.SouffleSymbolType;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

public class RenameProvider {
    public RenameProvider() {
    }

    public WorkspaceEdit getRename(RenameParams params) {
        WorkspaceEdit edit = new WorkspaceEdit();
        Map<String, List<TextEdit>> textEdits = new HashMap<String, List<TextEdit>>();
        Position cursorPosition = params.getPosition();
        cursorPosition.setCharacter(cursorPosition.getCharacter() - 1);
        Range cursor = Utils.positionToRange(cursorPosition);
        //定位。从项目的SouffleProjectContext 中 根据 文件的getTextDocument().getUri() 获取该文件的 context
        SouffleContext context = SouffleProjectContext.getInstance().getContext(params.getTextDocument().getUri(), cursor);
        if (context != null) {
            SouffleSymbol currentSymbol = context.getSymbol(cursor); //搜索：根据光标的range，从context中获得对应的符号
            if (currentSymbol != null) {
                switch (currentSymbol.getKind()) {
                    case RELATION_DECL:
                    case TYPE_DECL:
                    case COMPONENT_INIT:
                    case COMPONENT_DECL:
                    case TYPE_USE:
                    case RELATION_USE:
                    case RULE:
                        //对引用的地方进行修改。这个函数是搜索 + 遍历
                        List<Location> references = new ReferenceProvider().getReferences(params, false);
                        for (Location reference : references) {
                            if (!textEdits.containsKey(reference.getUri())) {
                                textEdits.put(reference.getUri(), new ArrayList<TextEdit>());
                            }
                            TextEdit textEdit1 = new TextEdit();
                            textEdit1.setRange(reference.getRange());
                            textEdit1.setNewText(params.getNewName());
                            textEdits.get(reference.getUri()).add(textEdit1);
//                                System.err.println(reference);
                        }
                        break;
                    case ATTRIBUTE:
                        // 获取所有同名符号进行修改
                        textEdits.put(params.getTextDocument().getUri(), new ArrayList<TextEdit>());
                        List<SouffleSymbol> vars = context.getSymbols(currentSymbol.getName())
                                .stream()
                                .filter(symbol -> symbol.getKind() == SouffleSymbolType.ATTRIBUTE)
                                .collect(Collectors.toList());
                        for (SouffleSymbol var : vars) {
                            TextEdit textEdit = new TextEdit();
                            textEdit.setRange(var.getRange());
                            textEdit.setNewText(params.getNewName());
                            textEdits.get(params.getTextDocument().getUri()).add(textEdit);
                        }

                        break;
//                    case TYPE_USE:
//                    case RELATION_USE:
//                    case RULE:
//                        textEdits.put(params.getTextDocument().getUri(), new ArrayList<TextEdit>());
//                        TextEdit textEdit = new TextEdit();
//                        textEdit.setRange(currentSymbol.getRange());
//                        textEdit.setNewText(params.getNewName());
//                        textEdits.get(params.getTextDocument().getUri()).add(textEdit);
//                        break;
                }
            }
        }
        edit.setChanges(textEdits);
        return edit;
    }
}