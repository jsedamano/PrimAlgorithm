"""
Run prim.py with a selected input and compare its output to a sample.

Edit the file choices below, then run: python3 compare_prim.py
Only Python's standard library is needed.
"""

import csv
from pathlib import Path
import re
import subprocess
import sys


# Change these file choices to select a different test.
FOLDER = Path(__file__).resolve().parent
PRIM_FILE = FOLDER / "prim.py"
INPUT_FILE = FOLDER / "prim-test1.txt"
EXPECTED_OUTPUT_FILE = FOLDER / "prim-test1-output.txt"
ACTUAL_OUTPUT_FILE = FOLDER / "prim-actual-output.txt"


def read_graph(filename):
    with open(filename, "r", newline="") as input_file:
        data = next(csv.reader(input_file))

    number_of_vertices = int(data[0])
    values = [int(value) for value in data[1:]]
    if number_of_vertices < 1 or len(values) != number_of_vertices ** 2:
        raise ValueError("The input does not contain the expected adjacency matrix.")

    return [
        values[start:start + number_of_vertices]
        for start in range(0, len(values), number_of_vertices)
    ]


def parse_output(text):
    """Read the vertex count, edge sequence, and total from printed output."""
    vertex_count = None
    edges = []
    total = None

    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("First row:"):
            continue  # Allow the temporary input-check print in prim.py.

        header = re.fullmatch(r"(\d+)\s+vertices found\.", line)
        edge = re.fullmatch(
            r"Adding edge\s*\(\s*(\d+)\s*,\s*(\d+)\s*\)"
            r"\s*with weight\s+(-?\d+)\s*\.", line
        )
        final = re.fullmatch(r"Total weight of spanning tree:\s*(-?\d+)", line)

        if header and vertex_count is None and not edges and total is None:
            vertex_count = int(header.group(1))
        elif edge and vertex_count is not None and total is None:
            edges.append(tuple(int(value) for value in edge.groups()))
        elif final and vertex_count is not None and total is None:
            total = int(final.group(1))
        else:
            raise ValueError(f"Unexpected output line: {line!r}")

    if vertex_count is None or total is None:
        raise ValueError("Output must include the vertex count and final total.")

    return vertex_count, edges, total


def validate_prim_output(graph, result):
    """Check each printed edge against Prim's rule, allowing any cheapest tie."""
    vertex_count, edges, total = result
    n = len(graph)

    if vertex_count != n:
        raise ValueError(
            f"Output reports {vertex_count} vertices; the selected input has {n}. "
            "Check that prim.py reads the filename passed in sys.argv[1]."
        )
    if len(edges) != n - 1:
        raise ValueError(f"Expected {n - 1} edges, but found {len(edges)}.")
    if sum(weight for _, _, weight in edges) != total:
        raise ValueError("The printed total does not equal the sum of the edge weights.")

    included = {0}
    for step, (start, end, weight) in enumerate(edges, start=1):
        if not (0 <= start < n and 0 <= end < n):
            raise ValueError(f"Edge {step}: a vertex number is outside the input graph.")
        if graph[start][end] == 0 or graph[start][end] != weight:
            raise ValueError(f"Edge {step}: the edge or its weight does not match the input.")
        if (start in included) == (end in included):
            raise ValueError(f"Edge {step}: exactly one endpoint must be in the tree.")

        # Independently check the cheapest edge leaving the current tree.
        cheapest = min(
            graph[u][v]
            for u in included
            for v in range(n)
            if v not in included and graph[u][v] != 0
        )
        if weight != cheapest:
            raise ValueError(
                f"Edge {step}: selected weight {weight}, but an eligible edge "
                f"with weight {cheapest} was available."
            )

        included.update((start, end))


def normalized_edges(result):
    """An undirected edge (8, 4) is equivalent to (4, 8)."""
    return [(min(u, v), max(u, v), weight) for u, v, weight in result[1]]


def main():
    try:
        graph = read_graph(INPUT_FILE)
        expected = parse_output(EXPECTED_OUTPUT_FILE.read_text())
        validate_prim_output(graph, expected)
    except (OSError, ValueError, StopIteration) as error:
        print(f"CHECKER SETUP ERROR: {error}")
        return 1

    try:
        completed = subprocess.run(
            [sys.executable, str(PRIM_FILE), str(INPUT_FILE)],
            cwd=PRIM_FILE.parent,
            capture_output=True,
            text=True,
            timeout=60,
        )
        ACTUAL_OUTPUT_FILE.write_text(completed.stdout)
    except (OSError, subprocess.TimeoutExpired) as error:
        print(f"COULD NOT RUN PRIM: {error}")
        return 1

    print(f"📌 Input: {INPUT_FILE.name}")
    print(f"📌 Expected output: {EXPECTED_OUTPUT_FILE.name}")
    print(f"📌 Your output saved to: {ACTUAL_OUTPUT_FILE}")

    if completed.returncode != 0:
        print("❌ FAIL: prim.py stopped with an error.")
        print(completed.stderr.strip())
        return 1

    try:
        actual = parse_output(completed.stdout)
        validate_prim_output(graph, actual)
        if actual[2] != expected[2]:
            raise ValueError(
                f"Total weight {actual[2]} differs from the expected {expected[2]}."
            )
    except ValueError as error:
        print(f"FAIL: {error}")
        return 1

    print(f"✅ PASS: {len(actual[1])} valid Prim edges; total weight {actual[2]}.")
    if normalized_edges(actual) == normalized_edges(expected):
        print("The edge sequence matches the sample, allowing reversed endpoints.")
    else:
        print("The edge sequence differs, but every choice obeys Prim's rule.")
        print("This is a valid alternative caused by equal-weight ties.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
