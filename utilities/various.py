# Determine if the given string is an int, float, or string (all python primitive types)
def getType(str_val):
    try:
        int(str_val)
        return int
    except:
        try:
            float(str_val)
            return float
        except:
            return str