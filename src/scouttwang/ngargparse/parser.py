from types import SimpleNamespace
from typing import Optional, Sequence, Tuple


class NgArgumentParser:
    def add_argument(self):
        """dispatcher method"""

    def add_bool_arguments(self):
        pass

    def parse_args(self, args: Optional[Sequence[str]] = None) -> SimpleNamespace:
        sn, _ = self.parser_known_args(args)
        return sn

    def parser_known_args(self, args: Optional[Sequence[str]] = None) -> Tuple[SimpleNamespace, Sequence[str]]:
        return SimpleNamespace(), []
