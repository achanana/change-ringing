# Erin Triples encodings

SAT encodings, in KNF (CNF plus "at least k" constraints), of the search for a
peal of Erin Triples.

The problem is a directed graph. Its 2520 nodes are the rows that can start a
lead, and each has two outgoing edges (plain and bob). Rows are grouped into
840 clumps of 3. A peal is a single cycle through rounds (1234567) that enters
and leaves every clump exactly once, using the same row for both. There is one
variable per edge (5040 in total).

## Setup

Requires Python 3 (tested with 3.14) and
[PySAT](https://pysathq.github.io/):

```bash
pip install python-sat
```

To solve the formulas, fetch and build
[Cardinality-CDCL](https://github.com/jreeves3/Cardinality-CDCL), which is
included as a submodule:

```bash
git submodule update --init
cd third_party/Cardinality-CDCL
sh build.sh
```

## Usage

From the repository root, write an encoding:

```bash
python encoding.py ternary
python encoding.py weak-binary --min-clumps 100
```

Then solve it:

```bash
third_party/Cardinality-CDCL/cardinality-cadical/build/cadical erin_triples_ternary.knf
```

## Variants

| Variant        | Each clump is used | Entering and leaving by the same row |
|----------------|--------------------|--------------------------------------|
| `ternary`      | exactly once       | 3-literal implications               |
| `binary`       | exactly once       | 2-literal exclusions                 |
| `weak-ternary` | at most once       | 3-literal implications               |
| `weak-binary`  | at most once       | 2-literal exclusions, plus 7-literal clauses requiring an exit |

All variants require a cycle through rounds. The weak variants also accept
`--min-clumps N` (default 0) to require that at least `N` clumps are entered.

### Size

All variants have 5040 variables. "Clauses" are ordinary clauses, and
"cardinality" counts the `k` lines.

| Variant        | Clauses | Cardinality | Total |
|----------------|--------:|------------:|------:|
| `ternary`      |   11761 |        1680 | 13441 |
| `binary`       |   21841 |        1680 | 23521 |
| `weak-ternary` |   10081 |        1680 | 11761 |
| `weak-binary`  |   30241 |        1680 | 31921 |

With `--min-clumps N` for `N` above 0, a weak variant has one more cardinality
constraint.

## Limitations

A solution may contain **several separate cycles**, so a satisfying assignment
is not necessarily a peal. Nothing here eliminates the extra cycles yet.

To inspect a solution, use `decode_edges`, `loops_of` and `cycle_problems` from
`graph_helpers.py`. `cycle_problems` checks for a full peal, so it reports any
clump that a weak variant skips.

## Files

| File                 | Contents                                       |
|----------------------|------------------------------------------------|
| `encoding.py`        | The four encodings and the command line        |
| `knf.py`             | KNF container and file writer                  |
| `graph_helpers.py`   | Edge and clump lookups, solution checks        |
| `synthetic_graph.py` | Small random graphs of the same shape          |
| `erin_common/`       | Permutations, the two leads and the lead graph |
| `third_party/`       | The KNF solver (submodule)                     |

## KNF format

```
p knf <variables> <constraints>
1 -2 3 0          clause
k 2 1 3 -5 0      at least 2 of these literals are true
```

See section 2.2.5 of
[J. Reeves's PhD thesis](https://www.cs.cmu.edu/~jereeves/research/jereeves_phd_csd_2025.pdf).
