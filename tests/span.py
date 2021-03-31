import unittest
from hdlpy._span import span, rspan

class test_span(unittest.TestCase):
	def test_map(self):
		tests = (
			(span(start = 0, end = 31), 0, 0),
			(span(start = 0, end = 31), 1, 1),
			(span(start = 0, end = 31), 31, 31),
			(span(start = 0, end = 31), -1, 31),
			(span(start = 0, end = 31), -2, 30),
			(span(start = 8, end = 31), 8, 0),
			(span(start = 8, end = 31), 9, 1),
			(span(start = 8, end = 31), 31, 23),
			(span(start = 8, end = 31), -1, 23),
			(span(start = 8, end = 31), -2, 22),

			(span(start = 0, end = 31), slice(0, None), slice(0, None)),
			(span(start = 0, end = 31), slice(0, 31), slice(0, None)),
			(span(start = 0, end = 31), slice(1, None), slice(1, None)),
			(span(start = 0, end = 31), slice(1, 31), slice(1, None)),
			(span(start = 0, end = 31), slice(1, 30), slice(1, 31)),
			(span(start = 0, end = 31), slice(None, 31), slice(0, None)),
			(span(start = 0, end = 31), slice(31, 31), slice(31, None)),
			(span(start = 0, end = 31), slice(0, -1), slice(0, None)),
			(span(start = 0, end = 31), slice(-1, None), slice(31, None)),
			(span(start = 0, end = 31), slice(-2, None), slice(30, None)),
			(span(start = 0, end = 31), slice(-2, -1), slice(30, None)),

			(span(start = 8, end = 31), slice(8, None), slice(0, None)),
			(span(start = 8, end = 31), slice(8, 31), slice(0, None)),
			(span(start = 8, end = 31), slice(9, None), slice(1, None)),
			(span(start = 8, end = 31), slice(9, 31), slice(1, None)),
			(span(start = 8, end = 31), slice(9, 30), slice(1, 23)),
			(span(start = 8, end = 31), slice(None, 31), slice(0, None)),
			(span(start = 8, end = 31), slice(31, 31), slice(23, None)),
			(span(start = 8, end = 31), slice(-1, None), slice(23, None)),
			(span(start = 8, end = 31), slice(-2, None), slice(22, None)),
		)

		for obj, index, expected in tests:
			with self.subTest(obj = obj, index = index, expected = expected):
				actual = obj.map(index)
				self.assertEqual(actual, expected)

	def test_rmap(self):
		tests = (
			(span(start = 0, end = 31), 0, 0),
			(span(start = 0, end = 31), 1, 1),
			(span(start = 0, end = 31), 31, 31),
			(span(start = 0, end = 31), 30, 30),
			(span(start = 8, end = 31), 0, 8),
			(span(start = 8, end = 31), 1, 9),
			(span(start = 8, end = 31), 23, 31),
			(span(start = 8, end = 31), 22, 30),

			(span(start = 0, end = 31), slice(0, None), slice(0, 31)),
			(span(start = 0, end = 31), slice(1, None), slice(1, 31)),
			(span(start = 0, end = 31), slice(1, 31), slice(1, 30)),
			(span(start = 0, end = 31), slice(31, None), slice(31, 31)),
			(span(start = 0, end = 31), slice(30, None), slice(30, 31)),

			(span(start = 8, end = 31), slice(0, None), slice(8, 31)),
			(span(start = 8, end = 31), slice(1, None), slice(9, 31)),
			(span(start = 8, end = 31), slice(1, 23), slice(9, 30)),
			(span(start = 8, end = 31), slice(23, None), slice(31, 31)),
			(span(start = 8, end = 31), slice(22, None), slice(30, 31)),
		)

		for obj, index, expected in tests:
			with self.subTest(obj = obj, index = index, expected = expected):
				actual = obj.rmap(index)
				self.assertEqual(actual, expected)


class test_rspan(unittest.TestCase):
	def test_map(self):
		tests = (
			(rspan(start = 31, end = 0), 0, 31),
			(rspan(start = 31, end = 0), 1, 30),
			(rspan(start = 31, end = 0), 31, 0),
			(rspan(start = 31, end = 0), -1, 0),
			(rspan(start = 31, end = 0), -2, 1),
			(rspan(start = 31, end = 8), 8, 23),
			(rspan(start = 31, end = 8), 9, 22),
			(rspan(start = 31, end = 8), 31, 0),
			(rspan(start = 31, end = 8), -1, 0),
			(rspan(start = 31, end = 8), -2, 1),

			(rspan(start = 31, end = 0), slice(31, None), slice(0, None)),
			(rspan(start = 31, end = 0), slice(31, 0), slice(0, None)),
			(rspan(start = 31, end = 0), slice(30, None), slice(1, None)),
			(rspan(start = 31, end = 0), slice(30, 0), slice(1, None)),
			(rspan(start = 31, end = 0), slice(30, 1), slice(1, 31)),
			(rspan(start = 31, end = 0), slice(None, 0), slice(0, None)),
			(rspan(start = 31, end = 0), slice(0, 0), slice(31, None)),
			(rspan(start = 31, end = 0), slice(-1, 0), slice(0, None)),
			(rspan(start = 31, end = 0), slice(-1, None), slice(0, None)),
			(rspan(start = 31, end = 0), slice(-2, None), slice(1, None)),
			(rspan(start = 31, end = 0), slice(-1, -2), slice(0, 2)),

			(rspan(start = 31, end = 8), slice(31, None), slice(0, None)),
			(rspan(start = 31, end = 8), slice(31, 8), slice(0, None)),
			(rspan(start = 31, end = 8), slice(30, None), slice(1, None)),
			(rspan(start = 31, end = 8), slice(30, 8), slice(1, None)),
			(rspan(start = 31, end = 8), slice(30, 9), slice(1, 23)),
			(rspan(start = 31, end = 8), slice(None, 8), slice(0, None)),
			(rspan(start = 31, end = 8), slice(8, 8), slice(23, None)),
			(rspan(start = 31, end = 8), slice(-1, None), slice(0, None)),
			(rspan(start = 31, end = 8), slice(-2, None), slice(1, None)),
		)

		for obj, index, expected in tests:
			with self.subTest(obj = obj, index = index, expected = expected):
				actual = obj.map(index)
				self.assertEqual(actual, expected)

	def test_rmap(self):
		tests = (
			(rspan(start = 31, end = 0), 31, 0),
			(rspan(start = 31, end = 0), 30, 1),
			(rspan(start = 31, end = 0), 0, 31),
			(rspan(start = 31, end = 0), 1, 30),
			(rspan(start = 31, end = 8), 23, 8),
			(rspan(start = 31, end = 8), 22, 9),
			(rspan(start = 31, end = 8), 0, 31),
			(rspan(start = 31, end = 8), 1, 30),

			(rspan(start = 31, end = 0), slice(0, None), slice(31, 0)),
			(rspan(start = 31, end = 0), slice(1, None), slice(30, 0)),
			(rspan(start = 31, end = 0), slice(1, 31), slice(30, 1)),
			(rspan(start = 31, end = 0), slice(31, None), slice(0, 0)),
			(rspan(start = 31, end = 0), slice(0, 2), slice(31, 30)),

			(rspan(start = 31, end = 8), slice(0, None), slice(31, 8)),
			(rspan(start = 31, end = 8), slice(1, None), slice(30, 8)),
			(rspan(start = 31, end = 8), slice(1, 23), slice(30, 9)),
			(rspan(start = 31, end = 8), slice(23, None), slice(8, 8)),
		)

		for obj, index, expected in tests:
			with self.subTest(obj = obj, index = index, expected = expected):
				actual = obj.rmap(index)
				self.assertEqual(actual, expected)
