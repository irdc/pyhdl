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

from enum import Enum, EnumMeta

from ._lib import export

class _LogicEnumMeta(EnumMeta):
	def __call__(cls, value = 'X'):
		if type(value) is cls:
			return value

		if type(value) is bool:
			return cls.zero if value == False else cls.one

		if type(value) is int:
			if value == 0:
				return cls.zero
			elif value == 1:
				return cls.one

		if type(value) is str:
			if value == '0':
				return cls.zero
			elif value == '1':
				return cls.one
			elif value == 'Z':
				return cls.hi_z
			elif value == 'X':
				return cls.unknown

		raise ValueError(f"{value!r}: not a valid logic value")

@export
class logic(str, Enum, metaclass = _LogicEnumMeta):
	"""Represents a logic signal and implements multi-value logic.

	Value can be any of:
		'0' or 0: a logical zero
		'1' or 1: a logical one
		'Z': an high-impedance signal
		'X': an unknown signal
	"""

	zero = '0'
	one = '1'
	hi_z = 'Z'
	unknown = 'X'

	def __repr__(self):
		return f"<logic '{self!s}'>"

	def __str__(self):
		return self._value_

	def __format__(self, fmt):
		if fmt != '':
			raise ValueError(fmt)
		return str(self)

	def __eq__(self, other):
		try:
			return (type(other) is str and other == '-') or self is logic(other)
		except ValueError:
			return NotImplemented

	def __ne__(self, other):
		try:
			return not ((type(other) is str and other == '-') or self is logic(other))
		except ValueError:
			return NotImplemented

	def _cmp(self, other):
		try:
			return ord(self._value_) - ord(other._value_)
		except AttributeError:
			return NotImplemented

	def __lt__(self, other):
		cmp = self._cmp(other)
		return NotImplemented if cmp is NotImplemented else cmp < 0

	def __le__(self, other):
		cmp = self._cmp(other)
		return NotImplemented if cmp is NotImplemented else cmp <= 0

	def __gt__(self, other):
		cmp = self._cmp(other)
		return NotImplemented if cmp is NotImplemented else cmp > 0

	def __ge__(self, other):
		cmp = self._cmp(other)
		return NotImplemented if cmp is NotImplemented else cmp >= 0

	def __bool__(self):
		"""self is logic.one"""

		return self is logic.one

	def __invert__(self):
		"""~self -> result

		self result
		---- ------
		 0     1
		 1     0
		 Z     X
		 X     X
		"""

		if self is logic.zero: return logic.one
		if self is logic.one: return logic.zero

		return logic.unknown

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

		try:
			other = logic(other)
			if self is logic.one and other is logic.one: return logic.one
			if self is logic.zero or other is logic.zero: return logic.zero

			return logic.unknown
		except ValueError:
			return NotImplemented

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

		try:
			other = logic(other)
			if self is logic.zero and other is logic.zero: return logic.zero
			if self is logic.one or other is logic.one: return logic.one

			return logic.unknown
		except ValueError:
			return NotImplemented

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

		try:
			other = logic(other)
			if self is logic.zero:
				if other is logic.one: return logic.one
				if other is logic.zero: return logic.zero
			if self is logic.one:
				if other is logic.one: return logic.zero
				if other is logic.zero: return logic.one

			return logic.unknown
		except ValueError:
			return NotImplemented
