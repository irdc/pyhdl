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

@export
class Sim:
	__slots__ = '_now', '_ticks', '_setattr', '_tasks', '_current_task'

	def __init__(self, root):
		self._now = timestamp(0)
		self._ticks = 0
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
		self._setattr[(obj, attr)] = self._ticks

	def is_changed(self, since, obj, attr, value = None):
		if self._setattr.get((obj, attr), -1) <= since:
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
						task.run(self._now, self._ticks)

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

				self._ticks += 1
