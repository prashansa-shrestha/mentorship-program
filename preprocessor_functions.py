def make_lowercase(col):
    if col.dtype=="object":
        return col.str.lower()
    else:
        return col