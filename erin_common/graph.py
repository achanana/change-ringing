"""The lead graph: rows a lead can start from, and the clumps they belong to."""
from collections import deque

from .leads import FIRST_SUFFIX_POSITION, LEAD_PERMUTATIONS, NUM_BELLS
from .permutation import Permutation, identity, then

START_STATE = 0  # rounds


def back_bells(perm: Permutation) -> tuple[int, ...]:
    """The bells in the back positions of the row that ``perm`` reaches.

    ``perm`` says where each bell moved to; the row says which bell is in each
    position, so invert it first.
    """
    row = [0] * NUM_BELLS
    for bell, position in enumerate(perm):
        row[position] = bell
    return tuple(row[FIRST_SUFFIX_POSITION:])


class LeadGraph:
    """Every row reachable from rounds by plain and bob leads.

    - ``successors[s]`` is ``(row after a plain lead, row after a bob lead)``.
    - Rows with the same back bells form a clump: ``clump_of[s]`` is the clump
      of row ``s``, and ``clump_states[c]`` lists the rows in clump ``c``.
    - Row ``START_STATE`` is rounds.
    """

    def __init__(self) -> None:
        # Breadth-first search from rounds, numbering rows as they are found.
        rounds = identity(NUM_BELLS)
        index_of = {rounds: START_STATE}
        rows = [rounds]
        self.successors: list[tuple[int, int]] = []
        queue = deque(rows)
        while queue:
            row = queue.popleft()
            targets = []
            for lead_perm in LEAD_PERMUTATIONS:
                next_row = then(row, lead_perm)
                if next_row not in index_of:
                    index_of[next_row] = len(rows)
                    rows.append(next_row)
                    queue.append(next_row)
                targets.append(index_of[next_row])
            self.successors.append((targets[0], targets[1]))

        self.start_state = START_STATE
        self.num_states = len(rows)
        clump_ids: dict[tuple[int, ...], int] = {}
        self.clump_of = [
            clump_ids.setdefault(back_bells(row), len(clump_ids)) for row in rows
        ]
        self.num_clumps = len(clump_ids)
        self.clump_states: list[list[int]] = [[] for _ in range(self.num_clumps)]
        for state, clump in enumerate(self.clump_of):
            self.clump_states[clump].append(state)
