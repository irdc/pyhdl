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

from .._lib import make_async, timestamp
from ._wait import Wait

class Task:
	class Factory:
		__slots__ = '_sim', '_obj'

		def __init__(self, sim, obj):
			self._sim = sim
			self._obj = obj

		def once(self, fun):
			return OnceTask(self._sim, self._obj, fun)

		def always(self, fun):
			return AlwaysTask(self._sim, self._obj, fun)

		def when(self, fun, **conds):
			return WhenTask(self._sim, self._obj, fun, **conds)

	__slots__ = '_sim', '_obj', '_fun', '_coro', '_last_time', '_last_tick', '_wait'

	def __init__(self, sim, obj, fun):
		self._sim = sim
		self._obj = obj
		self._fun = make_async(fun)
		self._coro = None
		self._last_time = timestamp(-1)
		self._last_tick = -1
		self._wait = Wait.nowait()

	def is_changed(self, obj, attr, value = None):
		return self._sim.is_changed(self._last_tick, obj, attr, value)

	def is_elapsed(self, time):
		return self._sim.is_elapsed(self._last_time + time)

	@property
	def ready(self):
		return self._wait.ready(self) \
		if self._wait is not None else \
		False

	@property
	def until(self):
		return self._wait.until(self._last_time) \
		if self._wait is not None else \
		None

	def __part_getattr__(self, obj, attr, value):
		pass

	def __part_setattr__(self, obj, attr, value):
		pass

	async def _start(self):
		raise NotImplementedError

	def run(self, now, ticks):
		if self._coro is None:
			self._coro = self._start()

		try:
			self._wait = self._coro.send(None)
		except StopIteration:
			self._wait = None

		self._last_time = now
		self._last_tick = ticks


class OnceTask(Task):
	def __init__(self, sim, obj, fun):
		super().__init__(sim, obj, fun)

	async def _start(self):
		await self._fun(self._obj)


class AlwaysTask(Task):
	__slots__ = '_getattr',

	def __init__(self, sim, obj, fun):
		super().__init__(sim, obj, fun)
		self._getattr = set()

	def __part_getattr__(self, obj, attr, value):
		self._getattr.add((obj, attr))

	async def _start(self):
		while True:
			self._getattr.clear()
			await self._fun(self._obj)
			await Wait.any(*(Wait.change(o, a) for o, a in self._getattr))


class WhenTask(Task):
	__slots__ = '_cond',

	def __init__(self, sim, obj, fun, **conds):
		super().__init__(sim, obj, fun)

		waiters = []
		for cond, value in conds.items():
			if value is not None:
				if cond in ('change', 'rising', 'falling'):
					if type(value) is str:
						value = (value,)
					waiters.append(getattr(Wait, cond)(self._obj, *value))
				elif cond == 'delay':
					waiters.append(Wait.delay(value))
		self._cond = Wait.any(*waiters)
		self._wait = self._cond

	async def _start(self):
		while True:
			await self._fun(self._obj)
			await self._cond
