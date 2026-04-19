def cant_see_item(issues: list[str], phrases: list[str]) -> bool:
    joined = " ".join(issues).lower()
    return any(phrase in joined for phrase in phrases)
