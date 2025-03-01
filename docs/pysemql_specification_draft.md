# pySemQL Specification Draft

The SPARQL syntax is very hard to read, hard to remember and close to very old concepts of SQL. How could a modern syntax look like, which should be closer to native English (or at least python with it's pythonic simplicity) ? Please make a proposal that covers the main SPARQL language features.


## Design Goals
Readability: Less punctuation, natural-language keywords (maybe, either/or).

Familiarity: Leverages Python-like syntax and method chaining.

Expressiveness: Retains SPARQL’s power (property paths, subqueries, federated queries).

Tooling-Friendly: Easy to parse and auto-format (like Python’s PEP8).
Cleaner syntax: No ?, $, or {}.

Natural language flow: Reads like a structured English sentence.

## Feature	pySemQL  Syntax	SPARQL Equivalent

| Feature            | pySemQL Syntax                          | SPARQL Equivalent          |
|--------------------|-----------------------------------------|----------------------------|
| Variables          | scientist                               | ?scientist                 |
| Triple Patterns    | subject has predicate object            | ?subject ex:pred ?object   |
| Optional Patterns  | maybe: block with indentation           | OPTIONAL { ... }           |
| Unions             | either: and or: blocks                  | { ... } UNION { ... }      |
| Filters            | filter + Python-like conditions         | FILTER(?age > 30)          |
| Order/Limit        | order by, limit                         | ORDER BY, LIMIT            |


## Exmaples

```
find scientist discovery where
    scientist is dbo:Scientist
        has dbo:discovery discovery
        has dbo:birthPlace city
    city has dbo:country "Germany"
    filter discovery.year > 1900
order by discovery.year desc
limit 5

```