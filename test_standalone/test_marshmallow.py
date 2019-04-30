from marshmallow import Schema, fields
from flask import jsonify




class TestData:
    def __init__(self, a, b, c):
        self.a = a
        self.b = b
        self.c = c

    def __repr__(self):
        return '{} {} {}'.format(self.a, self.b, self.c)


class TestSchema(Schema):
    a = fields.Int()
    b = fields.Int()
    c = fields.Int()


t1 = TestData(1, 2, 3)
t2 = TestData(4, 5, 6)
t3 = TestData(7, 8, 9)

tschema = TestSchema()

r1 = tschema.dump(t1)
r2 = tschema.dump(t2)
r3 = tschema.dump(t3)

jr1 = jsonify({'testdata': r1})

pass
