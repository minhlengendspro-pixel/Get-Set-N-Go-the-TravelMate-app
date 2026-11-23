from backend.config.tag_config import SUPPORTED_TAGS

# Chuyển sở thích người dùng nhập thành tags chuẩn
SYNONYM_TO_TAG = {
    # Biển đảo
    "đi biển": "biển đảo",
    "du lịch biển": "biển đảo",
    # Núi rừng và thiên nhiên
    "khám phá rừng núi": "núi rừng",
    "ngắm cảnh thiên nhiên": "thiên nhiên",
    # Sông nước
    "đi chợ nổi": "sông nước",
    "du ngoạn sông": "sông nước",
    # Làng quê
    "khám phá làng quê": "làng quê & đồng bằng",
    # Đô thị
    "khám phá thành phố": "đô thị",
    # Nghỉ dưỡng
    "nghỉ ngơi": "nghỉ dưỡng",
    "thư giãn": "nghỉ dưỡng",
    # Văn hóa và lịch sử
    "khám phá văn hóa": "văn hóa - lịch sử",
    "tìm hiểu lịch sử": "văn hóa - lịch sử",
    "tham quan di tích": "kiến trúc & di tích cổ",
    "khám phá kiến trúc cổ": "kiến trúc & di tích cổ",
    # Ẩm thực
    "khám phá ẩm thực": "ẩm thực",
    "ăn hải sản": "hải sản tươi sống",
    "ăn đặc sản": "đặc sản địa phương",
    "ăn vặt đường phố": "ẩm thực đường phố",
    "uống cà phê": "cà phê & trà",
    "uống trà": "cà phê & trà",
    # Giải trí
    "trò chơi giải trí": "vui chơi giải trí",
    "đi công viên giải trí": "vui chơi giải trí",
    "chụp ảnh check-in": "check-in sống ảo",
    "sống ảo": "check-in sống ảo",
    "lặn ngắm san hô": "tắm biển & lặn ngắm san hô",
    "tắm biển": "tắm biển & lặn ngắm san hô",
    "tham gia lễ hội": "lễ hội dân gian",
    # Leo núi
    "leo núi": "leo núi & trekking",
    "trekking": "leo núi & trekking",
    # Hoàng hôn và bình minh
    "ngắm hoàng hôn": "ngắm hoàng hôn & bình minh",
    "ngắm bình minh": "ngắm hoàng hôn & bình minh",
    # Tâm linh
    "hành hương": "du lịch tâm linh",
    "đi chùa": "du lịch tâm linh",
    "viếng đền": "du lịch tâm linh",
}

def normalize_text(text: str):
    text = text.lower()
    text = " ".join(text.split())
    return text

def is_negative(text: str, keyword: str):
    negative_phrases = [
        "không thích " + keyword,
        "không muốn " + keyword,
        "ghét " + keyword,
    ]
    for phrase in negative_phrases:
        if phrase in text:
            return True
    return False

def extract_tags(interests: list[str], user_text: str):
    found_tags = []
    # Xử lý tag chọn sẵn từ interest
    for interest in interests:
        if interest not in SUPPORTED_TAGS:
            raise ValueError("Tag không hợp lệ: " + interest)
        if interest not in found_tags:
            found_tags.append(interest)
    # Chuẩn hoá user text và tìm tag chuẩn từ từ khoá đồng nghĩa
    normalize_user_text = normalize_text(user_text)
    for keyword, tag in SYNONYM_TO_TAG.items():
        if keyword in normalize_user_text:
            if not is_negative(normalize_user_text, keyword):
                if tag not in found_tags:
                    found_tags.append(tag)
    return found_tags
