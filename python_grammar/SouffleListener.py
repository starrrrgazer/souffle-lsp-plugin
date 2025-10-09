# Generated from Souffle.g4 by ANTLR 4.13.1
from antlr4 import *
if "." in __name__:
    from .SouffleParser import SouffleParser
else:
    from SouffleParser import SouffleParser

# This class defines a complete listener for a parse tree produced by SouffleParser.
class SouffleListener(ParseTreeListener):

    # Enter a parse tree produced by SouffleParser#program.
    def enterProgram(self, ctx:SouffleParser.ProgramContext):
        pass

    # Exit a parse tree produced by SouffleParser#program.
    def exitProgram(self, ctx:SouffleParser.ProgramContext):
        pass


    # Enter a parse tree produced by SouffleParser#unit.
    def enterUnit(self, ctx:SouffleParser.UnitContext):
        pass

    # Exit a parse tree produced by SouffleParser#unit.
    def exitUnit(self, ctx:SouffleParser.UnitContext):
        pass


    # Enter a parse tree produced by SouffleParser#qualified_name.
    def enterQualified_name(self, ctx:SouffleParser.Qualified_nameContext):
        pass

    # Exit a parse tree produced by SouffleParser#qualified_name.
    def exitQualified_name(self, ctx:SouffleParser.Qualified_nameContext):
        pass


    # Enter a parse tree produced by SouffleParser#type_decl.
    def enterType_decl(self, ctx:SouffleParser.Type_declContext):
        pass

    # Exit a parse tree produced by SouffleParser#type_decl.
    def exitType_decl(self, ctx:SouffleParser.Type_declContext):
        pass


    # Enter a parse tree produced by SouffleParser#record_type_list.
    def enterRecord_type_list(self, ctx:SouffleParser.Record_type_listContext):
        pass

    # Exit a parse tree produced by SouffleParser#record_type_list.
    def exitRecord_type_list(self, ctx:SouffleParser.Record_type_listContext):
        pass


    # Enter a parse tree produced by SouffleParser#union_type_list.
    def enterUnion_type_list(self, ctx:SouffleParser.Union_type_listContext):
        pass

    # Exit a parse tree produced by SouffleParser#union_type_list.
    def exitUnion_type_list(self, ctx:SouffleParser.Union_type_listContext):
        pass


    # Enter a parse tree produced by SouffleParser#adt_branch_list.
    def enterAdt_branch_list(self, ctx:SouffleParser.Adt_branch_listContext):
        pass

    # Exit a parse tree produced by SouffleParser#adt_branch_list.
    def exitAdt_branch_list(self, ctx:SouffleParser.Adt_branch_listContext):
        pass


    # Enter a parse tree produced by SouffleParser#adt_branch.
    def enterAdt_branch(self, ctx:SouffleParser.Adt_branchContext):
        pass

    # Exit a parse tree produced by SouffleParser#adt_branch.
    def exitAdt_branch(self, ctx:SouffleParser.Adt_branchContext):
        pass


    # Enter a parse tree produced by SouffleParser#relation_decl.
    def enterRelation_decl(self, ctx:SouffleParser.Relation_declContext):
        pass

    # Exit a parse tree produced by SouffleParser#relation_decl.
    def exitRelation_decl(self, ctx:SouffleParser.Relation_declContext):
        pass


    # Enter a parse tree produced by SouffleParser#relation_names.
    def enterRelation_names(self, ctx:SouffleParser.Relation_namesContext):
        pass

    # Exit a parse tree produced by SouffleParser#relation_names.
    def exitRelation_names(self, ctx:SouffleParser.Relation_namesContext):
        pass


    # Enter a parse tree produced by SouffleParser#attributes_list.
    def enterAttributes_list(self, ctx:SouffleParser.Attributes_listContext):
        pass

    # Exit a parse tree produced by SouffleParser#attributes_list.
    def exitAttributes_list(self, ctx:SouffleParser.Attributes_listContext):
        pass


    # Enter a parse tree produced by SouffleParser#non_empty_attributes.
    def enterNon_empty_attributes(self, ctx:SouffleParser.Non_empty_attributesContext):
        pass

    # Exit a parse tree produced by SouffleParser#non_empty_attributes.
    def exitNon_empty_attributes(self, ctx:SouffleParser.Non_empty_attributesContext):
        pass


    # Enter a parse tree produced by SouffleParser#attribute.
    def enterAttribute(self, ctx:SouffleParser.AttributeContext):
        pass

    # Exit a parse tree produced by SouffleParser#attribute.
    def exitAttribute(self, ctx:SouffleParser.AttributeContext):
        pass


    # Enter a parse tree produced by SouffleParser#relation_tags.
    def enterRelation_tags(self, ctx:SouffleParser.Relation_tagsContext):
        pass

    # Exit a parse tree produced by SouffleParser#relation_tags.
    def exitRelation_tags(self, ctx:SouffleParser.Relation_tagsContext):
        pass


    # Enter a parse tree produced by SouffleParser#non_empty_attribute_names.
    def enterNon_empty_attribute_names(self, ctx:SouffleParser.Non_empty_attribute_namesContext):
        pass

    # Exit a parse tree produced by SouffleParser#non_empty_attribute_names.
    def exitNon_empty_attribute_names(self, ctx:SouffleParser.Non_empty_attribute_namesContext):
        pass


    # Enter a parse tree produced by SouffleParser#dependency.
    def enterDependency(self, ctx:SouffleParser.DependencyContext):
        pass

    # Exit a parse tree produced by SouffleParser#dependency.
    def exitDependency(self, ctx:SouffleParser.DependencyContext):
        pass


    # Enter a parse tree produced by SouffleParser#dependency_list_aux.
    def enterDependency_list_aux(self, ctx:SouffleParser.Dependency_list_auxContext):
        pass

    # Exit a parse tree produced by SouffleParser#dependency_list_aux.
    def exitDependency_list_aux(self, ctx:SouffleParser.Dependency_list_auxContext):
        pass


    # Enter a parse tree produced by SouffleParser#dependency_list.
    def enterDependency_list(self, ctx:SouffleParser.Dependency_listContext):
        pass

    # Exit a parse tree produced by SouffleParser#dependency_list.
    def exitDependency_list(self, ctx:SouffleParser.Dependency_listContext):
        pass


    # Enter a parse tree produced by SouffleParser#fact.
    def enterFact(self, ctx:SouffleParser.FactContext):
        pass

    # Exit a parse tree produced by SouffleParser#fact.
    def exitFact(self, ctx:SouffleParser.FactContext):
        pass


    # Enter a parse tree produced by SouffleParser#souffle_rule.
    def enterSouffle_rule(self, ctx:SouffleParser.Souffle_ruleContext):
        pass

    # Exit a parse tree produced by SouffleParser#souffle_rule.
    def exitSouffle_rule(self, ctx:SouffleParser.Souffle_ruleContext):
        pass


    # Enter a parse tree produced by SouffleParser#rule_def.
    def enterRule_def(self, ctx:SouffleParser.Rule_defContext):
        pass

    # Exit a parse tree produced by SouffleParser#rule_def.
    def exitRule_def(self, ctx:SouffleParser.Rule_defContext):
        pass


    # Enter a parse tree produced by SouffleParser#head.
    def enterHead(self, ctx:SouffleParser.HeadContext):
        pass

    # Exit a parse tree produced by SouffleParser#head.
    def exitHead(self, ctx:SouffleParser.HeadContext):
        pass


    # Enter a parse tree produced by SouffleParser#body.
    def enterBody(self, ctx:SouffleParser.BodyContext):
        pass

    # Exit a parse tree produced by SouffleParser#body.
    def exitBody(self, ctx:SouffleParser.BodyContext):
        pass


    # Enter a parse tree produced by SouffleParser#disjunction.
    def enterDisjunction(self, ctx:SouffleParser.DisjunctionContext):
        pass

    # Exit a parse tree produced by SouffleParser#disjunction.
    def exitDisjunction(self, ctx:SouffleParser.DisjunctionContext):
        pass


    # Enter a parse tree produced by SouffleParser#conjunction.
    def enterConjunction(self, ctx:SouffleParser.ConjunctionContext):
        pass

    # Exit a parse tree produced by SouffleParser#conjunction.
    def exitConjunction(self, ctx:SouffleParser.ConjunctionContext):
        pass


    # Enter a parse tree produced by SouffleParser#term.
    def enterTerm(self, ctx:SouffleParser.TermContext):
        pass

    # Exit a parse tree produced by SouffleParser#term.
    def exitTerm(self, ctx:SouffleParser.TermContext):
        pass


    # Enter a parse tree produced by SouffleParser#atom.
    def enterAtom(self, ctx:SouffleParser.AtomContext):
        pass

    # Exit a parse tree produced by SouffleParser#atom.
    def exitAtom(self, ctx:SouffleParser.AtomContext):
        pass


    # Enter a parse tree produced by SouffleParser#constraint.
    def enterConstraint(self, ctx:SouffleParser.ConstraintContext):
        pass

    # Exit a parse tree produced by SouffleParser#constraint.
    def exitConstraint(self, ctx:SouffleParser.ConstraintContext):
        pass


    # Enter a parse tree produced by SouffleParser#arg_list.
    def enterArg_list(self, ctx:SouffleParser.Arg_listContext):
        pass

    # Exit a parse tree produced by SouffleParser#arg_list.
    def exitArg_list(self, ctx:SouffleParser.Arg_listContext):
        pass


    # Enter a parse tree produced by SouffleParser#non_empty_arg_list.
    def enterNon_empty_arg_list(self, ctx:SouffleParser.Non_empty_arg_listContext):
        pass

    # Exit a parse tree produced by SouffleParser#non_empty_arg_list.
    def exitNon_empty_arg_list(self, ctx:SouffleParser.Non_empty_arg_listContext):
        pass


    # Enter a parse tree produced by SouffleParser#arg.
    def enterArg(self, ctx:SouffleParser.ArgContext):
        pass

    # Exit a parse tree produced by SouffleParser#arg.
    def exitArg(self, ctx:SouffleParser.ArgContext):
        pass


    # Enter a parse tree produced by SouffleParser#functor_built_in.
    def enterFunctor_built_in(self, ctx:SouffleParser.Functor_built_inContext):
        pass

    # Exit a parse tree produced by SouffleParser#functor_built_in.
    def exitFunctor_built_in(self, ctx:SouffleParser.Functor_built_inContext):
        pass


    # Enter a parse tree produced by SouffleParser#aggregate_func.
    def enterAggregate_func(self, ctx:SouffleParser.Aggregate_funcContext):
        pass

    # Exit a parse tree produced by SouffleParser#aggregate_func.
    def exitAggregate_func(self, ctx:SouffleParser.Aggregate_funcContext):
        pass


    # Enter a parse tree produced by SouffleParser#aggregate_body.
    def enterAggregate_body(self, ctx:SouffleParser.Aggregate_bodyContext):
        pass

    # Exit a parse tree produced by SouffleParser#aggregate_body.
    def exitAggregate_body(self, ctx:SouffleParser.Aggregate_bodyContext):
        pass


    # Enter a parse tree produced by SouffleParser#query_plan.
    def enterQuery_plan(self, ctx:SouffleParser.Query_planContext):
        pass

    # Exit a parse tree produced by SouffleParser#query_plan.
    def exitQuery_plan(self, ctx:SouffleParser.Query_planContext):
        pass


    # Enter a parse tree produced by SouffleParser#query_plan_list.
    def enterQuery_plan_list(self, ctx:SouffleParser.Query_plan_listContext):
        pass

    # Exit a parse tree produced by SouffleParser#query_plan_list.
    def exitQuery_plan_list(self, ctx:SouffleParser.Query_plan_listContext):
        pass


    # Enter a parse tree produced by SouffleParser#plan_order.
    def enterPlan_order(self, ctx:SouffleParser.Plan_orderContext):
        pass

    # Exit a parse tree produced by SouffleParser#plan_order.
    def exitPlan_order(self, ctx:SouffleParser.Plan_orderContext):
        pass


    # Enter a parse tree produced by SouffleParser#non_empty_plan_order_list.
    def enterNon_empty_plan_order_list(self, ctx:SouffleParser.Non_empty_plan_order_listContext):
        pass

    # Exit a parse tree produced by SouffleParser#non_empty_plan_order_list.
    def exitNon_empty_plan_order_list(self, ctx:SouffleParser.Non_empty_plan_order_listContext):
        pass


    # Enter a parse tree produced by SouffleParser#component_decl.
    def enterComponent_decl(self, ctx:SouffleParser.Component_declContext):
        pass

    # Exit a parse tree produced by SouffleParser#component_decl.
    def exitComponent_decl(self, ctx:SouffleParser.Component_declContext):
        pass


    # Enter a parse tree produced by SouffleParser#component_head.
    def enterComponent_head(self, ctx:SouffleParser.Component_headContext):
        pass

    # Exit a parse tree produced by SouffleParser#component_head.
    def exitComponent_head(self, ctx:SouffleParser.Component_headContext):
        pass


    # Enter a parse tree produced by SouffleParser#component_type.
    def enterComponent_type(self, ctx:SouffleParser.Component_typeContext):
        pass

    # Exit a parse tree produced by SouffleParser#component_type.
    def exitComponent_type(self, ctx:SouffleParser.Component_typeContext):
        pass


    # Enter a parse tree produced by SouffleParser#component_type_params.
    def enterComponent_type_params(self, ctx:SouffleParser.Component_type_paramsContext):
        pass

    # Exit a parse tree produced by SouffleParser#component_type_params.
    def exitComponent_type_params(self, ctx:SouffleParser.Component_type_paramsContext):
        pass


    # Enter a parse tree produced by SouffleParser#component_param_list.
    def enterComponent_param_list(self, ctx:SouffleParser.Component_param_listContext):
        pass

    # Exit a parse tree produced by SouffleParser#component_param_list.
    def exitComponent_param_list(self, ctx:SouffleParser.Component_param_listContext):
        pass


    # Enter a parse tree produced by SouffleParser#component_body.
    def enterComponent_body(self, ctx:SouffleParser.Component_bodyContext):
        pass

    # Exit a parse tree produced by SouffleParser#component_body.
    def exitComponent_body(self, ctx:SouffleParser.Component_bodyContext):
        pass


    # Enter a parse tree produced by SouffleParser#component_init.
    def enterComponent_init(self, ctx:SouffleParser.Component_initContext):
        pass

    # Exit a parse tree produced by SouffleParser#component_init.
    def exitComponent_init(self, ctx:SouffleParser.Component_initContext):
        pass


    # Enter a parse tree produced by SouffleParser#functor_decl.
    def enterFunctor_decl(self, ctx:SouffleParser.Functor_declContext):
        pass

    # Exit a parse tree produced by SouffleParser#functor_decl.
    def exitFunctor_decl(self, ctx:SouffleParser.Functor_declContext):
        pass


    # Enter a parse tree produced by SouffleParser#functor_arg_type_list.
    def enterFunctor_arg_type_list(self, ctx:SouffleParser.Functor_arg_type_listContext):
        pass

    # Exit a parse tree produced by SouffleParser#functor_arg_type_list.
    def exitFunctor_arg_type_list(self, ctx:SouffleParser.Functor_arg_type_listContext):
        pass


    # Enter a parse tree produced by SouffleParser#non_empty_functor_arg_type_list.
    def enterNon_empty_functor_arg_type_list(self, ctx:SouffleParser.Non_empty_functor_arg_type_listContext):
        pass

    # Exit a parse tree produced by SouffleParser#non_empty_functor_arg_type_list.
    def exitNon_empty_functor_arg_type_list(self, ctx:SouffleParser.Non_empty_functor_arg_type_listContext):
        pass


    # Enter a parse tree produced by SouffleParser#functor_attribute.
    def enterFunctor_attribute(self, ctx:SouffleParser.Functor_attributeContext):
        pass

    # Exit a parse tree produced by SouffleParser#functor_attribute.
    def exitFunctor_attribute(self, ctx:SouffleParser.Functor_attributeContext):
        pass


    # Enter a parse tree produced by SouffleParser#pragma.
    def enterPragma(self, ctx:SouffleParser.PragmaContext):
        pass

    # Exit a parse tree produced by SouffleParser#pragma.
    def exitPragma(self, ctx:SouffleParser.PragmaContext):
        pass


    # Enter a parse tree produced by SouffleParser#directive_head.
    def enterDirective_head(self, ctx:SouffleParser.Directive_headContext):
        pass

    # Exit a parse tree produced by SouffleParser#directive_head.
    def exitDirective_head(self, ctx:SouffleParser.Directive_headContext):
        pass


    # Enter a parse tree produced by SouffleParser#directive_head_decl.
    def enterDirective_head_decl(self, ctx:SouffleParser.Directive_head_declContext):
        pass

    # Exit a parse tree produced by SouffleParser#directive_head_decl.
    def exitDirective_head_decl(self, ctx:SouffleParser.Directive_head_declContext):
        pass


    # Enter a parse tree produced by SouffleParser#directive_list.
    def enterDirective_list(self, ctx:SouffleParser.Directive_listContext):
        pass

    # Exit a parse tree produced by SouffleParser#directive_list.
    def exitDirective_list(self, ctx:SouffleParser.Directive_listContext):
        pass


    # Enter a parse tree produced by SouffleParser#relation_directive_list.
    def enterRelation_directive_list(self, ctx:SouffleParser.Relation_directive_listContext):
        pass

    # Exit a parse tree produced by SouffleParser#relation_directive_list.
    def exitRelation_directive_list(self, ctx:SouffleParser.Relation_directive_listContext):
        pass


    # Enter a parse tree produced by SouffleParser#non_empty_key_value_pairs.
    def enterNon_empty_key_value_pairs(self, ctx:SouffleParser.Non_empty_key_value_pairsContext):
        pass

    # Exit a parse tree produced by SouffleParser#non_empty_key_value_pairs.
    def exitNon_empty_key_value_pairs(self, ctx:SouffleParser.Non_empty_key_value_pairsContext):
        pass


    # Enter a parse tree produced by SouffleParser#kvp_value.
    def enterKvp_value(self, ctx:SouffleParser.Kvp_valueContext):
        pass

    # Exit a parse tree produced by SouffleParser#kvp_value.
    def exitKvp_value(self, ctx:SouffleParser.Kvp_valueContext):
        pass


    # Enter a parse tree produced by SouffleParser#preprocessor_macro.
    def enterPreprocessor_macro(self, ctx:SouffleParser.Preprocessor_macroContext):
        pass

    # Exit a parse tree produced by SouffleParser#preprocessor_macro.
    def exitPreprocessor_macro(self, ctx:SouffleParser.Preprocessor_macroContext):
        pass


    # Enter a parse tree produced by SouffleParser#macro_args.
    def enterMacro_args(self, ctx:SouffleParser.Macro_argsContext):
        pass

    # Exit a parse tree produced by SouffleParser#macro_args.
    def exitMacro_args(self, ctx:SouffleParser.Macro_argsContext):
        pass


    # Enter a parse tree produced by SouffleParser#non_empty_macro_args.
    def enterNon_empty_macro_args(self, ctx:SouffleParser.Non_empty_macro_argsContext):
        pass

    # Exit a parse tree produced by SouffleParser#non_empty_macro_args.
    def exitNon_empty_macro_args(self, ctx:SouffleParser.Non_empty_macro_argsContext):
        pass


    # Enter a parse tree produced by SouffleParser#macro_arg.
    def enterMacro_arg(self, ctx:SouffleParser.Macro_argContext):
        pass

    # Exit a parse tree produced by SouffleParser#macro_arg.
    def exitMacro_arg(self, ctx:SouffleParser.Macro_argContext):
        pass



del SouffleParser