from typing import Iterator, Optional, Protocol, TypeVar

T = TypeVar("T", covariant=True)


class Peek(Protocol[T]):
    def peek(self) -> T:
        raise NotImplementedError()


class Peekable(Iterator[T], Peek[T]):
    def __init__(self, it: Iterator[T]) -> None:
        super().__init__()
        self.it = it
        self.v: Optional[T] = None

    def peek(self) -> T:
        if self.v is None:
            self.v = next(self.it)
        return self.v

    def __next__(self) -> T:
        v, self.v = self.v, None
        if v is None:
            v = next(self.it)
        return v


def iterator_length(it: Iterator) -> int:
    return sum(1 for _ in it)


# isort: list
__all__ = ["Peek", "Peekable", "iterator_length"]
