from typing import Type, Tuple, Dict

# Determine if the given string is an int, float, or string (all python primitive types)
def getType(str_val: str) -> Type:
    try:
        int(str_val)
        return int
    except:
        try:
            float(str_val)
            return float
        except:
            return str


def checkInBounds(
    domain: Tuple[float, float], value: float, method: str, arg_dict: Dict = None
) -> None:
    l_paren = domain[0]
    r_paren = domain[-1]
    vals = domain[1:-1].split(",")
    types = [getType(vals[0]), getType(vals[1])]

    gt_lower = False
    lt_upper = False

    if l_paren == "(":
        if types[0] == str:
            gt_lower = arg_dict[vals[0]] < value
        else:
            gt_lower = types[0](vals[0]) < value

        if not gt_lower:
            raise Exception(
                "The value you enter for the "
                + method
                + " hyperparameter must be greater than "
                + str(vals[0])
                + ', because the "(" symbol in the valid values means the value you enter must be strictly greater than '
                + str(vals[0])
                + "."
            )
    elif l_paren == "[":
        if types[0] == str:
            gt_lower = arg_dict[vals[0]] <= value
        else:
            gt_lower = types[0](vals[0]) <= value

        if not gt_lower:
            raise Exception(
                "The value you enter for the "
                + method
                + " hyperparameter must be greater than or equal to "
                + str(vals[0])
                + ', because the "[" symbol in the valid values  means the value you enter must be greater than or equal to '
                + str(vals[0])
                + "."
            )
    else:
        raise Exception('Unknown bounding character "' + l_paren + '".')

    if r_paren == ")":
        if types[1] == str:
            lt_upper = arg_dict[vals[1]] > value
        else:
            lt_upper = types[1](vals[1]) > value

        if not lt_upper:
            raise Exception(
                "The value you enter for the "
                + method
                + " hyperparameter must be less than "
                + str(vals[1])
                + ', because the ")" symbol in the valid values  means the value you enter must be strictly less than '
                + str(vals[1])
                + "."
            )
    elif r_paren == "]":
        if types[1] == str:
            lt_upper = arg_dict[vals[1]] >= value
        else:
            lt_upper = types[1](vals[1]) >= value

        if not lt_upper:
            raise Exception(
                "The value you enter for the "
                + method
                + " hyperparameter must be less than or equal to "
                + str(vals[1])
                + ', because the "]" symbol in the valid values means the value you enter must be less than or equal to '
                + str(vals[1])
                + "."
            )
    else:
        raise Exception('Unknown bounding character "' + r_paren + '".')


# Return true if all is good, false otherwise
def checkTypeHierarchy(true_type: str, rec_type: str) -> bool:
    if true_type == "float":
        if rec_type in ["float", "int"]:
            return True
    elif true_type == "int":
        if rec_type == "int":
            return True
    elif true_type == "str":
        if rec_type == "str":
            return True

    return False
