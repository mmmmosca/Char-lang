from fileinput import FileInput
from sys import argv
from lexer import Lexer
from parser import Parser

scopes = [{}]
functions = {}

def create_scope():
    scopes.append({})

def destroy_scope():
    if len(scopes) == 1:
        raise RuntimeError("Cannot destroy the global scope")
    scopes.pop()

def define_var(name, value):
    if name in scopes[-1]:
        raise ValueError(f"Variable '{name}' already exists in this scope")
    scopes[-1][name] = value

def get_var(name):
    for scope in reversed(scopes):
        if name in scope:
            return scope[name]
    raise ValueError(f"Variable '{name}' not defined")

def evaluate(expression):
    if isinstance(expression, int):
        return expression
    if isinstance(expression, float):
        return expression

    operator = expression[0]

    if operator == "PRINT":
        result = evaluate(expression[1])
        print(result)
        return None

    elif operator == "BLOCK":
        create_scope()

        try:
            result = None

            for expr in expression[1]:
                result = evaluate(expr)

            return result
        finally:
            destroy_scope()

    elif operator == "INPUT":
        prompt = ""

        if expression[1] is None:
            pass
        else:
            prompt = evaluate(expression[1])
        return input(prompt)

    elif operator == "TOINT":
        result = evaluate(expression[1])
        return int(result)

    elif operator == "TOSTRING":
        result = evaluate(expression[1])
        return str(result)

    elif operator == "LIST":
        return [evaluate(element) for element in expression[1]]

    elif operator == "LEN":
        target = evaluate(expression[1])

        if not isinstance(target, (list, str)):
            raise ValueError("Only lists and strings can be used with len")

        return len(target)

    elif operator == "INDEX":
        target = evaluate(expression[1])
        index = evaluate(expression[2])

        if not isinstance(target, (list, str)):
            raise ValueError("Only lists and strings can be indexed")
        if not isinstance(index, int) or isinstance(index, bool):
            raise ValueError("Index must be an integer")
        if not -len(target) <= index < len(target):
            raise ValueError(f"Index {index} out of range")

        return target[index]

    elif operator == "FUN":
        name = expression[1]
        parameters = expression[2]
        body = expression[3]

        if name in functions:
            raise ValueError(f"Function '{name}' already exists")

        functions[name] = (parameters, body)
        return None

    elif operator == "UNDERSCORE":
        return expression[1]

    elif operator == "WHEN":
        for condition, value in expression[1]:
            if evaluate(condition):
                return evaluate(value)

        raise ValueError("No when branch matched")
    elif operator == "IMPORT":
        file_name = expression[1][1]
        if file_name.endswith(".char"):
            try:
                with open(file_name, "r") as imported:
                    imported_lines = imported.read()

                lexer = Lexer(imported_lines)
                parser = Parser(lexer.tokenize())

                while parser.count < len(parser.tokens):
                    parsed = parser.parse()
                    evaluate(parsed)

                return None
            except FileNotFoundError:
                raise FileNotFoundError(f"File not found: {expression[1]}")
        else:
            raise FileNotFoundError(f"File not found: {expression[1]}")

    elif operator == "NOT":
        result = not evaluate(expression[1])
        return result
    elif operator == "NEGATE":
        result = -evaluate(expression[1])
        return result
    elif operator == "LET":
        name = expression[1]
        value = evaluate(expression[2])
        define_var(name, value)
        return value
    elif operator == "VARIABLE":
        return get_var(expression[1])

    elif operator == "CALL":
        name = expression[1]
        arguments = expression[2]

        if name == "concat":
            if len(arguments) != 2:
                raise ValueError("concat expects two arguments")

            left = evaluate(arguments[0])
            right = evaluate(arguments[1])

            if isinstance(left, list) and isinstance(right, list):
                return left + right

            if isinstance(left, str) and isinstance(right, str):
                return left + right

            raise ValueError("concat expects two lists or two strings")

        if name not in functions:
            raise ValueError(f"Function '{name}' not defined")

        parameters, body = functions[name]

        if len(arguments) != len(parameters):
            raise ValueError(
                f"Function '{name}' expects {len(parameters)} arguments, got {len(arguments)}"
            )

        values = [evaluate(argument) for argument in arguments]

        create_scope()
        try:
            for parameter, value in zip(parameters, values):
                define_var(parameter, value)

            return evaluate(body)
        finally:
            destroy_scope()

    elif operator == "STRING" or operator == "BOOLEAN":
        return expression[1]


    left = evaluate(expression[1])
    right = evaluate(expression[2])

    if operator == "PLUS":
        return left + right
    elif operator == "MINUS":
        return left - right
    elif operator == "STAR":
        return left * right
    elif operator == "SLASH":
        return left / right
    elif operator == "PERCENT":
        return left % right
    elif operator == "POWER":
        return left ** right
    elif operator == "EQUALS":
        return left == right
    elif operator == "NOTEQUALS":
        return left != right
    elif operator == "OR":
        return left or right
    elif operator == "AND":
        return left and right
    elif operator == "LT":
        return left < right
    elif operator == "LTE":
        return left <= right
    elif operator == "GT":
        return left > right
    elif operator == "GTE":
        return left >= right

    raise ValueError(f"Unknown operator: {operator}")

if argv[1].endswith(".char"):
    with open(argv[1], "r") as file:
        source = file.read()

    lexer = Lexer(source)
    tokenized = lexer.tokenize()
    parser = Parser(tokenized)

    while parser.count < len(parser.tokens):
        parsed = parser.parse()
        evaluate(parsed)
else:
    raise FileExistsError("Files must end in .char")
