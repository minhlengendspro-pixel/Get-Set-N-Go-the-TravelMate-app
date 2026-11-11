DEFAULT_TAG_WEIGHT= 1.0
MODE_TAG_WEIGHT = {
    "solo": {
        "khám phá": 2.0,
        "thiên nhiên": 1.5,
    },
    "couple": {
        "lãng mạn": 2.0,
        "nghỉ dưỡng": 1.5,
    },
    "family": {
        "gia đình": 2.0,
        "nghỉ dưỡng": 1.5,
    },
    "random": {},
}

def get_tag_weight(mode: str, tag: str):
    mode_weights = MODE_TAG_WEIGHT[mode]
    return mode_weights.get(tag, DEFAULT_TAG_WEIGHT)