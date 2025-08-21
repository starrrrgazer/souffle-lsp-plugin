import org.eclipse.lsp4j.*;
import org.eclipse.lsp4j.jsonrpc.messages.Either;
import parsing.Utils;
import parsing.symbols.SouffleContext;
import parsing.symbols.SouffleProjectContext;
import parsing.symbols.SouffleSymbol;

import java.time.Duration;
import java.time.Instant;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;
import java.util.logging.Logger;

public class DefinitionProvider {
    private static final Logger LOG = Logger.getLogger("main");
    public DefinitionProvider() {
    }

    public Either<List<? extends Location>, List<? extends LocationLink>> getDefinition(DefinitionParams params) {
        List<Location> declLocations = new ArrayList<Location>();
        var started = Instant.now();
        Range cursor = Utils.positionToRange(params.getPosition());
        Optional<SouffleContext> context = Optional.ofNullable(SouffleProjectContext.getInstance().getContext(params.getTextDocument().getUri(), cursor)); //
        if (context.isPresent()) {
            Optional<SouffleSymbol> currentSymbol = Optional.ofNullable(context.get().getSymbol(cursor)); //定位 获取cursor对应的symbol
            if (currentSymbol.isPresent()) {
                for(SouffleSymbol symbol :currentSymbol.get().getDeclarations()){ //搜索
                    declLocations.add(new Location(symbol.getURI(), symbol.getRange()));
                }
            }
        }
        var elapsedMs = Duration.between(started, Instant.now()).toMillis();
        LOG.info("gotoDefinition: "+ elapsedMs + " document: " + LogUtils.extractRelativeUri(params.getTextDocument().getUri()));

        return Either.forLeft(declLocations);
    }

    //only for test definition time
    public Either<List<? extends Location>, List<? extends LocationLink>> getDefinition(TextDocumentPositionAndWorkDoneProgressParams params) {
        List<Location> declLocations = new ArrayList<Location>();
        var started = Instant.now();
        Range cursor = Utils.positionToRange(params.getPosition());
        Optional<SouffleContext> context = Optional.ofNullable(SouffleProjectContext.getInstance().getContext(params.getTextDocument().getUri(), cursor)); //
        if (context.isPresent()) {
            Optional<SouffleSymbol> currentSymbol = Optional.ofNullable(context.get().getSymbol(cursor)); //定位 获取cursor对应的symbol
            if (currentSymbol.isPresent()) {
                for(SouffleSymbol symbol :currentSymbol.get().getDeclarations()){ //搜索
                    declLocations.add(new Location(symbol.getURI(), symbol.getRange()));
                }
            }
        }
        var elapsedMs = Duration.between(started, Instant.now()).toMillis();
        LOG.info("gotoDefinition: "+ elapsedMs + " document: " + LogUtils.extractRelativeUri(params.getTextDocument().getUri()));

        return Either.forLeft(declLocations);
    }
}