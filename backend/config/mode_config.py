DEFAULT_TAG_WEIGHT= 1.0
MODE_TAG_WEIGHT = {
    "solo": {
        "leo núi & trekking": 2.0,
        "thiên nhiên": 1.5,
        "núi rừng": 1.5,
    },
    "couple": {
        "ngắm hoàng hôn & bình minh": 2.0,
        "nghỉ dưỡng": 1.5,
        "cà phê & trà": 1.5,
    },
    "family": {
        "vui chơi giải trí": 2.0,
        "nghỉ dưỡng": 1.5,
        "văn hóa - lịch sử": 1.5,
    },
    "random": {},
}

def get_tag_weight(mode: str, tag: str):
    mode_weights = MODE_TAG_WEIGHT[mode]
    return mode_weights.get(tag, DEFAULT_TAG_WEIGHT)