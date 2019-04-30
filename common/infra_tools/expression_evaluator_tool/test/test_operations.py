import datetime

from nose.tools import assert_equal, assert_not_equal, assert_true, assert_false, raises

import common.infra_tools.expression_evaluator_tool.operations as op


class TestOperations(object):

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

    def test_length_1(self):
        """length: test de longitud"""
        test_str = 'hello world!'
        test_list = [test_str]
        length = op.length(test_list)
        assert_equal(len(test_str), length)

    @raises(TypeError)
    def test_length_2(self):
        """length: test de longitud pasandole un numero en vez de una cadena"""
        test_int = 5555
        test_list = [test_int]
        op.length(test_list)

    def test_diff_dates_in_days_1(self):
        """diff_dates_in_days: test con formato estandar"""
        d1 = '2017-01-01 00:00:00'
        d2 = '2017-01-11 00:00:00'
        test_list = list()
        test_list.append(d1)
        test_list.append(d2)
        days = op.diff_dates_in_days(test_list)
        assert_equal(10, days)

    def test_diff_dates_in_days_2(self):
        """diff_dates_in_days: test con formato estandar con una hora distinta"""
        d1 = '2017-01-01 00:00:00'
        d2 = '2017-01-11 10:00:00'
        test_list = list()
        test_list.append(d1)
        test_list.append(d2)
        days = op.diff_dates_in_days(test_list)
        assert_equal(10, days)

    def test_diff_dates_in_days_3(self):
        """diff_dates_in_days: test con formato estandar con la hora limite del dia"""
        d1 = '2017-01-01 00:00:00'
        d2 = '2017-01-11 23:59:59'
        test_list = list()
        test_list.append(d1)
        test_list.append(d2)
        days = op.diff_dates_in_days(test_list)
        assert_equal(10, days)

    def test_diff_dates_in_days_4(self):
        """diff_dates_in_days: test con formato estandar con valor incorrecto"""
        d1 = '2017-01-01 00:00:00'
        d2 = '2017-01-12 00:00:01'
        test_list = list()
        test_list.append(d1)
        test_list.append(d2)
        days = op.diff_dates_in_days(test_list)
        assert_not_equal(10, days)

    def test_diff_dates_in_days_5(self):
        """diff_dates_in_days: test en formato año/mes/dia sin horas"""
        d1 = '2017/01/01'
        d2 = '2017/01/11'
        formatter = '%Y/%m/%d'
        test_list = list()
        test_list.append(d1)
        test_list.append(d2)
        test_list.append(formatter)
        days = op.diff_dates_in_days(test_list)
        assert_equal(10, days)

    @raises(ValueError)
    def test_diff_dates_in_days_6(self):
        """diff_dates_in_days: test sin formato estandar y sin especificarlo para que salte excepcion"""
        d1 = '2017/01/01'
        d2 = '2017/01/11'
        test_list = list()
        test_list.append(d1)
        test_list.append(d2)
        op.diff_dates_in_days(test_list)

    @raises(ValueError)
    def test_diff_dates_in_days_7(self):
        """diff_dates_in_days: test de fechas sin date pero si con time, con formato año/mes/dia para que salte
        excepcion"""
        d1 = '00:00:00'
        d2 = '10:00:00'
        formatter = '%Y/%m/%d'
        test_list = list()
        test_list.append(d1)
        test_list.append(d2)
        test_list.append(formatter)
        op.diff_dates_in_days(test_list)

    def test_diff_dates_in_days_8(self):
        """diff_dates_in_days: test de fechas sin date pero si con time, con formato año/mes/dia para que este
        en el mismo dia"""
        d1 = '00:00:00'
        d2 = '10:00:00'
        formatter = '%H:%M:%S'
        test_list = list()
        test_list.append(d1)
        test_list.append(d2)
        test_list.append(formatter)
        days = op.diff_dates_in_days(test_list)
        assert_equal(0, days)

    @raises(ValueError)
    def test_diff_dates_in_days_9(self):
        """diff_dates_in_days: test con menos argumentos de los necesarios para que salte excepcion"""
        d1 = '2017/01/01'
        test_list = list()
        test_list.append(d1)
        op.diff_dates_in_days(test_list)

    @raises(ValueError)
    def test_diff_dates_in_days_10(self):
        """diff_dates_in_days: test con mas argumentos de los necesarios para que salte excepcion"""
        d1 = '2017/01/01'
        d2 = '2017/01/11'
        d3 = ''
        d4 = ''
        test_list = list()
        test_list.append(d1)
        test_list.append(d2)
        test_list.append(d3)
        test_list.append(d4)
        op.diff_dates_in_days(test_list)

    def test_diff_dates_in_days_11(self):
        """diff_dates_in_days: test con fechas al reves"""
        d1 = '2017-01-11 00:00:00'
        d2 = '2017-01-01 00:00:00'
        test_list = list()
        test_list.append(d1)
        test_list.append(d2)
        days = op.diff_dates_in_days(test_list)
        assert_equal(-10, days)

    def test_have_passed_time_1(self):
        """have_passed_time: test con formato estandar calculando en segundos"""
        d = '2017-01-01 00:00:00'
        time = 10
        unit_time = 'seconds'
        test_list = list()
        test_list.append(d)
        test_list.append(time)
        test_list.append(unit_time)
        res = op.have_passed_time(test_list)
        assert_false(res)

    def test_have_passed_time_2(self):
        """have_passed_time: test con formato estandar calculando en minutos"""
        d = '2017-01-01 00:00:00'
        time = 10
        unit_time = 'minutes'
        test_list = list()
        test_list.append(d)
        test_list.append(time)
        test_list.append(unit_time)
        res = op.have_passed_time(test_list)
        assert_false(res)

    def test_have_passed_time_3(self):
        """have_passed_time: test con formato estandar calculando en horas"""
        d = '2017-01-01 00:00:00'
        time = 10
        unit_time = 'hours'
        test_list = list()
        test_list.append(d)
        test_list.append(time)
        test_list.append(unit_time)
        res = op.have_passed_time(test_list)
        assert_false(res)

    def test_have_passed_time_4(self):
        """have_passed_time: test con formato estandar calculando en dias"""
        d = '2017-01-01 00:00:00'
        time = 10
        unit_time = 'days'
        test_list = list()
        test_list.append(d)
        test_list.append(time)
        test_list.append(unit_time)
        res = op.have_passed_time(test_list)
        assert_false(res)

    def test_have_passed_time_5(self):
        """have_passed_time: test con formato estandar calculando en semanas"""
        d = '2017-01-01 00:00:00'
        time = 10
        unit_time = 'weeks'
        test_list = list()
        test_list.append(d)
        test_list.append(time)
        test_list.append(unit_time)
        res = op.have_passed_time(test_list)
        assert_false(res)

    @raises(ValueError)
    def test_have_passed_time_6(self):
        """have_passed_time: test con menos argumentos de los necesarios"""
        d = '2017-01-01 00:00:00'
        time = 10
        test_list = list()
        test_list.append(d)
        test_list.append(time)
        op.have_passed_time(test_list)

    @raises(ValueError)
    def test_have_passed_time_7(self):
        """have_passed_time: test con mas argumentos de los necesarios"""
        d = '2017-01-01 00:00:00'
        time = 10
        unit_time = 'weeks'
        formatter = '%Y-%m-%d %H:%M:%S'
        arg = ''
        test_list = list()
        test_list.append(d)
        test_list.append(time)
        test_list.append(unit_time)
        test_list.append(formatter)
        test_list.append(arg)
        op.have_passed_time(test_list)

    @raises(ValueError)
    def test_have_passed_time_8(self):
        """have_passed_time: test con formato de fecha incorrecto"""
        d = '2017-01-01 00:00:00'
        time = 10
        unit_time = 'weeks'
        arg = ''
        test_list = list()
        test_list.append(d)
        test_list.append(time)
        test_list.append(unit_time)
        test_list.append(arg)
        op.have_passed_time(test_list)

    def test_have_passed_time_9(self):
        """have_passed_time: test calculando en dias con fecha actual"""
        now = datetime.datetime.today()
        d = str(now)
        time = 10
        unit_time = 'days'
        test_list = list()
        test_list.append(d)
        test_list.append(time)
        test_list.append(unit_time)
        res = op.have_passed_time(test_list)
        assert_true(res)

    def test_date_is_eq_1(self):
        """date_is_eq: test de comparacion correcta"""
        d1 = '2017-01-01 00:00:00'
        d2 = '2017-01-01 00:00:00'
        test_list = list()
        test_list.append(d1)
        test_list.append(d2)
        res = op.date_is_eq(test_list)
        assert_true(res)

    def test_date_is_eq_2(self):
        """date_is_eq: test de comparacion incorrecta por date"""
        d1 = '2017-01-01 00:00:00'
        d2 = '2017-01-31 00:00:00'
        test_list = list()
        test_list.append(d1)
        test_list.append(d2)
        res = op.date_is_eq(test_list)
        assert_false(res)

    def test_date_is_eq_3(self):
        """date_is_eq: test de comparacion incorrecta por time"""
        d1 = '2017-01-01 00:00:00'
        d2 = '2017-01-01 11:00:00'
        test_list = list()
        test_list.append(d1)
        test_list.append(d2)
        res = op.date_is_eq(test_list)
        assert_false(res)

    def test_date_is_eq_4(self):
        """date_is_eq: test de comparacion correcta con otro formato"""
        d1 = '01/01/2017 00:00:00'
        d2 = '01/01/2017 00:00:00'
        formatter = '%d/%m/%Y %H:%M:%S'
        test_list = list()
        test_list.append(d1)
        test_list.append(d2)
        test_list.append(formatter)
        res = op.date_is_eq(test_list)
        assert_true(res)

    @raises(ValueError)
    def test_date_is_eq_5(self):
        """date_is_eq: test de comparacion incorrecta por formato"""
        d1 = '2017-01-01 00:00:00'
        d2 = '2017-01-01 00:00:00'
        formatter = '%d/%m/%Y %H:%M:%S'
        test_list = list()
        test_list.append(d1)
        test_list.append(d2)
        test_list.append(formatter)
        op.date_is_eq(test_list)

    def test_date_is_neq_1(self):
        """date_is_neq: test de comparacion correcta"""
        d1 = '2017-01-01 00:00:00'
        d2 = '2017-01-11 00:00:00'
        test_list = list()
        test_list.append(d1)
        test_list.append(d2)
        res = op.date_is_neq(test_list)
        assert_true(res)

    def test_date_is_neq_2(self):
        """date_is_neq: test de comparacion incorrecta por date"""
        d1 = '2017-01-01 00:00:00'
        d2 = '2017-01-01 00:00:00'
        test_list = list()
        test_list.append(d1)
        test_list.append(d2)
        res = op.date_is_neq(test_list)
        assert_false(res)

    def test_date_is_neq_3(self):
        """date_is_neq: test de comparacion correcta con otro formato"""
        d1 = '01/01/2017 00:00:00'
        d2 = '01/01/2017 00:11:00'
        formatter = '%d/%m/%Y %H:%M:%S'
        test_list = list()
        test_list.append(d1)
        test_list.append(d2)
        test_list.append(formatter)
        res = op.date_is_neq(test_list)
        assert_true(res)

    @raises(ValueError)
    def test_date_is_neq_4(self):
        """date_is_neq: test de comparacion incorrecta por formato"""
        d1 = '2017-01-01 00:00:00'
        d2 = '2017-01-01 00:00:00'
        formatter = '%d/%m/%Y %H:%M:%S'
        test_list = list()
        test_list.append(d1)
        test_list.append(d2)
        test_list.append(formatter)
        op.date_is_neq(test_list)

    def test_date_is_gt_1(self):
        """date_is_gt: test de comparacion correcta"""
        d1 = '2017-01-31 00:00:00'
        d2 = '2017-01-01 00:00:00'
        test_list = list()
        test_list.append(d1)
        test_list.append(d2)
        res = op.date_is_gt(test_list)
        assert_true(res)

    def test_date_is_gt_2(self):
        """date_is_gt: test de comparacion incorrecta por date"""
        d1 = '2017-01-01 00:00:00'
        d2 = '2017-01-31 00:00:00'
        test_list = list()
        test_list.append(d1)
        test_list.append(d2)
        res = op.date_is_gt(test_list)
        assert_false(res)

    def test_date_is_gt_3(self):
        """date_is_gt: test de comparacion incorrecta por time"""
        d1 = '2017-01-01 00:00:00'
        d2 = '2017-01-01 11:00:00'
        test_list = list()
        test_list.append(d1)
        test_list.append(d2)
        res = op.date_is_gt(test_list)
        assert_false(res)

    def test_date_is_gt_4(self):
        """date_is_gt: test de comparacion correcta con otro formato"""
        d1 = '01/01/2017 20:00:00'
        d2 = '01/01/2017 00:00:00'
        formatter = '%d/%m/%Y %H:%M:%S'
        test_list = list()
        test_list.append(d1)
        test_list.append(d2)
        test_list.append(formatter)
        res = op.date_is_gt(test_list)
        assert_true(res)

    @raises(ValueError)
    def test_date_is_gt_5(self):
        """date_is_gt: test de comparacion incorrecta por formato"""
        d1 = '2017-01-01 00:00:00'
        d2 = '2017-01-01 00:00:00'
        formatter = '%d/%m/%Y %H:%M:%S'
        test_list = list()
        test_list.append(d1)
        test_list.append(d2)
        test_list.append(formatter)
        op.date_is_gt(test_list)

    def test_date_is_gt_6(self):
        """date_is_gt: test de comparacion incorrecta con fechas iguales"""
        d1 = '2017-01-01 00:00:00'
        d2 = '2017-01-01 00:00:00'
        test_list = list()
        test_list.append(d1)
        test_list.append(d2)
        res = op.date_is_gt(test_list)
        assert_false(res)

    def test_date_is_gt_7(self):
        """date_is_gt: test de comparacion correcta con fechas inversas"""
        d1 = '2017-01-01 00:00:00'
        d2 = '2017-01-31 00:00:00'
        test_list = list()
        test_list.append(d1)
        test_list.append(d2)
        res = op.date_is_gt(test_list)
        assert_false(res)

    def test_date_is_lt_1(self):
        """date_is_lt: test de comparacion correcta"""
        d1 = '2017-01-01 00:00:00'
        d2 = '2017-01-31 00:00:00'
        test_list = list()
        test_list.append(d1)
        test_list.append(d2)
        res = op.date_is_lt(test_list)
        assert_true(res)

    def test_date_is_lt_2(self):
        """date_is_lt: test de comparacion incorrecta por date"""
        d1 = '2017-01-31 00:00:00'
        d2 = '2017-01-01 00:00:00'
        test_list = list()
        test_list.append(d1)
        test_list.append(d2)
        res = op.date_is_lt(test_list)
        assert_false(res)

    def test_date_is_lt_3(self):
        """date_is_lt: test de comparacion incorrecta por time"""
        d1 = '2017-01-01 11:00:00'
        d2 = '2017-01-01 00:00:00'
        test_list = list()
        test_list.append(d1)
        test_list.append(d2)
        res = op.date_is_lt(test_list)
        assert_false(res)

    def test_date_is_lt_4(self):
        """date_is_lt: test de comparacion correcta con otro formato"""
        d1 = '01/01/2017 00:00:00'
        d2 = '01/01/2017 11:00:00'
        formatter = '%d/%m/%Y %H:%M:%S'
        test_list = list()
        test_list.append(d1)
        test_list.append(d2)
        test_list.append(formatter)
        res = op.date_is_lt(test_list)
        assert_true(res)

    @raises(ValueError)
    def test_date_is_lt_5(self):
        """date_is_lt: test de comparacion incorrecta por formato"""
        d1 = '2017-01-01 00:00:00'
        d2 = '2017-01-01 00:00:00'
        formatter = '%d/%m/%Y %H:%M:%S'
        test_list = list()
        test_list.append(d1)
        test_list.append(d2)
        test_list.append(formatter)
        op.date_is_lt(test_list)

    def test_date_is_lt_6(self):
        """date_is_lt: test de comparacion incorrecta con fechas iguales"""
        d1 = '2017-01-01 00:00:00'
        d2 = '2017-01-01 00:00:00'
        test_list = list()
        test_list.append(d1)
        test_list.append(d2)
        res = op.date_is_lt(test_list)
        assert_false(res)

    def test_date_is_lt_7(self):
        """date_is_lt: test de comparacion correcta con fechas inversas"""
        d1 = '2017-01-31 00:00:00'
        d2 = '2017-01-01 00:00:00'
        test_list = list()
        test_list.append(d1)
        test_list.append(d2)
        res = op.date_is_lt(test_list)
        assert_false(res)

    def test_date_is_gte_1(self):
        """date_is_gte: test de comparacion correcta"""
        d1 = '2017-01-31 00:00:00'
        d2 = '2017-01-01 00:00:00'
        test_list = list()
        test_list.append(d1)
        test_list.append(d2)
        res = op.date_is_gte(test_list)
        assert_true(res)

    def test_date_is_gte_2(self):
        """date_is_gte: test de comparacion incorrecta por date"""
        d1 = '2017-01-01 00:00:00'
        d2 = '2017-01-31 00:00:00'
        test_list = list()
        test_list.append(d1)
        test_list.append(d2)
        res = op.date_is_gte(test_list)
        assert_false(res)

    def test_date_is_gte_3(self):
        """date_is_gte: test de comparacion incorrecta por time"""
        d1 = '2017-01-01 00:00:00'
        d2 = '2017-01-01 11:00:00'
        test_list = list()
        test_list.append(d1)
        test_list.append(d2)
        res = op.date_is_gte(test_list)
        assert_false(res)

    def test_date_is_gte_4(self):
        """date_is_gte: test de comparacion correcta con otro formato"""
        d1 = '01/01/2017 20:00:00'
        d2 = '01/01/2017 00:00:00'
        formatter = '%d/%m/%Y %H:%M:%S'
        test_list = list()
        test_list.append(d1)
        test_list.append(d2)
        test_list.append(formatter)
        res = op.date_is_gte(test_list)
        assert_true(res)

    @raises(ValueError)
    def test_date_is_gte_5(self):
        """date_is_gte: test de comparacion incorrecta por formato"""
        d1 = '2017-01-01 00:00:00'
        d2 = '2017-01-01 00:00:00'
        formatter = '%d/%m/%Y %H:%M:%S'
        test_list = list()
        test_list.append(d1)
        test_list.append(d2)
        test_list.append(formatter)
        op.date_is_gte(test_list)

    def test_date_is_gte_6(self):
        """date_is_gte: test de comparacion correcta con fechas iguales"""
        d1 = '2017-01-01 00:00:00'
        d2 = '2017-01-01 00:00:00'
        test_list = list()
        test_list.append(d1)
        test_list.append(d2)
        res = op.date_is_gte(test_list)
        assert_true(res)

    def test_date_is_gte_7(self):
        """date_is_gte: test de comparacion correcta con fechas inversas"""
        d1 = '2017-01-01 00:00:00'
        d2 = '2017-01-31 00:00:00'
        test_list = list()
        test_list.append(d1)
        test_list.append(d2)
        res = op.date_is_gte(test_list)
        assert_false(res)

    def test_date_is_lte_1(self):
        """date_is_lte: test de comparacion correcta"""
        d1 = '2017-01-01 00:00:00'
        d2 = '2017-01-31 00:00:00'
        test_list = list()
        test_list.append(d1)
        test_list.append(d2)
        res = op.date_is_lte(test_list)
        assert_true(res)

    def test_date_is_lte_2(self):
        """date_is_lte: test de comparacion incorrecta por date"""
        d1 = '2017-01-31 00:00:00'
        d2 = '2017-01-01 00:00:00'
        test_list = list()
        test_list.append(d1)
        test_list.append(d2)
        res = op.date_is_lte(test_list)
        assert_false(res)

    def test_date_is_lte_3(self):
        """date_is_lte: test de comparacion incorrecta por time"""
        d1 = '2017-01-01 11:00:00'
        d2 = '2017-01-01 00:00:00'
        test_list = list()
        test_list.append(d1)
        test_list.append(d2)
        res = op.date_is_lte(test_list)
        assert_false(res)

    def test_date_is_lte_4(self):
        """date_is_lte: test de comparacion correcta con otro formato"""
        d1 = '01/01/2017 00:00:00'
        d2 = '01/01/2017 11:00:00'
        formatter = '%d/%m/%Y %H:%M:%S'
        test_list = list()
        test_list.append(d1)
        test_list.append(d2)
        test_list.append(formatter)
        res = op.date_is_lte(test_list)
        assert_true(res)

    @raises(ValueError)
    def test_date_is_lte_5(self):
        """date_is_lte: test de comparacion incorrecta por formato"""
        d1 = '2017-01-01 00:00:00'
        d2 = '2017-01-01 00:00:00'
        formatter = '%d/%m/%Y %H:%M:%S'
        test_list = list()
        test_list.append(d1)
        test_list.append(d2)
        test_list.append(formatter)
        op.date_is_lte(test_list)

    def test_date_is_lte_6(self):
        """date_is_lte: test de comparacion incorrecta con fechas iguales"""
        d1 = '2017-01-01 00:00:00'
        d2 = '2017-01-01 00:00:00'
        test_list = list()
        test_list.append(d1)
        test_list.append(d2)
        res = op.date_is_lte(test_list)
        assert_true(res)

    def test_date_is_lte_7(self):
        """date_is_lte: test de comparacion correcta con fechas inversas"""
        d1 = '2017-01-31 00:00:00'
        d2 = '2017-01-01 00:00:00'
        test_list = list()
        test_list.append(d1)
        test_list.append(d2)
        res = op.date_is_lte(test_list)
        assert_false(res)

    def test_max_value(self):
        """max_value: test de verificacion de valor maximo"""
        test_list = list()
        test_list.append(1)
        test_list.append(2)
        test_list.append(3)
        test_list.append(4)
        res = op.max_value(test_list)
        assert_equal(4, res)

    def test_min_value(self):
        """max_value: test de verificacion de valor minimo"""
        test_list = list()
        test_list.append(1)
        test_list.append(2)
        test_list.append(3)
        test_list.append(4)
        res = op.min_value(test_list)
        assert_equal(1, res)
