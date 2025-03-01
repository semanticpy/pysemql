from parsimonious.nodes import NodeVisitor
from pysemql.indent_stack import IndentStack


from parsimonious.nodes import NodeVisitor

class PySemQLTranspiler(NodeVisitor):
    def __init__(self):
        self.sparql = []
        self.vars = set()
        self.indent_stack = IndentStack()
    
    def visit_Query(self, node, children):
        select, where, modifiers = children
        clauses = [
            "SELECT " + " ".join(f"?{var}" for var in self.vars),
            "WHERE {",
            where,
            "}",
            " ".join(modifiers) if modifiers else ""
        ]
        return " ".join(filter(None, clauses))
    
    def visit_IdentifierList(self, node, children):
        first, rest = children
        identifiers = [first] + [r[1] for r in rest]
        self.vars.update(identifiers)
        return " ".join(f"?{ident}" for ident in identifiers)
    
    def visit_Expression(self, node, children):
        return children[0]
    
    def visit_LogicalOr(self, node, children):
        left, rest = children
        for op, right in rest:
            left = f"({left} || {right})"
        return left
    
    def visit_LogicalAnd(self, node, children):
        left, rest = children
        for op, right in rest:
            left = f"({left} && {right})"
        return left
    
    def visit_Comparison(self, node, children):
        left, op, right = children
        return f"{left} {op} {right}"
    
    def visit_IdentifierOrLiteral(self, node, children):
        return children[0]
    
    def visit_Operator(self, node, children):
        return node.text
    
    def visit_Subject(self, node, children):
        subj = node.text
        self.vars.add(subj)
        return f"?{subj}"
    
    def visit_HasTriple(self, node, children):
        _, predicate, obj = children
        return f"{predicate} {obj} . "
    
    def visit_Object(self, node, children):
        obj = children[0]
        if isinstance(obj, str):
            if obj.startswith(('"', "'")):
                return obj
            elif ":" in obj:
                return obj
            else:
                self.vars.add(obj)
                return f"?{obj}"
        return obj
    
    def visit_Filter(self, node, children):
        _, expr = children
        return f"FILTER({expr}) "
    
    def visit_LineBlock(self, node, children):
        _, indent, lines, dedent = children
        self.indent_stack.push(len(indent.text) - 1)  # \n + 4 spaces
        result = lines
        self.indent_stack.pop()
        return result
    
    def generic_visit(self, node, children):
        return " ".join(filter(None, children)) if children else ""



# Example usage
if __name__ == "__main__":
    from pysemql.pysemql_grammar import pysemql_grammar
    query = """
    find scientist discovery where
        scientist is dbo:Scientist
            has dbo:discovery discovery
            has dbo:birthPlace city
        city has dbo:country "Germany"
        filter discovery.year > 1900
    order by discovery.year desc
    limit 5
    """
    transpiler = PySemQLTranspiler()
    ast = pysemql_grammar.parse(query)
    sparql = transpiler.visit(ast)
    print(sparql)