from parsimonious.grammar import Grammar

pyql_grammar = Grammar(
    r"""
    Query          = SelectClause WhereClause? LimitClause? OrderClause?
    SelectClause   = "select" IdentifierList
    IdentifierList = (Identifier ("," Identifier)*)
    WhereClause    = "where" Indent Pattern Dedent
    Pattern        = TriplePattern (Newline TriplePattern)*
    TriplePattern  = (Subject ("has" Predicate Object / "is" Type) / Filter / Optional / Union)
    Subject        = Identifier
    Predicate      = PrefixedURI
    Object         = Identifier / Literal / PrefixedURI
    Type           = PrefixedURI
    Filter         = "filter" Expression
    Optional       = "maybe:" Indent Pattern Dedent
    Union          = "either:" Indent Pattern "or:" Indent Pattern Dedent
    Literal        = StringLiteral / Number
    StringLiteral  = ~r'"[^"]*"'
    Number         = ~r'\d+'
    PrefixedURI    = ~r'[a-zA-Z0-9]+:[a-zA-Z0-9_/]+'
    Identifier     = ~r'[a-zA-Z_][a-zA-Z0-9_]*'  # Variables (no sigils)
    LimitClause    = "limit" Number
    OrderClause    = "order by" Identifier ("asc" / "desc")?
    Indent         = ~r'\n\s+'
    Dedent         = ~r'\n(?=\S)'
    Newline        = ~r'\n'
    """
)