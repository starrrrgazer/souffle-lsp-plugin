import logging.LSClientLogger;
import org.antlr.v4.runtime.CharStream;
import org.antlr.v4.runtime.CharStreams;
import org.antlr.v4.runtime.CommonTokenStream;
import org.antlr.v4.runtime.tree.ParseTree;
import org.eclipse.lsp4j.*;
import org.eclipse.lsp4j.jsonrpc.messages.Either;
import org.eclipse.lsp4j.services.TextDocumentService;
import parsing.*;
import parsing.preprocessor.PreprocessorLexer;
import parsing.preprocessor.PreprocessorParser;
import parsing.souffle.SouffleLexer;
import parsing.souffle.SouffleParser;
import parsing.symbols.*;

import java.io.BufferedReader;
import java.io.FileReader;
import java.io.IOException;
import java.io.LineNumberReader;
import java.net.URI;
import java.net.URISyntaxException;
import java.nio.file.Path;
import java.util.List;
import java.util.concurrent.CompletableFuture;
import java.util.logging.Logger;

/**
 * TextDocumentService implementation for Souffle Datalog.
 */
public class SouffleTextDocumentService implements TextDocumentService {

    private SouffleLanguageServer languageServer;
    private LSClientLogger  clientLogger;
    private SouffleProjectContext projectContext;
    private static final Logger LOG = Logger.getLogger("main");
    public SouffleTextDocumentService(SouffleLanguageServer languageServer) {
        this.languageServer = languageServer;
        this.clientLogger = LSClientLogger.getInstance();
        this.projectContext = SouffleProjectContext.getInstance();
    }

/*    private void consumeInput(String documentURI) throws IOException, URISyntaxException {
        URI uri = new URI(documentURI);
        CharStream input = CharStreams.fromPath(Path.of(uri));
        souffleLexer = new SouffleLexer(input);
        CommonTokenStream tokens = new CommonTokenStream(souffleLexer);
        souffleParser = new SouffleParser(tokens);
        souffleParser.removeErrorListeners();
        souffleParser.setErrorHandler(new parsing.SouffleError());
        souffleParser.addErrorListener(new SyntaxErrorListener(uri.toString()));
    }*/

    private void parseInput(String documentURI) throws IOException, URISyntaxException {
//        System.err.println("Parsing begin: " + documentURI);
        URI uri = new URI(documentURI);
        Path path = Path.of(uri);
        CharStream input = CharStreams.fromPath(path);
        preprocessInput(input);

        input = CharStreams.fromPath(path);
        SouffleLexer souffleLexer = new SouffleLexer(input, projectContext.defines);
        CommonTokenStream tokens = new CommonTokenStream(souffleLexer);
        SouffleParser souffleParser = new SouffleParser(tokens);
        souffleParser.removeErrorListeners();
        souffleParser.setErrorHandler(new SouffleError());
        souffleParser.addErrorListener(new SouffleSyntaxErrorListener(uri.toString()));
        SouffleProjectContext projectContext = SouffleProjectContext.getInstance();
        SouffleDeclarationVisitor visitor = new SouffleDeclarationVisitor(souffleParser, uri.toString(), projectContext);
        visitor.visit(souffleParser.program());

        projectContext.addDocument(uri.toString(), visitor.getDocumentContext());
        souffleParser.removeErrorListeners();
        souffleParser.reset();
        SouffleUsesVisitor visitor2 = new SouffleUsesVisitor(souffleParser, uri.toString());
        visitor2.visit(souffleParser.program());


        String fixedPath = uri.getPath();
        if (fixedPath.matches("^/[a-zA-Z]:.*")) {
            fixedPath = fixedPath.substring(1);  // 去掉开头的 '/'
        }
        countLineNum(fixedPath);
        countNodeNum(fixedPath);
        countDEFAndOCC(fixedPath);
    }

    private void countLineNum(String documentPath) throws IOException{
        int lineCount = 0;
        try (BufferedReader reader = new BufferedReader(new FileReader(documentPath))) {
            String line;
            while ((line = reader.readLine()) != null) {
                String trimmed = line.trim();
                // 跳过空行和注释行
                if (trimmed.isEmpty() || trimmed.startsWith("//")) {
                    continue;
                }
                lineCount++;
            }
        }
        LOG.info("LOC: "+ lineCount + " document: " + LogUtils.extractRelativeUri(documentPath));
    }

    private void countNodeNum(String documentPath) throws IOException {
        Path path = Path.of(documentPath);
        CharStream input = CharStreams.fromPath(path);
        SouffleLexer souffleLexer = new SouffleLexer(input, projectContext.defines);
        CommonTokenStream tokens = new CommonTokenStream(souffleLexer);
        SouffleParser souffleParser = new SouffleParser(tokens);

        ParseTree parseTree = souffleParser.program();

        int totalNodes = NodeNumVisitor.countNodes(parseTree);
        LOG.info("NOD: "+ totalNodes + " document: " + LogUtils.extractRelativeUri(documentPath));
    }

    private void countDEFAndOCC(String documentPath) throws IOException {
        Path path = Path.of(documentPath);
        CharStream input = CharStreams.fromPath(path);
        SouffleLexer souffleLexer = new SouffleLexer(input, projectContext.defines);
        CommonTokenStream tokens = new CommonTokenStream(souffleLexer);
        SouffleParser souffleParser = new SouffleParser(tokens);

        DEFAndOCCVisitor visitor = new DEFAndOCCVisitor();
        visitor.visit(souffleParser.program());

        LOG.info("DEF: "+ visitor.getDEF() + " document: " + LogUtils.extractRelativeUri(documentPath));
        LOG.info("OCC: "+ visitor.getOCC() + " document: " + LogUtils.extractRelativeUri(documentPath));
    }

    private void preprocessInput(CharStream input) {
        PreprocessorLexer preprocessorLexer = new PreprocessorLexer(input);
        CommonTokenStream preprocessorTokens = new CommonTokenStream(preprocessorLexer);
        PreprocessorParser preprocessorParser = new PreprocessorParser(preprocessorTokens);
        PreprocessorVisitor preprocessorVisitor = new PreprocessorVisitor(projectContext.defines);
        preprocessorVisitor.visit(preprocessorParser.program());
    }

    @Override
    public void didOpen(DidOpenTextDocumentParams didOpenTextDocumentParams) {
        try {
            URI uri = new URI(didOpenTextDocumentParams.getTextDocument().getUri());
            this.clientLogger.clearDiagnostics(uri.toString());
            parseInput(didOpenTextDocumentParams.getTextDocument().getUri());
//            SouffleContext context = SouffleProjectContext.getInstance().getDocumentContext(didOpenTextDocumentParams.getTextDocument().getUri());
//            logging.LSClientLogger.getInstance().reportHint(context.getRange(), uri.toString(), "Lint");
            this.clientLogger.logMessage("Operation '" + "text/didOpen" +
                    "' {fileUri: '" + uri + "'} opened");
        } catch (URISyntaxException | IOException e) {
            e.printStackTrace();
        }

    }

    @Override
    public void didChange(DidChangeTextDocumentParams didChangeTextDocumentParams) {
        SouffleProjectContext.getInstance().setChangedText(didChangeTextDocumentParams.getContentChanges().get(0).getText());
    }

    @Override
    public void didClose(DidCloseTextDocumentParams didCloseTextDocumentParams) {
        this.clientLogger.logMessage("Operation '" + "text/didClose" +
                "' {fileUri: '" + didCloseTextDocumentParams.getTextDocument().getUri() + "'} Closed");
    }

    @Override
    public void didSave(DidSaveTextDocumentParams didSaveTextDocumentParams) {
        this.clientLogger.clearDiagnostics(didSaveTextDocumentParams.getTextDocument().getUri());
        try {
            parseInput(didSaveTextDocumentParams.getTextDocument().getUri());
            CompletionProvider.state = CompletionState.IDLE;
            this.clientLogger.logMessage("Operation '" + "text/didSave" +
                    "' {fileUri: '" + didSaveTextDocumentParams.getTextDocument().getUri() + "'} Saved");



        } catch (IOException | URISyntaxException e) {
            e.printStackTrace();
        }


    }

    @Override
    public CompletableFuture<Either<List<? extends Location>, List<? extends LocationLink>>> definition(DefinitionParams params) {
        return CompletableFuture.supplyAsync(() -> new DefinitionProvider().getDefinition(params));
    }

    @Override
    public CompletableFuture<List<Either<Command, CodeAction>>> codeAction(CodeActionParams params) {
        return CompletableFuture.supplyAsync(() -> new CodeActionProvider().getCodeAction(params));
    }

//    @Override
//    public CompletableFuture<CodeAction> resolveCodeAction(CodeAction unresolved) {
//        return CompletableFuture.supplyAsync(() -> {
//            System.err.println(unresolved);
//            return unresolved;
//        });
//    }

    @Override
    public CompletableFuture<Hover> hover(HoverParams params) {
        return CompletableFuture.supplyAsync(() -> new HoverProvider().getHover(params));
    }


    //修改reference，调用definition，rename，completion
    //加入组件测试:定位 , 搜索
    @Override
    public CompletableFuture<List<? extends Location>> references(ReferenceParams params) {
        System.err.println("reference begin ");
        ReferenceProvider referenceProvider = new ReferenceProvider();
        referenceProvider.getLocateTime(params);
        referenceProvider.getSearchTime(params);
        System.err.println("locate / search end ");
        DefinitionProvider definitionProvider = new DefinitionProvider();
        definitionProvider.getDefinition(params);
        System.err.println("definition end ");
        RenameProvider renameProvider = new RenameProvider();
        renameProvider.getRename(params);
        System.err.println("rename end ");

        TestCompletion testCompletion = new TestCompletion();
        testCompletion.testCompletions(params);

        System.err.println("completion end ");

        return CompletableFuture.supplyAsync(() -> referenceProvider.getReferences(params));

    }

    @Override
    public CompletableFuture<Either<List<CompletionItem>, CompletionList>> completion(CompletionParams position) {
        return CompletableFuture.supplyAsync(() -> new CompletionProvider(position).getCompletions());
    }

    @Override
    public CompletableFuture<WorkspaceEdit> rename(RenameParams params) {
        return CompletableFuture.supplyAsync(() -> new RenameProvider().getRename(params));
    }

    @Override
    public CompletableFuture<Either<List<? extends Location>, List<? extends LocationLink>>> typeDefinition(TypeDefinitionParams params) {
        return CompletableFuture.supplyAsync(() -> new TypeDefinitionProvider().getTypeDefinition(params));
    }

    @Override
    public CompletableFuture<Either<List<? extends Location>, List<? extends LocationLink>>> implementation(ImplementationParams params) {
        return CompletableFuture.supplyAsync(() -> new ImplementationProvider().getImplementations(params));
    }

    @Override
    public CompletableFuture<SignatureHelp> signatureHelp(SignatureHelpParams params) {
        return CompletableFuture.supplyAsync(() -> new SignatureHelpProvider().getSignatureHelp(params));
    }

    @Override
    public CompletableFuture<List<Either<SymbolInformation, DocumentSymbol>>> documentSymbol(DocumentSymbolParams params) {
        return CompletableFuture.supplyAsync(() -> new DocumentSymbolProvider().getDocumentSymbols(params));
    }

}
