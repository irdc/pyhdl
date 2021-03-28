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
from hdlpy import logic, part, always

class test_part(unittest.TestCase):
	def test_empty_class(self):
		@part
		class EmptyClass:
			pass

	def test_getattr(self):
		@part
		class SignalWithType:
			signal: logic

		@part
		class SignalWithDefault:
			signal = logic(1)

		@part
		class SignalWithTypeAndDefault:
			signal: logic = logic(1)

		@part
		class SignalWithBlock:
			signal = logic(1)

			@always
			def foo(self):
				pass

		tests = (
			(SignalWithType, logic('X')),
			(SignalWithDefault, logic(1)),
			(SignalWithTypeAndDefault, logic(1)),
			(SignalWithBlock, logic(1)),
		)

		for cls, expected in tests:
			with self.subTest(cls = cls, expected = expected):
				test = cls()
				actual = test.signal
				self.assertIs(expected, actual)

	def test_setattr(self):
		@part
		class SignalWithType:
			signal: logic

		@part
		class SignalWithDefault:
			signal = logic(1)

		@part
		class SignalWithTypeAndDefault:
			signal: logic = logic(1)

		@part
		class SignalWithBlock:
			signal = logic(1)

			@always
			def foo(self):
				pass

		tests = (
			(SignalWithType),
			(SignalWithDefault),
			(SignalWithTypeAndDefault),
			(SignalWithBlock),
		)

		expected = logic('Z')
		for cls in tests:
			with self.subTest(cls = cls):
				test = cls()
				test.signal = 'Z'
				actual = test.signal
				self.assertIs(expected, actual)
