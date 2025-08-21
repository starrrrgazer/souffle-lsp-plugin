import org.checkerframework.checker.units.qual.A;
import org.eclipse.lsp4j.*;
import parsing.Utils;
import parsing.symbols.SouffleContext;
import parsing.symbols.SouffleContextType;
import parsing.symbols.SouffleProjectContext;
import parsing.symbols.SouffleSymbol;

import java.time.Duration;
import java.time.Instant;
import java.util.*;
import java.util.logging.Logger;

public class ReferenceProvider {
    private static final Logger LOG = Logger.getLogger("main");
    public ReferenceProvider() {
    }
    public List<Location> getReferences(TextDocumentPositionAndWorkDoneProgressParams params){
        return getReferences(params, true);
    }
    public List<Location> getReferences(TextDocumentPositionAndWorkDoneProgressParams params, boolean includeComponent) {
        Range cursor = Utils.positionToRange(params.getPosition());
        SouffleContext context = SouffleProjectContext.getInstance().getContext(params.getTextDocument().getUri(), cursor);
        Set<Location> references = new HashSet<>();
        if (context != null) {
            SouffleSymbol currentSymbol = context.getSymbol(cursor); //定位
            for (Map.Entry<String, SouffleContext> documentContext : SouffleProjectContext.getInstance().getDocuments().entrySet()) {
                //搜索。此处搜索 首先获取当前作用域下同名符号列表，然后递归查找子作用域，每个子作用域查找同名符号列表
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

    public void getLocateTime(TextDocumentPositionAndWorkDoneProgressParams params){
        var started = Instant.now();
        Range cursor = Utils.positionToRange(params.getPosition());
        SouffleContext context = SouffleProjectContext.getInstance().getContext(params.getTextDocument().getUri(), cursor);
        if (context != null) {
            SouffleSymbol currentSymbol = context.getSymbol(cursor);
        }
        var elapsedMs = Duration.between(started, Instant.now()).toMillis();
        LOG.info("locate: "+ elapsedMs + " document: " + LogUtils.extractRelativeUri(params.getTextDocument().getUri()));
    }

    public void getSearchTime(TextDocumentPositionAndWorkDoneProgressParams params){

        SouffleContext documentContext = SouffleProjectContext.getInstance().getDocumentContext(params.getTextDocument().getUri());
        ArrayList<String> items = new ArrayList<>();
        ArrayList<SouffleSymbol> souffleSymbols = new ArrayList<>();
        for (List<SouffleSymbol> symbols : documentContext.getScope().values()) {
            for (SouffleSymbol symbol : symbols) {
                if(!items.contains(symbol.toString())){
                    items.add(symbol.toString());
                    souffleSymbols.add(symbol);
                }
            }
        }

        Random random = new Random();
        var started = Instant.now();
        for (int i = 0; i < 10000; i++) {
            SouffleSymbol symbol = souffleSymbols.get(random.nextInt(souffleSymbols.size()));
            documentContext.getSymbol(symbol.getRange());
        }
        var elapsedMs = Duration.between(started, Instant.now()).toMillis();
        LOG.info("search: "+ elapsedMs + " document: " + LogUtils.extractRelativeUri(params.getTextDocument().getUri()));
    }

}