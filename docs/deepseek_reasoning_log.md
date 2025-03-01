Okay, the user wants me to improve the handling of nested indents in the PyQL grammar and make the rules stricter. Let me start by recalling how the current code handles indentation. The previous grammar used regular expressions for Indent and Dedent, but that might not be sufficient for nested structures.

Parsimonious doesn't have built-in support for indentation-sensitive parsing like some other parsers (e.g., ANTLR), so I need a way to track indentation levels manually. Maybe I can use a stateful approach, where each indent increases the current level and each dedent decreases it. But how to integrate that into the PEG grammar?

Wait, the user mentioned using the Parsimonious library. Since it's a PEG parser, perhaps I can create a custom node visitor that tracks the indentation level during parsing. That way, each Indent node would check that the whitespace is exactly one level more than the current, and Dedent nodes would reduce the level.

In the previous code, Indent was matched with a regex for newline followed by spaces, and Dedent was a newline not followed by spaces. But that's not checking the actual indentation depth. So the main issue is ensuring that each nested block increases the indentation by a consistent amount (e.g., 4 spaces) and that dedents properly step back.

I need to modify the grammar to enforce consistent indentation levels. Let's assume 4 spaces per indent level. For each Indent, the whitespace must be exactly current_level + 4. Dedent would then be a reduction by 4.

But how to represent this in the grammar? Maybe capture the exact number of spaces and track the current level in the visitor. However, Parsimonious doesn't support stateful parsing out of the box. Hmm.

Alternatively, the grammar can capture the whitespace for each line and then, in the visitor, verify that the indentation is correct relative to the parent. For example, each block starts with an Indent (specific number of spaces) that is exactly 4 more than the parent's indentation.

So, the Indent rule would need to match the expected number of spaces based on the current indentation level. But since PEG grammars are context-free, this might not be straightforward. Maybe the solution is to track the indentation level outside the grammar, in the visitor, and raise errors if the indentation doesn't match.

Wait, perhaps a better approach is to process the indentations in the visitor by keeping a stack of indentation levels. For each line, when we encounter an indentation, we check if it's exactly one level deeper than the current. If not, raise a parse error.

But integrating this into the Parsimonious grammar might require modifying how the Indent and Dedent nodes are handled. The grammar can capture the whitespace, and then the visitor checks the indentation levels against the stack.

Let me sketch this out. The Indent rule would match a newline followed by some spaces. The Dedent rule would match a newline followed by fewer spaces than the current level. In the visitor, each time we process an Indent, we push the new level onto the stack. For Dedent, we pop the level.

But how to enforce that the indentation is exactly one level deeper each time? The grammar can't enforce this dynamically, so it's up to the visitor to validate the indentation levels. So, the grammar would capture the whitespace, and the visitor would check the actual spaces count against the expected level.

So, modifying the grammar to capture the exact number of spaces for each indent. Then, in the visitor, track the current indentation level. For each Indent node, check that the whitespace is 4 spaces more than the current level, update the level, and proceed. For Dedent, check that the next line's indentation is less than the current level and adjust accordingly.

But how to represent this in the existing grammar? Let's adjust the Indent and Dedent rules:

Indent = ~r'\n( {4})+'

Dedent = ~r'\n( {0,3}(?=\S)|(?=\S))'

But this might not capture the exact levels. Alternatively, capture the whitespace as a string and then compute the level in the visitor.

In the grammar:

Indent = ~r'\n( +)'

Then, in the visitor, for each Indent node, check that the captured whitespace length is equal to (current_level + 4). Similarly, Dedent would require that the next line's indentation is less than current_level.

This approach requires the visitor to track the current indentation level and validate each Indent and Dedent against it.

Modify the Transpiler class to include a stack for indentation levels. For example:

class PyQLTranspiler(NodeVisitor):

def __init__(self):

self.indent_stack = [0]  # Start with 0 indentation

def visit_Indent(self, node, children):

whitespace = node.text[1:]  # Skip the newline

current_level = self.indent_stack[-1]

expected_level = current_level + 4

if len(whitespace) != expected_level:

raise ParseError(f"Expected {expected_level} spaces, got {len(whitespace)}")

self.indent_stack.append(len(whitespace))

def visit_Dedent(self, node, children):

# Dedent is handled when a line has less indentation

# This might need to be checked in the parent node's processing

pass

But how to detect dedents? Maybe Dedent isn't a separate node, but when processing a new line, the indentation is checked against the current level. If it's less, we pop the stack until we find a matching level.

Alternatively, the Dedent is not a separate token, and the visitor must track when the indentation decreases. This complicates the visitor logic.

Another approach: Use a stateful lexer to track indentation. But since we're using Parsimonious, which is a parsing expression grammar (PEG) parser, not a lexical analyzer, this might not be feasible.

Alternatively, pre-process the input to convert indentation into INDENT and DEDENT tokens, similar to how Python's tokenizer works. Then, the grammar can include these tokens.

But integrating that into the existing setup would require a pre-processing step. Let me think.

The user wants to use Parsimonious, so the solution must fit within that framework. Therefore, perhaps the best approach is to modify the grammar to capture the exact indentation level for each line and then, in the visitor, check that each nested block increases the indentation by exactly 4 spaces.

So, the grammar would have rules to capture the indentation for each line. For example:

Line = Indentation? Content

But integrating this into the current grammar structure might be complex. Alternatively, structure the grammar such that each block starts with an increase in indentation.

Alternatively, represent each level of indentation as a separate rule. For example:

Block = Indent Pattern Dedent

Where Indent requires the indentation to be exactly 4 spaces more than the current level, and Dedent checks for a return to the previous level.

But this requires tracking the indentation level in the visitor.

So, revising the grammar:

Indent = ~r'\n( {4})+'

But this would match any multiple of 4 spaces. Wait, no. The regex ~r'\n( {4})+' would match a newline followed by one or more groups of 4 spaces. So, for example, \n    (4 spaces) is one level, \n        (8 spaces) is two levels, etc.

But we want each indent to be exactly one level (4 spaces) more than the previous. So, in the visitor, we can track the expected indentation level. For example, when entering a block, the indentation must be current_level + 4.

So, in the visitor:

- Start with current_level = 0.

- When processing an Indent node, check that the total whitespace is current_level + 4.

- Update current_level to the new value.

- When processing a Dedent, current_level is reduced by 4.

But how to capture Dedent in the grammar? Dedent occurs when a line has less indentation than the current level. Since PEG parsers are greedy, perhaps we need to structure the grammar to expect a certain indentation level at each block.

Alternatively, the Dedent is implicit when a line's indentation is less than the current level. However, this is challenging in a PEG grammar.

Perhaps the solution is to structure the grammar to expect specific indentation levels for nested blocks. For example:

Block = Newline Indent(4) Pattern Dedent(4)

But Parsimonious doesn't support parameterized rules. Therefore, this approach isn't feasible.

Alternative idea: Use a separate rule for each indentation level. But that's impractical.

Given the time constraints and the need for a practical solution within Parsimonious, perhaps the best approach is to enforce that each indent is exactly 4 spaces more than the previous, and in the visitor, track the current indentation level, raising errors if the indentation doesn't match.

So, modifying the Indent and Dedent rules to capture the whitespace, and in the visitor, check the length.

In the grammar:

Indent = ~r'\n( +)'  # Capture newline followed by spaces

Then, in the visitor's visit_Indent method:

def visit_Indent(self, node, children):

indent_spaces = len(node.text[1:])  # Exclude the newline

current_level = self.indent_stack[-1]

expected_level = current_level + 4

if indent_spaces != expected_level:

raise ParseError(f"Expected {expected_level} spaces, got {indent_spaces}")

self.indent_stack.append(indent_spaces)

Similarly, when a Dedent occurs (i.e., a line with fewer spaces), the visitor would need to check that the indentation level is properly reduced. However, detecting Dedent in the grammar is tricky. Instead, during the processing of each line, the visitor can track the current indentation level and verify that subsequent lines either maintain, increase, or decrease the level appropriately.

Wait, perhaps the Dedent is not a separate node but is handled when a line's indentation is less than the current level. So, in the visitor, when processing a new line, compare its indentation to the current level. If it's less, then dedent to the appropriate level.

This approach would require modifying the visitor to handle each line's indentation and manage the stack accordingly. However, integrating this into the existing grammar would require restructuring the rules to process each line's indentation.

Alternatively, the grammar can be structured so that each block is a series of lines with increasing indentation. For example:

Block = Indent Line+ Dedent

But again, without state, this is hard.

Given the time, perhaps the best approach is to adjust the existing grammar to capture the exact indentation and modify the visitor to enforce consistent nesting.

In the previous code, the Indent rule was ~r'\n\s+', which matches any whitespace after a newline. But to enforce 4-space indentation, change it to ~r'\n {4}'.

Wait, but that would only match exactly 4 spaces. However, nested blocks would need 8, 12, etc. But in the visitor, each Indent node would push 4 more spaces onto the stack.

Wait, perhaps the grammar can match exactly 4 spaces for each indent level, and the visitor tracks the expected level.

But how to represent multiple indent levels? For example:

Block:

line1

line2

subline1

subline2

In this case, 'subline1' is indented by 8 spaces, which is two levels. So each level is 4 spaces. So, the grammar can have a rule for each Indent step:

Indent = ~r'\n( {4})'

But this would only match 4 spaces. To allow multiple levels, the visitor would track the expected indentation. Each time an Indent is encountered, it must be exactly 4 more than the current level.

Wait, no. Each Indent token in the grammar is exactly 4 spaces. Then, nested blocks would have multiple Indent tokens. For example, a block with two levels of indentation would have two Indent nodes.

Wait, perhaps the approach is to have each indent level represented by a separate Indent node. For example:

Line1

Line2 (Indent 4)

Line3 (Indent 8)

But in the grammar, each Indent is 4 spaces, so multiple Indents would add up. However, in the grammar, it's difficult to represent this because the new line's indentation is matched as a single Indent node of 4 spaces. So, for two levels, the indentation would be 8 spaces, which would be two Indent nodes? Or one node with 8 spaces?

Hmm. This is getting complicated. Maybe the key is to modify the Indent rule to capture the exact number of spaces and then, in the visitor, ensure that each indentation step is exactly 4 spaces more than the previous.

So, the grammar's Indent rule is:

Indent = ~r'\n( +)'

Then, in the visitor, when processing an Indent node:

def visit_Indent(self, node, children):

current_level = self.indent_stack[-1]

indent_spaces = len(node.text[1:])  # Length after newline

if indent_spaces != current_level + 4:

raise ParseError(...)

self.indent_stack.append(indent_spaces)

But how to handle dedents? For example, after a block, the next line has less indentation. The Dedent would be inferred when the indentation level decreases. However, in the grammar, each line's indentation is processed as part of the Indent node for that line.

So, during the processing of each line, the visitor checks the indentation level. If it's less than the current level, it dedents accordingly.

This would require the visitor to track the current indentation level and adjust it as each line is processed. But integrating this into the existing visitor structure might require significant changes.

Alternatively, restructure the grammar to process each line with its indentation and manage the stack in the visitor.

But given the time constraints, perhaps the best approach is to modify the existing code to track the indentation level in the visitor and raise errors if the indentation is inconsistent.

So, revising the transpiler's visit_Indent method to check the indentation level.

In the previous code, the Indent rule was matched with ~r'\n\s+', which includes the newline and spaces. The visitor would then check the length of the spaces and ensure it's exactly 4 more than the current level.

Let me adjust the grammar and visitor accordingly.

First, update the Indent rule to capture the spaces:

Indent = ~r'\n( +)'

Then, in the visitor:

def visit_Indent(self, node, children):

whitespace = node.text[1:]  # After the newline

current_level = self.indent_stack[-1]

expected_level = current_level + 4

if len(whitespace) != expected_level:

raise ValueError(f"Invalid indentation: expected {expected_level} spaces, got {len(whitespace)}")

self.indent_stack.append(len(whitespace))

return ''

But wait, each Indent in the grammar corresponds to a newline and spaces. However, in nested blocks, each subsequent line would have more spaces. For example:

select scientist where

scientist has dbo:discovery discovery

has dbo:year year

Here, the third line is indented by 8 spaces. The first indent after 'where' is 4 spaces, then the next line is 8. The visitor should check that each indent is exactly 4 more than the previous.

But in the grammar, each line's indentation is captured as an Indent node. So, for the third line, the Indent node's whitespace is 8 spaces. The visitor would check that 8 is equal to the current level (4) + 4 → 8, which is correct.

When the block ends, the dedent would occur when a line has less indentation. However, the grammar as written doesn't explicitly capture dedents. So, the visitor must track when the indentation decreases.

But how to detect dedents in the grammar? It's challenging because dedents aren't marked explicitly. Therefore, the visitor must handle this during processing.

For example, after processing a block, when the next line's indentation is less than the current level, the visitor must pop the stack until it matches.

But integrating this into the existing visitor requires that each line's indentation is checked against the current level. This suggests that the visitor needs to process each line's indentation, compare it to the current level, and adjust the stack accordingly.

This complicates the visitor logic, as the transpiler would need to manage the indentation stack for each line, not just for block structures.

Perhaps the solution is to restructure the grammar to handle each line's indentation explicitly and use the visitor to manage the stack.

However, given the complexity, maybe it's better to model the Dedent as a reduction in the indentation level. For example, after a block, when the next line's indentation is less than the current level, we generate a Dedent event.

But without modifying the grammar to recognize dedents, this is difficult. An alternative approach is to pre-process the input into tokens that include INDENT and DEDENT events based on the whitespace changes, similar to Python's tokenize module.

But integrating that with Parsimonious would require writing a custom tokenizer, which is beyond the current scope.

Given the time, perhaps the best way to proceed is to adjust the existing code to track the indentation level in the visitor and enforce that each nested block increases the indentation by exactly 4 spaces. Dedents are handled implicitly when the indentation level decreases, but the visitor would need to manage that.

So, in the transpiler's visit method for each line, check the indentation level, and adjust the stack as needed.

But how to associate each line with its indentation level in the grammar? Maybe the grammar should capture each line's indentation and content, then in the visitor, process them in order, checking the indentation level each time.

Restructuring the grammar to capture lines with their indentation:

Line = Indent? Content

But this is too simplistic. Alternatively, the Pattern rule could consist of multiple Line nodes, each with their own indentation.

But this requires significant changes to the existing grammar. For example:

Pattern = Line+

Line = Indent? TriplePattern

But this might not capture nested blocks properly.

Alternatively, each Block is defined by an increase in indentation. For example:

Block = Indent Pattern Dedent

But again, without state, it's hard to track.

Given the time constraints and the user's request to improve nested indent handling with stricter rules, the practical approach is to modify the existing code to track indentation levels in the visitor and enforce that each indent is exactly 4 spaces more than the current level, and dedents are handled by reducing the stack when the indentation decreases.

This involves:

1. Modifying the Indent rule to capture the whitespace.

2. In the visitor, checking that each indent is +4 spaces.

3. Managing a stack of indentation levels.

4. Raising errors on invalid indentation.

Implementing this would make the indentation handling stricter and ensure nested blocks are properly structured.

So, updating the grammar and visitor as follows:

Grammar:

Indent = ~r'\n( +)'

Visitor:

class PyQLTranspiler(NodeVisitor):

def __init__(self):

self.indent_stack = [0]  # initial indentation level

def visit_Indent(self, node, children):

whitespace = node.text[1:]  # after newline

current_level = self.indent_stack[-1]

if len(whitespace) != current_level + 4:

raise ValueError(f"Expected indentation of {current_level + 4} spaces, got {len(whitespace)}")

self.indent_stack.append(len(whitespace))

return ''

def visit_Dedent(self, node, children):

# Dedent occurs implicitly when a line has less indentation

# This would need to be handled when processing subsequent lines

# Not directly captured in the grammar, so may need to track in the visitor

pass

But dedent handling remains a challenge. To detect dedents, the visitor would need to compare the current line's indentation with the stack. This would require processing each line's indentation in sequence and adjusting the stack as needed.

Perhaps modifying the visitor's visit_Pattern method to handle each line and manage the indentation stack.

For example:

def visit_Pattern(self, node, children):

lines = children

output = []

for line in lines:

# line includes indentation and content

# process indentation level

# compare with current level

# adjust stack and generate SPARQL

pass

return ' '.join(output)

But this would require each line to have its indentation processed before the content.

This approach complicates the visitor's structure but allows for precise control over indentation levels.

In summary, the key steps are:

1. Modify the grammar to capture indentation spaces.

2. Track indentation levels in the visitor using a stack.

3. Enforce that each indent is +4 spaces.

4. Handle dedents by popping the stack when indentation decreases.

This will make nested indents stricter and improve the transpiler's accuracy.

Let’s refine the PyQL grammar to enforce strict, consistent indentation (4 spaces per level) and improve nested block handling. We’ll use parsimonious with a stateful IndentStack helper to track indentation levels. Here’s the improved version: