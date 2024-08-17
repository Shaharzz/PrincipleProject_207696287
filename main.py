# Lexer: Tokenizes the source code
class Lexer:
    def __init__(self, source_code):
        self.source_code = source_code
        self.tokens = []
        self.current_char = ''
        self.index = 0

    def next_char(self):
        if self.index < len(self.source_code):
            self.current_char = self.source_code[self.index]
            self.index += 1
        else:
            self.current_char = None

    def tokenize(self):
        self.next_char()
        while self.current_char is not None:
            if self.current_char.isspace():
                self.next_char()
            elif self.current_char.isalpha():
                self.tokenize_identifier_or_keyword()
            elif self.current_char.isdigit():
                self.tokenize_number()
            elif self.current_char == '=' and self.source_code[self.index:self.index+1] == '=':
                self.tokens.append(('EQUAL', '=='))
                self.index += 1
                self.next_char()

            elif self.current_char == '!' and self.source_code[self.index:self.index + 1] == '=':
                self.tokens.append(('NOTEQUAL', '!='))
                self.index += 1
                self.next_char()

            elif self.current_char in "+-*/":
                self.tokens.append(('OPERATOR', self.current_char))
                self.next_char()
            elif self.current_char == '{':
                self.tokens.append(('LBRACE', '{'))
                self.next_char()
            elif self.current_char == '}':
                self.tokens.append(('RBRACE', '}'))
                self.next_char()
            elif self.current_char == '(':
                self.tokens.append(('LPAREN', '('))
                self.next_char()
            elif self.current_char == ')':
                self.tokens.append(('RPAREN', ')'))
                self.next_char()
            elif self.current_char == ';':
                self.tokens.append(('SEMICOLON', ';'))
                self.next_char()
            elif self.current_char == '=':
                self.tokens.append(('ASSIGN', '='))
                self.next_char()
            elif self.current_char == '>':
                self.tokens.append(('Greater', '>'))
                self.next_char()
            elif self.current_char == '<':
                self.tokens.append(('Smaller', '<'))
                self.next_char()
            elif self.current_char == ',':
                self.tokens.append(('COMMA', ','))
                self.next_char()
            else:
                raise ValueError(f"Unknown character: {self.current_char}")
        return self.tokens

    def tokenize_identifier_or_keyword(self):
        identifier = ''
        while self.current_char is not None and self.current_char.isalnum():
            identifier += self.current_char
            self.next_char()

        keywords = {'if', 'else', 'while', 'for', 'in', 'print'}
        if identifier in keywords:
            self.tokens.append(('KEYWORD', identifier))
        else:
            self.tokens.append(('IDENTIFIER', identifier))

    def tokenize_number(self):
        number = ''
        while self.current_char is not None and self.current_char.isdigit():
            number += self.current_char
            self.next_char()
        self.tokens.append(('NUMBER', int(number)))

# Parser: Builds a syntax tree from tokens
class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.index = 0

    def parse(self):
        statements = []
        while self.index < len(self.tokens):
            statements.append(self.parse_statement())
        return statements

    def parse_statement(self):
        token_type, token_value = self.tokens[self.index]

        if token_type == 'IDENTIFIER' and self.tokens[self.index + 1][1] == '=':
            return self.parse_assignment()
        elif token_value == 'if':
            return self.parse_if_statement()
        elif token_value == 'while':
            return self.parse_while_statement()
        elif token_value == 'for':
            return self.parse_for_statement()
        elif token_value == 'print':
            return self.parse_print_statement()
        else:
            expr = self.parse_expression()
            self.index += 1  # skip ';'
            return expr

    def parse_assignment(self):
        variable_name = self.tokens[self.index][1]
        self.index += 2  # skip variable name and '='
        expression = self.parse_expression()
        self.index += 1  # skip ';'
        return ('ASSIGN', variable_name, expression)
    def parse_if_statement(self):
        self.index += 1  # skip 'if'
        condition = self.parse_expression()
        self.index += 1  # skip '{'
        if_body = []
        while self.tokens[self.index][0] != 'RBRACE':
            if_body.append(self.parse_statement())
        self.index += 1  # skip '}'
        else_body = []
        if self.index < len(self.tokens) and self.tokens[self.index][1] == 'else':
            self.index += 2  # skip 'else' and '{'
            while self.tokens[self.index][0] != 'RBRACE':
                else_body.append(self.parse_statement())
            self.index += 1  # skip '}'
        return ('IF', condition, if_body, else_body)

    def parse_while_statement(self):
        self.index += 1  # skip 'while'
        condition = self.parse_expression()
        self.index += 1  # skip '{'
        body = []
        while self.tokens[self.index][0] != 'RBRACE':
            body.append(self.parse_statement())
        self.index += 1  # skip '}'
        return ('WHILE', condition, body)

    def parse_print_statement(self):
        self.index += 1  # skip 'print'
        expression = self.parse_expression()
        self.index += 1  # skip ';'
        return ('PRINT', expression)

    def parse_expression(self):
        left = self.parse_comparison()
        while self.index < len(self.tokens) and self.tokens[self.index][0] in ('EQUAL', 'NOTEQUAL'):
            op = self.tokens[self.index][0]
            self.index += 1
            right = self.parse_comparison()
            left = (op, left, right)
        return left

    def parse_comparison(self):
        left = self.parse_term()
        while self.index < len(self.tokens) and self.tokens[self.index][0] in ('Greater', 'Smaller'):
            op = self.tokens[self.index][0]
            self.index += 1
            right = self.parse_term()
            left = (op, left, right)
        return left

    def parse_term(self):
        node = self.parse_factor()
        while self.index < len(self.tokens) and self.tokens[self.index][1] in ('+', '-'):
            token_type, operator = self.tokens[self.index]
            self.index += 1
            node = (operator, node, self.parse_factor())
        return node

    def parse_factor(self):
        node = self.parse_primary()
        while self.index < len(self.tokens) and self.tokens[self.index][1] in ('*', '/'):
            token_type, operator = self.tokens[self.index]
            self.index += 1
            node = (operator, node, self.parse_primary())
        return node

    def parse_primary(self):
        token_type, token_value = self.tokens[self.index]

        if token_value == '(':
            self.index += 1  # skip '('
            node = self.parse_expression()
            if self.tokens[self.index][1] == ')':
                self.index += 1  # skip ')'
                return node
            else:
                raise ValueError("Expected closing parenthesis")
        elif token_type == 'NUMBER':
            self.index += 1
            return ('NUMBER', token_value)
        elif token_type == 'IDENTIFIER':
            if self.tokens[self.index + 1][1] == '(':
                return self.parse_function_call()
            else:
                self.index += 1
                return ('IDENTIFIER', token_value)

        else:
            raise ValueError(f"Unexpected token: {token_value}")

    def parse_function_call(self):
        function_name = self.tokens[self.index][1]
        self.index += 2  # skip identifier and '('
        args = []
        while self.tokens[self.index][1] != ')':
            args.append(self.parse_expression())
            if self.tokens[self.index][1] == ',':
                self.index += 1
        self.index += 1  # skip ')'
        return ('FUNCTION_CALL', function_name, args)

    def parse_for_statement(self):
        self.index += 1  # skip 'for'
        variable = self.tokens[self.index][1]
        self.index += 1  # skip variable
        if self.tokens[self.index][1] != 'in':
            raise ValueError("Expected 'in' in for loop")
        self.index += 1  # skip 'in'
        iterable = self.parse_expression()
        self.index += 1  # skip '{'
        body = []
        while self.tokens[self.index][0] != 'RBRACE':
            body.append(self.parse_statement())
        self.index += 1  # skip '}'
        return ('FOR', variable, iterable, body)


# Interpreter: Executes the syntax tree
class Interpreter:
    def __init__(self, syntax_tree):
        self.syntax_tree = syntax_tree
        self.variables = {}
        self.functions = {}

    def evaluate_function_definition(self, statement):
        function_name = statement[1]
        parameters = statement[2]
        body = statement[3]
        self.functions[function_name] = (parameters, body)

    def evaluate_statement(self, statement):
        stmt_type = statement[0]

        if stmt_type == 'FUNCTION_DEF':
            self.evaluate_function_definition(statement)

    def evaluate(self):
        for statement in self.syntax_tree:
            self.evaluate_statement(statement)

    def evaluate_statement(self, statement):
        stmt_type = statement[0]

        if stmt_type == 'ASSIGN':
            self.evaluate_assignment(statement)
        elif stmt_type == 'IF':
            self.evaluate_if_statement(statement)
        elif stmt_type == 'WHILE':
            self.evaluate_while_statement(statement)
        elif stmt_type == 'FOR':
            self.evaluate_for_statement(statement)
        elif stmt_type == 'PRINT':
            self.evaluate_print_statement(statement)

    def evaluate_assignment(self, statement):
        variable_name = statement[1]
        expression_value = self.evaluate_expression(statement[2])
        self.variables[variable_name] = expression_value

    def evaluate_if_statement(self, statement):
        condition = self.evaluate_expression(statement[1])
        if condition:
            for stmt in statement[2]:
                self.evaluate_statement(stmt)
        elif statement[3]:  # else part
            for stmt in statement[3]:
                self.evaluate_statement(stmt)

    def evaluate_while_statement(self, statement):
        while self.evaluate_expression(statement[1]):
            for stmt in statement[2]:
                self.evaluate_statement(stmt)

    def evaluate_range(self, args):
        if len(args) == 1:
            start, stop, step = 0, self.evaluate_expression(args[0]), 1
        elif len(args) == 2:
            start, stop = self.evaluate_expression(args[0]), self.evaluate_expression(args[1])
            step = 1
        elif len(args) == 3:
            start = self.evaluate_expression(args[0])
            stop = self.evaluate_expression(args[1])
            step = self.evaluate_expression(args[2])
        else:
            raise ValueError("range() takes 1-3 arguments")

        return list(range(start, stop, step))
    def evaluate_for_statement(self, statement):
        variable = statement[1]
        iterable = self.evaluate_expression(statement[2])
        body = statement[3]

        for value in iterable:
            self.variables[variable] = value
            for stmt in body:
                self.evaluate_statement(stmt)
    def evaluate_print_statement(self, statement):
        print(self.evaluate_expression(statement[1]))

    def evaluate_expression(self, expression):
        expr_type = expression[0]
        if expr_type == 'NUMBER':
            return expression[1]
        elif expr_type == 'IDENTIFIER':
            return self.variables[expression[1]]
        elif expr_type in ('+', '-', '*', '/'):
            left = self.evaluate_expression(expression[1])
            right = self.evaluate_expression(expression[2])
            if expr_type == '+':
                return left + right
            elif expr_type == '-':
                return left - right
            elif expr_type == '*':
                return left * right
            elif expr_type == '/':
                if right == 0:
                    raise ZeroDivisionError("Cannot divide by zero")
                return left / right
        elif expr_type in ('Greater', 'Smaller', 'EQUAL', 'NOTEQUAL'):
            left = self.evaluate_expression(expression[1])
            right = self.evaluate_expression(expression[2])
            if expr_type == 'Greater':
                return left > right
            elif expr_type == 'Smaller':
                return left < right
            elif expr_type == 'EQUAL':
                return left == right
            elif expr_type == 'NOTEQUAL':
                return left != right

        elif expr_type == 'FUNCTION_CALL':
            function_name = expression[1]
            args = expression[2]
            if function_name == 'power':
                return self.evaluate_power(args)
            elif function_name == 'square':
                return self.evaluate_square(args)
            elif function_name == 'min':
                return self.evaluate_min(args)
            elif function_name == 'max':
                return self.evaluate_max(args)
            elif function_name == 'and':
                return self.evaluate_and(args)
            elif function_name == 'or':
                return self.evaluate_or(args)
            elif function_name == 'range':
                return self.evaluate_range(args)
            else:
                raise ValueError(f"Unknown function: {function_name}")

    def evaluate_power(self, args):
        if len(args) != 2:
            raise ValueError("power function expects two arguments")
        base = self.evaluate_expression(args[0])
        exponent = self.evaluate_expression(args[1])
        return base ** exponent

    def evaluate_square(self, args):
        if len(args) != 1:
            raise ValueError("square function expects one argument")
        value = self.evaluate_expression(args[0])
        return value ** 0.5

    def evaluate_min(self, args):
        if len(args) != 2:
            raise ValueError("min function expects two arguments")
        value1 = self.evaluate_expression(args[0])
        value2 = self.evaluate_expression(args[1])
        return min(value1, value2)

    def evaluate_max(self, args):
        if len(args) != 2:
            raise ValueError("max function expects two arguments")
        value1 = self.evaluate_expression(args[0])
        value2 = self.evaluate_expression(args[1])
        return max(value1, value2)
    def evaluate_and(self, args):
        if len(args) != 2:
            raise ValueError("and function expects two arguments")
        # Roi Zur is hatih and i love him!
        value1 = self.evaluate_expression(args[0])
        value2 = self.evaluate_expression(args[1])
        return value1 and value2
    def evaluate_or(self, args):
        if len(args) != 2:
            raise ValueError("or function expects two arguments")
        value1 = self.evaluate_expression(args[0])
        value2 = self.evaluate_expression(args[1])
        return value1 or value2

    def evaluate_function_call(self, function_name, args):
        if function_name not in self.functions:
            raise ValueError(f"Undefined function: {function_name}")

        parameters, body = self.functions[function_name]
        if len(args) != len(parameters):
            raise ValueError(f"Expected {len(parameters)} arguments, got {len(args)}")

        # Create a new scope for the function
        old_variables = self.variables.copy()
        self.variables = {param: self.evaluate_expression(arg) for param, arg in zip(parameters, args)}

        result = None
        for stmt in body:
            if stmt[0] == 'RETURN':
                result = self.evaluate_expression(stmt[1])
                break
            self.evaluate_statement(stmt)

        # Restore the old scope
        self.variables = old_variables
        return result

# Main: Putting everything together
def main():
    source_code = """
    x = 10;
    while (x > 0) {
        print(x);
        x = x - 1;
    }
    
    for i in range(5) {
        print(i);
    }
    
    if (x == 0) {
        print(x);
    } else {
        print(x);
    }
    
    
    """

    lexer = Lexer(source_code)
    tokens = lexer.tokenize()
    print("Tokens:", tokens)

    parser = Parser(tokens)
    syntax_tree = parser.parse()
    print("Syntax Tree:", syntax_tree)

    interpreter = Interpreter(syntax_tree)
    interpreter.evaluate()

if __name__ == '__main__':
    main()
