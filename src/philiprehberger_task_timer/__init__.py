"""Named timers for measuring multiple operations within a function or script."""

from __future__ import annotations

import sys
import time
from contextlib import asynccontextmanager, contextmanager
from typing import IO, Any, Generator

__all__ = ["TaskTimer"]


class TaskContext:
    """Internal context manager for timing a single task."""

    def __init__(self, timer: TaskTimer, name: str) -> None:
        self._timer = timer
        self._name = name
        self._start: float = 0.0

    def __enter__(self) -> TaskContext:
        self._start = time.perf_counter()
        self._timer._stack.append(self._name)
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        elapsed = time.perf_counter() - self._start
        key = "/".join(self._timer._stack)
        self._timer._tasks[key] = self._timer._tasks.get(key, 0.0) + elapsed
        self._timer._stack.pop()

    async def __aenter__(self) -> TaskContext:
        return self.__enter__()

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self.__exit__(exc_type, exc_val, exc_tb)


class TaskTimer:
    """Named timers for measuring multiple operations within a function or script.

    Usage::

        t = TaskTimer()
        with t.task("load data"):
            data = load()
        with t.task("process"):
            process(data)
        t.summary()
    """

    def __init__(self) -> None:
        self._tasks: dict[str, float] = {}
        self._stack: list[str] = []
        self._lap_time: float = time.perf_counter()

    def task(self, name: str) -> TaskContext:
        """Return a context manager that times the enclosed block.

        Supports both sync (``with``) and async (``async with``) usage.
        Tasks can be nested; nested tasks appear indented in the summary.
        """
        return TaskContext(self, name)

    def lap(self, name: str) -> None:
        """Record a lap (time since the last lap or timer creation)."""
        now = time.perf_counter()
        elapsed = now - self._lap_time
        self._lap_time = now
        if self._stack:
            key = "/".join(self._stack) + "/" + name
        else:
            key = name
        self._tasks[key] = self._tasks.get(key, 0.0) + elapsed

    def summary(self, *, file: IO[str] = sys.stdout) -> None:
        """Print a formatted summary table with name, duration, and percentage.

        Each line has the format::

            name    1.23s  (41%)

        Nested tasks are indented with two spaces per level.
        """
        total = self.total
        if total == 0.0:
            return
        name_width = max(
            (len(k.split("/")[-1]) + 2 * (k.count("/")) for k in self._tasks),
            default=0,
        )
        for key, elapsed in self._tasks.items():
            parts = key.split("/")
            depth = len(parts) - 1
            label = "  " * depth + parts[-1]
            pct = (elapsed / total) * 100
            print(f"{label:<{name_width}}    {elapsed:.2f}s  ({pct:.0f}%)", file=file)

    def as_dict(self) -> dict[str, float]:
        """Return a dict mapping task names to elapsed seconds.

        Nested task keys use ``/`` as a separator (e.g. ``"outer/inner"``).
        """
        return dict(self._tasks)

    @property
    def total(self) -> float:
        """Total time across all recorded tasks, in seconds."""
        return sum(self._tasks.values())

    def reset(self) -> None:
        """Clear all recorded tasks and reset the lap timer."""
        self._tasks.clear()
        self._stack.clear()
        self._lap_time = time.perf_counter()
