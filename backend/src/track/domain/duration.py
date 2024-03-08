def parse_isoduration(isostring: str) -> dict[str, int]:
    separators = {
        "H": "hours",
        "M": "minutes",
        "S": "seconds",
    }
    assert isostring[:2] == "PT"
    isostring = isostring[2:]

    duration_vals = {}
    for sep, unit in separators.items():
        partitioned = isostring.partition(sep)
        if partitioned[1] == sep:
            isostring = partitioned[2]
            duration = int(partitioned[0])
            duration_vals.update({unit: duration})
        else:
            duration_vals.update({unit: 0})
    return duration_vals
