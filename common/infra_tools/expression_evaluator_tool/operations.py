import operator
from datetime import datetime, timedelta


class Operations:
    # Cada operador es una tupla formada por una funcion, un numero de argumentos y una precedencia de operadores
    # La precedencia maxima es 1 y esta reservada para los parentesis
    OPERATORS = {
        '=': (operator.eq, 2, 3), '!=': (operator.ne, 2, 3), '<': (operator.lt, 2, 3),
        '>': (operator.gt, 2, 3), '>=': (operator.ge, 2, 3), '<=': (operator.le, 2, 3),
        'and': (operator.and_, 2, 2), 'or': (operator.or_, 2, 2), 'not': (operator.not_, 1, 2),
        'contains': (operator.contains, 2, 3), 'icontains': (lambda x, y: y.upper() in x.upper(), 2, 3),
        '+': (operator.add, 2, 2), '-': (operator.sub, 2, 2),
        '*': (operator.mul, 2, 3), '/': (operator.truediv, 2, 3)
    }


# Definicion de funciones
# Todas las funciones tienen como argumento una lista de valores
# Es responsabilidad de la funcion saber cuantos y de que tipo son sus argumentos


# Mensajes de las excepciones
ERROR_INVALID_ARGS = 'Invalid arguments'
ERROR_NUM_ARGS = 'Wrong arguments number'


def length(arg_list, additional_data):
    """
    Devuelve la longitud de una cadena
    :param arg_list:
        arg_list[0] -> cadena. Si es un numero elevara una excepcion TypeError
        arg_list[0] -> list.
    :return: longitud de la cadena
    """
    obj = arg_list[0]

    if type(obj) == list:
        return len(obj)
    else:
        return len(arg_list[0])


def _check_args_and_formatter(arg_list):
    """
    Metodo privado
    Verifica los argumentos y establece el formato a utilizar de las funciones que manejan fechas
    :param arg_list:
    :return:
    """

    num_args = len(arg_list)
    if num_args < 2 or num_args > 3:
        raise ValueError(ERROR_NUM_ARGS)
    elif num_args == 2:
        formatter = '%Y-%m-%d %H:%M:%S'
    else:
        formatter = arg_list[2]

    return formatter


def diff_dates_in_days(arg_list, additional_data):
    """
    Devuelve el numero de dias completos entre dos fechas con un formato especifico. Tiene en cuenta las horas
    :param arg_list:
        arg_list[0] -> primera fecha
        arg_list[1] -> segunda fecha
        arg_list[2] -> formato de las fechas. Si no se especifica el formato es %Y-%m-%d %H:%M:%S
            %Y -> año con cuatro cifras
            %m -> mes con dos cifras (01-12)
            %d -> dia con dos cifras (01-31)
            %H -> hora con dos cifras
            %M -> minutos con dos cifras
            %S -> segundos con dos cifras
            %f -> microsegundos con seis cifras
    :return: numero de dias completos de diferencia
    """

    formatter = _check_args_and_formatter(arg_list)

    try:
        d1 = datetime.strptime(arg_list[0], formatter)
        d2 = datetime.strptime(arg_list[1], formatter)
        return (d2 - d1).days
    except Exception as e:
        raise ValueError('{}: {}'.format(ERROR_INVALID_ARGS, e))


def have_passed_time(arg_list, additional_data):
    """
    Verifica si han pasado un determinado numero de unidad de tiempo (semanas, dias, horas, minutos y segundos)
    a partir de la fecha pasada como argumento
    :param arg_list:
            arg_list[0] -> fecha
            arg_list[1] -> numero de años, meses, dias, horas, minutos, segundos o microsegundos
            arg_list[2] -> unidad de tiempo a comparar: weeks, days, hours, minutes, seconds
            arg_list[3] -> formato de las fechas. Si no se especifica el formato es %Y-%m-%d %H:%M:%S
                %Y -> año con cuatro cifras
                %m -> mes con dos cifras (01-12)
                %d -> dia con dos cifras (01-31)
                %H -> hora con dos cifras
                %M -> minutos con dos cifras
                %S -> segundos con dos cifras
                %f -> microsegundos con seis cifras
    :return: booleano
    """

    num_args = len(arg_list)
    if num_args < 3 or num_args > 4:
        raise ValueError(ERROR_NUM_ARGS)
    elif num_args == 3:
        formatter = '%Y-%m-%d %H:%M:%S'
    else:
        formatter = arg_list[3]

    try:
        # Eliminar los microsegundos si existieran. Se busca el ultimo punto
        date = arg_list[0]
        pos_microseconds = date.rfind('.')
        if pos_microseconds != -1:
            date = date[0:pos_microseconds]

        d = datetime.strptime(date, formatter)
        unit_time = arg_list[2]
        delta_time = int(arg_list[1])

        delta_choices = {
            'seconds': lambda x: timedelta(seconds=x),
            'minutes': lambda x: timedelta(minutes=x),
            'hours': lambda x: timedelta(hours=x),
            'days': lambda x: timedelta(days=x),
            'weeks': lambda x: timedelta(weeks=x)
        }

        delta_function = delta_choices.get(unit_time, 'days')

        now = datetime.today()
        return d + delta_function(delta_time) < now
    except Exception as e:
        raise ValueError('{}: {}'.format(ERROR_INVALID_ARGS, e))


def date_is_eq(arg_list, additional_data):
    """
    Verifica si dos fechas son iguales o no
    :param arg_list:
            arg_list[0] -> fecha
            arg_list[1] -> fecha
            arg_list[2] -> formato de las fechas. Si no se especifica el formato es %Y-%m-%d %H:%M:%S
                %Y -> año con cuatro cifras
                %m -> mes con dos cifras (01-12)
                %d -> dia con dos cifras (01-31)
                %H -> hora con dos cifras
                %M -> minutos con dos cifras
                %S -> segundos con dos cifras
                %f -> microsegundos con seis cifras
    :return: booleano
    """

    formatter = _check_args_and_formatter(arg_list)

    try:
        d1 = datetime.strptime(arg_list[0], formatter)
        d2 = datetime.strptime(arg_list[1], formatter)
        return d1 == d2
    except Exception as e:
        raise ValueError('{}: {}'.format(ERROR_INVALID_ARGS, e))


def date_is_neq(arg_list, additional_data):
    """
    Verifica si dos fechas son distintas o no
    :param arg_list:
            arg_list[0] -> fecha
            arg_list[1] -> fecha
            arg_list[2] -> formato de las fechas. Si no se especifica el formato es %Y-%m-%d %H:%M:%S
                %Y -> año con cuatro cifras
                %m -> mes con dos cifras (01-12)
                %d -> dia con dos cifras (01-31)
                %H -> hora con dos cifras
                %M -> minutos con dos cifras
                %S -> segundos con dos cifras
                %f -> microsegundos con seis cifras
    :return: booleano
    """

    return not date_is_eq(arg_list)


def date_is_gt(arg_list, additional_data):
    """
    Verifica si una fecha es posterior a la otra
    :param arg_list:
            arg_list[0] -> fecha
            arg_list[1] -> fecha
            arg_list[2] -> formato de las fechas. Si no se especifica el formato es %Y-%m-%d %H:%M:%S
                %Y -> año con cuatro cifras
                %m -> mes con dos cifras (01-12)
                %d -> dia con dos cifras (01-31)
                %H -> hora con dos cifras
                %M -> minutos con dos cifras
                %S -> segundos con dos cifras
                %f -> microsegundos con seis cifras
    :return: booleano
    """

    formatter = _check_args_and_formatter(arg_list)

    try:
        d1 = datetime.strptime(arg_list[0], formatter)
        d2 = datetime.strptime(arg_list[1], formatter)
        return d1 > d2
    except Exception as e:
        raise ValueError('{}: {}'.format(ERROR_INVALID_ARGS, e))


def date_is_lt(arg_list, additional_data):
    """
    Verifica si una fecha es anterior a la otra
    :param arg_list:
            arg_list[0] -> fecha
            arg_list[1] -> fecha
            arg_list[2] -> formato de las fechas. Si no se especifica el formato es %Y-%m-%d %H:%M:%S
                %Y -> año con cuatro cifras
                %m -> mes con dos cifras (01-12)
                %d -> dia con dos cifras (01-31)
                %H -> hora con dos cifras
                %M -> minutos con dos cifras
                %S -> segundos con dos cifras
                %f -> microsegundos con seis cifras
    :return: booleano
    """

    formatter = _check_args_and_formatter(arg_list)

    try:
        d1 = datetime.strptime(arg_list[0], formatter)
        d2 = datetime.strptime(arg_list[1], formatter)
        return d1 < d2
    except Exception as e:
        raise ValueError('{}: {}'.format(ERROR_INVALID_ARGS, e))


def date_is_gte(arg_list, additional_data):
    """
    Verifica si una fecha es posterior o igual a la otra
    :param arg_list:
            arg_list[0] -> fecha
            arg_list[1] -> fecha
            arg_list[2] -> formato de las fechas. Si no se especifica el formato es %Y-%m-%d %H:%M:%S
                %Y -> año con cuatro cifras
                %m -> mes con dos cifras (01-12)
                %d -> dia con dos cifras (01-31)
                %H -> hora con dos cifras
                %M -> minutos con dos cifras
                %S -> segundos con dos cifras
                %f -> microsegundos con seis cifras
    :return: booleano
    """

    formatter = _check_args_and_formatter(arg_list)

    try:
        d1 = datetime.strptime(arg_list[0], formatter)
        d2 = datetime.strptime(arg_list[1], formatter)
        return d1 >= d2
    except Exception as e:
        raise ValueError('{}: {}'.format(ERROR_INVALID_ARGS, e))


def date_is_lte(arg_list, additional_data):
    """
    Verifica si una fecha es anterior o igual a la otra
    :param arg_list:
            arg_list[0] -> fecha
            arg_list[1] -> fecha
            arg_list[2] -> formato de las fechas. Si no se especifica el formato es %Y-%m-%d %H:%M:%S
                %Y -> año con cuatro cifras
                %m -> mes con dos cifras (01-12)
                %d -> dia con dos cifras (01-31)
                %H -> hora con dos cifras
                %M -> minutos con dos cifras
                %S -> segundos con dos cifras
                %f -> microsegundos con seis cifras
    :return: booleano
    """

    formatter = _check_args_and_formatter(arg_list)

    try:
        d1 = datetime.strptime(arg_list[0], formatter)
        d2 = datetime.strptime(arg_list[1], formatter)
        return d1 <= d2
    except Exception as e:
        raise ValueError('{}: {}'.format(ERROR_INVALID_ARGS, e))


def max_value(arg_list, additional_data):
    """
    Devuelve el maximo de los valores pasados
    :param arg_list: indefinido
    :return: valor maximo
    """

    return max(arg_list)


def min_value(arg_list, additional_data):
    """
    Devuelve el minimo de los valores pasados
    :param arg_list: indefinido
    :return: valor minimo
    """

    return min(arg_list)


def is_empty(arg_list, additional_data):
    """
    Return True if empty
    """

    return len(arg_list[0]) == 0
