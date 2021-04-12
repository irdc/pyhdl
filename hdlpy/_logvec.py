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

import operator
from functools import cache

from . import logic
from ._lib import export
from ._span import rspan

class _GenericLogvecType(type):
	@cache
	def _make(cls, span):
		class logvec(cls, metaclass = _LogvecType):
			_span = span
		logvec.__name__ = f"{cls.__name__}[{span}]"
		logvec.__qualname__ = f"{cls.__qualname__}[{span}]"
		logvec.__module__ = cls.__module__
		return logvec

	def __getitem__(cls, index):
		"""Create type with given range.

		Note that indices go from high to low and slices are
		inclusive instead of exclusive. Therefore self[31:0]
		returns a 32-element vector type.
		"""

		if type(index) is not slice:
			raise ValueError(f"{index!r}: not a slice")
		if index.start is None \
		or index.start < 0 \
		or index.stop is None \
		or index.stop < 0 \
		or index.start < index.stop \
		or index.step is not None:
			raise ValueError(f"{index!r}: bad slice")

		return logvec._make(rspan(start = index.start, end = index.stop))

	def _convert(cls, value):
		try:
			if type(value) is logic:
				result = (value,)
			elif type(value) is int:
				if value < 0:
					value = 2 ** (value.bit_length() + 1) + value
				value = bin(value)[2:]
			if len(value) == 0:
				raise ValueError(f"{value!r}: too short")

			result = tuple(logic(b) for b in value if b != '_')
		except TypeError:
			raise ValueError(value)

		return result

	def __call__(cls, value):
		if isinstance(value, cls):
			return value
		elif not isinstance(value, logvec):
			value = cls._convert(value)
		cls = cls[len(value) - 1:0]

		return cls.__new__(cls, value)


class _LogvecType(_GenericLogvecType):
	def _convert(cls, value):
		if type(value) is int and value < 0:
			value = 2 ** len(cls._span) + value

		result = super()._convert(value)

		if len(result) < len(cls._span):
			result = (logic(0),) * (len(cls._span) - len(result)) + result
		elif len(result) > len(cls._span):
			raise ValueError(f"{value!r}: too long for {cls.__name__}")

		return result

	def __getitem__(cls, index):
		raise RuntimeError("not a generic type")

	def __call__(cls, value = None):
		if isinstance(value, cls):
			return value
		elif value is None:
			value = (logic(),) * len(cls._span)
		elif not (isinstance(value, logvec) and cls._span == value._span):
			value = cls._convert(value)

		return cls.__new__(cls, value)


@export
class logvec(tuple, metaclass = _GenericLogvecType):
	_span = None

	def __new__(cls, value):
		assert cls._span is not None
		return tuple.__new__(cls, tuple(value))

	def __repr__(self):
		return f"<{type(self).__name__} '{self!s}'>"

	def __str__(self):
		return ''.join(b._value_ for b in self)

	def __format__(self, fmt):
		if fmt == 'b' or fmt == '':
			return str(self)
		elif fmt == 'o':
			bits = 3
		elif fmt == 'd' or fmt == 'n':
			return str(self.unsigned)
		elif fmt == 'x' or fmt == 'X':
			bits = 4
		else:
			raise ValueError(fmt)

		if len(self) == 0:
			return '0'
		elif len(self) == bits:
			try:
				return format(self.unsigned, fmt)
			except ValueError:
				return 'X' if fmt == 'X' else 'x'

		result = ''
		buf = [logic(0)] * (bits - len(self) % bits) if len(self) % bits != 0 else []
		for bit in self:
			buf.append(bit)
			if len(buf) == bits:
				result += format(logvec(buf), fmt)
				buf.clear()

		return result

	def __getitem__(self, index):
		"""self[index]

		Note that indices go from high to low and slices are
		inclusive instead of exclusive. Therefore:
		* self[0] returns the last (least significant) element
		* self[-1] returns the first (most significant) element
		* self[-1:0] returns the entire contents
		"""

		index = self._span.map(index)
		result = super().__getitem__(index)
		if type(result) is not logic:
			if len(result) == 0:
				result = logvec.empty
			else:
				result = logvec[self._span.rmap(index)](result)
		return result

	def __int__(self):
		"""Unsigned integer value of self."""

		return self.unsigned

	@property
	def unsigned(self):
		"""Unsigned integer value of self."""

		value = 0
		for bit in self:
			value <<= 1
			if bit is logic.one:
				value += 1
			elif bit is not logic.zero:
				raise ValueError("{self!r}")
		return value

	@property
	def signed(self):
		"""Signed integer value (as two's complement) of self."""

		value = self.unsigned
		return value - 2 ** len(self) if self[-1] else value

	def __eq__(self, other):
		try:
			if type(other) is str and '-' in other:
				other = tuple(
					logic(b) if b != '-' else a
					for a, b in zip(self, (b for b in other if b != '_'))
				)
			return super().__eq__(type(self)(other))
		except AttributeError:
			return NotImplemented
		except TypeError:
			return NotImplemented
		except ValueError:
			return NotImplemented

	def __ne__(self, other):
		eq = self.__eq__(other)
		return NotImplemented if eq is NotImplemented else not eq

	@staticmethod
	def _apply(oper, left, right):
		try:
			left, right = logvec(left), logvec(right)
			ty = type(left) if len(left) >= len(right) else type(right)
			return logvec.__new__(ty, (oper(l, r) for l, r in zip(ty(left), ty(right))))
		except AttributeError:
			return NotImplemented
		except TypeError:
			return NotImplemented
		except ValueError:
			return NotImplemented

	def __invert__(self):
		"""~self"""

		return logvec.__new__(type(self), (~b for b in self))

	def __and__(self, other):
		"""self & other"""

		return logvec._apply(operator.__and__, self, other)

	def __rand__(self, other):
		"""other & self"""

		return logvec._apply(operator.__and__, other, self)

	def __or__(self, other):
		"""self | other"""

		return logvec._apply(operator.__or__, self, other)

	def __ror__(self, other):
		"""other | self"""

		return logvec._apply(operator.__or__, other, self)

	def __xor__(self, other):
		"""self ^ other"""

		return logvec._apply(operator.__xor__, self, other)

	def __rxor__(self, other):
		"""other ^ self"""

		return logvec._apply(operator.__xor__, other, self)

	def shift_left(self, amount):
		"""Logically shift left by amount."""

		if amount < 0:
			raise ValueError(f"{amount!r}: negative shift count")
		if amount == 0:
			return self
		if amount >= len(self):
			return type(self)(0)
		return self[-(amount + 1):] + (logic(0),) * amount

	def __lshift__(self, amount):
		return self.shift_left(amount)

	def rotate_left(self, amount):
		"""Rotate left by amount."""

		if amount < 0:
			raise ValueError(f"{amount!r}: negative shift count")
		amount %= len(self)
		return self if amount == 0 else self[-(amount + 1):] + self[:-amount]


	def shift_right(self, amount):
		"""Logically shift right by amount."""

		if amount < 0:
			raise ValueError(f"{amount!r}: negative shift count")
		if amount == 0:
			return self
		if amount >= len(self):
			return type(self)(0)
		return (logic(0),) * amount + self[:amount]

	def __rshift__(self, amount):
		return self.shift_right(amount)

	def rotate_right(self, amount):
		"""Rotate right by amount."""

		if amount < 0:
			raise ValueError(f"{amount!r}: negative shift count")
		amount %= len(self)
		return self if amount == 0 else self[amount - 1:] + self[:amount]

	@staticmethod
	def _concat(left, right):
		try:
			return logvec((*logvec(left), *logvec(right)))
		except AttributeError:
			return NotImplemented
		except TypeError:
			return NotImplemented
		except ValueError:
			return NotImplemented

	def __add__(self, other):
		"""Concatenate self and other."""

		return logvec._concat(self, other)

	def __radd__(self, other):
		"""Concatenate other and self."""

		return logvec._concat(other, self)


class _logvec0(logvec):
	_span = rspan.empty
	def __new__(cls):
		return logvec.empty
_logvec0.__name__ = f"{logvec.__name__}.empty"
_logvec0.__qualname__ = f"{logvec.__qualname__}.empty"

logvec.empty = tuple.__new__(_logvec0, ())
