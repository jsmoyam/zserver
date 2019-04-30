import importlib
import re
import sys

from common.infra_tools.expression_evaluator_tool.operations import Operations


class Stack:
    def __init__(self):
        self.items = []

    def is_empty(self):
        return self.items == []

    def push(self, item):
        self.items.append(item)

    def pop(self):
        return self.items.pop()

    def peek(self):
        return self.items[len(self.items) - 1]

    def size(self):
        return len(self.items)


class Token:
    PARENTHESIS = 'PARENTHESIS'
    OPERATOR = 'OPERATOR'
    ATTRIBUTE = 'ATTRIBUTE'
    VALUE = 'VALUE'
    FUNCTION = 'FUNCTION'
    STRING = 'STRING'

    def __init__(self, token_type, value):
        self.token_type = token_type
        self.value = value

    def __str__(self):
        return '{}( {} )'.format(self.token_type, self.value)

    def __repr__(self):
        return self.__str__()

    def is_type(self, token_type):
        return token_type == self.token_type


class ExpressionEvaluator:
    def __init__(self, expr):
        self.expr = expr
        self.operators_functions = Operations.OPERATORS
        self.operators = list(Operations.OPERATORS.keys())
        self.expr_postfix = self._infix_to_postfix_boolean()
        self.function_modules = list()
        self.add_function_package('common.infra_tools.expression_evaluator_tool.operations')
        self.additional_data = None

    def add_function_package(self, function_module: str) -> None:
        if function_module not in self.function_modules:
            importlib.import_module(function_module)
            self.function_modules.append(function_module)

    def set_additional_data(self, additional_data):
        # Store additional data in class variable
        self.additional_data = additional_data

    def _infix_to_postfix_boolean(self):

        # Pila y variable de salida en notacion postfija
        stack = Stack()
        postfix = []

        # Orden de precedencias. El parentesis tiene prioridad. Los corchetes se usan para las funciones
        prec = dict()
        prec['('] = 1
        for op, value in self.operators_functions.items():
            prec[op] = value[2]
        parenthesis = ['(', ')']
        brackets = ['[', ']']

        # Limpiar la expresion: añadir espacios antes y despues de operadores, sustituir parentesis por
        # parentesis + espacio, eliminar espacio antes y despues de comas y corchetes (para funciones)
        # Lo que este entre comillas nunca tiene que hacerse dentro el split

        infix_expr = self.expr

        # Sustituir todas las cadenas de texto por un token de texto. Esto prevendra problemas a la hora de hacer split
        matched_quotes = re.findall(r'\"(.+?)\"', infix_expr)
        self.dict_strings = dict()
        i = 1
        for c in matched_quotes:
            key = '%%var' + str(i)
            self.dict_strings[key] = c
            infix_expr = infix_expr.replace('"' + c + '"', key)
            i += 1

        for c in infix_expr:
            if c in self.operators:
                infix_expr = infix_expr.replace(c, ' ' + c + ' ')
        infix_expr = infix_expr.replace('(', '( ')
        infix_expr = infix_expr.replace(')', ' )')
        infix_expr = infix_expr.replace(', ', ',')
        infix_expr = infix_expr.replace(' ,', ',')
        infix_expr = infix_expr.replace('[ ', '[')
        infix_expr = infix_expr.replace(' [', '[')
        infix_expr = infix_expr.replace(' ]', ']')
        infix_expr = infix_expr.replace('<  =', '<=')
        infix_expr = infix_expr.replace('>  =', '>=')
        infix_expr = infix_expr.replace('!  =', '!=')

        # Convertir una lista en split a una lista de tokens de parentesis, operadores y condiciones
        expr_splitted = infix_expr.split()

        token_list = list()
        for value in expr_splitted:
            if value in parenthesis:
                t = Token(Token.PARENTHESIS, value)
            elif value in self.operators:
                t = Token(Token.OPERATOR, value)
            elif brackets[0] in value:
                t = Token(Token.FUNCTION, value)
            elif value.isnumeric():
                t = Token(Token.VALUE, int(value))
            elif value == 'True' or value == 'False':
                t = Token(Token.VALUE, True if value == 'True' else False)
            else:
                t = Token(Token.ATTRIBUTE, value)
            token_list.append(t)

        # Creacion de pila
        # Para cada token:
        #     Si es atributo, valor o funcion --> añadir a cadena de salida postfija
        #     Si es ( --> añadir a pila
        #     Si es ) --> ir sacando elementos de pila hasta encontrar (
        #     En otro caso (operador) --> mientras se cumpla orden de precedencia, sacar elementos de pila para
        #       añadirlo a la salida. Finalmente añadir operador a salida
        for token in token_list:

            if token.is_type(Token.ATTRIBUTE) or token.is_type(Token.VALUE) or token.is_type(Token.FUNCTION):
                postfix.append(token)
            elif token.is_type(Token.PARENTHESIS) and token.value == '(':
                stack.push(token)
            elif token.is_type(Token.PARENTHESIS) and token.value == ')':
                top_token = stack.pop()
                while top_token.value != '(':
                    postfix.append(top_token)
                    top_token = stack.pop()
            else:
                while (not stack.is_empty()) and (prec[stack.peek().value] >= prec[token.value]):
                    postfix.append(stack.pop())
                stack.push(token)

        # Sacar elementos de pila hasta que este vacia
        while not stack.is_empty():
            token = stack.pop()
            postfix.append(token)

        return postfix

    def evaluate(self, arg_values):
        s = Stack()

        for token in self.expr_postfix:
            if token.is_type(Token.VALUE):
                s.push(token.value)
            elif token.is_type(Token.ATTRIBUTE):
                if token.value in arg_values:
                    s.push(arg_values[token.value])
                elif token.value in self.dict_strings:
                    s.push(self.dict_strings[token.value])
                else:
                    raise ValueError
            elif token.is_type(Token.FUNCTION):
                # Evaluar la funcion y meter el resultado en la pila. En token.value esta function_name[args]
                # Para ello se busca el nombre de la funcion, sus argumentos ,
                # se sustituyen los argumentos por los valores proporcionados en values y en el diccionario de cadenas,
                # se coge el metodo de la clase y se ejecuta
                pos_bracket_open = token.value.find('[')
                pos_bracket_close = token.value.find(']')
                function_name = token.value[0:pos_bracket_open]
                arguments = token.value[pos_bracket_open + 1:pos_bracket_close].split(',')

                arguments_subst = list()
                for x in arguments:
                    if x in arg_values:
                        arguments_subst.append(arg_values[x])
                    elif x in self.dict_strings:
                        arguments_subst.append(str(self.dict_strings[x]))
                    else:
                        arguments_subst.append(x)

                for function_module in self.function_modules:
                    try:
                        method = getattr(sys.modules[function_module], function_name)
                        res = method(arguments_subst, self.additional_data)
                        s.push(res)
                        break
                    except ValueError as ve:
                        raise ve
                    except Exception as e:
                        pass
            else:
                operation = token.value
                num_args = self.operators_functions[operation][1]
                # No se permiten operadores de mas de dos argumentos. Para eso hay que usar funciones
                res = None
                if num_args == 2:
                    op2 = s.pop()
                    op1 = s.pop()
                    res = self.operators_functions[operation][0](op1, op2)
                elif num_args == 1:
                    op1 = s.pop()
                    res = self.operators_functions[operation][0](op1)

                s.push(res)

        # Si hay mas de un valor en la pila es que la expresion no estaba correctamente formada
        if s.size() != 1:
            raise ValueError()

        return s.pop()
