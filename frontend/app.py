import streamlit as st
import requests
import urllib.parse
from datetime import datetime, timezone
from zoneinfo import ZoneInfo


# ============================================================
# 1. CẤU HÌNH TRANG VÀ API
# ============================================================

st.set_page_config(
    page_title="TravelMate AI",
    page_icon="✈️",
    layout="wide"
)

API_BASE_URL = "http://127.0.0.1:8000"

API = {
    "health": f"{API_BASE_URL}/",
    "destinations": f"{API_BASE_URL}/api/places/destinations",
    "recommend": f"{API_BASE_URL}/api/places/recommend",
    "random": f"{API_BASE_URL}/api/random-challenge/",
    "scheduler": f"{API_BASE_URL}/api/scheduler/",
    "history": f"{API_BASE_URL}/api/search-history/",
    "foods": f"{API_BASE_URL}/api/foods/",
    "food_destinations": f"{API_BASE_URL}/api/foods/destinations",
    "restaurants_prune": f"{API_BASE_URL}/api/restaurants/prune-safe",
}

RECOMMEND_API = API["recommend"]
RANDOM_API = API["random"]
HISTORY_API = API["history"]
DESTINATIONS_API = API["destinations"]
SCHEDULER_API = API["scheduler"]


# ============================================================
# 2. SESSION STATE
# ============================================================

DEFAULT_STATES = {
    "is_submitted": False,
    "results": [],
    "recommendation_response": None,

    "random_result": None,
    "schedule_result": None,

    "history_by_type": {},
    "selected_history_id": None,
    "selected_history_detail": None,

    "hobby": [],
    "place": "Hà Nội",
    "budget": 100000,
    "duration": 1,
    "mode": "solo",

    # Food
    "food_results": [],
    "food_destination": None,
    "food_type": "Tất cả",
    "food_tag": "",

    # Restaurant
    "restaurant_data": None,
    "selected_dining_places": [],
    "group_allergens": [],
    "max_budget_per_meal": 150000,
    "group_size": 2,
    "restaurant_destination": None,
}

for key, value in DEFAULT_STATES.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ============================================================
# 3. DỮ LIỆU AI RECOMMENDATION
# ============================================================

HOBBY_TAGS = {
    "Đi biển": "biển đảo",
    "Leo núi": "leo núi & trekking",
    "Tham quan địa điểm lịch sử": "kiến trúc & di tích cổ",
    "Ngắm cảnh đẹp thiên nhiên": "thiên nhiên",
    "Ẩm thực địa phương": "ẩm thực",
}

MODE_OPTIONS = {
    "Đi du lịch một mình": "solo",
    "Đi du lịch cùng người yêu": "couple",
    "Đi du lịch cùng gia đình": "family",
    "Để AI tự do lựa chọn": "random",
}

MODE_LABELS = {
    "solo": "Đi một mình",
    "couple": "Đi cùng người yêu",
    "family": "Đi cùng gia đình",
    "random": "AI tự lựa chọn",
}

HISTORY_TYPE_LABELS = {
    "random_challenge": "🎲 Random Challenge",
    "scheduler": "🗓️ Lập lịch trình",
    "place_recommendation": "📍 Tìm kiếm địa điểm",
}

FOOD_TYPE_OPTIONS = [
    "Tất cả",
    "Món chính",
    "Món ăn nhẹ",
    "Đồ uống",
    "Tráng miệng",
]

ALLERGEN_OPTIONS = [
    "Lạc/đậu phộng",
    "Vừng/mè",
    "Hải sản",
    "Tôm",
    "Cua",
    "Cá",
    "Sữa",
    "Trứng",
    "Đậu nành",
    "Gluten",
]


# ============================================================
# 4. CSS GIAO DIỆN TV4
# ============================================================

st.markdown(
    """
    <style>
    .main-title {
        text-align: center;
        font-size: 36px;
        font-weight: bold;
        color: #D4AF37;
        margin-bottom: 5px;
    }

    .sub-title {
        text-align: center;
        color: gray;
        margin-bottom: 25px;
    }

    .random-wheel {
        width: 160px;
        height: 160px;
        border-radius: 50%;
        border: 12px solid #D4AF37;
        border-top-color: #0F2238;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 65px;
        margin: 25px auto;
    }

    .random-wheel.spinning {
        animation: spin 0.7s linear infinite;
    }

    @keyframes spin {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }

    .random-heading {
        text-align: center;
        font-size: 24px;
        font-weight: bold;
        color: #D4AF37;
    }

    div[data-testid="stSidebar"] {
        background-color: #0F2238;
    }

    div[data-testid="stSidebar"] * {
        color: #FFFFFF;
    }

    div[data-testid="stSidebar"] input,
    div[data-testid="stSidebar"] textarea {
        color: #222222 !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# 5. HÀM HỖ TRỢ CHUNG
# ============================================================

def format_datetime(value):
    """Chuyển thời gian UTC sang giờ Việt Nam."""

    if not value:
        return "Không có thông tin"

    try:
        if isinstance(value, datetime):
            date_value = value
        else:
            date_value = datetime.fromisoformat(
                str(value).replace("Z", "+00:00")
            )

        if date_value.tzinfo is None:
            date_value = date_value.replace(
                tzinfo=timezone.utc
            )

        vietnam_time = date_value.astimezone(
            ZoneInfo("Asia/Ho_Chi_Minh")
        )

        return vietnam_time.strftime(
            "%H:%M:%S - %d/%m/%Y"
        )

    except (ValueError, TypeError):
        return str(value)


def format_list(value):
    if isinstance(value, list):
        return ", ".join(
            str(item) for item in value
        ) if value else "Không có"

    if value is None:
        return "Không có"

    return str(value)


def money_format(value):
    try:
        return f"{int(float(value)):,} VNĐ"
    except (ValueError, TypeError):
        return str(value) if value is not None else "Chưa có thông tin"


def display_safe_image(image_url, width="stretch"):
    """
    Chỉ hiển thị URL HTTP/HTTPS hợp lệ.
    Tránh Streamlit hiểu chuỗi không phải URL thành đường dẫn file.
    """

    if (
        isinstance(image_url, str)
        and image_url.strip().startswith(("http://", "https://"))
    ):
        try:
            st.image(
                image_url.strip(),
                width=width
            )
        except Exception:
            st.caption("Không thể tải hình ảnh.")
    else:
        st.caption("Chưa có hình ảnh hợp lệ.")


def extract_list(data, possible_keys=None):
    """Chuẩn hóa các dạng response danh sách từ Backend."""

    if possible_keys is None:
        possible_keys = [
            "data",
            "results",
            "items",
            "foods",
            "restaurants",
            "places",
            "destinations",
            "safe_restaurants",
            "safe_dishes",
        ]

    if isinstance(data, list):
        return data

    if not isinstance(data, dict):
        return []

    for key in possible_keys:
        value = data.get(key)

        if isinstance(value, list):
            return value

        if isinstance(value, dict):
            nested = extract_list(value, possible_keys)
            if nested:
                return nested

    return []


def get_google_maps_url(name, destination=""):
    query_text = f"{name}, {destination}".strip(", ")
    query = urllib.parse.quote(query_text)

    return (
        "https://www.google.com/maps/search/"
        f"?api=1&query={query}"
    )


def get_history_attributes(item):
    """Lấy thuộc tính tìm kiếm để hiển thị trong lịch sử."""

    if not isinstance(item, dict):
        return ["Chưa có thuộc tính tìm kiếm"]

    search_type = item.get("search_type")
    request_data = item.get("request_data", {})

    if not isinstance(request_data, dict):
        request_data = {}

    attributes = []

    if search_type == "random_challenge":
        tags = request_data.get("selected_tags", [])

        if tags:
            attributes.append(
                f"Tags: {format_list(tags)}"
            )
        else:
            attributes.append("Thuộc tính: Random tags")

    elif search_type == "scheduler":
        input_context = request_data.get(
            "input_context",
            {}
        )

        if not isinstance(input_context, dict):
            input_context = {}

        duration = input_context.get("duration")

        if duration is not None:
            attributes.append(
                f"Thời lượng: {duration} ngày"
            )

        tags = input_context.get("tags", [])

        if tags:
            attributes.append(
                f"Sở thích: {format_list(tags)}"
            )

        places = request_data.get("places", [])

        if isinstance(places, list):
            attributes.append(
                f"Số địa điểm đầu vào: {len(places)}"
            )

    elif search_type == "place_recommendation":
        interests = request_data.get("interests", [])

        if interests:
            attributes.append(
                f"Sở thích: {format_list(interests)}"
            )

        mode = request_data.get("mode")

        if mode:
            attributes.append(
                f"Đối tượng: {MODE_LABELS.get(mode, mode)}"
            )

        budget = request_data.get("budget")

        if budget is not None:
            attributes.append(
                f"Ngân sách: {money_format(budget)}"
            )

        duration = request_data.get("duration")

        if duration is not None:
            attributes.append(
                f"Thời gian: {duration} ngày"
            )

    return attributes or ["Chưa có thuộc tính tìm kiếm"]


def request_json(method, url, **kwargs):
    timeout = kwargs.pop("timeout", 30)

    try:
        response = requests.request(
            method=method,
            url=url,
            timeout=timeout,
            **kwargs
        )

        response.raise_for_status()

        if not response.text.strip():
            return {}, None

        return response.json(), None

    except requests.exceptions.HTTPError as exc:
        message = ""
        try:
            message = exc.response.text
        except Exception:
            pass

        return None, f"Lỗi HTTP: {exc}. {message[:500]}"

    except requests.exceptions.RequestException as exc:
        return None, f"Không thể kết nối API: {exc}"

    except ValueError as exc:
        return None, f"Lỗi đọc dữ liệu JSON: {exc}"


# ============================================================
# 6. BACKEND API - ĐỊA ĐIỂM
# ============================================================

@st.cache_data(ttl=300)
def get_destinations():
    data, error = request_json(
        "GET",
        DESTINATIONS_API
    )

    if error:
        return []

    destinations = extract_list(
        data,
        ["data", "destinations", "items"]
    )

    # Một số API trả trực tiếp danh sách chuỗi.
    if not destinations and isinstance(data, dict):
        raw_data = data.get("data", [])
        if isinstance(raw_data, list):
            destinations = raw_data

    cleaned = []

    for item in destinations:
        if isinstance(item, str) and item.strip():
            cleaned.append(item.strip())

    return sorted(
        set(cleaned),
        key=str.casefold
    )


def get_recommendations(destination, interests, mode):
    payload = {
        "destination": destination,
        "interests": interests,
        "top_k": 10,
        "mode": mode,
    }

    data, error = request_json(
        "POST",
        RECOMMEND_API,
        json=payload
    )

    if error:
        st.error(
            f"Không thể kết nối API Recommendation: {error}"
        )
        return None

    return data


# ============================================================
# 7. BACKEND API - RANDOM CHALLENGE
# ============================================================

def run_random_challenge(destination):
    data, error = request_json(
        "POST",
        RANDOM_API,
        json={"destination": destination},
        timeout=60
    )

    if error:
        st.error(error)
        return None

    return data


# ============================================================
# 8. BACKEND API - LỊCH SỬ
# ============================================================

def save_search_history(
    keyword,
    destination,
    search_type,
    request_data,
    result_data
):
    """Lưu đầu vào và toàn bộ kết quả sau khi chức năng chạy."""

    payload = {
        "keyword": keyword,
        "destination": destination,
        "search_type": search_type,
        "request_data": request_data,
        "result_data": result_data,
    }

    data, error = request_json(
        "POST",
        HISTORY_API,
        json=payload
    )

    if error:
        st.warning(
            "Kết quả đã được tạo nhưng chưa lưu được lịch sử: "
            f"{error}"
        )
        return None

    return data


def get_search_history(search_type=None):
    """Lấy lịch sử, sắp xếp mới nhất lên trước."""

    params = {"limit": 100}

    if search_type:
        params["search_type"] = search_type

    data, error = request_json(
        "GET",
        HISTORY_API,
        params=params
    )

    if error:
        st.error(f"Không thể tải lịch sử: {error}")
        return []

    histories = extract_list(
        data,
        ["data", "items", "results"]
    )

    if search_type:
        histories = [
            item for item in histories
            if isinstance(item, dict)
            and item.get("search_type") == search_type
        ]

    def get_sort_time(item):
        value = item.get("created_at")

        try:
            if not value:
                return datetime.min.replace(
                    tzinfo=timezone.utc
                )

            if isinstance(value, str):
                value = datetime.fromisoformat(
                    value.replace("Z", "+00:00")
                )

            if value.tzinfo is None:
                value = value.replace(
                    tzinfo=timezone.utc
                )

            return value.astimezone(timezone.utc)

        except (ValueError, TypeError):
            return datetime.min.replace(
                tzinfo=timezone.utc
            )

    histories.sort(
        key=get_sort_time,
        reverse=True
    )

    return histories


def refresh_history_cache(search_type):
    st.session_state.history_by_type[search_type] = (
        get_search_history(search_type)
    )


def get_search_history_detail(history_id):
    data, error = request_json(
        "GET",
        f"{HISTORY_API}{history_id}",
        timeout=30
    )

    if error:
        st.error(
            f"Không thể tải chi tiết lịch sử: {error}"
        )
        return None

    if isinstance(data, dict):
        return data.get("data", data)

    return None



# ============================================================
# 9. BACKEND API - FOOD
# ============================================================

@st.cache_data(ttl=300)
def get_food_destinations():
    """
    Lấy danh sách địa điểm có dữ liệu món ăn.
    """

    data, error = request_json(
        "GET",
        API["food_destinations"]
    )

    if error:
        st.error(
            f"Không thể tải danh sách địa điểm món ăn: {error}"
        )
        return []

    raw_items = extract_list(
        data,
        ["data", "destinations", "items"]
    )

    # Hỗ trợ API trả về danh sách trực tiếp trong data.
    if not raw_items and isinstance(data, dict):
        raw_data = data.get("data", [])

        if isinstance(raw_data, list):
            raw_items = raw_data

    destinations = []

    for item in raw_items:

        if isinstance(item, str):
            name = item.strip()

        elif isinstance(item, dict):
            name = (
                item.get("destination")
                or item.get("name")
                or ""
            )

            name = str(name).strip()

        else:
            continue

        if name:
            destinations.append(name)

    return sorted(
        set(destinations),
        key=str.casefold
    )


def fetch_foods(
    destination=None,
    food_type=None,
    tag=None,
    limit=20,
    skip=0
):
    """
    Tìm kiếm món ăn từ Food API.

    Hỗ trợ:
    - Lọc theo địa điểm.
    - Lọc theo loại món.
    - Lọc theo tag.
    - Giới hạn số lượng kết quả.
    - Phân trang bằng skip.
    """

    params = {
        "limit": max(1, min(int(limit), 300)),
        "skip": max(0, int(skip))
    }

    # Lọc theo địa điểm.
    if destination and destination != "Tất cả":
        params["destination"] = destination

    # Lọc theo loại món.
    if food_type and food_type != "Tất cả":
        params["food_type"] = food_type

    # Lọc theo tag.
    if tag and str(tag).strip():
        params["tag"] = str(tag).strip()

    data, error = request_json(
        "GET",
        API["foods"],
        params=params
    )

    if error:
        st.error(
            f"Không thể tải danh sách món ăn: {error}"
        )
        return []

    foods = extract_list(
        data,
        ["data", "foods", "items", "results"]
    )

    return [
        food
        for food in foods
        if isinstance(food, dict)
    ]


def display_food_cards(foods):
    """
    Hiển thị danh sách món ăn.
    """

    if not foods:
        st.info(
            "Không tìm thấy món ăn phù hợp với bộ lọc hiện tại."
        )
        return

    st.caption(
        f"Tìm thấy {len(foods)} món ăn."
    )

    for index, food in enumerate(foods, start=1):

        if not isinstance(food, dict):
            continue

        # Tên món ăn.
        name = (
            food.get("name")
            or food.get("food_name")
            or "Món ăn chưa có tên"
        )

        with st.container(border=True):

            col_image, col_info = st.columns(
                [1, 2]
            )

            # ------------------------------------------------
            # ẢNH MÓN ĂN
            # ------------------------------------------------

            with col_image:

                image_url = (
                    food.get("image_url")
                    or food.get("image")
                )

                display_safe_image(image_url)

            # ------------------------------------------------
            # THÔNG TIN MÓN ĂN
            # ------------------------------------------------

            with col_info:

                st.markdown(
                    f"### {index}. {name}"
                )

                # Mô tả.
                description = (
                    food.get("description")
                    or food.get("detail")
                    or "Chưa có mô tả."
                )

                st.write(description)

                # Địa điểm.
                destination = food.get("destination")

                if destination:
                    st.write(
                        f"📍 **Địa điểm:** {destination}"
                    )

                # Loại món.
                food_type = (
                    food.get("food_type")
                    or food.get("type")
                    or food.get("category")
                )

                if food_type:
                    st.write(
                        f"🍽️ **Loại món:** {food_type}"
                    )

                # Giá.
                price = food.get("price")

                if price is None:
                    price = food.get("estimated_price")

                if price is not None:
                    st.write(
                        f"💰 **Giá tham khảo:** "
                        f"{money_format(price)}"
                    )

                # Đánh giá.
                rating = food.get("rating")

                if rating is not None:
                    st.write(
                        f"⭐ **Đánh giá:** {rating}"
                    )

                # Nguyên liệu.
                ingredients = food.get(
                    "ingredients",
                    []
                )

                if ingredients:
                    st.write(
                        "**Nguyên liệu:**",
                        format_list(ingredients)
                    )

                # Thông tin dị ứng.
                allergens = food.get(
                    "allergens",
                    []
                )

                if allergens:
                    st.warning(
                        "Thông tin dị ứng được ghi nhận: "
                        + format_list(allergens)
                    )
                else:
                    st.caption(
                        "Dữ liệu hiện chưa ghi nhận "
                        "thông tin dị ứng."
                    )

                # Tags.
                tags = food.get("tags", [])

                if tags:
                    st.write(
                        "🏷️ **Tags:**",
                        format_list(tags)
                    )





# ============================================================
# 10. BACKEND API - RESTAURANT
# ============================================================

from urllib.parse import quote_plus


def prune_safe_restaurants(
    destination,
    group_allergens,
    max_budget_per_person,
    group_size
):
    payload = {
        "destination": destination,
        "group_allergens": group_allergens,
        "max_budget_per_person": int(max_budget_per_person),
        "group_size": int(group_size),
    }

    data, error = request_json(
        "POST",
        API["restaurants_prune"],
        json=payload,
        timeout=60
    )

    if error:
        st.error(
            f"Không thể lọc nhà hàng an toàn: {error}"
        )
        return None

    st.session_state.restaurant_data = data
    st.session_state.selected_dining_places = []

    return data


# ============================================================
# LẤY DANH SÁCH NHÀ HÀNG
# ============================================================

def get_restaurant_list(result):

    if not isinstance(result, dict):
        return []

    restaurants = result.get("safe_restaurants")

    if isinstance(restaurants, list):
        return restaurants

    data = result.get("data")

    if isinstance(data, dict):
        restaurants = data.get("safe_restaurants")

        if isinstance(restaurants, list):
            return restaurants

    return extract_list(
        result,
        ["restaurants", "items", "results"]
    )


# ============================================================
# LẤY DANH SÁCH MÓN ĂN AN TOÀN
# ============================================================

def get_safe_dishes(result):

    if not isinstance(result, dict):
        return []

    dishes = result.get("safe_dishes")

    if isinstance(dishes, list):
        return dishes

    data = result.get("data")

    if isinstance(data, dict):
        dishes = data.get("safe_dishes")

        if isinstance(dishes, list):
            return dishes

    restaurants = get_restaurant_list(result)

    collected_dishes = []
    seen = set()

    for restaurant in restaurants:

        if not isinstance(restaurant, dict):
            continue

        restaurant_dishes = (
            restaurant.get("safe_dishes")
            or restaurant.get("dishes")
            or []
        )

        if not isinstance(restaurant_dishes, list):
            continue

        for dish in restaurant_dishes:

            if isinstance(dish, dict):

                dish_id = (
                    dish.get("dish_id")
                    or dish.get("id")
                    or dish.get("_id")
                )

                identity = (
                    str(dish_id)
                    if dish_id is not None
                    else str(
                        dish.get("dish_name")
                        or dish.get("name")
                        or dish.get("food_name")
                        or dish
                    )
                )

            else:
                identity = str(dish)

            if identity not in seen:
                seen.add(identity)
                collected_dishes.append(dish)

    return collected_dishes


# ============================================================
# HIỂN THỊ CHI TIẾT MÓN ĂN
# ============================================================

def display_dish_card(dish):

    if not isinstance(dish, dict):
        st.write(f"🍜 {dish}")
        return

    dish_name = (
        dish.get("dish_name")
        or dish.get("name")
        or dish.get("food_name")
        or "Món ăn chưa có tên"
    )

    price = dish.get("price")

    ingredients = dish.get("ingredients") or []
    allergens = dish.get("allergens") or []
    matched_allergens = dish.get("matched_allergens") or []

    with st.container(border=True):

        st.markdown(f"**🍜 {dish_name}**")

        col_price, col_signature = st.columns(2)

        with col_price:

            if price is not None:
                st.write(
                    f"💰 **Giá:** {money_format(price)}"
                )
            else:
                st.write(
                    "💰 **Giá:** Chưa có dữ liệu"
                )

        with col_signature:

            if dish.get("is_signature") is True:
                st.write("⭐ **Món đặc trưng**")

        st.divider()

        if ingredients:
            st.markdown("**🥬 Nguyên liệu**")
            st.write(format_list(ingredients))
        else:
            st.caption(
                "Chưa có thông tin nguyên liệu."
            )

        if allergens:
            st.markdown(
                "**⚠️ Thành phần dị ứng được ghi nhận**"
            )
            st.write(format_list(allergens))
        else:
            st.caption(
                "Chưa có thông tin thành phần dị ứng."
            )

        if matched_allergens:
            st.warning(
                "Thành phần trùng với danh sách cần tránh: "
                + format_list(matched_allergens)
            )

        if dish.get("reason"):
            st.info(
                f"Thông tin lọc: {dish['reason']}"
            )


# ============================================================
# GOOGLE MAPS - NHÀ HÀNG
# Chỉ sử dụng name + address + destination
# ============================================================

def get_restaurant_google_maps_url(restaurant):

    if not isinstance(restaurant, dict):
        return ""

    name = restaurant.get("name") or ""
    address = restaurant.get("address") or ""
    destination = restaurant.get("destination") or ""

    search_parts = [
        str(part).strip()
        for part in [
            name,
            address,
            destination,
            "Việt Nam"
        ]
        if part and str(part).strip()
    ]

    if not search_parts:
        return ""

    query = ", ".join(search_parts)

    return (
        "https://www.google.com/maps/search/?api=1&query="
        + quote_plus(query)
    )


# ============================================================
# HIỂN THỊ DANH SÁCH NHÀ HÀNG
# ============================================================
def display_restaurants(result, key_prefix="restaurant"):

    if not isinstance(result, dict):
        st.warning(
            "Dữ liệu nhà hàng không hợp lệ."
        )
        return

    restaurants = get_restaurant_list(result)
    all_dishes = get_safe_dishes(result)

    st.subheader(
        "🍽️ Danh sách nhà hàng phù hợp"
    )

    if not restaurants:

        st.info(
            "Không tìm thấy nhà hàng phù hợp với điều kiện hiện tại."
        )

    else:

        st.caption(
            f"Tìm thấy {len(restaurants)} nhà hàng phù hợp."
        )

        selected_ids = []

        for index, restaurant in enumerate(
            restaurants,
            start=1
        ):

            if not isinstance(restaurant, dict):
                continue

            name = (
                restaurant.get("name")
                or "Nhà hàng chưa có tên"
            )

            restaurant_id = str(
                restaurant.get("id")
                or restaurant.get("_id")
                or name
            )

            restaurant_dishes = (
                restaurant.get("safe_dishes")
                or restaurant.get("dishes")
                or []
            )

            if not isinstance(restaurant_dishes, list):
                restaurant_dishes = []

            with st.container(border=True):

                # ----------------------------------------
                # THÔNG TIN NHÀ HÀNG
                # ----------------------------------------

                st.markdown(
                    f"### 🍽️ {index}. {name}"
                )

                col_image, col_info = st.columns([1, 2])

                with col_image:

                    display_safe_image(
                        restaurant.get("image_url")
                    )

                with col_info:

                    address = restaurant.get("address")

                    if address:
                        st.write(f"📍 {address}")

                    rating = restaurant.get("rating")

                    if rating is not None:
                        st.write(
                            f"⭐ Đánh giá: {rating}/5"
                        )

                    avg_cost = restaurant.get(
                        "avg_cost_per_person"
                    )

                    if avg_cost is not None:
                        st.write(
                            "💰 Chi phí trung bình/người: "
                            f"{money_format(avg_cost)}"
                        )

                    price_range = restaurant.get(
                        "price_range"
                    )

                    if price_range:
                        st.write(
                            f"💵 Khoảng giá: {price_range}"
                        )

                    description = restaurant.get(
                        "description"
                    )

                    if description:
                        st.write(description)

                    # Google Maps sử dụng địa chỉ thật.
                    map_url = get_restaurant_google_maps_url(
                        restaurant
                    )

                    if map_url:
                        st.markdown(
                            f"[📍 Xem trên Google Maps]({map_url})"
                        )

                # ----------------------------------------
                # THÔNG TIN CHUYÊN MÓN
                # ----------------------------------------

                specialties = restaurant.get(
                    "specialties"
                ) or []

                if specialties:
                    st.markdown("**🍜 Món đặc trưng**")
                    st.write(format_list(specialties))

                # ----------------------------------------
                # THÔNG TIN NGUY CƠ NHIỄM CHÉO
                # ----------------------------------------

                contamination_risk = restaurant.get(
                    "cross_contamination_risk"
                )

                if contamination_risk:

                    risk_labels = {
                        "low": "Thấp",
                        "medium": "Trung bình",
                        "high": "Cao"
                    }

                    risk_text = risk_labels.get(
                        str(contamination_risk).lower(),
                        str(contamination_risk)
                    )

                    st.write(
                        f"⚠️ Nguy cơ nhiễm chéo: {risk_text}"
                    )

                st.divider()

                # ----------------------------------------
                # CÁC MÓN ĂN CỦA NHÀ HÀNG
                # ----------------------------------------

                st.markdown(
                    "#### 🥘 Các món ăn của nhà hàng"
                )

                if restaurant_dishes:

                    st.caption(
                        f"Có {len(restaurant_dishes)} món ăn được ghi nhận."
                    )

                    for dish_index, dish in enumerate(
                        restaurant_dishes,
                        start=1
                    ):

                        st.markdown(
                            f"**Món {dish_index}**"
                        )

                        display_dish_card(dish)

                else:

                    st.info(
                        "Nhà hàng chưa có thông tin món ăn."
                    )

                st.divider()

                # ----------------------------------------
                # CHỌN NHÀ HÀNG CHO LỊCH TRÌNH
                # ----------------------------------------

                current_selected = (
                    st.session_state.get(
                        "selected_dining_places",
                        []
                    )
                )

                already_selected = any(
                    isinstance(item, dict)
                    and str(
                        item.get("id")
                        or item.get("_id")
                        or item.get("name")
                    ) == restaurant_id
                    for item in current_selected
                )

                checked = st.checkbox(
                    "Chọn nhà hàng này cho lịch trình",
                    value=already_selected,
                    key=f"{key_prefix}_select_{restaurant_id}"
                )

                if checked:
                    selected_ids.append(restaurant_id)

        # Lưu danh sách nhà hàng được chọn.
        st.session_state.selected_dining_places = [
            restaurant
            for restaurant in restaurants
            if isinstance(restaurant, dict)
            and str(
                restaurant.get("id")
                or restaurant.get("_id")
                or restaurant.get("name")
            ) in selected_ids
        ]

    # ========================================================
    # DANH SÁCH TỔNG HỢP TOÀN BỘ MÓN ĂN
    # ========================================================

    st.divider()

    st.subheader(
        "🥘 Toàn bộ món ăn đã qua bộ lọc"
    )

    st.write(
        "Danh sách tổng hợp các món ăn được trả về "
        "từ những nhà hàng phù hợp với điều kiện tìm kiếm."
    )

    if all_dishes:

        st.success(
            f"Tổng cộng {len(all_dishes)} món ăn được ghi nhận."
        )

        for index, dish in enumerate(
            all_dishes,
            start=1
        ):

            st.markdown(
                f"**MÓN ĂN {index}**"
            )

            display_dish_card(dish)

    else:

        st.info(
            "Chưa có thông tin món ăn được trả về."
        )

    # ========================================================
    # LƯU Ý VỀ DỊ ỨNG
    # ========================================================

    st.warning(
        "Lưu ý: Kết quả lọc dựa trên thông tin có trong dữ liệu. "
        "Nếu thành viên có dị ứng, hãy xác nhận trực tiếp với "
        "nhà hàng về thành phần nguyên liệu và nguy cơ nhiễm chéo."
    )

# ============================================================
# 11. SCHEDULER - TẠO LỊCH TRÌNH
# ============================================================

def create_travel_schedule():
    """
    Scheduler sử dụng kết quả AI Recommendation.
    Không sử dụng Random Challenge.
    Không chạy Simulated Annealing ở Frontend.

    Nếu đã lọc nhà hàng:
    - tv2_result nhận safe_dishes từ kết quả lọc.
    - tv3_result nhận nhà hàng người dùng đã chọn.
    """

    places = st.session_state.get("results", [])

    if not isinstance(places, list) or not places:
        st.warning(
            "Bạn cần tạo kết quả AI Recommendation trước khi lập lịch."
        )
        return None

    interests = [
        HOBBY_TAGS[item]
        for item in st.session_state.get("hobby", [])
        if item in HOBBY_TAGS
    ]

    input_context = {
        "destination": st.session_state.get("place", ""),
        "duration": int(
            st.session_state.get("duration", 1)
        ),
        "tags": interests,
    }

    restaurant_data = (
        st.session_state.get("restaurant_data") or {}
    )

    safe_dishes = get_safe_dishes(restaurant_data)

    selected_restaurants = (
        st.session_state.get("selected_dining_places") or []
    )

    # Chỉ đưa nhà hàng đã được người dùng chọn vào Scheduler.
    # Nếu chưa chọn nhà hàng, Scheduler vẫn có thể chạy với danh sách rỗng.
    dining = selected_restaurants

    payload = {
        "input_context": input_context,
        "places": places,
        "tv2_result": {
            "safe_dishes": safe_dishes
        },
        "tv3_result": {
            "restaurants": dining
        },
    }

    data, error = request_json(
        "POST",
        SCHEDULER_API,
        json=payload,
        timeout=60
    )

    if error:
        st.error(
            f"Không thể tạo lịch trình: {error}"
        )
        return None

    if isinstance(data, dict) and data.get("success"):
        saved = save_search_history(
            keyword=(
                f"Lịch trình {input_context['duration']} ngày"
            ),
            destination=input_context["destination"],
            search_type="scheduler",
            request_data={
                "input_context": input_context,
                "places": places,
                "tv2_result": {
                    "safe_dishes": safe_dishes
                },
                "tv3_result": {
                    "restaurants": dining
                },
            },
            result_data=data
        )

        if saved:
            refresh_history_cache("scheduler")
            st.success(
                "Đã tạo lịch trình và lưu lịch sử thành công!"
            )
        else:
            st.warning(
                "Đã tạo lịch trình nhưng chưa lưu được lịch sử."
            )

    return data


# ============================================================
# 12. HIỂN THỊ KẾT QUẢ AI RECOMMENDATION
# ============================================================

def display_recommendations(results, destination=None):
    st.subheader("Danh sách địa điểm gợi ý")

    if not results:
        st.warning(
            "Không tìm thấy địa điểm phù hợp. "
            "Bạn thử thay đổi sở thích nhé!"
        )
        return

    destination = (
        destination
        or st.session_state.get("place", "")
    )

    for item in results:
        if not isinstance(item, dict):
            continue

        name = item.get("name", "Chưa có tên")

        with st.container(border=True):
            st.subheader(name)

            display_safe_image(
                item.get("image_url")
            )

            rating = item.get("rating", 0)

            st.write(
                f"⭐ Đánh giá: {rating}/5"
            )

            st.write(
                item.get("description") or "Chưa có mô tả."
            )

            tags = item.get("tags", [])

            st.write(
                "🏷️ Sở thích phù hợp:",
                format_list(tags)
            )

            score = item.get("score", 0)

            try:
                score_text = f"{float(score) * 100:.1f}%"
            except (ValueError, TypeError):
                score_text = str(score)

            st.write(
                f"🎯 Điểm phù hợp: {score_text}"
            )

            map_url = get_google_maps_url(
                name,
                destination
            )

            st.markdown(
                f"[📍 Xem trên Google Maps]({map_url})"
            )


# ============================================================
# 13. HIỂN THỊ ĐỊA ĐIỂM RANDOM
# ============================================================

def display_random_places(places, destination):
    if not places:
        st.warning(
            "Không tìm thấy địa điểm phù hợp với tags được chọn."
        )
        return

    st.success(
        f"Thuật toán tìm được {len(places)} địa điểm."
    )

    for index, item in enumerate(places, start=1):
        if not isinstance(item, dict):
            continue

        name = item.get(
            "name",
            "Địa điểm chưa có tên"
        )

        with st.container(border=True):
            col_image, col_info = st.columns([1, 2])

            with col_image:
                display_safe_image(
                    item.get("image_url")
                )

            with col_info:
                st.markdown(
                    f"### {index}. {name}"
                )

                rating = item.get("rating")

                if rating is not None:
                    st.write(
                        f"⭐ Rating: {rating}"
                    )

                place_tags = item.get("tags", [])

                st.write("**Tags của địa điểm:**")
                st.write(format_list(place_tags))

                matched_tags = item.get(
                    "matched_tags",
                    []
                )

                st.write("**Tags khớp với thử thách:**")

                if matched_tags:
                    st.success(
                        format_list(matched_tags)
                    )
                else:
                    st.write(
                        "Không có thông tin tags khớp."
                    )

                match_count = item.get(
                    "match_count",
                    len(matched_tags)
                    if isinstance(matched_tags, list)
                    else 0
                )

                st.write(
                    f"**Số tags khớp:** {match_count}"
                )

                match_ratio = item.get("match_ratio")

                if match_ratio is not None:
                    st.write(
                        f"**Tỷ lệ khớp:** {match_ratio}"
                    )

                map_url = get_google_maps_url(
                    name,
                    destination
                )

                st.markdown(
                    f"[📍 Xem trên Google Maps]({map_url})"
                )


# ============================================================
# 14. HIỂN THỊ KẾT QUẢ RANDOM CHALLENGE
# ============================================================

def display_random_result(result):
    if not isinstance(result, dict):
        return

    data = result.get("data", {})

    if not isinstance(data, dict):
        st.error(
            "Dữ liệu trả về từ Random Challenge không hợp lệ."
        )
        return

    destination = result.get(
        "destination",
        st.session_state.get("random_destination", "")
    )

    tags = data.get("tags", [])
    fitness = data.get("fitness")
    places = data.get("places", [])

    st.divider()

    st.markdown(
        '<div class="random-heading">'
        '🎉 KẾT QUẢ RANDOM CHALLENGE'
        '</div>',
        unsafe_allow_html=True
    )

    st.write(f"**Điểm đến:** {destination}")

    st.subheader("🎯 Tags ngẫu nhiên được lựa chọn")

    if tags:
        tag_columns = st.columns(
            min(len(tags), 4)
        )

        for index, tag in enumerate(tags):
            with tag_columns[index % len(tag_columns)]:
                st.info(f"🏷️ {tag}")
    else:
        st.warning("Backend chưa trả về tags.")

    if fitness is not None:
        st.metric("Fitness", fitness)

    st.divider()

    st.subheader(
        "📍 Địa điểm được tìm thấy từ các tags"
    )

    display_random_places(
        places,
        destination
    )



# ============================================================
# 15. HIỂN THỊ KẾT QUẢ SCHEDULER
# ============================================================

def unwrap_schedule_result(result):
    """Hỗ trợ response Scheduler có thể được bọc trong data."""

    current = result

    for _ in range(3):
        if not isinstance(current, dict):
            break

        if isinstance(current.get("schedule"), list):
            return current

        nested = current.get("data")

        if isinstance(nested, dict):
            current = nested
        else:
            break

    return current


def get_activity_details(activity):
    """
    Lấy dữ liệu chi tiết từ activity hoặc object lồng bên trong.
    Hỗ trợ các cấu trúc place, restaurant, details, data.
    """

    if not isinstance(activity, dict):
        return {}

    details = dict(activity)

    nested_keys = [
        "details",
        "place",
        "restaurant",
        "place_data",
        "restaurant_data",
        "source",
        "data",
    ]

    for key in nested_keys:
        nested = activity.get(key)

        if isinstance(nested, dict):
            details.update(nested)

    return details


def get_schedule_activity_type(activity):
    """Chỉ nhận địa điểm và nhà hàng."""

    if not isinstance(activity, dict):
        return None

    activity_type = str(
        activity.get("type")
        or activity.get("category")
        or ""
    ).strip().casefold()

    if activity_type in [
        "place",
        "places",
        "địa điểm",
        "dia diem",
    ]:
        return "place"

    if activity_type in [
        "restaurant",
        "restaurants",
        "nhà hàng",
        "nha hang",
    ]:
        return "restaurant"

    # Dự phòng nếu backend thiếu type nhưng có dữ liệu nhận diện.
    if (
        activity.get("restaurant_name")
        or activity.get("safe_dishes")
        or activity.get("dishes")
    ):
        return "restaurant"

    if (
        activity.get("matched_tags")
        or activity.get("match_ratio") is not None
        or activity.get("fitness") is not None
    ):
        return "place"

    return None


def get_schedule_activity_name(activity, details):
    return (
        details.get("name")
        or details.get("restaurant_name")
        or details.get("place_name")
        or activity.get("name")
        or activity.get("restaurant_name")
        or activity.get("place_name")
        or "Chưa có tên"
    )


def display_place_schedule_detail(details):
    """Hiển thị chi tiết địa điểm giống trang Tìm địa điểm."""

    st.markdown("**📍 Thông tin địa điểm**")

    image_url = (
        details.get("image_url")
        or details.get("image")
    )

    if image_url:
        display_safe_image(image_url)

    rating = details.get("rating")

    if rating is not None:
        st.write(f"⭐ **Đánh giá:** {rating}/5")

    description = details.get("description")

    if description:
        st.write("**📝 Mô tả:**")
        st.write(description)

    destination = details.get("destination")

    if destination:
        st.write(f"📍 **Điểm đến:** {destination}")

    address = (
        details.get("address")
        or details.get("location")
    )

    if address:
        st.write(f"🏠 **Địa chỉ:** {address}")

    tags = (
        details.get("matched_tags")
        or details.get("tags")
        or []
    )

    if tags:
        st.write(
            "🏷️ **Sở thích phù hợp:**",
            format_list(tags)
        )

    fitness = (
        details.get("match_ratio")
        if details.get("match_ratio") is not None
        else details.get("fitness")
    )

    if fitness is not None:
        try:
            fitness = float(fitness)

            # Hỗ trợ cả tỷ lệ dạng 0.548 và phần trăm dạng 54.8.
            if 0 <= fitness <= 1:
                fitness *= 100

            st.write(
                f"🎯 **Điểm phù hợp:** {fitness:.1f}%"
            )
        except (TypeError, ValueError):
            st.write(f"🎯 **Điểm phù hợp:** {fitness}")

    map_location = address or destination

    if map_location:
        map_url = get_google_maps_url(
            get_schedule_activity_name(details, details),
            map_location
        )

        st.markdown(
            f"[📍 Xem trên Google Maps]({map_url})"
        )


def display_restaurant_schedule_detail(details):
    """Hiển thị chi tiết nhà hàng và toàn bộ món ăn."""

    st.markdown("**🍽️ Thông tin nhà hàng**")

    image_url = (
        details.get("image_url")
        or details.get("image")
    )

    if image_url:
        display_safe_image(image_url)

    rating = details.get("rating")

    if rating is not None:
        st.write(f"⭐ **Đánh giá:** {rating}/5")

    address = (
        details.get("address")
        or details.get("location")
    )

    if address:
        st.write(f"📍 **Địa chỉ:** {address}")

    destination = details.get("destination")

    if destination:
        st.write(f"🗺️ **Điểm đến:** {destination}")

    description = details.get("description")

    if description:
        st.write("**📝 Mô tả:**")
        st.write(description)

    price = (
        details.get("average_price")
        or details.get("price")
        or details.get("estimated_price")
    )

    if price is not None:
        st.write(
            f"💰 **Giá tham khảo:** {money_format(price)}"
        )

    map_location = address or destination

    restaurant_name = (
        details.get("name")
        or details.get("restaurant_name")
        or "Nhà hàng"
    )

    if map_location:
        map_url = get_google_maps_url(
            restaurant_name,
            map_location
        )

        st.markdown(
            f"[📍 Xem trên Google Maps]({map_url})"
        )

    # --------------------------------------------------------
    # TOÀN BỘ MÓN ĂN CỦA NHÀ HÀNG
    # --------------------------------------------------------

    dishes = (
        details.get("safe_dishes")
        or details.get("dishes")
        or details.get("foods")
        or []
    )

    if not isinstance(dishes, list):
        dishes = []

    st.divider()
    st.markdown("**🥘 Danh sách món ăn của nhà hàng**")

    if not dishes:
        st.info(
            "Chưa có thông tin món ăn được lưu trong dữ liệu lịch trình."
        )
        return

    st.caption(f"Tổng cộng {len(dishes)} món ăn.")

    for dish_index, dish in enumerate(dishes, start=1):
        if isinstance(dish, dict):
            dish_name = (
                dish.get("dish_name")
                or dish.get("name")
                or dish.get("food_name")
                or f"Món ăn {dish_index}"
            )
        else:
            dish_name = str(dish)

        with st.expander(
            f"🍜 {dish_index}. {dish_name}",
            expanded=False
        ):
            display_dish_card(dish)


def display_schedule_result(result):
    if not result:
        return

    if not isinstance(result, dict):
        st.warning("Dữ liệu lịch trình không hợp lệ.")
        return

    result = unwrap_schedule_result(result)

    if not isinstance(result, dict):
        st.warning("Không đọc được dữ liệu lịch trình.")
        return

    if result.get("success") is False:
        st.error(
            result.get(
                "message",
                "Không thể tạo lịch trình."
            )
        )
        return

    schedule = result.get("schedule", [])

    if not isinstance(schedule, list):
        schedule = []

    if not schedule:
        st.warning(
            "Backend chưa trả về danh sách lịch trình."
        )
        return

    # Chỉ giữ hoạt động địa điểm và nhà hàng.
    filtered_schedule = []

    for day_index, day in enumerate(schedule, start=1):
        if not isinstance(day, dict):
            continue

        activities = day.get("activities", [])

        if not isinstance(activities, list):
            activities = []

        visible_activities = []

        for activity in activities:
            if not isinstance(activity, dict):
                continue

            activity_type = get_schedule_activity_type(activity)

            if activity_type in ["place", "restaurant"]:
                visible_activities.append(
                    (activity, activity_type)
                )

        filtered_schedule.append({
            "day": day.get("day", day_index),
            "activities": visible_activities
        })

    total_activities = sum(
        len(day["activities"])
        for day in filtered_schedule
    )

    # --------------------------------------------------------
    # TỔNG QUAN LỊCH TRÌNH
    # --------------------------------------------------------

    st.success("Đã tạo lịch trình thành công!")

    col1, col2 = st.columns(2)

    col1.metric(
        "Tổng số ngày",
        len(filtered_schedule)
    )

    col2.metric(
        "Địa điểm & nhà hàng",
        total_activities
    )

    st.caption(
        "Các món ăn được hiển thị bên trong phần chi tiết "
        "nhà hàng, không được tính thành hoạt động riêng."
    )

    st.divider()

    # --------------------------------------------------------
    # HIỂN THỊ TỪNG NGÀY
    # --------------------------------------------------------

    for day in filtered_schedule:

        day_number = day["day"]
        activities = day["activities"]

        st.markdown(
            f"### 📅 Ngày {day_number}"
        )

        if not activities:
            st.info(
                "Ngày này chưa có địa điểm hoặc nhà hàng."
            )
            st.divider()
            continue

        for activity_index, item in enumerate(
            activities,
            start=1
        ):
            activity, activity_type = item

            details = get_activity_details(activity)

            activity_name = get_schedule_activity_name(
                activity,
                details
            )

            time_value = (
                activity.get("time")
                or activity.get("start_time")
            )

            description = (
                details.get("description")
                or activity.get("description")
            )

            address = (
                details.get("address")
                or details.get("location")
                or activity.get("address")
                or activity.get("location")
            )

            image_url = (
                details.get("image_url")
                or details.get("image")
            )

            # ------------------------------------------------
            # THẺ TÓM TẮT
            # ------------------------------------------------

            with st.container(border=True):

                col_image, col_info = st.columns(
                    [1, 3],
                    vertical_alignment="center"
                )

                with col_image:
                    if image_url:
                        display_safe_image(image_url)

                with col_info:
                    if activity_type == "place":
                        st.markdown(
                            f"**📍 {activity_index}. {activity_name}**"
                        )
                        st.caption("Địa điểm tham quan")
                    else:
                        st.markdown(
                            f"**🍽️ {activity_index}. {activity_name}**"
                        )
                        st.caption("Nhà hàng")

                    if time_value:
                        st.caption(f"🕒 {time_value}")

                    if address:
                        st.caption(f"📍 {address}")

                    if description:
                        short_description = str(description)

                        if len(short_description) > 180:
                            short_description = (
                                short_description[:180] + "..."
                            )

                        st.write(short_description)

                # ------------------------------------------------
                # CHI TIẾT CÓ THỂ MỞ / THU GỌN
                # ------------------------------------------------

                with st.expander(
                    "🔎 Xem chi tiết",
                    expanded=False
                ):

                    if activity_type == "place":
                        display_place_schedule_detail(
                            details
                        )

                    elif activity_type == "restaurant":
                        display_restaurant_schedule_detail(
                            details
                        )

        st.divider()



# ============================================================
# 16. HIỂN THỊ CHI TIẾT LỊCH SỬ
# ============================================================

def display_history_detail(detail):

    if not isinstance(detail, dict):
        return

    st.divider()

    st.subheader(
        "📖 Chi tiết lần tìm kiếm đã lưu"
    )

    history_id = detail.get(
        "id",
        detail.get("_id", "unknown")
    )

    if st.button(
        "✖ Đóng chi tiết",
        key=f"close_detail_{history_id}"
    ):
        st.session_state.selected_history_id = None
        st.session_state.selected_history_detail = None
        st.rerun()

    st.write(
        f"**Từ khóa:** {detail.get('keyword', 'Không có')}"
    )

    st.write(
        f"**Điểm đến:** {detail.get('destination') or 'Không có'}"
    )

    st.write(
        f"**Thời gian:** {format_datetime(detail.get('created_at'))}"
    )

    search_type = detail.get("search_type")

    extra_type_labels = {
        "restaurant": "Nhà hàng",
        "food": "Món ăn",
    }

    st.write(
        "**Loại lịch sử:** "
        f"{HISTORY_TYPE_LABELS.get(search_type, extra_type_labels.get(search_type, search_type))}"
    )

    request_data = detail.get("request_data", {})

    if request_data:
        with st.expander("📥 Xem đầy đủ thông tin đầu vào"):
            st.json(request_data)

    result_data = detail.get("result_data")

    if result_data is None:
        st.warning(
            "Lịch sử này chưa lưu nội dung kết quả chi tiết."
        )
        return

    st.divider()

    # --------------------------------------------------------
    # RANDOM CHALLENGE
    # --------------------------------------------------------

    if search_type == "random_challenge":

        display_random_result(result_data)

    # --------------------------------------------------------
    # SCHEDULER
    # --------------------------------------------------------

    elif search_type == "scheduler":

        display_schedule_result(result_data)

    # --------------------------------------------------------
    # AI RECOMMENDATION
    # --------------------------------------------------------

    elif search_type == "place_recommendation":

        if isinstance(result_data, dict):

            recommendation_results = (
                result_data.get("data")
                or result_data.get("results")
                or result_data.get("places")
                or result_data.get("recommendations")
                or []
            )

            if isinstance(recommendation_results, dict):
                recommendation_results = extract_list(
                    recommendation_results
                )

        elif isinstance(result_data, list):

            recommendation_results = result_data

        else:

            recommendation_results = []

        display_recommendations(
            recommendation_results,
            detail.get("destination", "")
        )

    # --------------------------------------------------------
    # RESTAURANT
    # --------------------------------------------------------

    elif search_type == "restaurant":

        st.subheader(
            "🍽️ Kết quả lọc nhà hàng đã lưu"
        )

        display_restaurants(
            result_data,
            key_prefix="history_restaurant"
        )

    # --------------------------------------------------------
    # FOOD
    # --------------------------------------------------------

    elif search_type == "food":

        st.subheader(
            "🍜 Danh sách món ăn đã lưu"
        )

        food_items = []

        if isinstance(result_data, list):

            food_items = result_data

        elif isinstance(result_data, dict):

            for key in [
                "foods",
                "data",
                "items",
                "results",
            ]:

                value = result_data.get(key)

                if isinstance(value, list):

                    food_items = value
                    break

                if isinstance(value, dict):

                    for nested_key in [
                        "foods",
                        "items",
                        "results",
                    ]:

                        nested_value = value.get(nested_key)

                        if isinstance(nested_value, list):
                            food_items = nested_value
                            break

                    if food_items:
                        break

        if food_items:

            display_food_cards(food_items)

        else:

            st.info(
                "Bản ghi này không có danh sách món ăn để hiển thị."
            )

    else:

        st.json(result_data)

    # --------------------------------------------------------
    # DỮ LIỆU GỐC
    # --------------------------------------------------------

    with st.expander(
        "📦 Xem toàn bộ dữ liệu kết quả gốc"
    ):
        st.json(result_data)

# ============================================================
# 17. TẢI DANH SÁCH ĐIỂM ĐẾN
# ============================================================

destinations = get_destinations()

recommendation_destinations = destinations or [
    "Hà Nội",
    "Đà Nẵng",
    "Thành phố Hồ Chí Minh",
]

destination_options = ["Toàn Việt Nam"] + destinations

food_destinations = get_food_destinations()

if not food_destinations:
    food_destinations = destinations

if not food_destinations:
    food_destinations = [
        "Hà Nội",
        "Đà Nẵng",
        "Thành phố Hồ Chí Minh",
    ]


# ============================================================
# 18. HEADER
# ============================================================

st.markdown(
    '<div class="main-title">✈️ TravelMate AI</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="sub-title">'
    'Your AI-powered travel companion'
    '</div>',
    unsafe_allow_html=True
)


# ============================================================
# 19. CÁC TAB CHÍNH
# ============================================================

tab_home, tab_food, tab_restaurant, tab_random, tab_schedule, tab_history = st.tabs(
    [
        "Trang chủ",
        "🍜 Ẩm thực",
        "🍽️ Nhà hàng",
        "🎲 Random Challenge",
        "🗓️ Lịch trình",
        "📚 Lịch sử",
    ]
)


# ============================================================
# 20. TAB TRANG CHỦ - AI RECOMMENDATION TV4
# ============================================================

with tab_home:

    with st.sidebar:
        st.header("Đặc điểm cá nhân nổi bật")

        mode_values = list(MODE_OPTIONS.values())

        current_mode = st.session_state.mode

        if current_mode not in mode_values:
            current_mode = "solo"

        selected_mode = st.selectbox(
            "Bạn đi du lịch với ai?",
            options=list(MODE_OPTIONS.keys()),
            index=mode_values.index(current_mode),
        )

        mode = MODE_OPTIONS[selected_mode]

        hobby = st.multiselect(
            "Sở thích",
            list(HOBBY_TAGS.keys()),
            default=[
                item
                for item in st.session_state.hobby
                if item in HOBBY_TAGS
            ],
        )

        default_place = st.session_state.place

        if default_place not in recommendation_destinations:
            default_place = recommendation_destinations[0]

        place = st.selectbox(
            "Thành phố dự kiến muốn đi",
            recommendation_destinations,
            index=recommendation_destinations.index(default_place),
        )

        budget = st.number_input(
            "Ngân sách dự kiến (VNĐ)",
            min_value=100000,
            max_value=10000000,
            value=int(st.session_state.budget),
            step=100000,
        )

        duration = st.number_input(
            "Thời gian dự kiến (Ngày)",
            min_value=1,
            max_value=10,
            value=int(st.session_state.duration),
            step=1,
        )

        submit = st.button(
            "Tìm kiếm địa điểm AI",
            type="primary",
            use_container_width=True,
        )

    if submit:
        if not hobby:
            st.warning(
                "Bạn hãy chọn ít nhất một sở thích nhé!"
            )

        else:
            interests = [
                HOBBY_TAGS[item]
                for item in hobby
            ]

            with st.spinner(
                "TravelMate đang tìm địa điểm phù hợp..."
            ):
                data = get_recommendations(
                    place,
                    interests,
                    mode,
                )

            if data is not None:
                if isinstance(data, dict):
                    results = data.get("data", [])
                elif isinstance(data, list):
                    results = data
                else:
                    results = []

                if not isinstance(results, list):
                    results = []

                st.session_state.results = results
                st.session_state.recommendation_response = data
                st.session_state.schedule_result = None
                st.session_state.is_submitted = True

                st.session_state.mode = mode
                st.session_state.place = place
                st.session_state.budget = budget
                st.session_state.duration = duration
                st.session_state.hobby = hobby

                saved = save_search_history(
                    keyword="Tìm kiếm địa điểm theo sở thích",
                    destination=place,
                    search_type="place_recommendation",
                    request_data={
                        "destination": place,
                        "interests": interests,
                        "mode": mode,
                        "budget": budget,
                        "duration": duration,
                    },
                    result_data=data,
                )

                if saved:
                    refresh_history_cache(
                        "place_recommendation"
                    )

                    st.success(
                        "Đã tìm kiếm và lưu lịch sử thành công!"
                    )

    if not st.session_state.is_submitted:
        st.info(
            "Chào mừng bạn đến với TravelMate AI! "
            "Vui lòng điền thông tin bên thanh sidebar "
            "để nhận gợi ý."
        )

    else:
        st.write(
            "**Chế độ du lịch:**",
            MODE_LABELS.get(
                st.session_state.mode,
                st.session_state.mode,
            ),
        )

        col_card, col_map = st.columns([1, 1])

        with col_map:
            st.subheader("Bản đồ gợi ý")

            st.info(
                "Chọn địa điểm trong danh sách kết quả "
                "để xem vị trí trên Google Maps."
            )

            if st.session_state.results:
                for item in st.session_state.results:
                    if isinstance(item, dict) and item.get("name"):
                        map_url = get_google_maps_url(
                            item["name"],
                            st.session_state.place,
                        )

                        st.markdown(
                            f"[📍 {item['name']}]({map_url})"
                        )

        with col_card:
            display_recommendations(
                st.session_state.results,
                st.session_state.place,
            )



# ============================================================
# 21. TAB ẨM THỰC - FOOD
# ============================================================

with tab_food:

    st.title("🍜 Khám phá ẩm thực địa phương")

    st.write(
        "Tìm hiểu các món ăn đặc trưng theo từng tỉnh/thành."
    )

    st.divider()

    # --------------------------------------------------------
    # KIỂM TRA DANH SÁCH ĐỊA ĐIỂM
    # --------------------------------------------------------

    if not food_destinations:

        st.warning(
            "Chưa tải được danh sách địa điểm có dữ liệu món ăn. "
            "Vui lòng kiểm tra kết nối Backend hoặc API Food."
        )

    else:

        food_col1, food_col2 = st.columns(2)

        # ----------------------------------------------------
        # CHỌN ĐIỂM ĐẾN
        # ----------------------------------------------------

        with food_col1:

            default_food_destination = (
                st.session_state.get(
                    "food_destination",
                    "Tất cả"
                )
            )

            destination_options = (
                ["Tất cả"] + food_destinations
            )

            if default_food_destination not in destination_options:
                default_food_destination = "Tất cả"

            selected_food_destination = st.selectbox(
                "Chọn điểm đến",
                destination_options,
                index=destination_options.index(
                    default_food_destination
                ),
                key="food_destination_select",
            )

        # ----------------------------------------------------
        # CHỌN LOẠI MÓN
        # ----------------------------------------------------

        with food_col2:

            food_type_options = (
                FOOD_TYPE_OPTIONS
                if FOOD_TYPE_OPTIONS
                else ["Tất cả"]
            )

            selected_food_type = st.selectbox(
                "Loại món ăn",
                food_type_options,
                index=(
                    food_type_options.index(
                        st.session_state.get(
                            "food_type",
                            "Tất cả"
                        )
                    )
                    if st.session_state.get(
                        "food_type",
                        "Tất cả"
                    ) in food_type_options
                    else 0
                ),
                key="food_type_select",
            )

        # ----------------------------------------------------
        # TÌM THEO TAG
        # ----------------------------------------------------

        food_tag = st.text_input(
            "Tìm theo tag (không bắt buộc)",
            value=st.session_state.get(
                "food_tag",
                ""
            ),
            placeholder=(
                "Ví dụ: đặc sản, truyền thống, hải sản..."
            ),
            key="food_tag_input",
        )

        # ----------------------------------------------------
        # NÚT TÌM KIẾM
        # ----------------------------------------------------

        if st.button(
            "🔎 Tìm món ăn",
            type="primary",
            use_container_width=True,
            key="search_food_button",
        ):

            with st.spinner(
                "Đang tải danh sách món ăn..."
            ):

                foods = fetch_foods(
                    destination=selected_food_destination,
                    food_type=selected_food_type,
                    tag=food_tag,
                    limit=20,
                    skip=0
                )

            st.session_state.food_results = foods

            st.session_state.food_destination = (
                selected_food_destination
            )

            st.session_state.food_type = (
                selected_food_type
            )

            st.session_state.food_tag = food_tag

            # ------------------------------------------------
            # TỰ ĐỘNG LƯU LỊCH SỬ FOOD
            # ------------------------------------------------

            if foods is not None:

                save_search_history(
                    keyword="Tìm món ăn địa phương",
                    destination=selected_food_destination,
                    search_type="food",

                    request_data={
                        "destination": selected_food_destination,
                        "food_type": selected_food_type,
                        "tag": food_tag,
                        "limit": 20,
                        "skip": 0,
                    },

                    result_data=foods,
                )

        # ----------------------------------------------------
        # HIỂN THỊ KẾT QUẢ
        # ----------------------------------------------------

        if st.session_state.get("food_results"):

            st.divider()

            result_destination = (
                st.session_state.get(
                    "food_destination",
                    "Tất cả"
                )
            )

            if result_destination == "Tất cả":
                result_title = "Tất cả địa điểm"
            else:
                result_title = result_destination

            st.subheader(
                f"🍽️ Món ăn tại {result_title}"
            )

            display_food_cards(
                st.session_state.food_results
            )

        else:

            st.info(
                "Chọn điểm đến và nhấn "
                "'Tìm món ăn' để xem danh sách."
            )



# ============================================================
# 22. TAB NHÀ HÀNG - RESTAURANT
# ============================================================

with tab_restaurant:

    st.title("🍽️ Tìm nhà hàng phù hợp")

    st.write(
        "Lọc nhà hàng dựa trên điểm đến, dị ứng của nhóm "
        "và ngân sách dự kiến."
    )

    st.divider()

    restaurant_col1, restaurant_col2 = st.columns(2)

    with restaurant_col1:

        default_restaurant_destination = (
            st.session_state.restaurant_destination
            or st.session_state.place
        )

        if default_restaurant_destination not in destinations:
            default_restaurant_destination = (
                destinations[0]
                if destinations
                else "Hà Nội"
            )

        restaurant_destination = st.selectbox(
            "Điểm đến",
            destinations or ["Hà Nội"],
            index=(
                destinations.index(default_restaurant_destination)
                if default_restaurant_destination in destinations
                else 0
            ),
            key="restaurant_destination_select",
        )

    with restaurant_col2:

        group_size = st.number_input(
            "Số thành viên",
            min_value=1,
            max_value=30,
            value=int(st.session_state.group_size),
            step=1,
            key="restaurant_group_size",
        )

    st.subheader("⚠️ Dị ứng của thành viên")

    group_allergens = st.multiselect(
        "Chọn các thành phần cần tránh",
        ALLERGEN_OPTIONS,
        default=[
            item
            for item in st.session_state.group_allergens
            if item in ALLERGEN_OPTIONS
        ],
        key="restaurant_allergens",
    )

    max_budget_per_person = st.number_input(
        "Ngân sách tối đa mỗi người cho một bữa (VNĐ)",
        min_value=10000,
        max_value=10000000,
        value=int(st.session_state.max_budget_per_meal),
        step=10000,
        key="restaurant_budget",
    )

    # --------------------------------------------------------
    # LỌC NHÀ HÀNG
    # --------------------------------------------------------

    if st.button(
        "🔎 LỌC NHÀ HÀNG PHÙ HỢP",
        type="primary",
        use_container_width=True,
        key="prune_restaurants_button",
    ):

        st.session_state.restaurant_destination = (
            restaurant_destination
        )

        st.session_state.group_allergens = group_allergens
        st.session_state.group_size = group_size

        st.session_state.max_budget_per_meal = (
            max_budget_per_person
        )

        with st.spinner(
            "Đang lọc nhà hàng và món ăn phù hợp..."
        ):

            restaurant_result = prune_safe_restaurants(
                destination=restaurant_destination,
                group_allergens=group_allergens,
                max_budget_per_person=max_budget_per_person,
                group_size=group_size,
            )

        if restaurant_result is not None:

            st.success("Đã hoàn thành lọc nhà hàng.")

            # ------------------------------------------------
            # TỰ ĐỘNG LƯU LỊCH SỬ RESTAURANT
            # ------------------------------------------------

            save_search_history(
                keyword="Lọc nhà hàng phù hợp",
                destination=restaurant_destination,
                search_type="restaurant",

                request_data={
                    "destination": restaurant_destination,
                    "group_allergens": group_allergens,
                    "group_size": group_size,
                    "max_budget_per_person": max_budget_per_person,
                },

                result_data=restaurant_result,
            )

    # --------------------------------------------------------
    # HIỂN THỊ KẾT QUẢ
    # --------------------------------------------------------

    if st.session_state.restaurant_data:

        st.divider()

        display_restaurants(
            st.session_state.restaurant_data
        )

        selected_count = len(
            st.session_state.selected_dining_places
        )

        st.info(
            f"Bạn đã chọn {selected_count} nhà hàng "
            "để đưa vào lịch trình."
        )

    else:

        st.info(
            "Nhập điều kiện lọc rồi nhấn nút để tìm nhà hàng."
        )


# ============================================================
# 23. TAB RANDOM CHALLENGE - TV4
# ============================================================

with tab_random:

    st.title("🎲 Random Challenge")

    st.write(
        "Để TravelMate AI lựa chọn ngẫu nhiên "
        "các tags và tìm những địa điểm phù hợp."
    )

    st.divider()

    if destination_options:

        random_destination = st.selectbox(
            "Chọn điểm đến",
            destination_options,
            key="random_destination",
        )

        st.write(
            "Nhấn nút bên dưới để bắt đầu thử thách."
        )

        st.markdown(
            """
            <div class="random-wheel">
                🎯
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button(
            "🎲 BẮT ĐẦU RANDOM",
            type="primary",
            use_container_width=True,
        ):
            st.session_state.random_result = None

            wheel_placeholder = st.empty()

            wheel_placeholder.markdown(
                """
                <div class="random-wheel spinning">
                    🎯
                </div>

                <h3 style="text-align:center">
                    Đang random tags và tìm địa điểm...
                </h3>
                """,
                unsafe_allow_html=True,
            )

            result = run_random_challenge(
                random_destination
            )

            wheel_placeholder.empty()

            if (
                isinstance(result, dict)
                and result.get("success")
            ):
                st.session_state.random_result = result

                result_data = result.get("data", {})

                selected_tags = []

                if isinstance(result_data, dict):
                    selected_tags = result_data.get(
                        "tags",
                        []
                    )

                saved = save_search_history(
                    keyword="Random Challenge",
                    destination=random_destination,
                    search_type="random_challenge",
                    request_data={
                        "destination": random_destination,
                        "selected_tags": selected_tags,
                    },
                    result_data=result,
                )

                if saved:
                    refresh_history_cache(
                        "random_challenge"
                    )

                    st.success(
                        "🎉 Random Challenge hoàn thành "
                        "và đã lưu lịch sử!"
                    )
                else:
                    st.warning(
                        "Kết quả đã được tạo nhưng chưa lưu được lịch sử."
                    )

            elif result:
                st.error(
                    result.get(
                        "message",
                        "Không thể tạo Random Challenge.",
                    )
                )

    else:
        st.warning(
            "Không có danh sách tỉnh/thành. "
            "Hãy kiểm tra Backend API."
        )

    if st.session_state.random_result:
        display_random_result(
            st.session_state.random_result
        )


# ============================================================
# 24. TAB LỊCH TRÌNH - SCHEDULER TV4 + RESTAURANT
# ============================================================

with tab_schedule:

    st.subheader("🗓️ Lập lịch trình du lịch")

    if st.session_state.is_submitted:

        st.write(
            f"**Điểm đến:** {st.session_state.place}"
        )

        st.write(
            f"**Số ngày:** {st.session_state.duration}"
        )

        st.write(
            f"**Ngân sách:** {st.session_state.budget:,} VNĐ"
        )

        st.write(
            f"**Sở thích:** "
            f"{', '.join(st.session_state.hobby)}"
        )

        st.caption(
            "Scheduler sẽ tự động phân chia các địa điểm "
            "được AI Recommendation gợi ý thành lịch trình "
            "theo số ngày bạn đã chọn."
        )

        restaurant_data = (
            st.session_state.get("restaurant_data") or {}
        )

        selected_restaurants = (
            st.session_state.get("selected_dining_places") or []
        )

        safe_dishes = get_safe_dishes(restaurant_data)

        if selected_restaurants or safe_dishes:
            st.info(
                f"Thông tin bổ sung: "
                f"{len(selected_restaurants)} nhà hàng đã chọn, "
                f"{len(safe_dishes)} món ăn đã qua bộ lọc."
            )
        else:
            st.caption(
                "Bạn chưa chọn nhà hàng. "
                "Scheduler vẫn có thể tạo lịch trình địa điểm."
            )

        if st.button(
            "🗓️ TẠO LỊCH TRÌNH",
            type="primary",
            use_container_width=True,
        ):
            with st.spinner(
                "Scheduler đang sắp xếp địa điểm theo từng ngày..."
            ):
                st.session_state.schedule_result = (
                    create_travel_schedule()
                )

        if st.session_state.schedule_result:
            display_schedule_result(
                st.session_state.schedule_result
            )

    else:
        st.info(
            "Hãy vào tab Trang chủ, chọn điểm đến và sở thích, "
            "sau đó nhấn Tìm kiếm địa điểm AI trước."
        )


# ============================================================
# 25. TAB LỊCH SỬ
# ============================================================

with tab_history:

    st.subheader("📚 Lịch sử hoạt động")

    st.write(
        "Xem lại những lần tìm kiếm địa điểm, "
        "Random Challenge, tạo lịch trình, "
        "lọc nhà hàng và khám phá món ăn trước đây."
    )

    st.caption(
        "Mỗi hoạt động được lưu thành một bản ghi riêng. "
        "Bạn có thể mở từng bản ghi để xem lại toàn bộ kết quả."
    )

    # --------------------------------------------------------
    # 5 TAB LỊCH SỬ TRÊN CÙNG MỘT HÀNG
    # --------------------------------------------------------

    (
        history_random,
        history_schedule,
        history_places,
        history_restaurant,
        history_food,
    ) = st.tabs(
        [
            "🎲 Random Challenge",
            "🗓️ Lịch trình",
            "📍 Tìm kiếm địa điểm",
            "🍽️ Nhà hàng",
            "🍜 Món ăn",
        ]
    )

    # --------------------------------------------------------
    # HIỂN THỊ DANH SÁCH LỊCH SỬ
    # --------------------------------------------------------

    def display_history_list(search_type):

        histories = get_search_history(search_type)

        st.session_state.history_by_type[search_type] = histories

        if st.button(
            "🔄 Tải lại lịch sử",
            key=f"load_history_{search_type}",
        ):

            refresh_history_cache(search_type)
            st.rerun()

        if not histories:

            st.info(
                "Chưa có lịch sử trong mục này."
            )

            return

        st.caption(
            f"Tổng số hoạt động: {len(histories)}"
        )

        extra_type_labels = {
            "restaurant": "Nhà hàng",
            "food": "Món ăn",
        }

        for index, item in enumerate(histories, start=1):

            if not isinstance(item, dict):
                continue

            history_id = (
                item.get("id")
                or item.get("_id")
            )

            if not history_id:
                continue

            history_id = str(history_id)

            is_selected = (
                str(st.session_state.selected_history_id)
                == history_id
            )

            with st.container(border=True):

                # --------------------------------------------
                # TÊN HOẠT ĐỘNG
                # --------------------------------------------

                st.markdown(
                    f"**{index}. "
                    f"{item.get('keyword', 'Không có từ khóa')}**"
                )

                # --------------------------------------------
                # THỜI GIAN
                # --------------------------------------------

                st.write(
                    f"🕒 **Thời gian:** "
                    f"{format_datetime(item.get('created_at'))}"
                )

                # --------------------------------------------
                # LOẠI LỊCH SỬ
                # --------------------------------------------

                item_type = item.get("search_type")

                type_label = HISTORY_TYPE_LABELS.get(
                    item_type,
                    extra_type_labels.get(
                        item_type,
                        item_type or "Không xác định"
                    ),
                )

                st.write(
                    f"📂 **Loại:** {type_label}"
                )

                # --------------------------------------------
                # ĐIỂM ĐẾN
                # --------------------------------------------

                st.write(
                    f"📍 **Điểm đến:** "
                    f"{item.get('destination') or 'Không có'}"
                )

                # --------------------------------------------
                # THUỘC TÍNH TÌM KIẾM
                # --------------------------------------------

                st.write(
                    "**🔎 Thuộc tính tìm kiếm:**"
                )

                attributes = get_history_attributes(item)

                if attributes:

                    for attribute in attributes:
                        st.caption(f"• {attribute}")

                else:

                    request_data = item.get(
                        "request_data",
                        {}
                    )

                    if request_data:
                        st.caption(
                            "Thông tin điều kiện tìm kiếm đã được lưu."
                        )
                    else:
                        st.caption(
                            "Không có thông tin bổ sung."
                        )

                # --------------------------------------------
                # NÚT MỞ / ĐÓNG CHI TIẾT
                # --------------------------------------------

                button_label = (
                    "▲ Thu gọn kết quả"
                    if is_selected
                    else "▼ Xem toàn bộ kết quả"
                )

                if st.button(
                    button_label,
                    key=f"detail_{search_type}_{history_id}",
                    use_container_width=True,
                ):

                    if is_selected:

                        st.session_state.selected_history_id = None

                        st.session_state.selected_history_detail = None

                    else:

                        detail = get_search_history_detail(
                            history_id
                        )

                        if detail:

                            st.session_state.selected_history_id = (
                                history_id
                            )

                            st.session_state.selected_history_detail = (
                                detail
                            )

                        else:

                            st.error(
                                "Không thể tải chi tiết lịch sử."
                            )

                    st.rerun()

            # --------------------------------------------
            # HIỂN THỊ CHI TIẾT ĐÃ CHỌN
            # --------------------------------------------

            if (
                str(st.session_state.selected_history_id)
                == history_id
                and st.session_state.selected_history_detail
            ):

                with st.container(border=True):

                    display_history_detail(
                        st.session_state.selected_history_detail
                    )

    # --------------------------------------------------------
    # TAB 1: RANDOM CHALLENGE
    # --------------------------------------------------------

    with history_random:

        display_history_list(
            "random_challenge"
        )

    # --------------------------------------------------------
    # TAB 2: SCHEDULER
    # --------------------------------------------------------

    with history_schedule:

        display_history_list(
            "scheduler"
        )

    # --------------------------------------------------------
    # TAB 3: AI RECOMMENDATION
    # --------------------------------------------------------

    with history_places:

        display_history_list(
            "place_recommendation"
        )

    # --------------------------------------------------------
    # TAB 4: RESTAURANT
    # --------------------------------------------------------

    with history_restaurant:

        display_history_list(
            "restaurant"
        )

    # --------------------------------------------------------
    # TAB 5: FOOD
    # --------------------------------------------------------

    with history_food:

        display_history_list(
            "food"
        )

# ============================================================
# 26. FOOTER
# ============================================================

st.divider()

st.markdown(
    """
    <div style="text-align:center; color:gray;">
        ✈️ TravelMate AI
        <br>
        Your AI-powered travel companion
    </div>
    """,
    unsafe_allow_html=True,
)