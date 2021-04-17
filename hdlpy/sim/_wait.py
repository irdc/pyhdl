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

from .. import logic
from .._lib import export, timestamp

@export
class Wait:
	def __await__(self):
		return (yield self)

	def ready(self, task):
		raise NotImplementedError

	def until(self, last):
		return None

	@staticmethod
	def nowait():
		return WaitNowait()

	@staticmethod
	def any(*inner):
		if len(inner) == 1:
			return inner[0]
		return WaitAny(inner)

	@staticmethod
	def all(*inner):
		if len(inner) == 1:
			return inner[0]
		return WaitAll(inner)

	@staticmethod
	def change(obj, *attrs):
		return WaitChange(obj, attrs)

	@staticmethod
	def rising(obj, *attrs):
		return WaitRising(obj, attrs)

	@staticmethod
	def falling(obj, *attrs):
		return WaitFalling(obj, attrs)

	@staticmethod
	def delay(time):
		return WaitDelay(timestamp(time))


class WaitNowait(Wait):
	_instance = None

	def __new__(self):
		if WaitNowait._instance is None:
			WaitNowait._instance = object.__new__(WaitNowait)
		return WaitNowait._instance

	def ready(self, task):
		return True


class WaitMulti(Wait):
	__slots__ = '_inner',

	def __init__(self, inner):
		self._inner = tuple(inner)

	def until(self, last):
		until = None
		for wait in self._inner:
			inner_until = wait.until(last)
			if inner_until is not None \
			and inner_until < until:
				until = inner_until
		return until


class WaitAll(WaitMulti):
	def ready(self, task):
		return all(wait.ready(task) for wait in self._inner)


class WaitAny(WaitMulti):
	def ready(self, task):
		return any(wait.ready(task) for wait in self._inner)


class WaitChange(Wait):
	__slots__ = '_obj', '_attrs'

	def __init__(self, obj, attrs):
		self._obj = obj
		self._attrs = tuple(attrs)

	def ready(self, task):
		return any(
			task.is_changed(self._obj, attr)
			for attr in self._attrs)


class WaitRising(WaitChange):
	def ready(self, task):
		return any(
			task.is_changed(self._obj, attr, logic.one)
			for attr in self._attrs)


class WaitFalling(WaitChange):
	def ready(self, task):
		return any(
			task.is_changed(self._obj, attr, logic.zero)
			for attr in self._attrs)


class WaitDelay(Wait):
	__slots__ = '_time',

	def __init__(self, time):
		self._time = time

	def ready(self, task):
		return task.is_elapsed(self._time)

	def until(self, last):
		return self._time + last
