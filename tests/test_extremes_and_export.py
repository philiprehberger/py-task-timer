"""Tests for slowest(), fastest(), and export_json()."""

from __future__ import annotations

import json
import time
from pathlib import Path

from philiprehberger_task_timer import TaskTimer


def test_slowest_and_fastest_return_extreme_tasks() -> None:
    timer = TaskTimer()
    with timer.task("fast"):
        time.sleep(0.01)
    with timer.task("slow"):
        time.sleep(0.05)

    slowest = timer.slowest()
    fastest = timer.fastest()

    assert slowest is not None
    assert fastest is not None
    assert slowest[0] == "slow"
    assert fastest[0] == "fast"
    assert slowest[1] == timer.as_dict()["slow"]
    assert fastest[1] == timer.as_dict()["fast"]
    assert slowest[1] > fastest[1]


def test_slowest_and_fastest_return_none_when_empty() -> None:
    timer = TaskTimer()
    assert timer.slowest() is None
    assert timer.fastest() is None


def test_export_json_writes_summary(tmp_path: Path) -> None:
    timer = TaskTimer()
    with timer.task("work"):
        time.sleep(0.01)

    out = tmp_path / "out.json"
    timer.export_json(out)

    assert out.exists()
    loaded = json.loads(out.read_text(encoding="utf-8"))
    assert loaded == timer.as_dict()


def test_export_json_creates_parent_directories(tmp_path: Path) -> None:
    timer = TaskTimer()
    with timer.task("work"):
        time.sleep(0.01)

    out = tmp_path / "nested" / "sub" / "out.json"
    timer.export_json(out)

    assert out.exists()
    loaded = json.loads(out.read_text(encoding="utf-8"))
    assert loaded == timer.as_dict()
