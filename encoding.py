from argparse import ArgumentParser
from itertools import permutations, product
from pathlib import Path

from pysat.formula import IDPool

from graph_helpers import ClumpGraph
from knf import KNF

# Fewest clumps a weak encoding must enter; 0 adds no constraint.
DEFAULT_MIN_CLUMPS = 0

class ErinTriplesEncodings:
    def __init__(self):
        self.vpool = IDPool(start_from=1)
        self.g = ClumpGraph.lead_graph()

    def generate_ternary_knf(self, require_every_clump=True,
                             min_clumps=DEFAULT_MIN_CLUMPS):
        knf = KNF()

        # If an in-edge is used, one of the corresponding out-edges must be
        # used, and vice-a-versa
        for state in range(self.g.graph.num_states):
            in_edges = self.g.edges_into_state(state)
            out_edges = self.g.edges_out_of_state(state)

            for i in in_edges:
                clause = [-self.vpool.id(i)]
                clause.extend([self.vpool.id(j) for j in out_edges])
                knf.add_clause(clause)

            for j in out_edges:
                clause = [-self.vpool.id(j)]
                clause.extend([self.vpool.id(i) for i in in_edges])
                knf.add_clause(clause)

        self._add_cycle_constraints(knf, require_every_clump, min_clumps)

        return knf

    def generate_binary_knf(self, require_every_clump=True,
                            min_clumps=DEFAULT_MIN_CLUMPS):
        knf = KNF()

        # If an in-edge of one row is used, no out-edge of any other row in the
        # same clump may be used
        for rows in self.g.graph.clump_states:
            for in_row, out_row in permutations(rows, 2):
                for i, j in product(self.g.edges_into_state(in_row),
                                    self.g.edges_out_of_state(out_row)):
                    knf.add_clause([-self.vpool.id(i), -self.vpool.id(j)])

        # Without "at least one" per clump, nothing above requires leaving a
        # clump that was entered
        if not require_every_clump:
            self._add_clump_flow_clauses(knf)

        self._add_cycle_constraints(knf, require_every_clump, min_clumps)

        return knf

    def _add_clump_flow_clauses(self, knf):
        """A used in-edge requires an out-edge of its clump, and vice versa."""
        for clump in range(self.g.graph.num_clumps):
            ins = [self.vpool.id(e) for e in self.g.edges_into_clump(clump)]
            outs = [self.vpool.id(e) for e in self.g.edges_out_of_clump(clump)]

            for used, required in ((ins, outs), (outs, ins)):
                for literal in used:
                    knf.add_clause([-literal, *required])

    def _add_cycle_constraints(self, knf, require_every_clump, min_clumps):
        """Constraints shared by all encodings.

        One cycle passes through rounds. If ``require_every_clump`` is True,
        every clump is entered and left exactly once (``min_clumps`` is
        ignored). Otherwise each clump is used at most once and at least
        ``min_clumps`` of them are entered.
        """
        for clump in range(self.g.graph.num_clumps):
            in_edges = self.g.edges_into_clump(clump)
            out_edges = self.g.edges_out_of_clump(clump)

            for edges in (in_edges, out_edges):
                literals = [self.vpool.id(e) for e in edges]
                if require_every_clump:
                    # At least one is an ordinary clause.
                    knf.add_clause(literals)
                knf.add_at_most(literals, 1)

        # A cycle passes through rounds
        rounds_edges = self.g.edges_into_state(self.g.graph.start_state)
        knf.add_clause([self.vpool.id(e) for e in rounds_edges])

        if not require_every_clump:
            # Each clump has at most one used in edge, so counting used edges
            # counts the clumps entered
            knf.add_at_least([self.vpool.id(e) for e in self.g.edges],
                             min_clumps)

if __name__ == "__main__":
    encodings = ErinTriplesEncodings()
    # Variant name -> (generator, require_every_clump)
    variants = {
        "ternary": (encodings.generate_ternary_knf, True),
        "binary": (encodings.generate_binary_knf, True),
        "weak-ternary": (encodings.generate_ternary_knf, False),
        "weak-binary": (encodings.generate_binary_knf, False),
    }
    num_clumps = encodings.g.graph.num_clumps

    parser = ArgumentParser(description="Write an Erin Triples KNF encoding.")
    parser.add_argument("variant", choices=variants)
    parser.add_argument(
        "--min-clumps", type=int, metavar="N",
        help=f"weak variants only: enter at least N of the {num_clumps} "
             f"clumps (default {DEFAULT_MIN_CLUMPS})")
    args = parser.parse_args()

    generate, require_every_clump = variants[args.variant]
    min_clumps = args.min_clumps
    name = f"erin_triples_{args.variant}"
    if require_every_clump:
        if min_clumps is not None:
            parser.error("--min-clumps only applies to weak variants")
        knf = generate()
    else:
        if min_clumps is None:
            min_clumps = DEFAULT_MIN_CLUMPS
        if not 0 <= min_clumps <= num_clumps:
            parser.error(f"--min-clumps must be from 0 to {num_clumps}")
        knf = generate(require_every_clump, min_clumps)
        name += f"_min{min_clumps}"

    output_path = Path(f"{name}.knf")
    knf.to_file(output_path, encodings.vpool.top)
    print(f"{output_path}: {encodings.vpool.top} variables, "
          f"{len(knf.clauses)} clauses, "
          f"{len(knf.cardinalities)} cardinality constraints")
