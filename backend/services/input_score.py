from backend.config.mode_config import get_tag_weight, MODE_TAG_WEIGHT
from backend.config.tag_config import SUPPORTED_TAGS


def calculate_tag_weights(mode: str, tags: list[str]):
    if mode not in MODE_TAG_WEIGHT:
        raise ValueError("Mode không hợp lệ: " + mode)
    tag_weights = {}
    for tag in tags:
        if tag not in SUPPORTED_TAGS:
            raise ValueError("Tag không hợp lệ: " + tag)
        weight = get_tag_weight(mode, tag)
        tag_weights[tag] = weight
    return tag_weights
