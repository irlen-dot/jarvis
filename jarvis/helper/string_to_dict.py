import json
from typing import Any, Dict


def string_to_dict(input: str) -> Dict[str, Any]:
    # json_str = input.split("}")[0] + "}"
    dict: Dict[str, Any] = json.loads(input)
    return dict
