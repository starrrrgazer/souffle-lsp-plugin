import org.eclipse.lsp4j.*;
import org.eclipse.lsp4j.jsonrpc.messages.Either;
import parsing.Utils;
import parsing.symbols.*;

import java.time.Duration;
import java.time.Instant;
import java.util.*;
import java.util.logging.Logger;

enum CompletionState{
    IDLE,
    IN_ARGS
}
public class CompletionProvider {

    private static final String[] directives = new String[]{
            ".decl",
            ".output",
            ".input",
            ".type",
            ".comp",
            ".init",
            ".printsize",
            ".functor",
            ".limitsize",
            ".override",
            ".pragma",
            ".plan",
            ".symboltype",
            ".numbertype",
            ".include",
            ".once"
    };
    private static final Logger LOG = Logger.getLogger("main");
    static CompletionState state = CompletionState.IDLE;
    private final CompletionParams params;
    private final String documentUri;
    private final Position position;

    public CompletionProvider(CompletionParams params) {
        this.params = params;
        this.documentUri = params.getTextDocument().getUri();
        this.position = params.getPosition();
    }

    public Either<List<CompletionItem>, CompletionList> getCompletions() {
        Range range = Utils.positionToRange(position);
        List<CompletionItem> completionItems = new ArrayList<CompletionItem>();
        if( params.getContext().getTriggerCharacter() != null && params.getContext().getTriggerCharacter().equals("(")){
            state = CompletionState.IN_ARGS;
            return Either.forLeft(completionItems);
        }
        var started = Instant.now();
        switch (state){
            case IDLE:
                Set<String> items = new HashSet<>();
                SouffleContext context = SouffleProjectContext.getInstance().getContext(this.documentUri, range); //搜索
                boolean directiveTrigger = params.getContext().getTriggerCharacter() != null && params.getContext().getTriggerCharacter().equals(".");
                if(directiveTrigger){
                    for (String directive : directives) {
                        CompletionItem completionItem = new CompletionItem();
                        completionItem.setLabel(directive);
                        completionItem.setInsertText(directive.substring(1));
                        completionItem.setKind(CompletionItemKind.Keyword);
                        completionItems.add(completionItem);
                        if (directive.equals(".symboltype") || directive.equals(".numbertype")) {
                            completionItem.setTags(List.of(CompletionItemTag.Deprecated));
                        }
                    }
                }

                for (SouffleContext documentContext : SouffleProjectContext.getInstance().getDocuments().values()) {
                    //遍历 document 次数
                    findInScope(documentContext.getScope(), completionItems, items);
                }

                //遍历 1 次
                if(context != null){
                    if(context.getParent() != null && context.getParent().getKind() == SouffleContextType.COMPONENT){
                        context = context.getParent();
                    }
                    if(context.getKind() == SouffleContextType.COMPONENT){
                        findInScope(((SouffleComponent)context.getContextSymbols().get(0)).getScope(), completionItems, items);
                    }
                }
                addSnippets(completionItems);

//                return Either.forLeft(completionItems);
            case IN_ARGS:
                if( params.getContext().getTriggerCharacter() != null &&
                        (params.getContext().getTriggerCharacter().equals(")") || params.getContext().getTriggerCharacter().equals("."))){
                    state = CompletionState.IDLE;
                }
//                return Either.forLeft(completionItems);
        }
        var elapsedMs = Duration.between(started, Instant.now()).toMillis();
        LOG.info("completion: "+ elapsedMs + " document: " + LogUtils.extractRelativeUri(params.getTextDocument().getUri()));
        return Either.forLeft(completionItems);
//        return null;
    }

    private static void addSnippets(List<CompletionItem> completionItems) {
        CompletionItem factSnippet = new CompletionItem();
        factSnippet.setLabel("fact");
        factSnippet.setInsertText("$1($2).$0");
        factSnippet.setInsertTextFormat(InsertTextFormat.Snippet);
        factSnippet.setKind(CompletionItemKind.Snippet);
        factSnippet.setDetail("Snippet for fact template");
        completionItems.add(factSnippet);

        CompletionItem ruleSnippet = new CompletionItem();
        ruleSnippet.setLabel("rule");
        ruleSnippet.setInsertText("$1($2) :- $0.");
        ruleSnippet.setInsertTextFormat(InsertTextFormat.Snippet);
        ruleSnippet.setKind(CompletionItemKind.Snippet);
        ruleSnippet.setDetail("Snippet for rule template");
        completionItems.add(ruleSnippet);

        CompletionItem declSnippet = new CompletionItem();
        declSnippet.setLabel("decl");
        declSnippet.setInsertText(".decl $1($2)$0");
        declSnippet.setInsertTextFormat(InsertTextFormat.Snippet);
        declSnippet.setKind(CompletionItemKind.Snippet);
        declSnippet.setDetail("Snippet for declaration generation");
        completionItems.add(declSnippet);

        CompletionItem compSnippet = new CompletionItem();
        compSnippet.setLabel("comp");
        compSnippet.setInsertText(".comp ${1:compName}${2::superComp} {\n\t$0\n}");
        compSnippet.setInsertTextFormat(InsertTextFormat.Snippet);
        compSnippet.setKind(CompletionItemKind.Snippet);
        compSnippet.setDetail("Snippet for component generation");
        completionItems.add(compSnippet);

        CompletionItem dataStructureSnippet = new CompletionItem();
        dataStructureSnippet.setLabel("ds");
        dataStructureSnippet.setInsertText("${1|brie,btree,eqrel|}$0");
        dataStructureSnippet.setInsertTextFormat(InsertTextFormat.Snippet);
        dataStructureSnippet.setKind(CompletionItemKind.Unit);
        dataStructureSnippet.setDetail("List of relation data structures");
        completionItems.add(dataStructureSnippet);

        CompletionItem primitiveTypeSnippet = new CompletionItem();
        primitiveTypeSnippet.setLabel("type");
        primitiveTypeSnippet.setInsertText("${1|symbol,number,unsigned,float|}$0");
        primitiveTypeSnippet.setInsertTextFormat(InsertTextFormat.Snippet);
        primitiveTypeSnippet.setKind(CompletionItemKind.Interface);
        primitiveTypeSnippet.setDetail("List of primitive types");
        completionItems.add(primitiveTypeSnippet);
    }

    private void findInScope(Map<String, List<SouffleSymbol>> scope, List<CompletionItem> completionItems, Set<String> items) {
        //获取scope列表下的所有符号，每个进行对比
        for (List<SouffleSymbol> symbols : scope.values()) {
            for (SouffleSymbol symbol : symbols) {
                if(!items.contains(symbol.toString())){
                    items.add(symbol.toString());
                    CompletionItem completionItem = new CompletionItem();
                    completionItem.setLabel(symbol.toString());
                    completionItem.setInsertText(symbol.getName());
                    switch (symbol.getKind()) {
                        case TYPE_DECL:
                            completionItem.setKind(CompletionItemKind.Interface);
                            completionItem.setLabel(symbol.getName());
                            completionItem.setDetail(symbol.toString().replaceFirst(".type", ""));
                            completionItems.add(completionItem);
                            break;
                        case RELATION_DECL:
                            addCompletionItem(completionItem, symbol, CompletionItemKind.Method, completionItems);
                            break;
                        case COMPONENT_INIT:
                            addCompletionItem(completionItem, symbol, CompletionItemKind.Variable, completionItems);
                            break;
                        case COMPONENT_DECL:
                            completionItem.setDetail(".comp");
                            addCompletionItem(completionItem, symbol, CompletionItemKind.Class, completionItems);
                            break;
                    }
                }
            }
        }
    }

    private void addCompletionItem(CompletionItem completionItem, SouffleSymbol symbol, CompletionItemKind itemKind, List<CompletionItem> completionItems) {
        String triggerCharacter = params.getContext().getTriggerCharacter();
        if (triggerCharacter == null || !triggerCharacter.equals(":")) {
            completionItem.setKind(itemKind);
            completionItems.add(completionItem);
            if(symbol.getDocumentation() != null){
                completionItem.setDocumentation(symbol.getDocumentation());
            }
        }
    }
}