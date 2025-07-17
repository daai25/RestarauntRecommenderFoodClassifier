import os

def read_label_file(label_file_path: str) -> dict[int, str]:
    """
    Reads a label file and returns a dictionary mapping image names to their labels.

    Args:
        label_file_path (str): Path to the label file.

    Returns:
        dict: A dictionary where keys are image names and values are their corresponding labels.
    """
    if not os.path.exists(label_file_path):
        raise FileNotFoundError(f"Label file does not exist: {label_file_path}")

    labels = {}
    with open(label_file_path, 'r') as file:
        for line in file:
            parts = line.strip().lower().split('  ')
            if len(parts) != 2:
                continue  # Skip lines that do not have exactly two parts
            label_nr, label_name = parts
            # save the label number as an integer and the label name with leading and trailing spaces
            labels[int(label_nr)] = " " + label_name + " "
    return labels

def remove_all_adjectives(labels: dict[int, str]) -> dict[int, str]:
    """
    Removes all adjectives from the labels.

    Args:
        labels (dict): A dictionary of labels.

    Returns:
        dict: A new dictionary with adjectives removed from the labels.
    """
    adjectives = [" fresh ", " crispy ", " tasty ", " delicious ",
                  " spicy ", " sweet ", " savory ", " grilled ",
                  " dried ", " roasted ", " fried ", " baked ",
                  " steamed ", " smoked ", " sliced ", " chopped ",
                  " seasoned ", " marinated ", " homemade ", " organic ",
                  " local ", " traditional ", " authentic ", " premium ",
                  " scrambled ", " toasted ", " griddle ", " pickled "
                  " fresh", " stewed ", " crispy ", " braised "
                  " small ", " salted ", " roasted ", " stir-fried ",
                  " boiled ", " shredded ", " scalded ", " cold "
                  " radish ", " silky", " diving ", " soft ",
                  " oily ", "distilled ", "hot ", "spiced ",
                  " soft-", " sour ", " diced ", " cold eating ",
                  " glutinous ", " memixed", " mixed ", " small ",
                  " thick ", " salt ", " mashed ", " burning ",
                  " cooked ", " sauted ", " stinky ", " dry ",
                  " seasonal ", " cool ", " slippery ", " sizzling ",
                  " bitter ", " fatty ", " flavored ", " pointed ",
                  " pickled ", " tossed ", " steam "]
    new_labels = {}
    for label_nr, label_name in labels.items():
        for adjective in adjectives:
            label_name = label_name.replace(adjective, " ")
        new_labels[label_nr] = label_name

    return new_labels

def remove_all_colors(labels):
    """
    Removes all color names from the labels.

    Args:
        labels (dict): A dictionary of labels.

    Returns:
        dict: A new dictionary with color names removed from the labels.
    """
    colors = [" red ", " green ", " blue ", " yellow ", " orange ",
              " purple ", " pink ", " brown ", " black ", " white ",
              " golden ", " silver "]
    new_labels = {}

    for label_nr, label_name in labels.items():
        for color in colors:
            label_name = label_name.replace(color, " ")
        new_labels[label_nr] = label_name

    return new_labels

def remove_all_prepositions(labels: dict[int, str]) -> dict[int, str]:
    """
    Removes all prepositions from the labels.

    Args:
        labels (dict): A dictionary of labels.

    Returns:
        dict: A new dictionary with prepositions removed from the labels.
    """
    prepositions = [" in ", " on ", " at ", " to ", " for ", " with ",
                    " by ", " from ", " about ", " as ", " of ", " over ",
                    " under ", " between ", " through ", " during ",
                    " before ", " after ", " against ", " without ",
                    " within ", " along ", " across ", " behind ",
                    " beyond ", " despite ", " except ", " inside ",
                    " outside ", " towards ", " onto ", " upon ",
                    " the ", " and ", " so "
                    ]

    new_labels = {}

    for label_nr, label_name in labels.items():
        for prep in prepositions:
            label_name = label_name.replace(prep, " ")
        new_labels[label_nr] = label_name

    return new_labels

def remove_all_numbers(labels: dict[int, str]) -> dict[int, str]:
    """
    Removes all numbers from the labels.

    Args:
        labels (dict): A dictionary of labels.

    Returns:
        dict: A new dictionary with numbers removed from the labels.
    """
    numbers = [" one ", " two ", " three ", " four ", " five "]
    new_labels = {}

    for label_nr, label_name in labels.items():
        for number in numbers:
            label_name = label_name.replace(number, " ")
        new_labels[label_nr] = label_name

    return new_labels

def remove_custom_words(labels: dict[int, str], custom_words: list[str]) -> dict[int, str]:
    """
    Removes custom words from the labels.

    Args:
        labels (dict): A dictionary of labels.
        custom_words (list): A list of words to be removed from the labels.

    Returns:
        dict: A new dictionary with custom words removed from the labels.
    """
    new_labels = {}

    for label_nr, label_name in labels.items():
        for word in custom_words:
            label_name = label_name.replace(word, " ")
        new_labels[label_nr] = label_name

    return new_labels

def remove_empty_labels(labels: dict[int, str]) -> dict[int, str]:
    """
    Removes labels that are empty or consist only of whitespace.

    Args:
        labels (dict): A dictionary of labels.

    Returns:
        dict: A new dictionary with empty labels removed.
    """
    return {label_nr: label_name for label_nr, label_name in labels.items() if label_name.strip()}

def delete_labels(labels: dict[int, str], strings: list[str]) -> dict[int, str]:
    """
    Deletes labels that contain a specific string.

    Args:
        labels (dict): A dictionary of labels.
        strings (str): The string to search for in the labels.

    Returns:
        dict: A new dictionary with labels containing the specified string removed.
    """
    new_labels = {}
    for label_nr, label_name in labels.items():
        in_it = False
        for string in strings:
            if string in label_name:
                in_it = True
                break
        if not in_it:
            new_labels[label_nr] = label_name
    return new_labels

def write_labels_to_file(labels: dict[int, str], output_file_path: str):
    """
    Writes the cleaned labels to a new file.

    Args:
        labels (dict): A dictionary of cleaned labels.
        output_file_path (str): Path to the output file.
    """
    with open(output_file_path, 'w') as file:
        for label_nr, label_name in labels.items():
            file.write(f"{label_nr}  {label_name.strip()}\n")


def merge_labels(labels: dict[int, str]) -> dict[str, list[int]]:
    """
    Merges labels with the same name into a single entry.

    Args:
        labels (dict): A dictionary of labels.

    Returns:
        dict: A new dictionary where keys are label names and values are lists of label numbers.
    """
    merged_labels = {}
    for label_nr, label_name in labels.items():
        if label_name not in merged_labels:
            merged_labels[label_name] = []
        merged_labels[label_name].append(label_nr)

    return merged_labels

def write_merged_labels_to_file(merged_labels: dict[str, list[int]], output_file_path: str):
    """
    Writes the merged labels to a new file.

    Args:
        merged_labels (dict): A dictionary of merged labels.
        output_file_path (str): Path to the output file.
    """
    with open(output_file_path, 'w') as file:
        for label_name, label_nrs in merged_labels.items():
            file.write(f"{label_name.strip()}: {', '.join(map(str, label_nrs))}\n")

def _main():
    # read the label file
    labels = read_label_file("food2k_labels.txt")
    labels = remove_all_adjectives(labels)
    labels = remove_all_colors(labels)
    labels = remove_all_prepositions(labels)
    labels = remove_all_numbers(labels)
    labels = remove_custom_words(labels, [
        " dip ", " beggar’s ", " gluten ", " yolk ", " chinese ",
        " family ", " portrait ", " pan-long ", " box ", " box"
        " finding nemo ", " powder ", " hair ", " pepper ",
        " tfoil ", " small ", " braised ", " slices ",
        " slices", " burst ", " screws ", " cup ",
        " smell ", " tip ", " elbow ", " double ",
        " pot ", " body ", "-flavobeef ",
        " garlic ", " dressing ", " oil ",
        " products ", " bang bang ", " pepper ",
        " secret ", " preserved ", " drumsticks ",
        " honey ", " firewood ", " drumsticks ", " pointed ",
        " chop ", " capers ", " stick ",
        " mustard ", " brisket ", " refreshing ", " gizzards ",
        " mother’s "
    ])
    labels = remove_custom_words(labels, [
        " new orleans "
    ])

    labels = remove_empty_labels(labels)
    labels = delete_labels(labels, [
        "plate reinforcement", " choy ", " bazhen ",
        " intestine ", "colorful face lift", " eryngii ",
        " brain ", " head ", " feet ", " pimple ", " skin ",
        " larimichthys ", " liver ", " tail ", " belly "
        " leg ", " bone "
    ])

    # Save the cleaned labels to a new file
    write_labels_to_file(labels, "cleaned_food2k_labels.txt")

    # list all label numbers with the same label name
    # single label names will be written on a single line
    merged_labels = merge_labels(labels)
    write_merged_labels_to_file(merged_labels, "merged_food2k_labels.txt")

    return 0


if __name__ == "__main__":
    _main()