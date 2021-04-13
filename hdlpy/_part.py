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

import sys, copy, threading, contextlib, types, typing, inspect
from ._lib import export, makefun, ReadOnlyDict, timestamp, join

class Signal:
	__slots__ = '_name', '_type', '_default'

	def __init__(self, name, ty, default):
		self._name = name
		self._type = ty
		self._default = ty(default) \
			if isinstance(ty, type) \
			and type(default) is not ty \
			and default is not None else \
			default

	@property
	def name(self):
		return self._name

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


class Block:
	__slots__ = '__name__', '__qualname__', '_fun',

	def __init__(self, fun):
		self._fun = fun

	def __set_name__(self, owner, name):
		self.__name__ = name
		self.__qualname__ = owner.__name__ + '.' + name

	def apply(self, target):
		raise NotImplementedError


class OnceBlock(Block):
	def apply(self, target):
		return target.once(self._fun)


class AlwaysBlock(Block):
	def apply(self, target):
		return target.always(self._fun)


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

	def apply(self, target):
		return target.when(
			self._fun,
			change = self._change,
			rising = self._rising,
			falling = self._falling,
			delay = self._delay)


class PartMeta(type):
	_observer = threading.local()

	@property
	def current_observer(self):
		return getattr(self._observer, 'current', None)

	@contextlib.contextmanager
	def make_current_observer(self, sim):
		old = getattr(self._observer, 'current', None)
		self._observer.current = sim
		yield
		self._observer.current = old


class Part(metaclass = PartMeta):
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

	def parts(self, obj):
		"""Get all direct child parts."""

		for signal in self.signals.values():
			value = getattr(obj, signal.name)
			try:
				Part(type(value))
				yield value
			except ValueError:
				pass

	def all_parts(self, obj):
		"""Get all parts from the entire subtree."""

		yield obj
		for part in self.parts(obj):
			yield from Part(type(part)).all_parts(part)


class FunctionPart:
	__slots__ = '__qualname__', '__name__', '_fun',

	def __init__(self, fun):
		self._fun = fun
		self.__name__ = fun.__name__
		self.__qualname__ = f"{fun.__module__}.{fun.__name__}"

	def __call__(self, *args, **kwargs):
		return self._fun(*args, **kwargs)

	def __getitem__(self, index):
		if type(index) is tuple:
			return self._fun(*index)
		return self._fun(index)

	def __repr__(self):
		return "<function part '{self.__qualname__}'>"

	def __set_name__(self, obj, name):
		self.__name__ = name
		self.__qualname__ = f"{obj.__name__}.{name}"


@export
def part(obj = None):
	"""Make obj a part."""

	def isdunder(name):
		return name.startswith('__') and name.endswith('__')

	def issignaltype(ty):
		return ty is not typing.Final \
		and typing.get_origin(ty) is not typing.Final \
		and not (type(ty) is type and issubclass(ty, Block))

	def issignal(value):
		return issignaltype(type(value)) \
		   and not hasattr(value, '__get__') \
		   and not callable(value)

	def isblock(value):
		return isinstance(value, Block)

	def make_type_part(cls):
		annotations = getattr(cls, '__annotations__', {})
		attrs = cls.__dict__

		# gather all signals
		signals = {
			attr: signal
			for attr, signal
			in join(
				annotations.items(),
				((k, v) for k, v in attrs.items() if issignal(v)),
				key = lambda x: x[0],
				select = lambda x: x[1],
				combine = Signal)
			if not isdunder(attr)
			and issignaltype(signal.type)
			and issignal(signal.default)
		}

		# remove attributes that have been turned into signals from
		# the class dict
		for attr in signals.keys():
			if hasattr(cls, attr):
				delattr(cls, attr)

		# set slots
		setattr(cls, '__slots__', tuple(signals.keys()))

		# gather all blocks
		blocks = tuple(
			v
			for k, v in attrs.items()
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
			'\tsuper().__setattr__(signal.name, signal.default)',
			'return orig_init(self, *args, **kwargs)'
			)),
			globals = sys.modules[cls.__module__].__dict__,
			locals = {'__class__': cls, 'Part': Part, 'orig_init': cls.__init__}
		)
		setattr(cls, fun.__name__, fun)

		# hook __getattribute__ to wire in our observer
		fun = makefun(
			'__getattribute__',
			('self', 'name'),
			'\n'.join((
			'value = super().__getattribute__(name)',
			'if (observer := Part.current_observer) is not None:',
			'\tobserver.__part_getattr__(self, name, value)',
			'return value'
			)),
			globals = sys.modules[cls.__module__].__dict__,
			locals = {'__class__': cls, 'Part': Part})
		setattr(cls, fun.__name__, fun)

		# hook __setattr__ to perform type conversion and wire in our observer
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
			'if super().__getattribute__(name) != value:',
			'\tif (observer := Part.current_observer) is not None:',
			'\t\tobserver.__part_setattr__(self, name, value)',
			'\tsuper().__setattr__(name, value)',
			)),
			globals = sys.modules[cls.__module__].__dict__,
			locals = {'__class__': cls, 'Part': Part})
		setattr(cls, fun.__name__, fun)

		return cls

	def make_fun_part(fun):
		return FunctionPart(fun)

	def make_frame_part():
		frame = inspect.currentframe()
		try:
			caller = frame.f_back.f_back

			# generate class name based on function arguments
			arg_info = inspect.getargvalues(caller)
			name = inspect.getframeinfo(caller).function + '[' + \
				inspect.formatargvalues(*arg_info)[1:-2] + ']'

			# determine class attributes, adding arguments as
			# Final so they appear on the class instead of on
			# the instance and won't be able to be modified
			attrs = dict(caller.f_locals)
			attrs['__module__'] = caller.f_globals.get('__name__', '__main__')
			attrs['__annotations__'] = {arg: typing.Final[type(arg)] for arg in arg_info.args}

			# create the class
			cls = type(name, (), attrs)
			for attr, value in attrs.items():
				if hasattr(value, '__set_name__'):
					value.__set_name__(cls, attr)

			# turn it into a part
			return make_type_part(cls)
		finally:
			del frame

	if type(obj) is type:
		return make_type_part(obj)
	elif callable(obj):
		return make_fun_part(obj)
	else:
		return make_frame_part()

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
