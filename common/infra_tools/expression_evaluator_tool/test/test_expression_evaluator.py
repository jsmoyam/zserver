from nose.tools import assert_equal, assert_true, assert_false, raises

from common.infra_tools.expression_evaluator_tool.expression_evaluator import Stack, Token, ExpressionEvaluator


class TestExpressionEvaluator(object):

    @classmethod
    def setup_class(cls):
        """This method is run once for each class before any tests are run"""

    @classmethod
    def teardown_class(cls):
        """This method is run once for each class _after_ all tests are run"""

    def setup(self):
        """This method is run once before _each_ test method is executed"""

    def teardown(self):
        """This method is run once after _each_ test method is executed"""

    def test_stack(self):
        """stack: test de clase Stack"""
        s = Stack()
        s.push(1)
        data = s.pop()
        assert_equal(data, 1)
        assert_true(s.is_empty())

        s.push(2)
        data = s.peek()
        assert_equal(data, 2)
        assert_false(s.is_empty())

        s.push(2)
        assert_equal(s.size(), 2)

    # @raises(TypeError)
    # def test_length_2(self):
    #     """length: test de longitud pasandole un numero en vez de una cadena"""
    #     test_int = 5555
    #     test_list = [test_int]
    #     op.length(test_list)

    def test_token(self):
        """token: test de clase Token"""
        t1 = Token(Token.FUNCTION, 1)
        t2 = Token(Token.VALUE, 2)
        t3 = Token(Token.ATTRIBUTE, 3)
        t4 = Token(Token.PARENTHESIS, 4)
        t5 = Token(Token.OPERATOR, 5)

        str(t1)
        repr(t1)
        str(t2)
        repr(t2)
        str(t3)
        repr(t3)
        str(t4)
        repr(t4)
        str(t5)
        repr(t5)

        assert_true(t1.is_type(Token.FUNCTION))
        assert_true(t2.is_type(Token.VALUE))
        assert_true(t3.is_type(Token.ATTRIBUTE))
        assert_true(t4.is_type(Token.PARENTHESIS))
        assert_true(t5.is_type(Token.OPERATOR))

    def test_evaluate_1(self):
        """evaluate: test de evaluacion 1 con resultado correcto y expresion simple"""
        expr = 'a>3 and b<=7'
        values = {'a': 5, 'b': 5, 'c': 0, 'd': 2}
        ev = ExpressionEvaluator(expr)
        res = ev.evaluate(values)
        assert_true(res)

    def test_evaluate_2(self):
        """evaluate: test de evaluacion 2 con resultado correcto y expresion con parentesis"""
        expr = '(a>3 and b<7) and (c=0 or d=1)'
        values = {'a': 5, 'b': 5, 'c': 0, 'd': 2}
        ev = ExpressionEvaluator(expr)
        res = ev.evaluate(values)
        assert_true(res)

    def test_evaluate_3(self):
        """evaluate: test de evaluacion 3 con resultado correcto y expresion con funcion simple y operadores
        de un argumento"""
        expr = 'length[a]=9 and (not xxx and a contains "hola") and (b<10 or c=6)'
        values = {'a': 'holamundo', 'b': 8, 'c': 6, 'xxx': False}
        ev = ExpressionEvaluator(expr)
        res = ev.evaluate(values)
        assert_true(res)

    def test_evaluate_4(self):
        """evaluate: test de evaluacion 4 con resultado correcto y expresion con funcion simple, operadores
        de un argumento y comparaciones con booleanos"""
        expr = 'length[a]=9 and (not xxx and a contains "hola") and (b<10 or c=6) and xxx=False'
        values = {'a': 'holamundo', 'b': 8, 'c': 6, 'xxx': False}
        ev = ExpressionEvaluator(expr)
        res = ev.evaluate(values)
        assert_true(res)

    def test_evaluate_5(self):
        """evaluate: test de evaluacion 5 con resultado correcto y expresion con funciones multiples, operadores
        de un argumento y comparaciones con booleanos"""
        expr = 'length[a]=9 and (not xxx and a contains "hola") and (b<10 or c=6) and (xxx=False and ' \
               'True=have_passed_time["2017-01-01 00:00:00",60,weeks])'
        values = {'a': 'holamundo', 'b': 8, 'c': 6, 'xxx': False}
        ev = ExpressionEvaluator(expr)
        res = ev.evaluate(values)
        assert_true(res)

    def test_evaluate_6(self):
        """evaluate: test de evaluacion 6 con resultado correcto y expresion con funciones multiples, operadores
        de un argumento y comparaciones con booleanos"""
        expr = 'length["hola"]'
        values = {'a': 'holamundo', 'b': 8, 'c': 6, 'xxx': False}
        ev = ExpressionEvaluator(expr)
        res = ev.evaluate(values)
        assert_true(res)

    def test_evaluate_7(self):
        """evaluate: test de evaluacion 7 con resultado correcto y expresion con funciones multiples, operadores
        de un argumento y comparaciones con booleanos"""
        expr = 'have_passed_time["2017-01-01 00:00:00", 60, weeks]'
        values = {'a': 'holamundo', 'b': 8, 'c': 6, 'xxx': False}
        ev = ExpressionEvaluator(expr)
        res = ev.evaluate(values)
        assert_true(res)

    def test_evaluate_8(self):
        """evaluate: test de evaluacion 8 con resultado correcto y expresion icontains"""
        expr = '"HOLAMUNDO" icontains "hola"'
        values = dict()
        ev = ExpressionEvaluator(expr)
        res = ev.evaluate(values)
        assert_true(res)

    def test_evaluate_9(self):
        """evaluate: test de evaluacion 9 con resultado correcto y expresion algebraica simple"""
        expr = '3+5'
        # values = {'a': 'holamundo', 'b': 8, 'c': 6, 'xxx': False}
        values = dict()
        ev = ExpressionEvaluator(expr)
        res = ev.evaluate(values)
        assert_equal(8, res)

    def test_evaluate_10(self):
        """evaluate: test de evaluacion 10 con resultado correcto y expresion algebraica compleja"""
        expr = '(3+5)*a-4*3+10/5'
        values = {'a': 2}
        ev = ExpressionEvaluator(expr)
        res = ev.evaluate(values)
        assert_equal(6, res)

    def test_evaluate_11(self):
        """evaluate: test de evaluacion 11 con resultado correcto y expresion mixta booleana y algebraica"""
        expr = '(a+3)<b'
        values = {'a': 2, 'b': 10}
        ev = ExpressionEvaluator(expr)
        res = ev.evaluate(values)
        assert_true(res)

    def test_evaluate_12(self):
        """evaluate: test de evaluacion 12 con resultado correcto y expresion con funciones multiples, operadores
        de un argumento, expresiones algebraicas y comparaciones con booleanos"""
        expr = 'length[a]=9 and (not xxx and a contains "hola") and (b<10 or c=6) and (xxx=False and ' \
               'True=have_passed_time["2017-01-01 00:00:00",60,weeks]) and ((2*c)<b or (b+c)=50)'
        values = {'a': 'holamundo', 'b': 8, 'c': 6, 'xxx': False}
        ev = ExpressionEvaluator(expr)
        res = ev.evaluate(values)
        assert_false(res)

    @raises(ValueError)
    def test_evaluate_13(self):
        """evaluate: test de evaluacion 13 con resultado incorrecto por expresion mal formada"""
        expr = 'have_passed_time[2017-01-01 00:00:00", 60, weeks]'
        values = {'a': 'holamundo', 'b': 8, 'c': 6, 'xxx': False}
        ev = ExpressionEvaluator(expr)
        ev.evaluate(values)

    @raises(ValueError)
    def test_evaluate_14(self):
        """evaluate: test de evaluacion 14 con resultado incorrecto por expresion mal formada"""
        expr = 'a>3 and b 7'
        values = {'a': 5, 'b': 5, 'c': 0, 'd': 2}
        ev = ExpressionEvaluator(expr)
        ev.evaluate(values)

    @raises(ValueError)
    def test_evaluate_15(self):
        """evaluate: test de evaluacion 15 con resultado incorrecto por variable no encontrada"""
        expr = 'a>3 and b=7'
        values = {'a': 5}
        ev = ExpressionEvaluator(expr)
        ev.evaluate(values)

    def test_evaluate_16(self):
        """evaluate: test de evaluacion 16 con resultado correcto devolviendo literal"""
        expr = '"hola"'
        values = {}
        ev = ExpressionEvaluator(expr)
        res = ev.evaluate(values)
        assert_equal(res, 'hola')
