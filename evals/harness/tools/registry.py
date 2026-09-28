"""Every registry key names the same tool its schema advertises."""
from tool import REGISTRY


def names_match():
    for key, (schema, fn) in REGISTRY.items():
        assert schema["function"]["name"] == key, f"{key} advertises {schema['function']['name']}"
        assert callable(fn), f"{key} has no function"


CASES = [{"name": "registry_names_match", "check": names_match}]
