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


        ArrayList<SouffleSymbol> souffleSymbolArrayList = new ArrayList<>();
        for (List<SouffleSymbol> symbols : documentContext.getScope().values()) {
            for (SouffleSymbol symbol : symbols) {
                if (!souffleSymbolArrayList.contains(symbol))
                    souffleSymbolArrayList.add(symbol);
            }
        }
//        System.err.println("symbol size: " + souffleSymbols.size() + "\nSymbols: " + souffleSymbols);
//        LOG.info("OCC: "+ OCC + " document: " + LogUtils.extractRelativeUri(params.getTextDocument().getUri()));
//        LOG.info("DEF: "+ DEF.size() + " document: " + LogUtils.extractRelativeUri(params.getTextDocument().getUri()));


        int subContextNum = 1;


        if (documentContext.getSubContext() != null) {
            for (SouffleContext ruleContext : documentContext.getSubContext().values()) {
                if ((documentContext.getKind() == SouffleContextType.COMPONENT || ruleContext.getKind() != SouffleContextType.COMPONENT)){
                    subContextNum = subContextNum + 1;
                }
            }
        }

        Random random = new Random();
        ArrayList<SouffleSymbol> randomSymbols = new ArrayList<>();
        for (int i = 0; i < 10000; i++) {
            randomSymbols.add(souffleSymbolArrayList.get(random.nextInt(souffleSymbolArrayList.size())));
        }



        // 一个 search 是 在 一个 document 里 根据 一个 name  搜索 一个 列表
        //就是一次 getReference 的 耗时
        var started = Instant.now();
        for (int i = 0; i < 10000; i++) {
            SouffleSymbol currentSymbol = randomSymbols.get(i);
            String name = currentSymbol.getName();
//            LOG.info("searchSymbol: "+ name + " document: " + LogUtils.extractRelativeUri(params.getTextDocument().getUri()));
            Set<Location> references = new HashSet<>();
//            String key = params.getTextDocument().getUri();
            Range cursor = Utils.positionToRange(params.getPosition());
            SouffleContext context = SouffleProjectContext.getInstance().getContext(params.getTextDocument().getUri(), cursor);

            if (context != null) {
//                SouffleSymbol currentSymbol = context.getSymbol(cursor);
                for (Map.Entry<String, SouffleContext> souffleContextEntry : SouffleProjectContext.getInstance().getDocuments().entrySet()) {
                    //搜索。此处搜索 首先获取当前作用域下同名符号列表，然后递归查找子作用域，每个子作用域查找同名符号列表
                    Optional.ofNullable(souffleContextEntry.getValue()
                                    .getSymbols(name))
                            .ifPresent(souffleSymbols -> souffleSymbols.forEach(symbol -> references.add(new Location(souffleContextEntry.getKey(), symbol.getRange()))));
                    if(souffleContextEntry.getValue().getSubContext() != null){
                        for (SouffleContext ruleContext : souffleContextEntry.getValue().getSubContext().values()) {
                            if (
                                    (context.getKind() == SouffleContextType.COMPONENT || ruleContext.getKind() != SouffleContextType.COMPONENT)) {
                                Optional.ofNullable(ruleContext
                                                .getSymbols(name))
                                        .ifPresent(souffleSymbols ->
                                                souffleSymbols.forEach(symbol ->{
                                                    if(symbol.getURI() != null && symbol.getURI().equals(souffleContextEntry.getKey()))
                                                        references.add(new Location(souffleContextEntry.getKey(), symbol.getRange()));
                                                    else if(symbol.getURI() == null)
                                                        references.add(new Location(souffleContextEntry.getKey(), symbol.getRange()));
                                                }));
                            }
                        }
                    }
                }
            }

//            Optional.ofNullable(documentContext
//                            .getSymbols(name))
//                    .ifPresent(souffleSymbols -> souffleSymbols.forEach(symbol -> references.add(new Location(key, symbol.getRange()))));
//            if(documentContext.getSubContext() != null){
//                for (SouffleContext ruleContext : documentContext.getSubContext().values()) {
//                    if ((documentContext.getKind() == SouffleContextType.COMPONENT || ruleContext.getKind() != SouffleContextType.COMPONENT)) {
//                        Optional.ofNullable(ruleContext
//                                        .getSymbols(name))
//                                .ifPresent(souffleSymbols ->
//                                        souffleSymbols.forEach(symbol ->{
//                                            if(symbol.getURI() != null && symbol.getURI().equals(key))
//                                                references.add(new Location(key, symbol.getRange()));
//                                            else if(symbol.getURI() == null)
//                                                references.add(new Location(key, symbol.getRange()));
//                                        }));
//                    }
//                }
//            }
        }
        var elapsedMs = Duration.between(started, Instant.now()).toMillis();
        LOG.info("search: "+ elapsedMs + " document: " + LogUtils.extractRelativeUri(params.getTextDocument().getUri()));
        LOG.info("subcontextNum: "+ subContextNum + " document: " + LogUtils.extractRelativeUri(params.getTextDocument().getUri()));
    }

}