"""KNF: CNF extended with native AtLeastK cardinality constraints.

Format: J. Reeves, PhD thesis (CMU, 2025), section 2.2.5, as read by the
solver at https://github.com/jreeves3/Cardinality-CDCL.

    p knf <variables> <constraints>
    1 -2 3 0          clause
    k 2 1 3 -5 0      at least 2 of the literals are true
"""
from dataclasses import dataclass, field
from pathlib import Path
from typing import NamedTuple, Sequence


class AtLeast(NamedTuple):
    """At least ``bound`` of ``literals`` are true."""

    bound: int
    literals: list[int]


@dataclass
class KNF:
    clauses: list[list[int]] = field(default_factory=list)
    cardinalities: list[AtLeast] = field(default_factory=list)

    def add_clause(self, literals: Sequence[int]) -> None:
        self.clauses.append(list(literals))

    def add_at_least(self, literals: Sequence[int], bound: int) -> None:
        if bound > 0:  # otherwise it always holds
            self.cardinalities.append(AtLeast(bound, list(literals)))

    def add_at_most(self, literals: Sequence[int], bound: int) -> None:
        """KNF only has AtLeastK: at most k true is at least n - k false."""
        self.add_at_least([-literal for literal in literals],
                          len(literals) - bound)

    def to_file(self, path: Path, num_variables: int) -> None:
        num_constraints = len(self.clauses) + len(self.cardinalities)
        with path.open("w") as file:
            print(f"p knf {num_variables} {num_constraints}", file=file)
            for clause in self.clauses:
                print(*clause, 0, file=file)
            for bound, literals in self.cardinalities:
                print("k", bound, *literals, 0, file=file)
