import org.eclipse.lsp4j.*;
import parsing.Utils;
import parsing.symbols.SouffleContext;
import parsing.symbols.SouffleContextType;
import parsing.symbols.SouffleProjectContext;
import parsing.symbols.SouffleSymbol;

import java.util.*;

public class ReferenceProvider {

    public ReferenceProvider() {
    }
    public List<Location> getReferences(TextDocumentPositionAndWorkDoneProgressParams params){
        return getReferences(params, true);
    }
    public List<Location> getReferences(TextDocumentPositionAndWorkDoneProgressParams params, boolean includeComponent) {
        Range cursor = Utils.positionToRange(params.getPosition()); //搜索
        SouffleContext context = SouffleProjectContext.getInstance().getContext(params.getTextDocument().getUri(), cursor);
        Set<Location> references = new HashSet<>();
        if (context != null) {
            SouffleSymbol currentSymbol = context.getSymbol(cursor); //搜索
            for (Map.Entry<String, SouffleContext> documentContext : SouffleProjectContext.getInstance().getDocuments().entrySet()) {
                //遍历。此处遍历 首先获取当前作用域下同名符号列表，然后递归查找子作用域，每个子作用域查找同名符号列表
                Optional.ofNullable(documentContext.getValue()
                                .getSymbols(currentSymbol.getName()))
                        .ifPresent(souffleSymbols -> souffleSymbols.forEach(symbol -> references.add(new Location(documentContext.getKey(), symbol.getRange()))));
                if(documentContext.getValue().getSubContext() != null){
                    for (SouffleContext ruleContext : documentContext.getValue().getSubContext().values()) {
                        if (includeComponent ||
                                (context.getKind() == SouffleContextType.COMPONENT || ruleContext.getKind() != SouffleContextType.COMPONENT)) {
                            Optional.ofNullable(ruleContext
                                            .getSymbols(currentSymbol.getName()))
                                    .ifPresent(souffleSymbols ->
                                            souffleSymbols.forEach(symbol ->{
                                                if(symbol.getURI() != null && symbol.getURI().equals(documentContext.getKey()))
                                                    references.add(new Location(documentContext.getKey(), symbol.getRange()));
                                                else if(symbol.getURI() == null)
                                                    references.add(new Location(documentContext.getKey(), symbol.getRange()));
                                            }));
                        }
                    }
                }
            }
        }
        return new ArrayList<>(references);
    }
}