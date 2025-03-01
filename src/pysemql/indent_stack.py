class IndentStack:
    def __init__(self):
        self.stack = [0]  # Initial indentation level (0 spaces)
    
    def push(self, indent_level):
        expected = self.stack[-1] + 4
        if indent_level != expected:
            raise SyntaxError(f"Expected {expected} spaces, got {indent_level}")
        self.stack.append(indent_level)
    
    def pop(self):
        if len(self.stack) > 1:
            self.stack.pop()
    
    def current(self):
        return self.stack[-1]