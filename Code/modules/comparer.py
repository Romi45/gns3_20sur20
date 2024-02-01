import json

def load_json(file_path):
    """
    Loads a json file into a python dictionnary object.
    """
    with open(file_path, 'r') as file:
        return json.load(file)

def compare_values(key, value1, value2, differences):
    """
    Compares the differences between the values of two different dicts for a give key.
    """
    if value1 != value2:
        differences[key] = [value1, value2]

def compare_dicts(dict1, dict2):
    """
    Uses compare_values to compare two dict, returns the differences as a dict.
    """
    differences = {}
    for key in dict1:
        if key in dict2:
            if isinstance(dict1[key], dict) and isinstance(dict2[key], dict):
                sub_diff = compare_dicts(dict1[key], dict2[key])
                if sub_diff:
                    differences[key] = sub_diff
            else:
                compare_values(key, dict1[key], dict2[key], differences)
        else:
            differences[key] = [dict1[key], 'Not present in second file']
    for key in dict2:
        if key not in dict1:
            differences[key] = ['Not present in first file', dict2[key]]
    return differences

def compareLoopbacks(dico1, dico2):
    """
    Compares the loopback @s of the new and old intent files.
    """
    differences = {}
    for key in dico1:
        disparues = set(dico1[key]) - set(dico2.get(key, []))
        nouvelles = set(dico2.get(key, [])) - set(dico1[key])
        if disparues or nouvelles:
            differences[key] = {}
            if disparues:
                differences[key]['disparues'] = list(disparues)
            if nouvelles:
                differences[key]['nouvelles'] = list(nouvelles)
    return differences
