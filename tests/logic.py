#
# Part of hdlpy.
# Copyright (c) 2021, Willemijn Coene
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
#

import unittest, operator
from hdlpy import logic

class test_logic(unittest.TestCase):
	def test_default(self):
		expected = logic.unknown
		actual = logic()
		self.assertIs(expected, actual)

	def test_new(self):
		tests = (
			(logic.zero, logic.zero),
			(logic.one, logic.one),
			(logic.hi_z, logic.hi_z),
			(logic.unknown, logic.unknown),
			(False, logic.zero),
			(True, logic.one),
			(0, logic.zero),
			(1, logic.one),
			('0', logic.zero),
			('1', logic.one),
			('Z', logic.hi_z),
			('X', logic.unknown),
		)

		for value, expected in tests:
			with self.subTest(value = value, expected = expected):
				actual = logic(value)
				self.assertIs(expected, actual)

	def test_new_invalid(self):
		tests = (
			None,
			2,
			'',
			'supercalifragilisticexpialidocious',
			(),
			object(),
		)

		for value in tests:
			with self.subTest(value = value):
				with self.assertRaises(ValueError):
					logic(value)

	def test_repr(self):
		tests = (
			(logic.zero, "<logic '0'>"),
			(logic.one, "<logic '1'>"),
			(logic.hi_z, "<logic 'Z'>"),
			(logic.unknown, "<logic 'X'>"),
		)

		for value, expected in tests:
			with self.subTest(value = value, expected = expected):
				actual = repr(value)
				self.assertEqual(expected, actual)

	def test_str(self):
		tests = (
			(logic.zero, '0'),
			(logic.one, '1'),
			(logic.hi_z, 'Z'),
			(logic.unknown, 'X')
		)

		for value, expected in tests:
			with self.subTest(value = value, expected = expected):
				actual = str(value)
				self.assertEqual(expected, actual)

	def test_format(self):
		tests = (
			(logic.zero, '', '0'),
			(logic.one, '', '1'),
			(logic.hi_z, '', 'Z'),
			(logic.unknown, '', 'X'),
		)

		for value, fmt, expected in tests:
			with self.subTest(value = value, fmt = fmt, expected = expected):
				actual = format(value, fmt)
				self.assertEqual(expected, actual)

	def test_format_invalid(self):
		tests = (
			'd',
			'supercalifragilisticexpialidocious'
		)

		for fmt in tests:
			with self.subTest(fmt = fmt):
				with self.assertRaises(ValueError):
					format(logic.zero, fmt)

	def test_int(self):
		self.assertEqual(0, int(logic(0)))
		self.assertEqual(1, int(logic(1)))
		with self.assertRaises(ValueError):
			int(logic('Z'))
		with self.assertRaises(ValueError):
			int(logic('X'))

	def test_eq(self):
		tests = (
			(logic.zero, logic.zero, True),
			(logic.zero, logic.one, False),
			(logic.zero, logic.hi_z, False),
			(logic.zero, logic.unknown, False),
			(logic.zero, '-', True),

			(logic.one, logic.zero, False),
			(logic.one, logic.one, True),
			(logic.one, logic.hi_z, False),
			(logic.one, logic.unknown, False),
			(logic.one, '-', True),

			(logic.hi_z, logic.zero, False),
			(logic.hi_z, logic.one, False),
			(logic.hi_z, logic.hi_z, True),
			(logic.hi_z, logic.unknown, False),
			(logic.hi_z, '-', True),

			(logic.unknown, logic.zero, False),
			(logic.unknown, logic.one, False),
			(logic.unknown, logic.hi_z, False),
			(logic.unknown, logic.unknown, True),
			(logic.unknown, '-', True),
		)

		for a, b, expected in tests:
			with self.subTest(a = a, b = b, expected = expected):
				actual = a.__eq__(b)
				self.assertEqual(expected, actual)

	def test_eq_notimplemented(self):
		tests = (
			None,
			2,
			'',
			'supercalifragilisticexpialidocious',
			(),
			object(),
		)

		for other in tests:
			with self.subTest(other = other):
				actual = logic.zero.__eq__(other)
				self.assertIs(NotImplemented, actual)

	def test_ne(self):
		tests = (
			(logic.zero, logic.zero, False),
			(logic.zero, logic.one, True),
			(logic.zero, logic.hi_z, True),
			(logic.zero, logic.unknown, True),
			(logic.zero, '-', False),

			(logic.one, logic.zero, True),
			(logic.one, logic.one, False),
			(logic.one, logic.hi_z, True),
			(logic.one, logic.unknown, True),
			(logic.one, '-', False),

			(logic.hi_z, logic.zero, True),
			(logic.hi_z, logic.one, True),
			(logic.hi_z, logic.hi_z, False),
			(logic.hi_z, logic.unknown, True),
			(logic.hi_z, '-', False),

			(logic.unknown, logic.zero, True),
			(logic.unknown, logic.one, True),
			(logic.unknown, logic.hi_z, True),
			(logic.unknown, logic.unknown, False),
			(logic.unknown, '-', False),
		)

		for a, b, expected in tests:
			with self.subTest(a = a, b = b, expected = expected):
				actual = a.__ne__(b)
				self.assertEqual(expected, actual)

	def test_ne_notimplemented(self):
		tests = (
			None,
			2,
			'',
			'supercalifragilisticexpialidocious',
			(),
			object(),
		)

		for other in tests:
			with self.subTest(other = other):
				actual = logic.zero.__ne__(other)
				self.assertIs(NotImplemented, actual)

	def test_cmp(self):
		tests = (
			(logic.zero, logic.zero, False, False),
			(logic.zero, logic.one, True, False),
			(logic.zero, logic.hi_z, True, False),
			(logic.zero, logic.unknown, True, False),

			(logic.one, logic.zero, False, True),
			(logic.one, logic.one, False, False),
			(logic.one, logic.hi_z, True, False),
			(logic.one, logic.unknown, True, False),

			(logic.hi_z, logic.zero, False, True),
			(logic.hi_z, logic.one, False, True),
			(logic.hi_z, logic.hi_z, False, False),
			(logic.hi_z, logic.unknown, False, True),

			(logic.unknown, logic.zero, False, True),
			(logic.unknown, logic.one, False, True),
			(logic.unknown, logic.hi_z, True, False),
			(logic.unknown, logic.unknown, False, False),
		)

		for a, b, lt, gt in tests:
			with self.subTest(fun = '__lt__', a = a, b = b, expected = lt):
				actual = a.__lt__(b)
				self.assertEqual(lt, actual)
			with self.subTest(fun = '__ge__', a = a, b = b, expected = not lt):
				actual = a.__ge__(b)
				self.assertEqual(not lt, actual)
			with self.subTest(fun = '__gt__', a = a, b = b, expected = gt):
				actual = a.__gt__(b)
				self.assertEqual(gt, actual)
			with self.subTest(fun = '__le__', a = a, b = b, expected = not gt):
				actual = a.__le__(b)
				self.assertEqual(not gt, actual)

	def test_cmp_notimplemented(self):
		tests = (
			None,
			2,
			'',
			'supercalifragilisticexpialidocious',
			(),
			object(),
		)

		for other in tests:
			with self.subTest(fun = '__lt__', other = other):
				actual = logic.zero.__lt__(other)
				self.assertIs(NotImplemented, actual)
			with self.subTest(fun = '__ge__', other = other):
				actual = logic.zero.__ge__(other)
				self.assertIs(NotImplemented, actual)
			with self.subTest(fun = '__gt__', other = other):
				actual = logic.zero.__gt__(other)
				self.assertIs(NotImplemented, actual)
			with self.subTest(fun = '__le__', other = other):
				actual = logic.zero.__le__(other)
				self.assertIs(NotImplemented, actual)

	def test_bool(self):
		tests = (
			(logic.zero, False),
			(logic.one, True),
			(logic.hi_z, False),
			(logic.unknown, False)
		)

		for value, expected in tests:
			with self.subTest(value = value, expected = expected):
				actual = value.__bool__()
				self.assertEqual(expected, actual)

	def test_invert(self):
		tests = (
			(logic.zero, logic.one),
			(logic.one, logic.zero),
			(logic.hi_z, logic.unknown),
			(logic.unknown, logic.unknown),
		)

		for value, expected in tests:
			with self.subTest(value = value, expected = expected):
				actual = value.__invert__()
				self.assertIs(expected, actual)

	def test_and(self):
		tests = (
			(logic.zero, logic.zero, logic.zero),
			(logic.zero, logic.one, logic.zero),
			(logic.zero, logic.hi_z, logic.zero),
			(logic.zero, logic.unknown, logic.zero),

			(logic.one, logic.zero, logic.zero),
			(logic.one, logic.one, logic.one),
			(logic.one, logic.hi_z, logic.unknown),
			(logic.one, logic.unknown, logic.unknown),

			(logic.hi_z, logic.zero, logic.zero),
			(logic.hi_z, logic.one, logic.unknown),
			(logic.hi_z, logic.hi_z, logic.unknown),
			(logic.hi_z, logic.unknown, logic.unknown),

			(logic.unknown, logic.zero, logic.zero),
			(logic.unknown, logic.one, logic.unknown),
			(logic.unknown, logic.hi_z, logic.unknown),
			(logic.unknown, logic.unknown, logic.unknown),
		)

		for a, b, expected in tests:
			with self.subTest(a = a, b = b, expected = expected):
				actual = a.__and__(b)
				self.assertIs(expected, actual)

	def test_and_notimplemented(self):
		tests = (
			None,
			2,
			'',
			'supercalifragilisticexpialidocious',
			(),
			object(),
		)

		for other in tests:
			with self.subTest(other = other):
				actual = logic.zero.__and__(other)
				self.assertIs(NotImplemented, actual)

	def test_or(self):
		tests = (
			(logic.zero, logic.zero, logic.zero),
			(logic.zero, logic.one, logic.one),
			(logic.zero, logic.hi_z, logic.unknown),
			(logic.zero, logic.unknown, logic.unknown),

			(logic.one, logic.zero, logic.one),
			(logic.one, logic.one, logic.one),
			(logic.one, logic.hi_z, logic.one),
			(logic.one, logic.unknown, logic.one),

			(logic.hi_z, logic.zero, logic.unknown),
			(logic.hi_z, logic.one, logic.one),
			(logic.hi_z, logic.hi_z, logic.unknown),
			(logic.hi_z, logic.unknown, logic.unknown),

			(logic.unknown, logic.zero, logic.unknown),
			(logic.unknown, logic.one, logic.one),
			(logic.unknown, logic.hi_z, logic.unknown),
			(logic.unknown, logic.unknown, logic.unknown),
		)

		for a, b, expected in tests:
			with self.subTest(a = a, b = b, expected = expected):
				actual = a.__or__(b)
				self.assertIs(expected, actual)

	def test_or_notimplemented(self):
		tests = (
			None,
			2,
			'',
			'supercalifragilisticexpialidocious',
			(),
			object(),
		)

		for other in tests:
			with self.subTest(other = other):
				actual = logic.zero.__or__(other)
				self.assertIs(NotImplemented, actual)

	def test_xor(self):
		tests = (
			(logic.zero, logic.zero, logic.zero),
			(logic.zero, logic.one, logic.one),
			(logic.zero, logic.hi_z, logic.unknown),
			(logic.zero, logic.unknown, logic.unknown),

			(logic.one, logic.zero, logic.one),
			(logic.one, logic.one, logic.zero),
			(logic.one, logic.hi_z, logic.unknown),
			(logic.one, logic.unknown, logic.unknown),

			(logic.hi_z, logic.zero, logic.unknown),
			(logic.hi_z, logic.one, logic.unknown),
			(logic.hi_z, logic.hi_z, logic.unknown),
			(logic.hi_z, logic.unknown, logic.unknown),

			(logic.unknown, logic.zero, logic.unknown),
			(logic.unknown, logic.one, logic.unknown),
			(logic.unknown, logic.hi_z, logic.unknown),
			(logic.unknown, logic.unknown, logic.unknown),
		)

		for a, b, expected in tests:
			with self.subTest(a = a, b = b, expected = expected):
				actual = a.__xor__(b)
				self.assertIs(expected, actual)

	def test_xor_notimplemented(self):
		tests = (
			None,
			2,
			'',
			'supercalifragilisticexpialidocious',
			(),
			object(),
		)

		for other in tests:
			with self.subTest(other = other):
				actual = logic.zero.__xor__(other)
				self.assertIs(NotImplemented, actual)
