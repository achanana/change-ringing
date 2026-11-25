"""Permutations of bell positions, as tuples.

``p[j]`` is the position that the bell at position ``j`` moves to (0-indexed).
"""
from typing import Iterable

Permutation = tuple[int, ...]


def identity(size: int) -> Permutation:
    return tuple(range(size))


def from_swaps(size: int, swaps: Iterable[tuple[int, int]]) -> Permutation:
    """Swap each given pair of positions; all other positions stay put."""
    perm = list(identity(size))
    for a, b in swaps:
        perm[a], perm[b] = b, a
    return tuple(perm)


def then(first: Permutation, second: Permutation) -> Permutation:
    """Apply ``first``, then ``second``."""
    return tuple(second[target] for target in first)
