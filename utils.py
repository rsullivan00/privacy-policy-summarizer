def ctr_len(ctr):
    """
    Returns the total length of tokens contained in
    a collections.Counter object.
    """
    return sum(ctr.values())
