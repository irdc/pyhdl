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
from hdlpy import logic, when

class test_when(unittest.TestCase):
	def test_attr(self):
		tests = (
			None,
			'foo',
			'_bar',
			'_123',
			(),
			('foo', 'bar'),
			[],
			['foo', 'bar'],
			set(),
			{'foo', 'bar'},
		)

		def fun(self): pass

		for value in tests:
			with self.subTest(value = value):
				when(change = value)(fun)
				when(rising = value)(fun)
				when(falling = value)(fun)

	def test_attr_invalid(self):
		tests = (
			True,
			42,
			'',
			'123',
			'()',
			('foo', '123'),
			('foo', 42),
			['foo', '123'],
			['foo', 42],
			{'foo', '123'},
			{'foo', 42},
			{},
			{'a': 'foo', 'b': 42},
		)

		def fun(self): pass

		for cond in ('change', 'rising', 'falling'):
			for value in tests:
				with self.subTest(cond = cond, value = value), \
				     self.assertRaises(ValueError):
					when(**{cond: value})(fun)

	def test_delay(self):
		tests = (
			None,
			123,
			'123ps',
			'123us',
			'123ns',
			'123s',
		)

		def fun(self): pass

		for value in tests:
			with self.subTest(value = value):
				when(delay = value)(fun)

	def test_delay_invalid(self):
		tests = (
			True,
			'',
			'123',
			'()'
		)

		def fun(self): pass

		for value in tests:
			with self.subTest(value = value), \
			     self.assertRaises(ValueError):
				when(delay = value)(fun)
