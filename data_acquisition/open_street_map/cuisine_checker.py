valid_file = "cuisine_types.txt"     # One valid cuisine per line
input_file = "included_cuisines.txt"       # One cuisine per line to be checked

# Read list of all cuisines
with open(valid_file, 'r', encoding='utf-8') as f:
    valid_cuisines = set(line.strip() for line in f if line.strip())

# Compare mapped cuisines to list of all cuisines
hallucinated_garbage = set()
with open(input_file, 'r', encoding='utf-8') as f:
    for line in f:
        cuisine = line.strip()
        if cuisine and cuisine not in valid_cuisines:
            hallucinated_garbage.add(cuisine)

print(f"Hallucinated Garbage: {hallucinated_garbage}")