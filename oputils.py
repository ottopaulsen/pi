
def stringToInt(stringToConvert, defaultValue = 0) :
    try : 
        res = int(stringToConvert)
    except ValueError:
        res = defaultValue
    return res

