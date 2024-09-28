from __future__ import annotations
import sys
import typing
from types import TracebackType
from typing import Iterable, Iterator
from progressbar import base

class TextIOOutputWrapper(base.TextIO):

    def __init__(self, stream: base.TextIO):
        self.stream = stream

    def __next__(self) -> str:
        return self.stream.__next__()

    def __iter__(self) -> Iterator[str]:
        return self.stream.__iter__()

    def __exit__(self, __t: type[BaseException] | None, __value: BaseException | None, __traceback: TracebackType | None) -> None:
        return self.stream.__exit__(__t, __value, __traceback)

    def __enter__(self) -> base.TextIO:
        return self.stream.__enter__()

class LineOffsetStreamWrapper(TextIOOutputWrapper):
    UP = '\x1b[F'
    DOWN = '\x1b[B'

    def __init__(self, lines=0, stream=sys.stderr):
        self.lines = lines
        super().__init__(stream)

class LastLineStream(TextIOOutputWrapper):
    line: str = ''

    def __iter__(self) -> typing.Generator[str, typing.Any, typing.Any]:
        yield self.line