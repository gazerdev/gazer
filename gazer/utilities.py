def escapeString(query_string):
    scs = ["'"]
    for sc in scs:
        query_string = query_string.replace(sc, "''")
    return query_string
