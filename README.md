# philiprehberger-task-timer

[![Tests](https://github.com/philiprehberger/py-task-timer/actions/workflows/publish.yml/badge.svg)](https://github.com/philiprehberger/py-task-timer/actions/workflows/publish.yml)
[![PyPI version](https://img.shields.io/pypi/v/philiprehberger-task-timer.svg)](https://pypi.org/project/philiprehberger-task-timer/)
[![License](https://img.shields.io/github/license/philiprehberger/py-task-timer)](LICENSE)

Named timers for measuring multiple operations within a function or script.

## Install

```bash
pip install philiprehberger-task-timer
```

## Usage

```python
from philiprehberger_task_timer import TaskTimer

t = TaskTimer()

with t.task("load data"):
    data = load_from_disk()

with t.task("process"):
    result = process(data)

with t.task("save"):
    save(result)

t.summary()
```

Output:

```
load data    0.52s  (26%)
process      1.23s  (62%)
save         0.24s  (12%)
```

### Nested tasks

Tasks can be nested. Nested tasks appear indented in the summary output.

```python
t = TaskTimer()

with t.task("pipeline"):
    with t.task("step 1"):
        do_step_1()
    with t.task("step 2"):
        do_step_2()

t.summary()
```

Output:

```
pipeline      2.05s  (100%)
  step 1      0.80s  (39%)
  step 2      1.25s  (61%)
```

### Laps

Use `lap()` to record incremental time without context managers.

```python
t = TaskTimer()
load()
t.lap("load")
process()
t.lap("process")
t.summary()
```

### as_dict

Retrieve raw timing data as a dictionary.

```python
t = TaskTimer()
with t.task("work"):
    do_work()

print(t.as_dict())  # {"work": 1.234}
```

### Async support

The `task()` context manager works with `async with` as well.

```python
t = TaskTimer()
async with t.task("fetch"):
    await fetch_data()
t.summary()
```

## API

| Method / Property | Description |
|-------------------|-------------|
| `task(name)` | Context manager that times the enclosed block (sync and async) |
| `lap(name)` | Record time since the last lap or timer creation |
| `summary(*, file=sys.stdout)` | Print formatted summary with name, duration, and percentage |
| `as_dict()` | Return `dict[str, float]` of task name to seconds |
| `total` | Property returning the total time across all tasks |
| `reset()` | Clear all recorded tasks |


## Development

```bash
pip install -e .
python -m pytest tests/ -v
```

## License

MIT
