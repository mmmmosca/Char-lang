class Lexer:
    def __init__(self, line):
        self.line = line

    def tokenize(self):
        i = 0
        length_line = len(self.line)
        result = []

        while i < length_line:
            current = self.line[i]

            if current == "+":
                result.append("PLUS")

            elif current == "-":
                result.append("MINUS")

            elif current == "*":
                result.append("STAR")

            elif current == "/":
                result.append("SLASH")

            elif current == "%":
                result.append("PERCENT")

            elif current == "^":
                result.append("POWER")

            elif current == ",":
                result.append("COMMA")

            elif current == "_":
                result.append("UNDERSCORE")

            elif current == "#":
                while i < length_line and self.line[i] != "\n":
                    i += 1
                continue

            elif current == "=":
                if self.line[i+1] == ">":
                    result.append("ARROW")
                    i += 2
                    continue
                else:
                    result.append("EQUALS")

            elif current == "|":
                if self.line[i+1] == "|":
                    result.append("OR")
                    i += 2
                    continue
                else:
                    result.append("PIPE")

            elif current == "&":
                result.append("AND")

            elif current == "!":
                if self.line[i+1] == "=":
                    result.append("NOTEQUALS")
                    i += 2
                    continue
                else:
                    result.append("NOT")

            elif current == ">":
                if self.line[i+1] == "=":
                    result.append("GTE")
                    i += 2
                    continue
                else:
                    result.append("GT")

            elif current == "<":
                if self.line[i+1] == "=":
                    result.append("LTE")
                    i += 2
                    continue
                else:
                    result.append("LT")

            elif current == "(":
                result.append("LPAREN")

            elif current == ")":
                result.append("RPAREN")

            elif current == "{":
                result.append("LBRACKET")

            elif current == "}":
                result.append("RBRACKET")

            elif current == "[":
                result.append("LSQUARE")

            elif current == "]":
                result.append("RSQUARE")

            elif current.isdigit():
                j = i

                while j < length_line and self.line[j].isdigit():
                    j += 1

                if j < length_line and self.line[j] == '.':
                    j += 1

                    while j < length_line and self.line[j].isdigit():
                        j += 1

                    number = self.line[i:j]

                    if number.endswith('.'):
                        raise ValueError(f"Unexpected value {number}")

                    result.append(("FLOATING_NUMBER", float(number)))
                else:
                    result.append(("NUMBER", int(self.line[i:j])))

                i = j
                continue

            elif current.isalpha():
                j = i

                while j < length_line and (self.line[j].isalnum() or self.line[j] == '_'):
                    j += 1

                keyword = self.line[i:j]

                if keyword == "print":
                    result.append("PRINT")
                elif keyword == "input":
                    result.append("INPUT")
                elif keyword == "toint":
                    result.append("TOINT")
                elif keyword == "tostring":
                    result.append("TOSTRING")
                elif keyword == "let":
                    result.append("LET")
                elif keyword == "fun":
                    result.append("FUNCTION")
                elif keyword == "when":
                    result.append("WHEN")
                elif keyword == "true":
                    result.append("TRUE")
                elif keyword == "false":
                    result.append("FALSE")
                elif keyword == "import":
                    result.append("IMPORT")
                elif keyword == "len":
                    result.append("LEN")
                else:
                    result.append(("IDENTIFIER", keyword))
                i = j
                continue

            elif current == '"':
                j = i + 1

                while j < length_line and self.line[j] != '"':
                    j += 1

                if j == length_line:
                    raise SyntaxError("Unterminated string literal")

                result.append(("STRING", self.line[i + 1:j]))

                i = j + 1
                continue
            elif current.isspace():
                pass
            else:
                raise SyntaxError(f"Unexpected character: {current}")
            i += 1
        return result


#lexer = Lexer("fun test n => + n 1")
#print(lexer.tokenize())
