
PRECEDENCE = {
    "OR": 1,
    "AND": 2,
    "EQUALS": 3,
    "NOTEQUALS": 3,
    "GT": 4,
    "GTE": 4,
    "LT": 4,
    "LTE": 4,
    "PLUS": 5,
    "MINUS": 5,
    "STAR": 6,
    "SLASH": 6,
    "PERCENT": 6,
    "POWER": 7
}


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.count = 0
        self.functions = set()

    def advance(self):
        self.count += 1

    def current(self):
        if self.count >= len(self.tokens):
            raise SyntaxError("Unexpected end of input")
        return self.tokens[self.count]

    def check(self, token):
        return (
            self.count < len(self.tokens)
            and self.tokens[self.count] == token
        )

    def number(self):
        return self.current()[1]

    def identifier(self):
        return self.current()[1]

    def string(self):
        return self.current()[1]

    def parse(self):
        return self.parse_expression()

    def parse_program(self):
        expressions = []

        while self.count < len(self.tokens):
            expressions.append(self.parse_expression())

        return expressions

    def parse_expression(self, min_precedence=1):
        left = self.parse_postfix()

        while self.count < len(self.tokens):
            operator = self.current()

            if operator not in PRECEDENCE:
                break

            precedence = PRECEDENCE[operator]

            if precedence < min_precedence:
                break

            self.advance()

            if operator == "POWER":
                next_precedence = precedence
            else:
                next_precedence = precedence + 1

            right = self.parse_expression(next_precedence)
            left = (operator, left, right)

        return left

    def parse_postfix(self):
        node = self.parse_prefix()

        while self.check("LSQUARE"):
            self.advance()
            index = self.parse_expression()

            if not self.check("RSQUARE"):
                raise SyntaxError("Expected closing bracket")

            self.advance()
            node = ("INDEX", node, index)

        return node

    def parse_prefix(self):
        token = self.current()

        if token == "LPAREN":
            self.advance()
            result = self.parse_expression()

            if not self.check("RPAREN"):
                raise SyntaxError("Expected closing parenthesis")

            self.advance()
            return result

        elif token == "LBRACKET":
            self.advance()
            expressions = []

            while not self.check("RBRACKET"):
                if self.count >= len(self.tokens):
                    raise SyntaxError("Expected closing brace")

                expressions.append(self.parse_expression())

            if not expressions:
                raise SyntaxError("Empty blocks are not allowed")

            self.advance()
            return ("BLOCK", expressions)

        elif token == "LSQUARE":
            self.advance()
            elements = []

            if not self.check("RSQUARE"):
                elements.append(self.parse_expression())

                while self.check("COMMA"):
                    self.advance()
                    elements.append(self.parse_expression())

            if not self.check("RSQUARE"):
                raise SyntaxError("Expected closing bracket")

            self.advance()
            return ("LIST", elements)

        elif token == "MINUS":
            self.advance()
            return ("NEGATE", self.parse_expression(8))

        elif token == "NOT":
            self.advance()
            return ("NOT", self.parse_expression(8))

        elif token == "LEN":
            self.advance()
            return ("LEN", self.parse_expression(8))

        elif (
            isinstance(token, tuple)
            and token[0] in ("NUMBER", "FLOATING_NUMBER")
        ):
            value = self.number()
            self.advance()
            return value

        elif isinstance(token, tuple) and token[0] == "STRING":
            value = self.string()
            self.advance()
            return ("STRING", value)

        elif token == "PRINT":
            self.advance()
            return ("PRINT", self.parse_expression())

        elif token == "INPUT":
            self.advance()

            if (
                self.count < len(self.tokens)
                and isinstance(self.current(), tuple)
                and self.current()[0] == "STRING"
            ):
                return ("INPUT", self.parse_expression())

            return ("INPUT", None)

        elif token in ("TOINT", "TOSTRING"):
            command = token
            self.advance()
            return (command, self.parse_expression(8))

        elif token == "IMPORT":
            command = token
            self.advance()
            if (
                self.count < len(self.tokens)
                and isinstance(self.current(), tuple)
                and self.current()[0] == "STRING"
            ):
                return (command, self.parse_expression(8))
            else:
                raise SyntaxError("Expected path to char file")

        elif token == "FUNCTION":
            self.advance()

            if (
                not isinstance(self.current(), tuple)
                or self.current()[0] != "IDENTIFIER"
            ):
                raise SyntaxError("Expected function name")

            name = self.identifier()
            self.advance()

            parameters = []

            while not self.check("ARROW"):
                if (
                    self.count >= len(self.tokens)
                    or not isinstance(self.current(), tuple)
                    or self.current()[0] != "IDENTIFIER"
                ):
                    raise SyntaxError("Expected parameter name or '=>'")

                parameters.append(self.identifier())
                self.advance()

                if self.check("COMMA"):
                    self.advance()
                elif not self.check("ARROW"):
                    raise SyntaxError("Expected '=>'")

            self.advance()
            self.functions.add(name)
            body = self.parse_expression()

            return ("FUN", name, parameters, body)

        elif token == "WHEN":
            self.advance()
            branches = []

            while True:
                condition = self.parse_expression()

                if not self.check("ARROW"):
                    raise SyntaxError("Expected '=>' in when expression")

                self.advance()
                value = self.parse_expression()
                branches.append((condition, value))

                if not self.check("PIPE"):
                    break

                self.advance()

            return ("WHEN", branches)

        elif token == "UNDERSCORE":
            self.advance()
            return ("UNDERSCORE", True)

        elif token == "LET":
            self.advance()

            if (
                self.count >= len(self.tokens)
                or not isinstance(self.current(), tuple)
                or self.current()[0] != "IDENTIFIER"
            ):
                raise SyntaxError("Expected variable name")

            name = self.identifier()
            self.advance()

            if not self.check("EQUALS"):
                raise SyntaxError("Expected '=' in variable declaration")

            self.advance()
            value = self.parse_expression()

            return ("LET", name, value)

        elif token in ("TRUE", "FALSE"):
            self.advance()
            return ("BOOLEAN", token == "TRUE")

        elif isinstance(token, tuple) and token[0] == "IDENTIFIER":
            name = self.identifier()
            self.advance()

            if self.check("LPAREN"):
                self.advance()
                arguments = []

                if not self.check("RPAREN"):
                    arguments.append(self.parse_expression())

                    while self.check("COMMA"):
                        self.advance()
                        arguments.append(self.parse_expression())

                if not self.check("RPAREN"):
                    raise SyntaxError("Expected closing parenthesis")

                self.advance()
                return ("CALL", name, arguments)

            return ("VARIABLE", name)

        raise SyntaxError(
            f"Unexpected token: {token} at position {self.count}; "
        )
