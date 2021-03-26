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

import contextlib

from .._lib import export, timestamp
from .._part import Part
from ._task import Task

class sequence(tuple):
	def __new__(self, ts, num):
		return tuple.__new__(self, (timestamp(ts), num))

	@property
	def timestamp(self):
		return self[0]

	@property
	def number(self):
		return self[1]

	def __add__(self, other):
		if type(other) is sequence:
			return sequence(self.timestamp + other.timestamp, self.number + other.number)
		else:
			try:
				return sequence(self.timestamp + other, 0)
			except:
				return NotImplemented

	def __radd__(self, other):
		return self.__add__(other)

	def __eq__(self, other):
		if type(self) is type(other):
			return super().__eq__(other)
		return self.timestamp == other

	def __lt__(self, other):
		if type(self) is type(other):
			return super().__lt__(other)
		return self.timestamp < other

	def __le__(self, other):
		if type(self) is type(other):
			return super().__le__(other)
		return self.timestamp <= other

	def __gt__(self, other):
		if type(self) is type(other):
			return super().__gt__(other)
		return self.timestamp > other

	def __ge__(self, other):
		if type(self) is type(other):
			return super().__ge__(other)
		return self.timestamp >= other

@export
class Sim:
	__slots__ = '_now', '_setattr', '_tasks', '_current_task'

	def __init__(self, root):
		self._now = sequence(timestamp(0), 0)
		self._setattr = {}

		tasks = []
		for part in Part(type(root)).all_parts(root):
			factory = Task.Factory(self, part)
			for block in Part(type(part)).blocks:
				tasks.append(block.apply(factory))
		self._tasks = tuple(tasks)
		self._current_task = None

	@contextlib.contextmanager
	def _make_current_task(self, task):
		old = self._current_task
		self._current_task = task
		yield
		self._current_task = old

	def __part_getattr__(self, obj, attr, value):
		if self._current_task is not None:
			self._current_task.__part_getattr__(obj, attr, value)

	def __part_setattr__(self, obj, attr, value):
		if self._current_task is not None:
			self._current_task.__part_setattr__(obj, attr, value)
		self._setattr[(obj, attr)] = self._now

	def is_changed(self, since, obj, attr, value = None):
		if self._setattr.get((obj, attr), sequence(-1, 0)) <= since:
			return False
		if value is not None:
			return getattr(obj, attr) == value
		return True

	def is_elapsed(self, time):
		return self._now >= time

	def run(self):
		with Part.make_current_observer(self):
			while True:
				# run ready tasks
				ready = [t for t in self._tasks if t.ready]
				for task in ready:
					with self._make_current_task(task):
						task.run(self._now)
					self._now += sequence(0, 1)

				# if no tasks were ready, determine the
				# earliest moment a new task will become
				# ready
				if len(ready) == 0:
					next_time = None
					for task in self._tasks:
						until = task.until
						if until is not None \
						and (next_time is None or until < next_time):
							next_time = until

					if next_time is None:
						# no more tasks will become ready
						break

					self._now = next_time
