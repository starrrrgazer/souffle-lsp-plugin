package parsing;

import logging.LSClientLogger;
import org.antlr.v4.runtime.tree.TerminalNode;
import org.eclipse.lsp4j.Range;
import org.eclipse.xtext.xbase.lib.Pair;
import parsing.souffle.SouffleBaseVisitor;
import parsing.souffle.SouffleParser;
import parsing.symbols.*;

import java.util.ArrayDeque;
import java.util.List;

public class DEFAndOCCVisitor  extends SouffleBaseVisitor<SouffleSymbol> {

    int OCC;
    int DEF;

    public DEFAndOCCVisitor() {
        this.OCC = 0;
        this.DEF = 0;
    }

    public int getOCC() {
        return OCC;
    }

    public int getDEF() {
        return DEF;
    }

    @Override
    public SouffleSymbol visitProgram(SouffleParser.ProgramContext ctx) {

        return super.visitProgram(ctx);
    }

    @Override
    public SouffleSymbol visitComponent_decl(SouffleParser.Component_declContext ctx) {
        this.DEF = this.DEF + 1;
        return super.visitComponent_decl(ctx);
    }
    @Override
    public SouffleSymbol visitRelation_decl(SouffleParser.Relation_declContext ctx) {
        this.DEF = this.DEF + 1;
        return super.visitRelation_decl(ctx);
    }

    @Override
    public SouffleSymbol visitType_decl(SouffleParser.Type_declContext ctx) {
        this.DEF = this.DEF + 1;
        return super.visitType_decl(ctx);
    }

    @Override
    public SouffleSymbol visitFunctor_decl(SouffleParser.Functor_declContext ctx) {
        this.DEF = this.DEF + 1;
        return super.visitFunctor_decl(ctx);
    }

    @Override
    public SouffleSymbol visitRelation_names(SouffleParser.Relation_namesContext ctx) {
        this.OCC = this.OCC + 1;
        return super.visitRelation_names(ctx);
    }



    @Override
    public SouffleSymbol visitQualified_name(SouffleParser.Qualified_nameContext ctx) {
        this.OCC = this.OCC + 1;
        return super.visitQualified_name(ctx);
    }

    @Override
    public SouffleSymbol visitNon_empty_attribute_names(SouffleParser.Non_empty_attribute_namesContext ctx) {
        this.OCC = this.OCC + 1;
        return super.visitNon_empty_attribute_names(ctx);
    }

    @Override
    public SouffleSymbol visitDirective_head_decl(SouffleParser.Directive_head_declContext ctx) {

        return super.visitDirective_head_decl(ctx);
    }
}
