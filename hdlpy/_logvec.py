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

from ._logic import logic
from ._lib import export, type_property
from ._span import rspan

class _GenericLogvecType(type):
	@cache
	def _make_type(cls, span):
		class logvec(cls, metaclass = _LogvecType):
			__origin__ = cls
			__args__ = (span,)

		if '.' in cls.__qualname__:
			prefix = cls.__qualname__.rsplit(sep = '.', maxsplit = 1)[0] + '.'
		else:
			prefix = ''

		if len(span) > 0:
			logvec.__name__ = cls._name_fmt.format(str(span))
		elif '_' in cls.__name__:
			logvec.__name__ = 'logvec.empty.' + cls.__name__.split(sep = '_', maxsplit = 1)[0]
		else:
			logvec.__name__ = 'logvec.empty'
		logvec.__qualname__ = prefix + logvec.__name__
		logvec.__module__ = cls.__module__
		return logvec

	def __getitem__(cls, index):
		"""Create type with given range.

		Note that indices go from high to low and slices are
		inclusive instead of exclusive. Therefore self[31:0]
		returns a 32-element vector type.
		"""

		if type(index) is not rspan:
			if type(index) is not slice:
				raise ValueError(f"{index!r}: not a slice")
			if index.start is None \
			or index.start < 0 \
			or index.stop is None \
			or index.stop < 0 \
			or index.start < index.stop \
			or index.step is not None:
				raise ValueError(f"{index!r}: bad slice")
			index = rspan(start = index.start, end = index.stop)

		return cls._make_type(index)

	def _convert(cls, value):
		try:
			if isinstance(value, logvec):
				return tuple(value)

			if type(value) is int:
				if value < 0:
					value = 2 ** (value.bit_length() + 1) + value
				result = []
				while True:
					result.append(logic.one if value % 2 == 1 else logic.zero)
					value >>= 1
					if value == 0:
						break
				result.reverse()
				return tuple(result)

			try:
				return (value._logic_value,)
			except:
				try:
					return tuple(v._logic_value for v in value)
				except:
					return tuple(logic(b) for b in value if b != '_')
		except TypeError:
			raise ValueError(value)

	def __call__(cls, value):
		if isinstance(value, cls):
			return value
		elif not isinstance(value, logvec):
			value = cls._convert(value)
		if len(value) == 0:
			return cls.empty

		return cls._make_type(rspan(start = len(value) - 1, end = 0))._new(value)


class _LogvecType(_GenericLogvecType):
	def _convert(cls, value):
		if type(value) is int and value < 0:
			value = 2 ** len(cls.__args__[0]) + value

		result = super()._convert(value)

		span = cls.__args__[0]
		if len(result) < len(span):
			if len(result) == 0:
				result = (logic.zero,) * len(span)
			else:
				result = (cls._extend_with(result[0]),) * (len(span) - len(result)) + result
		elif len(result) > len(span):
			raise ValueError(f"{value!r}: too long for {cls.__name__}")

		return result

	def __getitem__(cls, index):
		raise RuntimeError("not a generic type")

	def _new(cls, value):
		return tuple.__new__(cls, value)

	def __call__(cls, value = None):
		if type(value) is cls:
			return value
		elif value is None:
			value = (logic.unknown,) * len(cls.__args__[0])
		elif not (isinstance(value, logvec) and len(value) == len(cls.__args__[0])):
			value = cls._convert(value)

		return cls._new(value)


@export
class logvec(tuple, metaclass = _GenericLogvecType):
	_name_fmt = 'logvec[{0}]'

	@staticmethod
	def _extend_with(val):
		return logic.zero

	@staticmethod
	def _unsigned(obj):
		value = 0
		for bit in obj:
			value <<= 1
			if bit is logic.one:
				value += 1
			elif bit is not logic.zero:
				raise ValueError("{obj!r}")
		return value

	@staticmethod
	def _same_types(left, right):
		"""Ensure left and right are of the same type (excluding length)."""

		if not isinstance(left, logvec):
			left = logvec(left)
		if not isinstance(right, logvec):
			right = logvec(right)

		if type(left).__origin__ == type(right).__origin__:
			return left, right
		elif type(left).__origin__ == logvec \
		and type(right).__origin__ != logvec:
			return right.__origin__[left.__args__[0]]._new(left), right
		elif type(left).__origin__ != logvec \
		and type(right).__origin__ == logvec:
			return left, left.__origin__[right.__args__[0]]._new(right)
		else:
			raise ValueError(f"bad operation for {left!r} and {right!r}")

	@staticmethod
	def _enlarge(obj, new_len):
		if len(obj) < new_len:
			obj = obj.__origin__[rspan(
				start = obj.__args__[0].start + new_len - len(obj),
				end = obj.__args__[0].end)](obj)
		return obj

	@staticmethod
	def _same_length(left, right):
		left, right = logvec._same_types(left, right)
		return logvec._enlarge(left, len(right)), logvec._enlarge(right, len(left))

	@staticmethod
	def _apply(oper, left, right):
		try:
			left, right = logvec._same_length(left, right)
			return type(left)._new((oper(l, r) for l, r in zip(left, right)))
		except (TypeError, ValueError):
			return NotImplemented

	@staticmethod
	def _concat(left, right):
		try:
			left, right = logvec._same_types(left, right)
			ty = left.__origin__[rspan(
				start = len(left.__args__[0]) + len(right.__args__[0]) - 1,
				end = 0)]
			return ty._new((*left, *right))
		except (TypeError, ValueError):
			return NotImplemented

	@staticmethod
	def _cmp(left, right):
		try:
			left, right = logvec._same_length(left, right)
			for l, r in zip(left, right):
				if l != r:
					return -1 if l < r else 1
			return 0
		except (TypeError, ValueError):
			return NotImplemented

	@staticmethod
	def _add(left, right, carry = logic.zero):
		try:
			left, right = logvec._same_length(left, right)
			result = []
			for l, r in zip(reversed(left), reversed(right)):
				result.append(l ^ r ^ carry)
				carry = (carry & l) | (carry & r) | (l & r)
			result.reverse()
			return type(left)(result)
		except (TypeError, ValueError):
			return NotImplemented

	@staticmethod
	def _sub(left, right):
		try:
			left, right = logvec._same_length(left, right)
			return logvec._add(left, ~right, logic.one)
		except (TypeError, ValueError):
			return NotImplemented

	@staticmethod
	def _mul(left, right):
		try:
			left, right = logvec._same_types(left, right)
			ty = left.__origin__[rspan(
				start = len(left) + len(right) - 1,
				end = 0)]
			result, right = ty(0), ty(right)
			for l in reversed(left):
				if l is logic.one:
					result += right
				elif l is not logic.zero:
					return ty()
				right <<= 1
			return result
		except (TypeError, ValueError):
			return NotImplemented

	@staticmethod
	def _divmod(num, denom):
		if denom == 0:
			raise ValueError(denom)
		try:
			num, denom = logvec._same_length(num, denom)
			bits = len(num)

			quot = type(num)(0)
			zeroes = logic.zero * bits
			num = logvec._concat(zeroes, num)
			denom = logvec._concat(denom, zeroes)

			for i in range(bits, 0, -1):
				if num >= denom:
					num -= denom
					quot |= 2**i
				denom >>= 1

			return quot, num[-(bits + 1):]
		except (TypeError, ValueError):
			return NotImplemented, NotImplemented

	def __repr__(self):
		return f"<{type(self).__name__} '{self!s}'>"

	def __str__(self):
		return ''.join(str(b) for b in self)

	def __format__(self, fmt):
		if fmt == 'b' or fmt == '':
			return str(self)
		elif fmt == 'o':
			bits = 3
		elif fmt == 'd' or fmt == 'n':
			return str(int(self.unsigned))
		elif fmt == 'x' or fmt == 'X':
			bits = 4
		else:
			raise ValueError(fmt)

		if len(self) == 0:
			return '0'
		elif len(self) == bits:
			try:
				return format(int(self.unsigned), fmt)
			except ValueError:
				return 'X' if fmt == 'X' else 'x'

		result = ''
		buf = [logic.zero] * (bits - len(self) % bits) if len(self) % bits != 0 else []
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

		index = self.__args__[0].map(index)
		result = super().__getitem__(index)

		try:
			return result._logic_value
		except:
			if len(result) == 0:
				return cls.empty
			return self.__origin__[self.__args__[0].rmap(index)](result)

	def __reversed__(self):
		"""reversed(self)"""

		for i in range(len(self) - 1, -1, -1):
			yield super().__getitem__(i)

	logvec = type_property()
	unsigned = type_property()
	signed = type_property()

	@logvec.type
	def logvec(cls):
		return logvec[cls.__args__[0]]

	@logvec.value
	def logvec(self):
		return type(self).logvec._new(self)

	@unsigned.type
	def unsigned(cls):
		return unsigned_logvec[cls.__args__[0]]

	@unsigned.value
	def unsigned(self):
		return type(self).unsigned._new(self)

	@signed.type
	def signed(cls):
		return signed_logvec[cls.__args__[0]]

	@signed.value
	def signed(self):
		return type(self).signed._new(self)

	def __eq__(self, other):
		try:
			if type(other) is str and '-' in other:
				other = tuple(
					logic(b) if b != '-' else a
					for a, b in zip(self, (b for b in other if b != '_'))
				)
			return super().__eq__(type(self)(other))
		except (TypeError, ValueError):
			return NotImplemented

	def __ne__(self, other):
		eq = self.__eq__(other)
		return NotImplemented if eq is NotImplemented else not eq

	def __invert__(self):
		"""~self"""

		return type(self)._new((~b for b in self))

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

	def shift_left(self, amount, fill = logic.zero):
		"""Logically shift left by amount."""

		if type(amount) is not int:
			try:
				amount = amount.__index__()
			except:
				raise ValueError(amount)
		if amount < 0:
			raise ValueError(f"{amount!r}: negative shift count")
		if amount == 0:
			return self
		try:
			if amount >= len(self):
				return type(self)(fill._logic_value * len(self))
			return logvec._concat(self[-(amount + 1):], fill._logic_value * amount)
		except:
			return self.shift_left(amount, logic(fill))

	def __lshift__(self, amount):
		return self.shift_left(amount)

	def rotate_left(self, amount):
		"""Rotate left by amount."""

		if type(amount) is not int:
			try:
				amount = amount.__index__()
			except:
				raise ValueError(amount)
		if amount < 0:
			raise ValueError(f"{amount!r}: negative shift count")
		amount %= len(self)
		return self if amount == 0 else logvec._concat(self[-(amount + 1):], self[:-amount])

	def shift_right(self, amount, fill = logic.zero):
		"""Logically shift right by amount."""

		if type(amount) is not int:
			try:
				amount = amount.__index__()
			except:
				raise ValueError(amount)
		if amount < 0:
			raise ValueError(f"{amount!r}: negative shift count")
		if amount == 0:
			return self
		try:
			if amount >= len(self):
				return type(self)(fill._logic_value * len(self))
			return logvec._concat(fill._logic_value * amount, self[:amount])
		except:
			return self.shift_right(amount, logic(fill))

	def __rshift__(self, amount):
		return self.shift_right(amount)

	def rotate_right(self, amount):
		"""Rotate right by amount."""

		if type(amount) is not int:
			try:
				amount = amount.__index__()
			except:
				raise ValueError(amount)
		if amount < 0:
			raise ValueError(f"{amount!r}: negative shift count")
		amount %= len(self)
		return self if amount == 0 else logvec._concat(self[amount - 1:], self[:amount])

	def __add__(self, other):
		"""Concatenate self and other."""

		return logvec._concat(self, other)

	def __radd__(self, other):
		"""Concatenate other and self."""

		return logvec._concat(other, self)

	def __mul__(self, other):
		"""Repeat self times other."""

		try:
			if other <= 0:
				return NotImplemented if other < 0 else self.empty
			else:
				return logvec[len(self) * other - 1:0]._new(tuple(self) * other)
		except (TypeError, ValueError):
			return NotImplemented

	def __rmul__(self, other):
		"""Repeat self times other."""

		return self.__mul__(other)


class unsigned_logvec(logvec):
	_name_fmt = 'logvec[{0}].unsigned'

	def __eq__(self, other):
		try:
			if type(other) is not str:
				self, other = logvec._same_types(self, other)
			return super().__eq__(other)
		except (TypeError, ValueError):
			return NotImplemented

	def __int__(self):
		"""Unsigned integer value of self."""

		return logvec._unsigned(self)

	def __index__(self):
		return self.__int__()

	def __format__(self, fmt):
		if fmt == 'd' or fmt == 'n':
			return format(int(self), fmt)
		return super().__format__(fmt)

	@property
	def unsigned(self):
		return self

	def __lt__(self, other):
		cmp = logvec._cmp(self, other)
		return NotImplemented if cmp is NotImplemented else cmp < 0

	def __le__(self, other):
		cmp = logvec._cmp(self, other)
		return NotImplemented if cmp is NotImplemented else cmp <= 0

	def __gt__(self, other):
		cmp = logvec._cmp(self, other)
		return NotImplemented if cmp is NotImplemented else cmp > 0

	def __ge__(self, other):
		cmp = logvec._cmp(self, other)
		return NotImplemented if cmp is NotImplemented else cmp >= 0

	def __add__(self, other):
		"""self + other"""

		return logvec._add(self, other)

	def __radd__(self, other):
		"""other + self"""

		return logvec._add(other, self)

	def __sub__(self, other):
		"""self - other"""

		return logvec._sub(self, other)

	def __rsub__(self, other):
		"""other - self"""

		return logvec._sub(other, self)

	def __mul__(self, other):
		"""self * other"""

		return logvec._mul(self, other)

	def __rmul__(self, other):
		"""other * self"""

		return logvec._mul(other, self)

	def __floordiv__(self, other):
		"""self // other"""

		return logvec._divmod(self, other)[0]

	def __rfloordiv__(self, other):
		"""other // self"""

		return logvec._divmod(other, self)[0]

	def __mod__(self, other):
		"""self % other"""

		return logvec._divmod(self, other)[1]

	def __rmod__(self, other):
		"""other % self"""

		return logvec._divmod(other, self)[1]


class signed_logvec(logvec):
	_name_fmt = 'logvec[{0}].signed'

	@staticmethod
	def _extend_with(val):
		return val

	def __eq__(self, other):
		try:
			if type(other) is not str:
				self, other = logvec._same_types(self, other)
			return super().__eq__(other)
		except (TypeError, ValueError):
			return NotImplemented

	def __int__(self):
		"""Signed integer value of self."""

		value = logvec._unsigned(self)
		return value - 2 ** len(self) if self[-1] else value

	def __index__(self):
		return self.__int__()

	def __format__(self, fmt):
		if fmt == 'd' or fmt == 'n':
			return format(int(self), fmt)
		return super().__format__(fmt)

	@property
	def signed(self):
		return self

	@staticmethod
	def _cmp(left, right):
		try:
			left, right = logvec._same_types(left, right)
			if left[-1] and not right[-1]:
				return -1
			elif not left[-1] and right[-1]:
				return 1
			cmp = logvec._cmp(left, right)
			if cmp is NotImplemented:
				return NotImplemented
			return -cmp if left[-1] and right[-1] else cmp
		except (TypeError, ValueError):
			return NotImplemented

	def __lt__(self, other):
		cmp = signed_logvec._cmp(self, other)
		return NotImplemented if cmp is NotImplemented else cmp < 0

	def __le__(self, other):
		cmp = signed_logvec._cmp(self, other)
		return NotImplemented if cmp is NotImplemented else cmp <= 0

	def __gt__(self, other):
		cmp = signed_logvec._cmp(self, other)
		return NotImplemented if cmp is NotImplemented else cmp > 0

	def __ge__(self, other):
		cmp = signed_logvec._cmp(self, other)
		return NotImplemented if cmp is NotImplemented else cmp >= 0

	def shift_right(self, amount, fill = None):
		"""Arithmetically shift right by amount."""

		try:
			return super().shift_right(amount, fill._logic_value)
		except:
			return super().shift_right(amount, self[-1] if fill is None else logic(fill))

	def __neg__(self):
		"""-self"""

		return ~self - 1

	def __abs__(self):
		"""abs(self)"""

		return -self if self[-1] else self

	def __add__(self, other):
		"""self + other"""

		return logvec._add(self, other)

	def __radd__(self, other):
		"""other + self"""

		return logvec._add(other, self)

	def __sub__(self, other):
		"""self - other"""

		return logvec._sub(self, other)

	def __rsub__(self, other):
		"""other - self"""

		return logvec._sub(other, self)

	@staticmethod
	def _mul(left, right):
		try:
			left, right = logvec._same_types(left, right)
			neg = left[-1] ^ right[-1]
			result = logvec._mul(abs(left).unsigned, abs(right).unsigned).signed
			return -result if neg else result
		except (TypeError, ValueError):
			return NotImplemented

	def __mul__(self, other):
		"""self * other"""

		return signed_logvec._mul(self, other)

	def __rmul__(self, other):
		"""other * self"""

		return signed_logvec._mul(other, self)

	@staticmethod
	def _divmod(left, right):
		try:
			left, right = logvec._same_types(left, right)
			neg = left[-1] ^ right[-1]
			quot, rem = logvec._divmod(abs(left).unsigned, abs(right).unsigned)
			quot, rem = quot.signed, rem.signed
			return -quot if neg else quot, -rem if left[-1] else rem
		except (TypeError, ValueError):
			return NotImplemented, NotImplemented

	def __floordiv__(self, other):
		"""self // other"""

		return signed_logvec._divmod(self, other)[0]

	def __rfloordiv__(self, other):
		"""other // self"""

		return signed_logvec._divmod(other, self)[0]

	def __mod__(self, other):
		"""self % other"""

		return signed_logvec._divmod(self, other)[1]

	def __rmod__(self, other):
		"""other % self"""

		return signed_logvec._divmod(other, self)[1]


logvec.empty = logvec[rspan.empty]._new(())
unsigned_logvec.empty = unsigned_logvec[rspan.empty]._new(())
signed_logvec.empty = signed_logvec[rspan.empty]._new(())
