import org.eclipse.lsp4j.DefinitionParams;
import org.eclipse.lsp4j.Location;
import org.eclipse.lsp4j.LocationLink;
import org.eclipse.lsp4j.Range;
import org.eclipse.lsp4j.jsonrpc.messages.Either;
import parsing.Utils;
import parsing.symbols.SouffleContext;
import parsing.symbols.SouffleProjectContext;
import parsing.symbols.SouffleSymbol;

import java.util.ArrayList;
import java.util.List;
import java.util.Optional;

public class DefinitionProvider {

    public DefinitionProvider() {
    }

    public Either<List<? extends Location>, List<? extends LocationLink>> getDefinition(DefinitionParams params) {
        List<Location> declLocations = new ArrayList<Location>();
        Range cursor = Utils.positionToRange(params.getPosition());
        Optional<SouffleContext> context = Optional.ofNullable(SouffleProjectContext.getInstance().getContext(params.getTextDocument().getUri(), cursor)); //
        if (context.isPresent()) {
            Optional<SouffleSymbol> currentSymbol = Optional.ofNullable(context.get().getSymbol(cursor)); //查表
            if (currentSymbol.isPresent()) {
                for(SouffleSymbol symbol :currentSymbol.get().getDeclarations()){
                    declLocations.add(new Location(symbol.getURI(), symbol.getRange())); //构建 useVisitor
                }
            }
        }

        return Either.forLeft(declLocations);
    }
}