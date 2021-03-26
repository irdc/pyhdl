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

class Signal:
	__slots__ = '_name', '_type', '_default'

	def __init__(self, name, type, default):
		self._name = name
		self._type = type
		self._default = default

	@property
	def type(self):
		if self._type is None:
			self._type = type(self._default)
		return self._type

	@property
	def default(self):
		if self._default is not None:
			return copy.deepcopy(self._default)
		return self._type()

	def get(self, obj):
		return getattr(obj, self._name)

	def set(self, obj, value):
		setattr(obj, self._name, value)


class Block:
	__slots__ = '__name__', '__qualname__', '_fun',

	def __init__(self, fun):
		self._fun = fun

	def __set_name__(self, owner, name):
		self.__name__ = name
		self.__qualname__ = owner.__name__ + '.' + name


class OnceBlock(Block):
	pass


class AlwaysBlock(Block):
	pass


class WhenBlock(Block):
	__slots__ = '_change', '_rising', '_falling', '_delay'

	def __init__(self, fun, *, change = None, rising = None, falling = None, delay = None):
		super().__init__(fun)
		self._change = self._parse_attr('change', change)
		self._rising = self._parse_attr('rising', rising)
		self._falling = self._parse_attr('falling', falling)
		self._delay = self._parse_timestamp('delay', delay)

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


class Part:
	__slots__ = '_type', '_signals', '_blocks'

	def __new__(self, type):
		try:
			return type.__part__
		except AttributeError:
			raise ValueError(f"{type!r}: not a part")

	@classmethod
	def new(cls, type, signals, blocks):
		"""Create a new Part instance."""

		part = object.__new__(cls)
		part._type = type
		part._signals = ReadOnlyDict(signals)
		part._blocks = tuple(blocks)
		type.__part__ = part
		return part

	@property
	def signals(self):
		return self._signals

	@property
	def blocks(self):
		return self._blocks


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

	# gather all signals
	defaults = {
		k: v
		for k, v in cls.__dict__.items()
		if not isdunder(k)
		and issignal(v)
	}
	types = {
		k: t
		for k, t in getattr(cls, '__annotations__', {}).items()
		if not isdunder(k)
		and issignaltype(t)
	}
	signals = {
		attr: Signal(
			attr,
			types.get(attr, None),
			defaults.get(attr, None))
		for attr in defaults.keys() | types.keys()
	}

	# set slots
	setattr(cls, '__slots__', tuple(signals.keys()))

	# gather all blocks
	blocks = tuple(
		v
		for k, v in cls.__dict__.items()
		if not isdunder(k)
		and isblock(v)
	)

	# create part
	Part.new(cls, signals, blocks)

	# hook __init__ to set all signals to their default upon instantiation
	fun = makefun(
		'__init__',
		('self', '*args', '**kwargs'),
		'\n'.join((
		'for signal in Part(type(self)).signals.values():',
		'\tsignal.set(self, signal.default)',
		'return orig_init(self, *args, **kwargs)'
		)),
		globals = sys.modules[cls.__module__].__dict__,
		locals = {'__class__': cls, 'Part': Part, 'orig_init': cls.__init__}
	)
	setattr(cls, fun.__name__, fun)

	# hook __setattr__ to perform type conversion
	fun = makefun(
		'__setattr__',
		('self', 'name', 'value'),
		'\n'.join((
		'try:',
		'\tattr_type = Part(type(self)).signals[name].type',
		'\tif type(value) is not attr_type:',
		'\t\tvalue = attr_type(value)',
		'except KeyError:',
		'\traise AttributeError(name)',
		'super().__setattr__(name, value)',
		)),
		globals = sys.modules[cls.__module__].__dict__,
		locals = {'__class__': cls, 'Part': Part})
	setattr(cls, fun.__name__, fun)

	return cls

@export
def once(fun):
	"""Make fun a block that's executed once."""

	return OnceBlock(fun)

@export
def always(fun):
	"""Make fun a block that's always executed."""

	return AlwaysBlock(fun)

@export
def when(change = None, rising = None, falling = None, delay = None):
	"""Make fun a block that's executed whenever any of the conditions are met.

	The change, rising and falling conditions each accept either the
	name of an attribute or an iterable of attribute names. If any of
	the given attributes change value, become 1 (for rising) or 0 (for
	falling) the block is executed.

	The delay condition specifies the interval time at which the block
	is to be repeatedly executed.
	"""

	def wrap(fun):
		return WhenBlock(
			fun,
			change = change,
			rising = rising,
			falling = falling,
			delay = delay
		)

	return wrap
