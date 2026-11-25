"""Helpers for writing a graph (edge-based) SAT encoding of the peal problem.

The graph is directed: each lead-start row (state) has two outgoing edges,
plain and bob. Rows are grouped into clumps of 3, and a peal is a single loop
of edges that enters and leaves every clump exactly once and passes through
rounds. The real lead graph has 2520 states, 840 clumps and 5040 edges; each
clump has 6 edges in and 6 edges out.

Variables: use ``pysat.formula.IDPool`` with ``pool.id(edge)``, and pass
``vpool=pool`` to ``pysat.card.CardEnc``. Solve and write DIMACS with pysat
directly (``Solver``, ``CNF``).

Run scripts from this directory, e.g. ``python encoding.py``.
"""
from collections import Counter
from typing import Iterable, NamedTuple, Sequence

from pysat.formula import IDPool

from erin_common.graph import LeadGraph


class Edge(NamedTuple):
    """Directed edge: a lead rung from row ``source`` arriving at ``target``."""

    source: int
    target: int


class ClumpGraph:
    """Directed edges of a ``LeadGraph`` (``.graph``), indexed by state and clump."""

    def __init__(self, graph: LeadGraph) -> None:
        self.graph = graph
        # dict.fromkeys keeps order and drops duplicates (a plain and a bob
        # lead to the same row, which happens only in synthetic test graphs).
        self.edges: list[Edge] = list(dict.fromkeys(
            Edge(source, target)
            for source, targets in enumerate(graph.successors)
            for target in targets
        ))
        self._out_of_state: list[list[Edge]] = [
            [] for _ in range(graph.num_states)
        ]
        self._into_state: list[list[Edge]] = [
            [] for _ in range(graph.num_states)
        ]
        for edge in self.edges:
            self._out_of_state[edge.source].append(edge)
            self._into_state[edge.target].append(edge)

    @classmethod
    def lead_graph(cls) -> "ClumpGraph":
        """The real Erin Triples lead graph."""
        return cls(LeadGraph())

    def edges_out_of_state(self, state: int) -> list[Edge]:
        return self._out_of_state[state]

    def edges_into_state(self, state: int) -> list[Edge]:
        return self._into_state[state]

    def edges_out_of_clump(self, clump: int) -> list[Edge]:
        return [edge for state in self.graph.clump_states[clump]
                for edge in self._out_of_state[state]]

    def edges_into_clump(self, clump: int) -> list[Edge]:
        return [edge for state in self.graph.clump_states[clump]
                for edge in self._into_state[state]]


def decode_edges(pool: IDPool, model: Iterable[int]) -> list[Edge]:
    """Edges set true in a solver model (auxiliary variables are skipped)."""
    return [edge for literal in model
            if literal > 0 and isinstance(edge := pool.obj(literal), Edge)]


def loops_of(chosen: Sequence[Edge]) -> list[list[Edge]]:
    """Split edges (one in and one out per used state) into disjoint loops."""
    next_edge = {edge.source: edge for edge in chosen}
    seen: set[int] = set()
    loops = []
    for first in next_edge:
        if first in seen:
            continue
        loop, state = [], first
        while state not in seen and state in next_edge:
            seen.add(state)
            loop.append(next_edge[state])
            state = next_edge[state].target
        loops.append(loop)
    return loops


def cycle_problems(graph: LeadGraph, chosen: Sequence[Edge]) -> list[str]:
    """Why ``chosen`` is not a peal (an empty list means it is one).

    A peal: every clump entered and left exactly once, the row entered is the
    row left, the edges form a single loop, and it passes through rounds.
    """
    problems = []
    entered = Counter(graph.clump_of[edge.target] for edge in chosen)
    left = Counter(graph.clump_of[edge.source] for edge in chosen)
    for clump in range(graph.num_clumps):
        if entered[clump] != 1 or left[clump] != 1:
            problems.append(f"clump {clump}: entered {entered[clump]} times, "
                            f"left {left[clump]} times")
    sources = Counter(edge.source for edge in chosen)
    problems += [f"state {state}: left by {count} edges"
                 for state, count in sources.items() if count > 1]
    problems += [f"state {edge.target}: entered by {edge} but never left"
                 for edge in chosen if edge.target not in sources]
    if problems:
        return problems
    loops = loops_of(chosen)
    if len(loops) != 1:
        sizes = sorted((len(loop) for loop in loops), reverse=True)
        problems.append(f"{len(loops)} separate loops (sizes {sizes}), "
                        "not a single cycle")
    if graph.start_state not in sources:
        problems.append("the loop does not pass through rounds")
    return problems


def cycle_calls(graph: LeadGraph, chosen: Sequence[Edge]) -> list[int]:
    """Calls (0 plain, 1 bob) along a valid cycle, starting from rounds."""
    next_target = {edge.source: edge.target for edge in chosen}
    calls, state = [], graph.start_state
    for _ in chosen:
        target = next_target[state]
        calls.append(graph.successors[state].index(target))
        state = target
    return calls
