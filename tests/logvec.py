import unittest
from hdlpy import logic, logvec

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

			with self.subTest(fun = '__ne__', a = a, b = b, expected = expected):
				actual = a.__ne__(b)
				self.assertEqual(not expected, actual)

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
				actual = int(value)
				self.assertEqual(expected, actual)

	def test_unsigned(self):
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
				actual = value.unsigned
				self.assertEqual(expected, actual)

	def test_signed(self):
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
				actual = value.signed
				self.assertEqual(expected, actual)

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

	def test_and(self):
		tests = (
			(logvec(1), logic(1), logvec(1)),
			(logic(1), logvec('01'), logvec('01')),
			(logvec('01ZX01ZX01ZX01ZX'), logvec('00001111ZZZZXXXX'), logvec('000001XX0XXX0XXX')),
			(logvec[7:0](42), logvec[7:0](42), logvec[7:0](42)),
			(logvec[15:8](42), logvec[7:0](42), logvec[15:8](42)),
		)

		for a, b, expected in tests:
			with self.subTest(a = a, b = b, expected = expected):
				actual = a & b
				self.assertEqual(expected, actual)

	def test_or(self):
		tests = (
			(logvec(0), logic(1), logvec(1)),
			(logic(0), logvec('01'), logvec('01')),
			(logvec('01ZX01ZX01ZX01ZX'), logvec('00001111ZZZZXXXX'), logvec('01XX1111X1XXX1XX')),
			(logvec[7:0](42), logvec[7:0](42), logvec[7:0](42)),
			(logvec[15:8](42), logvec[7:0](42), logvec[15:8](42)),
		)

		for a, b, expected in tests:
			with self.subTest(a = a, b = b, expected = expected):
				actual = a | b
				self.assertEqual(expected, actual)

	def test_xor(self):
		tests = (
			(logvec(0), logic(1), logvec(1)),
			(logic(0), logvec('01'), logvec('01')),
			(logvec('01ZX01ZX01ZX01ZX'), logvec('00001111ZZZZXXXX'), logvec('01XX10XXXXXXXXXX')),
			(logvec[7:0](42), logvec[7:0](42), logvec[7:0](0)),
			(logvec[15:8](42), logvec[7:0](42), logvec[15:8](0)),
		)

		for a, b, expected in tests:
			with self.subTest(a = a, b = b, expected = expected):
				actual = a ^ b
				self.assertEqual(expected, actual)

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
			with self.subTest(fun = 'shift_left', amount = amount, expected = expected):
				actual = vec.shift_left(amount)
				self.assertEqual(expected, actual)
			with self.subTest(fun = '__lshift__', amount = amount, expected = expected):
				actual = vec << amount
				self.assertEqual(expected, actual)

	def test_shift_left_invalid(self):
		with self.subTest(fun = 'shift_left'), self.assertRaises(ValueError):
			logvec('ZX101ZX').shift_left(-1)

		with self.subTest(fun = '__lshift__'), self.assertRaises(ValueError):
			logvec('ZX101ZX') << -1

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
			with self.subTest(amount = amount, expected = expected):
				actual = vec.rotate_left(amount)
				self.assertEqual(expected, actual)

	def test_rotate_left_invalid(self):
		with self.subTest(fun = 'rotate_left'), self.assertRaises(ValueError):
			logvec('ZX101ZX').rotate_left(-1)

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
			with self.subTest(fun = 'shift_right', amount = amount, expected = expected):
				actual = vec.shift_right(amount)
				self.assertEqual(expected, actual)
			with self.subTest(fun = '__rshift__', amount = amount, expected = expected):
				actual = vec >> amount
				self.assertEqual(expected, actual)

	def test_shift_right_invalid(self):
		with self.subTest(fun = 'shift_right'), self.assertRaises(ValueError):
			logvec('ZX101ZX').shift_right(-1)

		with self.subTest(fun = '__rshift__'), self.assertRaises(ValueError):
			logvec('ZX101ZX') >> -1

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
			with self.subTest(amount = amount, expected = expected):
				actual = vec.rotate_right(amount)
				self.assertEqual(expected, actual)

	def test_rotate_right_invalid(self):
		with self.subTest(fun = 'rotate_right'), self.assertRaises(ValueError):
			logvec('ZX101ZX').rotate_right(-1)

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
				self.assertEqual(expected, actual)
