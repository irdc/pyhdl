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

import sys, re

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
	return scope['__makefun__'](**locals)

class ReadOnlyDict(dict):
	"""Read-only dictionary."""

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

	def __new__(self, value):
		if isinstance(value, timestamp):
			return value
		elif isinstance(value, str):
			match = re.match('^([0-9]+)([mu\u03bcnp]?s)$', value)
			if match is None:
				raise ValueError(f"{value!r}: not a valid timestamp")

			if match[2] == 's': scale = 10 ** 12
			elif match[2] == 'ms': scale = 10 ** 9
			elif match[2] == 'us' or match[2] == '\u03bcs': scale = 10 ** 6
			elif match[2] == 'ns': scale = 10 ** 3
			elif match[2] == 'ps': scale = 1

			value = int(match[1]) * scale
		elif type(value) is not int:
			raise ValueError(f"{value!r}: not a valid timestamp")

		return int.__new__(self, value)

	def __add__(self, other):
		return timestamp(super().__add__(other))

	def __str__(self):
		return f"{super().__str__()}ps"
