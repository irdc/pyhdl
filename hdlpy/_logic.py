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

from ._lib import export

@export
class logic(tuple):
	"""Represents a logic signal and implements multi-value logic.

	Value can be any of:
		'0' or 0: a logical zero
		'1' or 1: a logical one
		'Z': an high-impedance signal
		'X': an unknown signal
	"""

	def __new__(cls, value = 'X'):
		try:
			return value._logic_value
		except:
			if type(value) is str:
				if value == '0':
					return cls.zero
				elif value == '1':
					return cls.one
				elif value == 'Z':
					return cls.hi_z
				elif value == 'X':
					return cls.unknown

			if type(value) is int:
				if value == 0:
					return cls.zero
				elif value == 1:
					return cls.one

			if value is True:
				return cls.one
			if value is False:
				return cls.zero

			raise ValueError(f"{value!r}: not a valid logic value")

	def __init_subclass__(cls):
		super().__init_subclass__()
		cls.__name__ = logic.__name__
		cls.__qualname__ = logic.__qualname__

	def __repr__(self):
		return f"<logic '{self!s}'>"

	def __format__(self, fmt):
		if fmt != '':
			raise ValueError(fmt)
		return str(self)

	def __int__(self):
		if self is logic.zero:
			return 0
		if self is logic.one:
			return 1
		raise ValueError(f"{self!r}")

	def __eq__(self, other):
		try:
			return self is other._logic_value
		except:
			try:
				return (type(other) is str and other == '-') \
					or self is logic(other)
			except ValueError:
				return NotImplemented

	def __ne__(self, other):
		try:
			return self is not other._logic_value
		except:
			try:
				return not ((type(other) is str and other == '-') \
					or self is logic(other))
			except ValueError:
				return NotImplemented

	def __lt__(self, other):
		try:
			return self._logic_order < other._logic_order
		except:
			try:
				return self._logic_order < logic(other)._logic_order
			except ValueError:
				return NotImplemented

	def __le__(self, other):
		try:
			return self._logic_order <= other._logic_order
		except:
			try:
				return self._logic_order <= logic(other)._logic_order
			except ValueError:
				return NotImplemented

	def __gt__(self, other):
		try:
			return self._logic_order > other._logic_order
		except:
			try:
				return self._logic_order > logic(other)._logic_order
			except ValueError:
				return NotImplemented

	def __ge__(self, other):
		try:
			return self._logic_order >= other._logic_order
		except:
			try:
				return self._logic_order >= logic(other)._logic_order
			except ValueError:
				return NotImplemented

	def __bool__(self):
		"""self is logic.one"""

		return False

	def __invert__(self):
		"""~self -> result

		self result
		---- ------
		 0     1
		 1     0
		 Z     X
		 X     X
		"""

		return logic.unknown

	def __copy__(self):
		return self

	def __deepcopy__(self, memo):
		return self

	def __and__(self, other):
		"""self & other -> result

		self other result
		---- ----- ------
		 0     0     0
		 0     1     0
		 0     Z     0
		 0     X     0

		 1     0     0
		 1     1     1
		 1     Z     X
		 1     X     X

		 Z     0     0
		 Z     1     X
		 Z     Z     X
		 Z     X     X

		 X     0     0
		 X     1     X
		 X     Z     X
		 X     X     X
		"""

		# implemented in subclass
		raise NotImplementedError

	def __or__(self, other):
		"""self | other -> result

		self other result
		---- ----- ------
		 0     0     0
		 0     1     1
		 0     Z     X
		 0     X     X

		 1     0     1
		 1     1     1
		 1     Z     1
		 1     X     1

		 Z     0     X
		 Z     1     1
		 Z     Z     X
		 Z     X     X

		 X     0     X
		 X     1     1
		 X     Z     X
		 X     X     X
		"""

		# implemented in subclass
		raise NotImplementedError

	def __xor__(self, other):
		"""self ^ other -> result

		self other result
		---- ----- ------
		 0     0     0
		 0     1     1
		 0     Z     X
		 0     X     X

		 1     0     1
		 1     1     0
		 1     Z     X
		 1     X     X

		 Z     0     X
		 Z     1     X
		 Z     Z     X
		 Z     X     X

		 X     0     X
		 X     1     X
		 X     Z     X
		 X     X     X
		"""

		# implemented in subclass
		raise NotImplementedError

	def __rand__(self, other):
		try:
			return self.__and__(logic(other))
		except ValueError:
			return NotImplemented

	def __ror__(self, other):
		try:
			return self.__or__(logic(other))
		except ValueError:
			return NotImplemented

	def __rxor__(self, other):
		try:
			return self.__xor__(logic(other))
		except ValueError:
			return NotImplemented

	def __add__(self, other):
		"""self + other -> result"""

		try:
			return logvec[1:0]._new((self, other._logic_value))
		except:
			try:
				return logvec[1:0]._new((self, logic(other)))
			except ValueError:
				return NotImplemented

	def __radd__(self, other):
		"""other + self -> result"""

		try:
			return logvec[1:0]._new((logic(other), self))
		except ValueError:
			return NotImplemented

	def __mul__(self, other):
		"""self * other -> result"""

		try:
			if other < 0:
				return NotImplemented
			elif other == 0:
				return logvec.empty
			else:
				return logvec[other - 1:0]._new((self,) * other)
		except (TypeError, ValueError):
			return NotImplemented

	def __rmul__(self, other):
		"""self * other -> result"""

		return self.__mul__(other)


class logic_zero(logic):
	@classmethod
	def _init(cls):
		cls._logic_value = logic.zero
		cls._logic_order = 0

		cls._and_zero = logic.zero
		cls._and_one = logic.zero
		cls._and_hi_z = logic.zero
		cls._and_unknown = logic.zero

		cls._or_zero = logic.zero
		cls._or_one = logic.one
		cls._or_hi_z = logic.unknown
		cls._or_unknown = logic.unknown

		cls._xor_zero = logic.zero
		cls._xor_one = logic.one
		cls._xor_hi_z = logic.unknown
		cls._xor_unknown = logic.unknown

	def __str__(self):
		return '0'

	def __invert__(self):
		return logic.one

	def __and__(self, other):
		try:
			return other._and_zero
		except:
			try:
				return logic(other)._and_zero
			except ValueError:
				return NotImplemented

	def __or__(self, other):
		try:
			return other._or_zero
		except:
			try:
				return logic(other)._or_zero
			except ValueError:
				return NotImplemented

	def __xor__(self, other):
		try:
			return other._xor_zero
		except:
			try:
				return logic(other)._xor_zero
			except ValueError:
				return NotImplemented


class logic_one(logic):
	@classmethod
	def _init(cls):
		cls._logic_value = logic.one
		cls._logic_order = 1

		cls._and_zero = logic.zero
		cls._and_one = logic.one
		cls._and_hi_z = logic.unknown
		cls._and_unknown = logic.unknown

		cls._or_zero = logic.one
		cls._or_one = logic.one
		cls._or_hi_z = logic.one
		cls._or_unknown = logic.one

		cls._xor_zero = logic.one
		cls._xor_one = logic.zero
		cls._xor_hi_z = logic.unknown
		cls._xor_unknown = logic.unknown

	def __str__(self):
		return '1'

	def __bool__(self):
		return True

	def __invert__(self):
		return logic.zero

	def __and__(self, other):
		try:
			return other._and_one
		except:
			try:
				return logic(other)._and_one
			except ValueError:
				return NotImplemented

	def __or__(self, other):
		try:
			return other._or_one
		except:
			try:
				return logic(other)._or_one
			except ValueError:
				return NotImplemented

	def __xor__(self, other):
		try:
			return other._xor_one
		except:
			try:
				return logic(other)._xor_one
			except ValueError:
				return NotImplemented


class logic_hi_z(logic):
	@classmethod
	def _init(cls):
		cls._logic_value = logic.hi_z
		cls._logic_order = 3

		cls._and_zero = logic.zero
		cls._and_one = logic.unknown
		cls._and_hi_z = logic.unknown
		cls._and_unknown = logic.unknown

		cls._or_zero = logic.unknown
		cls._or_one = logic.one
		cls._or_hi_z = logic.unknown
		cls._or_unknown = logic.unknown

		cls._xor_zero = logic.unknown
		cls._xor_one = logic.unknown
		cls._xor_hi_z = logic.unknown
		cls._xor_unknown = logic.unknown

	def __str__(self):
		return 'Z'

	def __and__(self, other):
		try:
			return other._and_hi_z
		except:
			try:
				return logic(other)._and_hi_zi
			except ValueError:
				return NotImplemented

	def __or__(self, other):
		try:
			return other._or_hi_z
		except:
			try:
				return logic(other)._or_hi_zi
			except ValueError:
				return NotImplemented

	def __xor__(self, other):
		try:
			return other._xor_hi_z
		except:
			try:
				return logic(other)._xor_hi_zi
			except ValueError:
				return NotImplemented


class logic_unknown(logic):
	@classmethod
	def _init(cls):
		cls._logic_value = logic.unknown
		cls._logic_order = 2

		cls._and_zero = logic.zero
		cls._and_one = logic.unknown
		cls._and_hi_z = logic.unknown
		cls._and_unknown = logic.unknown

		cls._or_zero = logic.unknown
		cls._or_one = logic.one
		cls._or_hi_z = logic.unknown
		cls._or_unknown = logic.unknown

		cls._xor_zero = logic.unknown
		cls._xor_one = logic.unknown
		cls._xor_hi_z = logic.unknown
		cls._xor_unknown = logic.unknown

	def __str__(self):
		return 'X'

	def __and__(self, other):
		try:
			return other._and_unknown
		except:
			try:
				return logic(other)._and_unknown
			except ValueError:
				return NotImplemented

	def __or__(self, other):
		try:
			return other._or_unknown
		except:
			try:
				return logic(other)._or_unknown
			except ValueError:
				return NotImplemented

	def __xor__(self, other):
		try:
			return other._xor_unknown
		except:
			try:
				return logic(other)._xor_unknown
			except ValueError:
				return NotImplemented


logic.zero = tuple.__new__(logic_zero)
logic.one = tuple.__new__(logic_one)
logic.hi_z = tuple.__new__(logic_hi_z)
logic.unknown = tuple.__new__(logic_unknown)

logic.zero._init()
logic.one._init()
logic.hi_z._init()
logic.unknown._init()

from ._logvec import logvec
