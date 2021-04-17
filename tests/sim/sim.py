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

import unittest
from hdlpy import logic, part, once, always, when
from hdlpy.sim import Sim, Wait

class test_sim(unittest.TestCase):
	def test(the_test):
		@part
		class Flipflop:
			clk: logic
			rst: logic
			en: logic
			d: logic
			o: logic
			no: logic

			@when(rising = ('rst', 'clk'))
			def process(self):
				if self.rst:
					self.o = 0
				elif self.clk and self.en:
					self.o = self.d

			@always
			def neg(self):
				self.no = ~self.o

		@part
		class Testbench:
			_flipflop = Flipflop()

			@once
			async def test(self):
				tests = (
					({'en': 0, 'd': 0, 'rst': 1}, {'o': 0, 'no': 1}),
					({'rst': 0}, {'o': 0, 'no': 1}),
					({'en': 1, 'd': 1}, {'o': 1, 'no': 0}),
					({'en': 0, 'd': 0}, {'o': 1, 'no': 0}),
					({'en': 1, 'd': 0}, {'o': 0, 'no': 1}),
					({'en': 0, 'd': 1}, {'o': 0, 'no': 1}),
				)

				self._flipflop.clk = 0
				await Wait.delay('200ns')
				for set, check in tests:
					for attr, value in set.items():
						setattr(self._flipflop, attr, value)

					self._flipflop.clk = ~self._flipflop.clk
					await Wait.delay('200ns')

					for attr, expected in check.items():
						actual = getattr(self._flipflop, attr)
						the_test.assertEqual(expected, actual)

		testbench = Testbench()
		Sim(testbench).run()

		# if this fails, the tests didn't actually run
		the_test.assertEqual(testbench._flipflop.clk, logic(0))
