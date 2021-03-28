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

import sys, re, asyncio, functools

def export(obj):
	"""Export obj from its module (ie. add its name to __all__)."""

	mod = sys.modules[obj.__module__]
	mod.__all__ = getattr(mod, '__all__', ()) + (obj.__name__,)
	return obj

def makefun(name, args, body, *, globals = None, locals = None):
	"""Make a new function."""

	if locals is None:
		locals = {}
	body = body.replace('\n', '\n\t\t')
	src = f"""
def __makefun__({', '.join(locals.keys())}):
	def {name}({', '.join(args)}):
		{body}
	return {name}
"""
	scope = {}
	exec(src, globals, scope)
	fun = scope['__makefun__'](**locals)
	if (cls := locals.get('__class__', None)) is not None:
		fun.__qualname__ = f"{cls.__name__}.{name}"
	return fun

def isasync(fun):
	"""Return if fun is async."""

	return asyncio.iscoroutinefunction(fun)

def make_async(fun):
	"""Make fun async."""

	async def sync(*args, **kwargs):
		return fun(*args, **kwargs)

	return fun if isasync(fun) else sync

class ReadOnlyDict(dict):
	"""Read-only dictionary."""

	def __new__(cls, value):
		if type(value) is ReadOnlyDict:
			return value
		return super().__new__(cls, value)

	def _readonly(self, *args, **kwargs):
		raise RuntimeError('Read-only dictionary')

	__setitem__ = _readonly
	__delitem__ = _readonly
	pop = _readonly
	popitem = _readonly
	clear = _readonly
	update = _readonly
	setdefault = _readonly

	del _readonly


class timestamp(int):
	"""Timestamp with picosecond resolution."""

	_units = ReadOnlyDict({
		'd': 24 * 3600 * 10 ** 12,
		'h': 3600 * 10 ** 12,
		'm': 60 * 10 ** 12,
		's': 10 ** 12,
		'ms': 10 ** 9,
		'\u03bcs': 10 ** 6,
		'us': 10 ** 6,
		'ns': 10 ** 3,
		'ps': 1
	})

	def __new__(self, value):
		if type(value) is timestamp:
			return value
		elif isinstance(value, str):
			match = re.match('^([0-9_]+) ?([mu\u03bcnp]?s|[mhd])$', value)
			if match is None:
				raise ValueError(f"{value!r}: not a valid timestamp")

			value = int(match[1]) * self._units[match[2]]
		elif type(value) is not int:
			raise ValueError(f"{value!r}: not a valid timestamp")

		return int.__new__(self, value)

	def __add__(self, other):
		if type(other) is int or type(other) is timestamp:
			return timestamp(super().__add__(other))
		return NotImplemented

	def __repr__(self):
		return f"<timestamp: {self!s}>"

	def __str__(self):
		for k, v in self._units.items():
			if self % v == 0:
				return f"{self // v} {k}"
