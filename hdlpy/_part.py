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

import sys, copy
from ._lib import export, makefun, ReadOnlyDict, timestamp

_DEFAULTS = '__part_defaults__'
_TYPES = '__part_types__'
_BLOCKS = '__part_blocks__'

@export
def part(cls):
	"""Make cls a part."""

	def isdunder(name):
		return name.startswith('__') and name.endswith('__')

	def issignaltype(type):
		return not issubclass(type, Block)

	def issignal(value):
		return issignaltype(type(value)) \
		   and not hasattr(value, '__get__') \
		   and not hasattr(value, '__part_defaults__') \
		   and not callable(value)

	def isblock(value):
		return isinstance(value, Block)

	# gather all defaults
	defaults = {
		k: v
		for k, v in cls.__dict__.items()
		if not isdunder(k)
		and issignal(v)
	}

	# gather all types
	types = {
		k: t
		for k, t in getattr(cls, '__annotations__', {}).items()
		if not isdunder(k)
		and issignaltype(t)
	}

	# gather all blocks
	blocks = tuple(
		v
		for k, v in cls.__dict__.items()
		if not isdunder(k)
		and isblock(v)
	)

	# combine
	setattr(cls, _DEFAULTS, ReadOnlyDict({k: t() for k, t in types.items()} | defaults))
	setattr(cls, _TYPES, ReadOnlyDict({k: type(v) for k, v in defaults.items()} | types))
	setattr(cls, _BLOCKS, blocks)

	# add attribute getters and setters
	fun = makefun(
		'__getattribute__',
		('self', 'name'),
		'\n'.join((
		'try:',
		'\treturn super().__getattribute__(name)',
		'except AttributeError:',
		'\ttry:',
		f'\t\tvalue = copy.deepcopy(self.{_DEFAULTS}[name])',
		'\t\tsetattr(self, name, value)',
		'\t\treturn value',
		'\texcept KeyError:',
		'\t\traise AttributeError(name)',
		)),
		globals = sys.modules[cls.__module__].__dict__,
		locals = {'__class__': cls, 'copy': copy})
	setattr(cls, fun.__name__, fun)

	fun = makefun(
		'__setattr__',
		('self', 'name', 'value'),
		f'super().__setattr__(name, self.{_TYPES}.get(name, lambda x: x)(value))',
		globals = sys.modules[cls.__module__].__dict__,
		locals = {'__class__': cls})
	setattr(cls, fun.__name__, fun)

	return cls


class Block:
	__slots__ = '__name__', '__qualname__', '_fun',

	def __init__(self, fun):
		self._fun = fun

	def __set_name__(self, owner, name):
		self.__name__ = name
		self.__qualname__ = owner.__name__ + '.' + name


class AlwaysBlock(Block):
	pass


class WhenBlock(Block):
	__slots__ = '_change', '_rising', '_falling', '_interval'

	def __init__(self, fun, *, change = None, rising = None, falling = None, interval = None):
		super().__init__(fun)
		self._change = self._parse_attr('change', change)
		self._rising = self._parse_attr('rising', rising)
		self._falling = self._parse_attr('falling', falling)
		self._interval = self._parse_timestamp('interval', interval)

	@classmethod
	def _parse_attr(cls, name, value):
		if value is None:
			return value
		elif type(value) is str:
			if value.isidentifier():
				return value
		elif not isinstance(value, dict):
			try:
				if all(map(lambda x: type(x) is str and x.isidentifier(), value)):
					return tuple(value)
			except TypeError:
				pass

		raise ValueError(f"{name}={value!r}: not an attribute or an iterable thereof")

	@classmethod
	def _parse_timestamp(cls, name, value):
		if value is None:
			return value

		return timestamp(value)


@export
def always(fun):
	"""Make fun a block that's always executed."""

	return AlwaysBlock(fun)

@export
def when(change = None, rising = None, falling = None, interval = None):
	"""Make fun a block that's executed whenever any of the conditions are met.

	The change, rising and falling conditions each accept either the
	name of an attribute or an iterable of attribute names. If any of
	the given attributes change value, become 1 (for rising) or 0 (for
	falling) the block is executed.

	The interval condition specifies the interval time at which the
	block is to be repeatedly executed.
	"""

	def wrap(fun):
		return WhenBlock(
			fun,
			change = change,
			rising = rising,
			falling = falling,
			interval = interval
		)

	return wrap
