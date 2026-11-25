"""Small random graphs with the same shape as LeadGraph, for checking the search."""
import random

CLUMP_SIZE = 3
OUT_DEGREE = 2


class SyntheticGraph:
    """``num_clumps`` clumps of 3 states; every state has two random successors."""

    def __init__(self, num_clumps: int, rng: random.Random, planted: bool) -> None:
        self.start_state = 0
        self.num_clumps = num_clumps
        self.num_states = num_clumps * CLUMP_SIZE
        self.clump_of = [s // CLUMP_SIZE for s in range(self.num_states)]
        self.clump_states = [list(range(c * CLUMP_SIZE, (c + 1) * CLUMP_SIZE)) for c in range(num_clumps)]
        slots = [[rng.randrange(self.num_states) for _ in range(OUT_DEGREE)] for _ in range(self.num_states)]
        self.planted_cycle: list[int] = []
        if planted:
            order = [0, *rng.sample(range(1, num_clumps), num_clumps - 1)]
            self.planted_cycle = [0] + [rng.choice(self.clump_states[c]) for c in order[1:]]
            for source, target in zip(self.planted_cycle, self.planted_cycle[1:] + [0]):
                slots[source][rng.randrange(OUT_DEGREE)] = target
        self.successors = [tuple(pair) for pair in slots]
