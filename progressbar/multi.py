from __future__ import annotations
import enum
import io
import itertools
import operator
import sys
import threading
import time
import timeit
import typing
from datetime import timedelta
import python_utils
from . import bar, terminal
from .terminal import stream
SortKeyFunc = typing.Callable[[bar.ProgressBar], typing.Any]

class SortKey(str, enum.Enum):
    """
    Sort keys for the MultiBar.

    This is a string enum, so you can use any
    progressbar attribute or property as a sort key.

    Note that the multibar defaults to lazily rendering only the changed
    progressbars. This means that sorting by dynamic attributes such as
    `value` might result in more rendering which can have a small performance
    impact.
    """
    CREATED = 'index'
    LABEL = 'label'
    VALUE = 'value'
    PERCENTAGE = 'percentage'

class MultiBar(typing.Dict[str, bar.ProgressBar]):
    fd: typing.TextIO
    _buffer: io.StringIO
    label_format: str
    prepend_label: bool
    append_label: bool
    initial_format: str | None
    finished_format: str | None
    update_interval: float
    remove_finished: float | None
    progressbar_kwargs: dict[str, typing.Any]
    sort_keyfunc: SortKeyFunc
    _previous_output: list[str]
    _finished_at: dict[bar.ProgressBar, float]
    _labeled: set[bar.ProgressBar]
    _print_lock: threading.RLock = threading.RLock()
    _thread: threading.Thread | None = None
    _thread_finished: threading.Event = threading.Event()
    _thread_closed: threading.Event = threading.Event()

    def __init__(self, bars: typing.Iterable[tuple[str, bar.ProgressBar]] | None=None, fd: typing.TextIO=sys.stderr, prepend_label: bool=True, append_label: bool=False, label_format='{label:20.20} ', initial_format: str | None='{label:20.20} Not yet started', finished_format: str | None=None, update_interval: float=1 / 60.0, show_initial: bool=True, show_finished: bool=True, remove_finished: timedelta | float=timedelta(seconds=3600), sort_key: str | SortKey=SortKey.CREATED, sort_reverse: bool=True, sort_keyfunc: SortKeyFunc | None=None, **progressbar_kwargs):
        self.fd = fd
        self.prepend_label = prepend_label
        self.append_label = append_label
        self.label_format = label_format
        self.initial_format = initial_format
        self.finished_format = finished_format
        self.update_interval = update_interval
        self.show_initial = show_initial
        self.show_finished = show_finished
        self.remove_finished = python_utils.delta_to_seconds_or_none(remove_finished)
        self.progressbar_kwargs = progressbar_kwargs
        if sort_keyfunc is None:
            sort_keyfunc = operator.attrgetter(sort_key)
        self.sort_keyfunc = sort_keyfunc
        self.sort_reverse = sort_reverse
        self._labeled = set()
        self._finished_at = {}
        self._previous_output = []
        self._buffer = io.StringIO()
        super().__init__(bars or {})

    def __setitem__(self, key: str, bar: bar.ProgressBar):
        """Add a progressbar to the multibar."""
        if bar.label != key or not key:
            bar.label = key
            bar.fd = stream.LastLineStream(self.fd)
            bar.paused = True
            bar.print = self.print
        if bar.index == -1:
            bar.index = next(bar._index_counter)
        super().__setitem__(key, bar)

    def __delitem__(self, key):
        """Remove a progressbar from the multibar."""
        super().__delitem__(key)
        self._finished_at.pop(key, None)
        self._labeled.discard(key)

    def __getitem__(self, key):
        """Get (and create if needed) a progressbar from the multibar."""
        try:
            return super().__getitem__(key)
        except KeyError:
            progress = bar.ProgressBar(**self.progressbar_kwargs)
            self[key] = progress
            return progress

    def render(self, flush: bool=True, force: bool=False):
        """Render the multibar to the given stream."""
        pass

    def print(self, *args, end='\n', offset=None, flush=True, clear=True, **kwargs):
        """
        Print to the progressbar stream without overwriting the progressbars.

        Args:
            end: The string to append to the end of the output
            offset: The number of lines to offset the output by. If None, the
                output will be printed above the progressbars
            flush: Whether to flush the output to the stream
            clear: If True, the line will be cleared before printing.
            **kwargs: Additional keyword arguments to pass to print
        """
        pass

    def run(self, join=True):
        """
        Start the multibar render loop and run the progressbars until they
        have force _thread_finished.
        """
        pass

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.join()