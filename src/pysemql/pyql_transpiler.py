from parsimonious.nodes import NodeVisitor
from pyql_grammar import pyql_grammar

class PyQLTranspiler(NodeVisitor):
    def __init__(self):
        self.sparql = []
        self.vars = set()

    def visit_Query(self, node, children):
        select, where, limit, order = children
        clauses = [
            "SELECT " + " ".join(f"?{var}" for var in self.vars),
            "WHERE {",
            where,
            "}",
            order,
            limit
        ]
        return " ".join(filter(None, clauses))

    def visit_SelectClause(self, node, children):
        _, identifiers = children
        return identifiers

    def visit_WhereClause(self, node, children):
        _, _, patterns, _ = children
        return patterns

    def visit_TriplePattern(self, node, children):
        for child in children:
            if isinstance(child, str):
                return child
            elif isinstance(child, dict):
                # Handle filters/optional/union
                return child["value"]
        return ""

    def visit_Subject(self, node, children):
        subj = node.text.strip()
        self.vars.add(subj)
        return f"?{subj} "

    def visit_Predicate(self, node, children):
        return node.text + " "

    def visit_Object(self, node, children):
        obj = node.text
        if obj.isdigit():
            return obj
        elif obj.startswith(('"', "'")):
            return obj
        elif ":" in obj:
            return obj
        else:
            self.vars.add(obj)
            return f"?{obj} "

    def visit_Filter(self, node, children):
        _, expr = children
        return f"FILTER({expr}) "

    def visit_Optional(self, node, children):
        _, _, patterns, _ = children
        return f"OPTIONAL {{ {patterns} }} "

    def visit_Union(self, node, children):
        _, _, patterns1, _, patterns2, _ = children
        return f"{{ {patterns1} }} UNION {{ {patterns2} }} "

    def generic_visit(self, node, children):
        return " ".join(filter(None, children)) if children else node.text

# Example usage
if __name__ == "__main__":
    query = """
    select scientist discovery where
        scientist is dbo:Scientist
            has dbo:discovery discovery
            has dbo:birthPlace city
        city has dbo:country "Germany"
        filter discovery.year > 1900
    order by discovery.year desc
    limit 5
    """
    transpiler = PyQLTranspiler()
    ast = pyql_grammar.parse(query)
    sparql = transpiler.visit(ast)
    print(sparql)