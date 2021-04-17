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

def _sign(value):
	return value // abs(value)

class _base_span(tuple):
	def __new__(cls, *, start, end):
		return tuple.__new__(cls, (start, end))

	@property
	def start(self):
		return self[0]

	@property
	def end(self):
		return self[1]

	def __repr__(self):
		return f"<{type(self).__name__} {self!s}>"

	def __str__(self):
		return f"{self.start}:{self.end}"

	def __add__(self, other):
		try:
			if self.end + 1 != other.start:
				raise ValueError(f"nonadjacent spans {self!r} and {other!r}")
			return type(self)(start = self.start, end = other.end)
		except TypeError:
			return NotImplemented

	__hash__ = tuple.__hash__

	def __eq__(self, other):
		if self is other:
			return True
		if type(self) is type(other):
			return super().__eq__(other)
		return NotImplemented


class span(_base_span):
	def __new__(cls, *, start, end):
		if start > end:
			raise ValueError(f"bad span {start!r}:{end!r}")

		return super().__new__(cls, start = start, end = end)

	def __len__(self):
		return self.end - self.start + 1

	def __and__(self, other):
		if type(other) is int:
			if other >= self.start and other <= self.end:
				return other
		elif type(other) is span:
			start = max(self.start, other.start)
			end = min(self.end, other.end)
			if start <= end:
				return span(start = start, end = end)

		return None

	def map(self, index):
		"""Translate index relative to span."""

		if type(index) is int:
			if index < 0:
				index = self.end - (-index - 1)

			if self & index != index:
				raise IndexError(f"{index!r}: out of bounds")

			return index - self.start
		elif type(index) is span:
			if self & index != index:
				raise IndexError(f"{index!r}: out of bounds")

			stop = self.map(index.end) + 1
			return slice(self.map(index.start), None if stop == len(self) else stop)
		elif type(index) is slice:
			stop = self.map(index.stop if index.stop is not None else self.end) + 1
			return slice(self.map(index.start if index.start is not None else self.start), None if stop == len(self) else stop)
		else:
			try:
				return self.map(index.__index__())
			except:
				raise ValueError(f"{index!r}: bad index")

	def rmap(self, index):
		"""Translate index in reverse."""

		if type(index) is int:
			if index < 0:
				index = len(self) - (-index - 1)

			result = index + self.start
			if self & result != result:
				raise IndexError(f"{index!r}: out of bounds")

			return result
		elif type(index) is slice:
			return slice(
				self.rmap(index.start if index.start is not None else self.start),
				self.rmap((index.stop if index.stop is not None else len(self)) - 1))
		else:
			try:
				return self.rmap(index.__index__())
			except:
				raise ValueError(f"{index!r}: bad index")

		raise ValueError(f"{index!r}: bad index")

span.empty = tuple.__new__(span, (0, -1))


class rspan(_base_span):
	def __new__(cls, *, start, end):
		if start < end:
			raise ValueError(f"bad span {start!r}:{end!r}")

		return super().__new__(cls, start = start, end = end)

	def __len__(self):
		return self.start - self.end + 1

	def __and__(self, other):
		if type(other) is int:
			if other <= self.start and other >= self.end:
				return other
		if type(other) is rspan:
			start = min(self.start, other.start)
			end = max(self.end, other.end)
			if start >= end:
				return rspan(start = start, end = end)

		return None

	def map(self, index):
		"""Translate index relative to span."""

		if type(index) is int:
			if index < 0:
				index = self.start - (-index - 1)

			if self & index != index:
				raise IndexError(f"{index!r}: out of bounds")

			return self.start - index
		elif type(index) is rspan:
			if self & index != index:
				raise IndexError(f"{index!r}: out of bounds")

			stop = self.map(index.end) + 1
			return slice(self.map(index.start), None if stop == len(self) else stop)
		elif type(index) is slice:
			stop = self.map(index.stop if index.stop is not None else self.end) + 1
			return slice(self.map(index.start if index.start is not None else self.start), None if stop == len(self) else stop)
		else:
			try:
				return self.map(index.__index__())
			except:
				raise ValueError(f"{index!r}: bad index")

		raise ValueError(f"{index!r}: bad index")

	def rmap(self, index):
		"""Translate index in reverse."""

		if type(index) is int:
			if index < 0:
				index = len(self) - (-index - 1)

			result = self.start - index
			if self & result != result:
				raise IndexError(f"{index!r}: out of bounds")

			return result
		elif type(index) is slice:
			return slice(
				self.rmap(index.start if index.start is not None else self.start),
				self.rmap((index.stop if index.stop is not None else len(self)) - 1))
		else:
			try:
				return self.rmap(index.__index__())
			except:
				raise ValueError(f"{index!r}: bad index")

		raise ValueError(f"{index!r}: bad index")

rspan.empty = tuple.__new__(rspan, (-1, 0))
