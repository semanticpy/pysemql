from parsimonious.grammar import Grammar

pysemql_grammar = Grammar(
    r"""
    Query          = SelectClause WhereClause? Modifiers?
    SelectClause   = "select" IdentifierList
    IdentifierList = Identifier ("," Identifier)*
    WhereClause    = "where" LineBlock
    LineBlock      = NewLine Indent Lines Dedent
    Lines          = (Triple / Filter / Optional / Union / Subquery)+
    Triple         = Subject (HasTriple / IsTriple)
    HasTriple      = "has" Predicate Object
    IsTriple       = "is" Type
    Optional       = "maybe" ":" LineBlock
    Union          = "either" ":" LineBlock "or" ":" LineBlock
    Subquery       = Identifier "=" "subquery" LineBlock
    Filter         = "filter" Expression
    Expression     = LogicalOr
    LogicalOr      = LogicalAnd ("or" LogicalAnd)*
    LogicalAnd     = Comparison ("and" Comparison)*
    Comparison     = IdentifierOrLiteral Operator IdentifierOrLiteral
    IdentifierOrLiteral = Identifier / Literal
    Operator       = "==" / "!=" / ">" / "<" / ">=" / "<="
    Subject        = Identifier
    Predicate      = PrefixedURI
    Object         = Identifier / Literal / PrefixedURI
    Type           = PrefixedURI
    Literal        = StringLiteral / Number
    StringLiteral  = ~r'"[^"]*"'
    Number         = ~r'\d+'
    PrefixedURI    = ~r'[a-zA-Z0-9]+:[a-zA-Z0-9_/]+'
    Identifier     = ~r'[a-zA-Z_][a-zA-Z0-9_]*'
    Modifiers      = (OrderClause / LimitClause)+
    OrderClause    = "order" "by" Identifier ("asc" / "desc")?
    LimitClause    = "limit" Number
    Indent         = ~r'\n {4}'  # Exactly 4 spaces
    Dedent         = ~r'(?=\n( {0,3}\S|\Z))'  # Lookahead for less indentation
    NewLine        = ~r'\n'
    """
)