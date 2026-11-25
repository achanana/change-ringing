"""The two leads (plain and bob) of Erin Triples on 7 bells.

A change ``p_i`` keeps bell position ``i`` (1-indexed) fixed and swaps the other
six positions in pairs. A lead is the changes p3 p1 p3 p1 p3, then one call
change: p7 for a plain lead, p5 for a bob.
"""
from functools import reduce

from .permutation import Permutation, from_swaps, identity, then

NUM_BELLS = 7
SUFFIX_LENGTH = 4  # the back bells that identify a clump
FIRST_SUFFIX_POSITION = NUM_BELLS - SUFFIX_LENGTH  # 0-indexed

LEAD_PREFIX_CHANGES = (3, 1, 3, 1, 3)
PLAIN_CALL = 7
BOB_CALL = 5


def change(fixed_position: int) -> Permutation:
    """p_i: keep position ``i`` (1-indexed) fixed, swap the rest in pairs."""
    others = [pos for pos in range(NUM_BELLS) if pos != fixed_position - 1]
    return from_swaps(NUM_BELLS, zip(others[::2], others[1::2]))


def lead(call: int) -> Permutation:
    """The whole lead ending in change ``p_call``, as one permutation."""
    changes = [change(i) for i in (*LEAD_PREFIX_CHANGES, call)]
    return reduce(then, changes, identity(NUM_BELLS))


# Indexed by call: 0 is a plain lead, 1 is a bob lead.
LEAD_PERMUTATIONS = (lead(PLAIN_CALL), lead(BOB_CALL))
