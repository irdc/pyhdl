import unittest
import operator
from hdlpy import logic, logvec

def unsigned(val):
	return val.unsigned if isinstance(val, logvec) else val

def signed(val):
	return val.signed if isinstance(val, logvec) else val

class test_logvec(unittest.TestCase):
	def assertEqual(self, first, second, msg = None):
		if type(first) != type(second):
			raise self.failureException(f"{type(first)!r} != {type(second)!r}")
		return super().assertEqual(first, second, msg = msg)

	def test_type(self):
		tests = (
			(0, 0, 'logvec[0:0]'),
			(31, 8, 'logvec[31:8]'),
		)

		for start, end, expected in tests:
			with self.subTest(start = start, end = end, expected = expected):
				actual = logvec[start:end].__name__
				self.assertEqual(expected, actual)

	def test_type_invalid(self):
		tests = (
			None,
			'supercalifragilisticexpialidocious',
			42,
			slice(0, -1),
			slice(31),
			slice(31, 0, 1),
			slice(31, 0, -1),
		)

		for index in tests:
			with self.subTest(index = index):
				with self.assertRaises(ValueError):
					logvec[index]

	def test_new(self):
		tests = (
			(0, "<logvec[0:0] '0'>"),
			(1, "<logvec[0:0] '1'>"),
			(42, "<logvec[5:0] '101010'>"),
			('0', "<logvec[0:0] '0'>"),
			('1', "<logvec[0:0] '1'>"),
			(logic('Z'), "<logvec[0:0] 'Z'>"),
			('101010', "<logvec[5:0] '101010'>"),
			(logvec('101010'), "<logvec[5:0] '101010'>"),
		)

		for value, expected in tests:
			with self.subTest(value = value, expected = expected):
				actual = repr(logvec(value))
				self.assertEqual(expected, actual)

	def test_new_invalid(self):
		tests = (
			(None),
			(''),
			('supercalifragilisticexpialidocious'),
		)

		for value in tests:
			with self.subTest(value = value):
				with self.assertRaises(ValueError):
					logvec(value)

	def test_new_typed(self):
		tests = (
			(None, 7, 0, "<logvec[7:0] 'XXXXXXXX'>"),
			(0, 7, 0, "<logvec[7:0] '00000000'>"),
			(0, 15, 8, "<logvec[15:8] '00000000'>"),
			(42, 7, 0, "<logvec[7:0] '00101010'>"),
			(42, 15, 8, "<logvec[15:8] '00101010'>"),
			(-2, 7, 0, "<logvec[7:0] '11111110'>"),
			(-2, 15, 8, "<logvec[15:8] '11111110'>"),
			(-42, 7, 0, "<logvec[7:0] '11010110'>"),
			(-42, 15, 8, "<logvec[15:8] '11010110'>"),
			(logic('Z'), 15, 8, "<logvec[15:8] '0000000Z'>"),
			('101010', 15, 8, "<logvec[15:8] '00101010'>"),
			(logvec('00101010'), 15, 8, "<logvec[15:8] '00101010'>"),
		)

		for value, start, end, expected in tests:
			with self.subTest(value = value, start = start, end = end, expected = expected):
				actual = repr(logvec[start:end](value))
				self.assertEqual(expected, actual)

	def test_new_invalid_typed(self):
		tests = (
			((), 3, 0),
			((None, None, None, None), 3, 0),
			('00000', 3, 0),
			(logvec('00101010'), 6, 0),
		)

		for value, start, end in tests:
			with self.subTest(value = value, start = start, end = end):
				with self.assertRaises(ValueError):
					logvec[start:end](value)

	def test_len(self):
		tests = (
			(logvec(0), 1),
			(logvec(1), 1),
			(logvec(42), 6),
			(logvec('0'), 1),
			(logvec('1'), 1),
			(logvec('101010'), 6),
			(logvec[7:0](0), 8),
			(logvec[15:8](0), 8),
			(logvec[7:0](42), 8),
			(logvec[15:8](42), 8),
			(logvec[7:0](-2), 8),
			(logvec[15:8](-2), 8),
			(logvec[7:0](-42), 8),
			(logvec[15:8](-42), 8),
		)

		for value, expected in tests:
			with self.subTest(value = value, expected = expected):
				actual = len(value)
				self.assertEqual(expected, actual)

	def test_repr(self):
		tests = (
			(logvec(0), "<logvec[0:0] '0'>"),
			(logvec(1), "<logvec[0:0] '1'>"),
			(logvec(42), "<logvec[5:0] '101010'>"),
			(logvec('0'), "<logvec[0:0] '0'>"),
			(logvec('1'), "<logvec[0:0] '1'>"),
			(logvec('101010'), "<logvec[5:0] '101010'>"),
			(logvec[7:0](0), "<logvec[7:0] '00000000'>"),
			(logvec[15:8](0), "<logvec[15:8] '00000000'>"),
			(logvec[7:0](42), "<logvec[7:0] '00101010'>"),
			(logvec[15:8](42), "<logvec[15:8] '00101010'>"),
			(logvec[7:0](-2), "<logvec[7:0] '11111110'>"),
			(logvec[15:8](-2), "<logvec[15:8] '11111110'>"),
			(logvec[7:0](-42), "<logvec[7:0] '11010110'>"),
			(logvec[15:8](-42), "<logvec[15:8] '11010110'>"),
		)

		for value, expected in tests:
			with self.subTest(value = value, expected = expected):
				actual = repr(value)
				self.assertEqual(expected, actual)

	def test_str(self):
		tests = (
			(logvec(0), '0'),
			(logvec(1), '1'),
			(logvec(42), '101010'),
			(logvec('0'), '0'),
			(logvec('1'), '1'),
			(logvec('101010'), '101010'),
			(logvec[7:0](0), '00000000'),
			(logvec[15:8](0), '00000000'),
			(logvec[7:0](42), '00101010'),
			(logvec[15:8](42), '00101010'),
			(logvec[7:0](-2), '11111110'),
			(logvec[15:8](-2), '11111110'),
			(logvec[7:0](-42), '11010110'),
			(logvec[15:8](-42), '11010110'),
		)

		for value, expected in tests:
			with self.subTest(value = value, expected = expected):
				actual = str(value)
				self.assertEqual(expected, actual)

	def test_format(self):
		tests = (
			(logvec(0), '', '0'),
			(logvec(1), '', '1'),
			(logvec(0), 'b', '0'),
			(logvec(1), 'b', '1'),
			(logvec(0), 'd', '0'),
			(logvec(1), 'd', '1'),
			(logvec(0), 'n', '0'),
			(logvec(1), 'n', '1'),
			(logvec(0), 'o', '0'),
			(logvec(1), 'o', '1'),
			(logvec(0), 'x', '0'),
			(logvec(1), 'x', '1'),
			(logvec(0), 'X', '0'),
			(logvec(1), 'X', '1'),
			(logvec(42), '', '101010'),
			(logvec(42), 'b', '101010'),
			(logvec(42), 'o', '52'),
			(logvec(42), 'd', '42'),
			(logvec(42), 'n', '42'),
			(logvec(42), 'x', '2a'),
			(logvec(42), 'X', '2A'),
			(logvec('1X1010'), '', '1X1010'),
			(logvec('1X1010'), 'b', '1X1010'),
			(logvec('1X1010'), 'o', 'x2'),
			(logvec('1X1010'), 'x', 'xa'),
			(logvec('1X1010'), 'X', 'XA'),
			(logvec('001X1010'), 'x', 'xa'),
			(logvec('001X1010'), 'X', 'XA'),
			(logvec.empty, '', ''),
			(logvec.empty, 'b', ''),
			(logvec.empty, 'o', '0'),
			(logvec.empty, 'd', '0'),
			(logvec.empty, 'n', '0'),
			(logvec.empty, 'x', '0'),
			(logvec.empty, 'X', '0'),
		)

		for value, fmt, expected in tests:
			with self.subTest(value = value, fmt = fmt, expected = expected):
				actual = format(value, fmt)
				self.assertEqual(expected, actual)

	def test_format_invalid(self):
		tests = (
			(logvec(0), 'supercalifragilisticexpialidocious'),
			(logvec('X'), 'd'),
			(logvec('Z'), 'd'),
			(logvec('X'), 'n'),
			(logvec('Z'), 'n'),
			(logvec('1X1010'), 'n'),
			(logvec('1X1010'), 'n'),
			(logvec('001X1010'), 'n'),
			(logvec('001X1010'), 'n'),
		)

		for value, fmt in tests:
			with self.subTest(value = value, fmt = fmt):
				with self.assertRaises(ValueError):
					format(value, fmt)

	def test_eq(self):
		tests = (
			(logvec(0), logvec(0), True),
			(logvec(0), logvec(1), False),
			(logvec(42), 42, True),
			(logvec(42), 13, False),
			(logvec(42), logvec(42), True),
			(logvec(42), logvec(13), False),
			(logvec[15:8](42), logvec[7:0](42), True),
			(logvec[15:8](42), logvec[7:0](13), False),
			(logvec(42), '101-10', True),
			(logvec(42), '10_10-0', True),
			(logvec(13), '10_10-0', False),
		)

		for a, b, expected in tests:
			with self.subTest(fun = '__eq__', a = a, b = b, expected = expected):
				actual = a.__eq__(b)
				self.assertEqual(expected, actual)

			expected = NotImplemented if expected is NotImplemented else not expected
			with self.subTest(fun = '__ne__', a = a, b = b, expected = expected):
				actual = a.__ne__(b)
				self.assertEqual(expected, actual)

	def test_getitem(self):
		tests = (
			(8, logic(1)),
			(23, logic(0)),
			(-1, logic(0)),
			(-5, logic(1)),
			(slice(16), logvec[23:16]('00001111')),
			(slice(23, 9), logvec[23:9]('000011110011010')),
			(slice(15, None), logvec[15:8]('00110101')),
			(slice(23, 16), logvec[23:16]('00001111')),
			(slice(9, None), logvec[9:8]('01')),
			(slice(10, 9), logvec[10:9]('10')),
			(slice(-1, None), logvec[23:8]('0000111100110101')),
			(slice(-1, -2), logvec[23:22]('00')),
		)

		vec = logvec[23:8]('0000111100110101')
		for index, expected in tests:
			with self.subTest(index = index, expected = expected):
				actual = vec[index]
				self.assertEqual(expected, actual)

	def test_getitem_invalid(self):
		tests = (
			7,
			24,
			-17,
			slice(24, 8),
			slice(15, 0),
		)

		vec = logvec[23:8]('0000111100110101')
		for index in tests:
			with self.subTest(index = index):
				with self.assertRaises(IndexError):
					vec[index]

	def test_invert(self):
		tests = (
			(logvec(0), logvec(1)),
			(logvec(1), logvec(0)),
			(logvec(42), logvec('010101')),
			(logvec[7:0](42), logvec[7:0]('11010101')),
			(logvec[15:8](42), logvec[15:8]('11010101')),
			(logvec(-42), logvec('0101001')),
			(logvec('01ZX'), logvec('10XX')),
		)

		for value, expected in tests:
			with self.subTest(value = value, expected = expected):
				actual = ~value
				self.assertEqual(expected, actual)
			with self.subTest(value = unsigned(value), expected = unsigned(expected)):
				actual = ~unsigned(value)
				self.assertEqual(unsigned(expected), actual)
			with self.subTest(value = signed(value), expected = signed(expected)):
				actual = ~signed(value)
				self.assertEqual(signed(expected), actual)

	def _test_binary(self, oper, a, b, expected):
		with self.subTest(a = a, b = b, expected = expected, types = 'logvec,logvec'):
			actual = oper(a, b)
			self.assertEqual(expected, actual)

		with self.subTest(a = unsigned(a), b = unsigned(b), expected = unsigned(expected), types = 'unsigned,unsigned'):
			actual = oper(unsigned(a), unsigned(b))
			self.assertEqual(unsigned(expected), actual)
		if unsigned(a) is not a:
			with self.subTest(a = unsigned(a), b = b, expected = unsigned(expected), types = 'unsigned,logvec'):
				actual = oper(unsigned(a), b)
				self.assertEqual(unsigned(expected), actual)
		if unsigned(b) is not b:
			with self.subTest(a = a, b = unsigned(b), expected = unsigned(expected), types = 'logvec,unsigned'):
				actual = oper(a, unsigned(b))
				self.assertEqual(unsigned(expected), actual)

		with self.subTest(a = signed(a), b = signed(b), expected = signed(expected), types = 'signed,signed'):
			actual = oper(signed(a), signed(b))
			self.assertEqual(signed(expected), actual)
		if signed(a) is not a:
			with self.subTest(a = signed(a), b = b, expected = signed(expected), types = 'signed,logvec'):
				actual = oper(signed(a), b)
				self.assertEqual(signed(expected), actual)
		if signed(b) is not b:
			with self.subTest(a = a, b = signed(b), expected = signed(expected), types = 'logvec,signed'):
				actual = oper(a, signed(b))
				self.assertEqual(signed(expected), actual)

	def test_and(self):
		tests = (
			(logvec(1), logic(1), logvec(1)),
			(logic(1), logvec('01'), logvec('01')),
			(logvec('01ZX01ZX01ZX01ZX'), logvec('00001111ZZZZXXXX'), logvec('000001XX0XXX0XXX')),
			(logvec[7:0](42), logvec[7:0](42), logvec[7:0](42)),
			(logvec[15:8](42), logvec[7:0](42), logvec[15:8](42)),
		)

		for a, b, expected in tests:
			self._test_binary(operator.and_, a, b, expected)

	def test_and_invalid(self):
		with self.assertRaises(TypeError):
			logvec('01').unsigned & logvec('01').signed

	def test_or(self):
		tests = (
			(logvec(0), logic(1), logvec(1)),
			(logic(0), logvec('01'), logvec('01')),
			(logvec('01ZX01ZX01ZX01ZX'), logvec('00001111ZZZZXXXX'), logvec('01XX1111X1XXX1XX')),
			(logvec[7:0](42), logvec[7:0](42), logvec[7:0](42)),
			(logvec[15:8](42), logvec[7:0](42), logvec[15:8](42)),
		)

		for a, b, expected in tests:
			self._test_binary(operator.or_, a, b, expected)

	def test_or_invalid(self):
		with self.assertRaises(TypeError):
			logvec('01').unsigned | logvec('01').signed

	def test_xor(self):
		tests = (
			(logvec(0), logic(1), logvec(1)),
			(logic(0), logvec('01'), logvec('01')),
			(logvec('01ZX01ZX01ZX01ZX'), logvec('00001111ZZZZXXXX'), logvec('01XX10XXXXXXXXXX')),
			(logvec[7:0](42), logvec[7:0](42), logvec[7:0](0)),
			(logvec[15:8](42), logvec[7:0](42), logvec[15:8](0)),
		)

		for a, b, expected in tests:
			self._test_binary(operator.xor, a, b, expected)

	def test_xor_invalid(self):
		with self.assertRaises(TypeError):
			logvec('01').unsigned ^ logvec('01').signed

	def _test_shift(self, fun, vec, amount, expected):
		with self.subTest(fun = fun.__name__, amount = amount, expected = expected):
			actual = fun(vec, amount)
			self.assertEqual(expected, actual)
		with self.subTest(fun = 'unsigned.' + fun.__name__, amount = amount, expected = unsigned(expected)):
			actual = fun(unsigned(vec), amount)
			self.assertEqual(unsigned(expected), actual)
		with self.subTest(fun = 'signed.' + fun.__name__, amount = amount, expected = signed(expected)):
			actual = fun(signed(vec), amount)
			self.assertEqual(signed(expected), actual)

	def _test_shift_invalid(self, fun, vec, amount):
		with self.subTest(fun = fun.__name__), self.assertRaises(ValueError):
			fun(vec, amount)
		with self.subTest(fun = 'unsigned.' + fun.__name__), self.assertRaises(ValueError):
			fun(vec.unsigned, amount)
		with self.subTest(fun = 'signed.' + fun.__name__), self.assertRaises(ValueError):
			fun(vec.signed, amount)

	def test_shift_left(self):
		tests = (
			(0, logvec('ZX101ZX')),
			(1, logvec('X101ZX0')),
			(2, logvec('101ZX00')),
			(6, logvec('X000000')),
			(7, logvec('0000000')),
			(8, logvec('0000000')),
		)

		vec = logvec('ZX101ZX')
		for amount, expected in tests:
			self._test_shift(type(vec).shift_left, vec, amount, expected)
			self._test_shift(type(vec).__lshift__, vec, amount, expected)

	def test_shift_left_invalid(self):
		vec = logvec('ZX101ZX')
		self._test_shift_invalid(type(vec).shift_left, vec, -1)
		self._test_shift_invalid(type(vec).__lshift__, vec, -1)

	def test_rotate_left(self):
		tests = (
			(0, logvec('ZX101ZX')),
			(1, logvec('X101ZXZ')),
			(2, logvec('101ZXZX')),
			(6, logvec('XZX101Z')),
			(7, logvec('ZX101ZX')),
			(8, logvec('X101ZXZ')),
		)

		vec = logvec('ZX101ZX')
		for amount, expected in tests:
			self._test_shift(type(vec).rotate_left, vec, amount, expected)

	def test_rotate_left_invalid(self):
		vec = logvec('ZX101ZX')
		self._test_shift_invalid(type(vec).rotate_left, vec, -1)

	def test_shift_right(self):
		tests = (
			(0, logvec('ZX101ZX')),
			(1, logvec('0ZX101Z')),
			(2, logvec('00ZX101')),
			(6, logvec('000000Z')),
			(7, logvec('0000000')),
			(8, logvec('0000000')),
		)

		vec = logvec('ZX101ZX')
		for amount, expected in tests:
			self._test_shift(type(vec).shift_right, vec, amount, expected)
			self._test_shift(type(vec).__rshift__, vec, amount, expected)

	def test_shift_right_invalid(self):
		vec = logvec('ZX101ZX')
		self._test_shift_invalid(type(vec).shift_right, vec, -1)
		self._test_shift_invalid(type(vec).__rshift__, vec, -1)

	def test_rotate_right(self):
		tests = (
			(0, logvec('ZX101ZX')),
			(1, logvec('XZX101Z')),
			(2, logvec('ZXZX101')),
			(6, logvec('X101ZXZ')),
			(7, logvec('ZX101ZX')),
			(8, logvec('XZX101Z')),
		)

		vec = logvec('ZX101ZX')
		for amount, expected in tests:
			self._test_shift(type(vec).rotate_right, vec, amount, expected)

	def test_rotate_right_invalid(self):
		vec = logvec('ZX101ZX')
		self._test_shift_invalid(type(vec).rotate_right, vec, -1)

	def test_add(self):
		tests = (
			(logvec(0), logvec('01'), logvec('001')),
			(logvec('00'), logic(1), logvec('001')),
			(logic(0), logvec('01'), logvec('001')),
			(logvec[15:8](42), logvec[7:0](13), logvec('0010101000001101')),
			(logvec[7:0](42), logvec[15:8](13), logvec('0010101000001101'))
		)

		for a, b, expected in tests:
			with self.subTest(a = a, b = b, expected = expected):
				actual = a + b

class test_logvec_unsigned(unittest.TestCase):
	def test_eq(self):
		tests = (
			(logvec(0).unsigned, logvec(0).unsigned, True),
			(logvec(0).unsigned, logvec(1).unsigned, False),
			(logvec(42).unsigned, 42, True),
			(logvec(42).unsigned, 13, False),
			(logvec(42).unsigned, logvec(42).unsigned, True),
			(logvec(42).unsigned, logvec(13).unsigned, False),
			(logvec[15:8](42).unsigned, logvec[7:0](42).unsigned, True),
			(logvec[15:8](42).unsigned, logvec[7:0](13).unsigned, False),
			(logvec[15:8](42).unsigned, logvec[7:0](42).signed, NotImplemented),
			(logvec[15:8](42).unsigned, logvec[7:0](13).signed, NotImplemented),
			(logvec(42).unsigned, '101-10', True),
			(logvec(42).unsigned, '10_10-0', True),
			(logvec(13).unsigned, '10_10-0', False),
		)

		for a, b, expected in tests:
			with self.subTest(fun = '__eq__', a = a, b = b, expected = expected):
				actual = a.__eq__(b)
				self.assertEqual(expected, actual)

			expected = NotImplemented if expected is NotImplemented else not expected
			with self.subTest(fun = '__ne__', a = a, b = b, expected = expected):
				actual = a.__ne__(b)
				self.assertEqual(expected, actual)

	def test_int(self):
		tests = (
			(logvec(0), 0),
			(logvec(1), 1),
			(logvec(42), 42),
			(logvec('0'), 0),
			(logvec('1'), 1),
			(logvec('101010'), 42),
			(logvec[7:0](0), 0),
			(logvec[15:8](0), 0),
			(logvec[7:0](42), 42),
			(logvec[15:8](42), 42),
			(logvec[7:0](-2), 254),
			(logvec[15:8](-2), 254),
			(logvec[7:0](-42), 214),
			(logvec[15:8](-42), 214),
		)

		for value, expected in tests:
			with self.subTest(value = value, expected = expected):
				actual = int(value.unsigned)
				self.assertEqual(expected, actual)

	def test_format(self):
		tests = (
			(logvec(0), '0'),
			(logvec(1), '1'),
			(logvec(42), '42'),
			(logvec('0'), '0'),
			(logvec('1'), '1'),
			(logvec('101010'), '42'),
			(logvec[7:0](0), '0'),
			(logvec[15:8](0), '0'),
			(logvec[7:0](42), '42'),
			(logvec[15:8](42), '42'),
			(logvec[7:0](-2), '254'),
			(logvec[15:8](-2), '254'),
			(logvec[7:0](-42), '214'),
			(logvec[15:8](-42), '214'),
		)

		for value, expected in tests:
			with self.subTest(value = value, fmt = 'd', expected = expected):
				actual = format(value.unsigned, 'd')
				self.assertEqual(expected, actual)

			with self.subTest(value = value, fmt = 'n', expected = expected):
				actual = format(value.unsigned, 'n')
				self.assertEqual(expected, actual)


class test_logvec_signed(unittest.TestCase):
	def test_eq(self):
		tests = (
			(logvec(0).signed, logvec(0).signed, True),
			(logvec(0).signed, logvec(1).signed, False),
			(logvec(42).signed, 42, True),
			(logvec(42).signed, 13, False),
			(logvec(42).signed, logvec(42).signed, True),
			(logvec(42).signed, logvec(13).signed, False),
			(logvec[15:8](42).signed, logvec[7:0](42).signed, True),
			(logvec[15:8](42).signed, logvec[7:0](13).signed, False),
			(logvec[15:8](42).signed, logvec[7:0](42).unsigned, NotImplemented),
			(logvec[15:8](42).signed, logvec[7:0](13).unsigned, NotImplemented),
			(logvec(42).signed, '101-10', True),
			(logvec(42).signed, '10_10-0', True),
			(logvec(13).signed, '10_10-0', False),
		)

		for a, b, expected in tests:
			with self.subTest(fun = '__eq__', a = a, b = b, expected = expected):
				actual = a.__eq__(b)
				self.assertEqual(expected, actual)

			expected = NotImplemented if expected is NotImplemented else not expected
			with self.subTest(fun = '__ne__', a = a, b = b, expected = expected):
				actual = a.__ne__(b)
				self.assertEqual(expected, actual)

	def test_int(self):
		tests = (
			(logvec(0), 0),
			(logvec(1), -1),
			(logvec(42), -22),
			(logvec('0'), 0),
			(logvec('1'), -1),
			(logvec('101010'), -22),
			(logvec('0101010'), 42),
			(logvec[7:0](0), 0),
			(logvec[15:8](0), 0),
			(logvec[7:0](42), 42),
			(logvec[15:8](42), 42),
			(logvec[7:0](-2), -2),
			(logvec[15:8](-2), -2),
			(logvec[7:0](-42), -42),
			(logvec[15:8](-42), -42),
		)

		for value, expected in tests:
			with self.subTest(value = value, expected = expected):
				actual = int(value.signed)
				self.assertEqual(expected, actual)

	def test_format(self):
		tests = (
			(logvec(0), '0'),
			(logvec(1), '-1'),
			(logvec(42), '-22'),
			(logvec('0'), '0'),
			(logvec('1'), '-1'),
			(logvec('101010'), '-22'),
			(logvec('0101010'), '42'),
			(logvec[7:0](0), '0'),
			(logvec[15:8](0), '0'),
			(logvec[7:0](42), '42'),
			(logvec[15:8](42), '42'),
			(logvec[7:0](-2), '-2'),
			(logvec[15:8](-2), '-2'),
			(logvec[7:0](-42), '-42'),
			(logvec[15:8](-42), '-42'),
		)

		for value, expected in tests:
			with self.subTest(value = value, fmt = 'd', expected = expected):
				actual = format(value.signed, 'd')
				self.assertEqual(expected, actual)

			with self.subTest(value = value, fmt = 'n', expected = expected):
				actual = format(value.signed, 'n')
				self.assertEqual(expected, actual)
