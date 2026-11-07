import csv

filename = "prim-deliverable2.txt"

# ------------------------ File I/O ------------------------
# Read the comma separated values as a list of strings
with open(filename, "r", newline="") as input_file:
    reader = csv.reader(input_file)
    data = next(reader)

# The number of vertices is the first number in the input file
number_of_vertices = int(data[0])

# Build the adjacency matrix one row at a time
graph = []  # The adjacency matrix
data_index = 1  # Tracks which position in "data" to read next

# Iterate through all of the rows
for row_number in range(number_of_vertices):
    row = []

    # Iterate through all of the columns
    for column_number in range(number_of_vertices):
        weight = int(data[data_index])
        row.append(weight)
        data_index += 1

    graph.append(row)

# Output message with the number of vertices found
print(f"{number_of_vertices} vertices found.")


# ------------------------ Algorithm ------------------------
tree = set()    # Create an empty set of vertices
tree.add(0)    # Add the starting vertex

# Keeps track of the total weight of all of the chosen edges
total_weight = 0

# The algorithm should continue until the tree has n vertices
while len(tree) < number_of_vertices:

    # Initialize the cheapest weight seen so far to infinity
    cheapest_weight = float("inf")

    # We haven't chosen an edge yet, so start with None
    cheapest_start = None   # Start vertex
    cheapest_end = None     # End vertex

    # Examine each vertex already included in the tree
    for start_vertex in tree:

        # Try every other vertex as the endpoint
        for end_vertex in range(number_of_vertices):

            # Lookup that pair's weight in the adjacency matrix
            # weight == 0: no edge exists between those vertices
            weight = graph[start_vertex][end_vertex]

            # Check that an edge exists + the endpoint is outside the current tree
            if weight != 0 and end_vertex not in tree:

                # Check if that edge's weight is less than the current cheapest_weight
                if weight < cheapest_weight:
                    cheapest_weight = weight    # Update the cheapest weight
                    cheapest_start = start_vertex   # Update the start vertex
                    cheapest_end = end_vertex   # Update the end vertex

    # Once both loops are done, the best vertex/edge is now known
    # Add the end vertex to the tree, turning it into a new possible starting point
    tree.add(cheapest_end)

    # Add the cheapest weight we just found to the final total weight
    total_weight += cheapest_weight

    # Output message with the cheapest edge we just found + its weight
    print(f"Adding edge ({cheapest_start},{cheapest_end}) with weight {cheapest_weight}.")

# Output message with the final total weight of the MST
print(f"\nTotal weight of spanning tree: {total_weight}")