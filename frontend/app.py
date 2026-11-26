
import streamlit as st
import requests
import urllib.parse
from datetime import datetime, timezone
from zoneinfo import ZoneInfo


# =====================================================
# 1. CẤU HÌNH TRANG
# =====================================================

st.set_page_config(
    page_title="TravelMate AI",
    page_icon="✈️",
    layout="wide"
)

API_BASE_URL = "http://127.0.0.1:8000"

RECOMMEND_API = f"{API_BASE_URL}/api/places/recommend"
RANDOM_API = f"{API_BASE_URL}/api/random-challenge/"
HISTORY_API = f"{API_BASE_URL}/api/search-history/"
DESTINATIONS_API = f"{API_BASE_URL}/api/places/destinations"
SCHEDULER_API = f"{API_BASE_URL}/api/scheduler/"


# =====================================================
# 2. SESSION STATE
# =====================================================

default_states = {
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
    "mode": "solo"
}

for key, value in default_states.items():
    if key not in st.session_state:
        st.session_state[key] = value


# =====================================================
# 3. DỮ LIỆU AI RECOMMENDATION
# =====================================================

HOBBY_TAGS = {
    "Đi biển": "biển đảo",
    "Leo núi": "leo núi & trekking",
    "Tham quan địa điểm lịch sử": "kiến trúc & di tích cổ",
    "Ngắm cảnh đẹp thiên nhiên": "thiên nhiên"
}

MODE_OPTIONS = {
    "Đi du lịch một mình": "solo",
    "Đi du lịch cùng người yêu": "couple",
    "Đi du lịch cùng gia đình": "family",
    "Để AI tự do lựa chọn": "random"
}

MODE_LABELS = {
    "solo": "Đi một mình",
    "couple": "Đi cùng người yêu",
    "family": "Đi cùng gia đình",
    "random": "AI tự lựa chọn"
}

HISTORY_TYPE_LABELS = {
    "random_challenge": "🎲 Random Challenge",
    "scheduler": "🗓️ Lập lịch trình",
    "place_recommendation": "📍 Tìm kiếm địa điểm"
}


# =====================================================
# 4. CSS GIAO DIỆN
# =====================================================

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
        from {
            transform: rotate(0deg);
        }

        to {
            transform: rotate(360deg);
        }
    }

    .random-heading {
        text-align: center;
        font-size: 24px;
        font-weight: bold;
        color: #D4AF37;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# =====================================================
# 5. HÀM HỖ TRỢ
# =====================================================

def format_datetime(value):
    """
    Chuyển thời gian UTC sang giờ Việt Nam.
    """

    if not value:
        return "Không có thông tin"

    try:
        if isinstance(value, datetime):
            date_value = value
        else:
            date_value = datetime.fromisoformat(
                str(value).replace("Z", "+00:00")
            )

        # MongoDB có thể trả datetime không có timezone.
        # Theo schema hiện tại, created_at được lưu theo UTC.
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
    """
    Chuyển list thành chuỗi để hiển thị.
    """

    if isinstance(value, list):
        return ", ".join(
            str(item) for item in value
        ) if value else "Không có"

    if value is None:
        return "Không có"

    return str(value)


def display_safe_image(image_url, width="stretch"):
    """
    Chỉ hiển thị ảnh khi image_url là URL HTTP/HTTPS hợp lệ.
    Tránh Streamlit hiểu chuỗi như 'q' là đường dẫn file.
    """

    if (
        isinstance(image_url, str)
        and image_url.strip().startswith(
            ("http://", "https://")
        )
    ):
        try:
            st.image(
                image_url.strip(),
                width=width
            )
        except Exception:
            st.caption(
                "Không thể tải hình ảnh địa điểm."
            )
    else:
        st.caption(
            "Chưa có hình ảnh hợp lệ cho địa điểm này."
        )


def get_history_attributes(item):
    """
    Lấy các thuộc tính tìm kiếm để hiển thị ở danh sách rút gọn.
    """

    search_type = item.get("search_type")
    request_data = item.get("request_data", {})

    if not isinstance(request_data, dict):
        request_data = {}

    attributes = []

    # -----------------------------------------
    # RANDOM CHALLENGE
    # -----------------------------------------

    if search_type == "random_challenge":

        tags = request_data.get("selected_tags", [])

        if tags:
            attributes.append(
                f"Tags: {format_list(tags)}"
            )
        else:
            attributes.append(
                "Thuộc tính: Random tags"
            )

    # -----------------------------------------
    # SCHEDULER
    # -----------------------------------------

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

    # -----------------------------------------
    # PLACE RECOMMENDATION
    # -----------------------------------------

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
            try:
                attributes.append(
                    f"Ngân sách: {int(budget):,} VNĐ"
                )
            except (ValueError, TypeError):
                attributes.append(
                    f"Ngân sách: {budget}"
                )

        duration = request_data.get("duration")

        if duration is not None:
            attributes.append(
                f"Thời gian: {duration} ngày"
            )

    return attributes or [
        "Chưa có thuộc tính tìm kiếm"
    ]


# =====================================================
# 6. BACKEND API FUNCTIONS
# =====================================================

# -----------------------------------------------------
# Lấy danh sách tỉnh/thành
# -----------------------------------------------------

@st.cache_data(ttl=300)
def get_destinations():

    try:
        response = requests.get(
            DESTINATIONS_API,
            timeout=15
        )

        response.raise_for_status()

        result = response.json()

        if isinstance(result, dict):
            destinations = result.get("data", [])
        else:
            destinations = []

        if not isinstance(destinations, list):
            return []

        return sorted(
            {
                item.strip()
                for item in destinations
                if isinstance(item, str) and item.strip()
            },
            key=str.casefold
        )

    except requests.RequestException:
        return []


# -----------------------------------------------------
# AI Recommendation
# -----------------------------------------------------

def get_recommendations(destination, interests, mode):

    payload = {
        "destination": destination,
        "interests": interests,
        "top_k": 10,
        "mode": mode
    }

    try:
        response = requests.post(
            RECOMMEND_API,
            json=payload,
            timeout=30
        )

        response.raise_for_status()

        return response.json()

    except requests.RequestException as error:
        st.error(
            f"Không thể kết nối API Recommendation: {error}"
        )
        return None


# -----------------------------------------------------
# Random Challenge
# -----------------------------------------------------

def run_random_challenge(destination):

    response = None

    try:
        response = requests.post(
            RANDOM_API,
            json={
                "destination": destination
            },
            timeout=60
        )

        response.raise_for_status()

        return response.json()

    except requests.RequestException as error:
        st.error(
            f"Không thể kết nối Backend: {error}"
        )

        if response is not None:
            st.code(response.text)

        return None


# -----------------------------------------------------
# LƯU LỊCH SỬ
# -----------------------------------------------------

def save_search_history(
    keyword,
    destination,
    search_type,
    request_data,
    result_data
):
    """
    Lưu thông tin đầu vào và toàn bộ kết quả
    sau khi chức năng chạy thành công.
    """

    payload = {
        "keyword": keyword,
        "destination": destination,
        "search_type": search_type,
        "request_data": request_data,
        "result_data": result_data
    }

    try:
        response = requests.post(
            HISTORY_API,
            json=payload,
            timeout=30
        )

        response.raise_for_status()

        return response.json()

    except requests.RequestException as error:
        st.warning(
            f"Kết quả đã được tạo nhưng chưa lưu được lịch sử: {error}"
        )

        return None


# -----------------------------------------------------
# LẤY DANH SÁCH LỊCH SỬ
# -----------------------------------------------------

def get_search_history(search_type=None):
    """
    Lấy danh sách lịch sử từ Backend.

    Mỗi loại hoạt động được lọc riêng.
    Tối đa 100 bản ghi mỗi lần tải.

    Sắp xếp mới nhất lên trước.
    """

    try:
        params = {
            "limit": 100
        }

        if search_type:
            params["search_type"] = search_type

        response = requests.get(
            HISTORY_API,
            params=params,
            timeout=15
        )

        response.raise_for_status()

        result = response.json()

        if isinstance(result, dict):

            data = result.get("data", [])

            if isinstance(data, list):

                # Lọc theo loại lịch sử
                if search_type:
                    data = [
                        item
                        for item in data
                        if item.get("search_type") == search_type
                    ]

                # Lấy thời gian để sắp xếp
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

                # Mới nhất lên đầu
                data.sort(
                    key=get_sort_time,
                    reverse=True
                )

                return data

        return []

    except requests.RequestException as error:
        st.error(
            f"Không thể tải lịch sử: {error}"
        )

        return []


# -----------------------------------------------------
# CẬP NHẬT CACHE LỊCH SỬ
# -----------------------------------------------------

def refresh_history_cache(search_type):
    """
    Tải lại danh sách lịch sử của một loại hoạt động
    và cập nhật Session State.
    """

    st.session_state.history_by_type[search_type] = (
        get_search_history(search_type)
    )


# -----------------------------------------------------
# LẤY CHI TIẾT MỘT LỊCH SỬ
# -----------------------------------------------------

def get_search_history_detail(history_id):

    try:
        response = requests.get(
            f"{HISTORY_API}{history_id}",
            timeout=30
        )

        response.raise_for_status()

        result = response.json()

        if isinstance(result, dict):
            return result.get("data")

        return None

    except requests.RequestException as error:
        st.error(
            f"Không thể tải chi tiết lịch sử: {error}"
        )

        return None


# =====================================================
# 7. SCHEDULER - TẠO LỊCH TRÌNH
# =====================================================

def create_travel_schedule():
    """
    Gửi kết quả AI Recommendation đến Scheduler.

    Không sử dụng Random Challenge.
    Không chạy Simulated Annealing.
    """

    places = st.session_state.get("results", [])

    if not isinstance(places, list) or not places:
        st.warning(
            "Bạn cần tạo kết quả AI Recommendation "
            "trước khi lập lịch."
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
        "tags": interests
    }

    payload = {
        "input_context": input_context,
        "places": places,
        "tv2_result": {},
        "tv3_result": {}
    }

    response = None

    try:
        response = requests.post(
            SCHEDULER_API,
            json=payload,
            timeout=60
        )

        response.raise_for_status()

        result = response.json()

        # Chỉ lưu khi Scheduler thành công
        if isinstance(result, dict) and result.get("success"):

            saved = save_search_history(
                keyword=f"Lịch trình {input_context['duration']} ngày",
                destination=input_context["destination"],
                search_type="scheduler",
                request_data={
                    "input_context": input_context,
                    "places": places
                },
                result_data=result
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

        return result

    except requests.HTTPError as error:

        st.error(
            f"Scheduler trả về lỗi: {error}"
        )

        if response is not None:
            st.code(response.text)

        return None

    except requests.RequestException as error:

        st.error(
            f"Không thể kết nối API Scheduler: {error}"
        )

        return None


# =====================================================
# 8. HIỂN THỊ KẾT QUẢ AI RECOMMENDATION
# =====================================================

def display_recommendations(results):

    st.subheader(
        "Danh sách địa điểm gợi ý"
    )

    if not results:
        st.warning(
            "Không tìm thấy địa điểm phù hợp. "
            "Bạn thử thay đổi sở thích nhé!"
        )
        return

    for item in results:

        if not isinstance(item, dict):
            continue

        with st.container(border=True):

            name = item.get(
                "name",
                "Chưa có tên"
            )

            st.subheader(name)

            image_url = item.get("image_url")

            display_safe_image(image_url)

            rating = item.get("rating", 0)

            st.write(
                f"⭐ Đánh giá: {rating}/5"
            )

            st.write(
                item.get("description") or "Chưa có mô tả."
            )

            tags = item.get("tags", [])

            if isinstance(tags, list):
                tags_text = ", ".join(
                    str(tag) for tag in tags
                )
            else:
                tags_text = str(tags)

            st.write(
                "🏷️ Sở thích phù hợp:",
                tags_text or "Chưa có tags"
            )

            score = item.get("score", 0)

            try:
                score_text = f"{float(score) * 100:.1f}%"
            except (ValueError, TypeError):
                score_text = str(score)

            st.write(
                f"🎯 Điểm phù hợp: {score_text}"
            )

            destination = st.session_state.get("place", "")

            query = urllib.parse.quote(
                f"{name}, {destination}"
            )

            map_url = (
                "https://www.google.com/maps/search/"
                f"?api=1&query={query}"
            )

            st.markdown(
                f"[📍 Xem trên Google Maps]({map_url})"
            )


# =====================================================
# 9. HIỂN THỊ ĐỊA ĐIỂM RANDOM
# =====================================================

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

        image_url = item.get("image_url")

        with st.container(border=True):

            col_image, col_info = st.columns([1, 2])

            with col_image:

                display_safe_image(image_url)

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

                st.write(
                    "**Tags của địa điểm:**"
                )

                if place_tags:
                    st.write(
                        format_list(place_tags)
                    )
                else:
                    st.write(
                        "Không có thông tin tags."
                    )

                matched_tags = item.get(
                    "matched_tags",
                    []
                )

                st.write(
                    "**Tags khớp với thử thách:**"
                )

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
                )

                st.write(
                    f"**Số tags khớp:** {match_count}"
                )

                match_ratio = item.get("match_ratio")

                if match_ratio is not None:
                    st.write(
                        f"**Tỷ lệ khớp:** {match_ratio}"
                    )

                query = urllib.parse.quote(
                    f"{name}, {destination}"
                )

                map_url = (
                    "https://www.google.com/maps/search/"
                    f"?api=1&query={query}"
                )

                st.markdown(
                    f"[📍 Xem trên Google Maps]({map_url})"
                )


# =====================================================
# 10. HIỂN THỊ KẾT QUẢ RANDOM CHALLENGE
# =====================================================

def display_random_result(result):

    if not result:
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

    st.write(
        f"**Điểm đến:** {destination}"
    )

    st.subheader(
        "🎯 Tags ngẫu nhiên được lựa chọn"
    )

    if tags:

        tag_columns = st.columns(len(tags))

        for index, tag in enumerate(tags):
            with tag_columns[index]:
                st.info(f"🏷️ {tag}")

    else:
        st.warning(
            "Backend chưa trả về tags."
        )

    if fitness is not None:
        st.metric(
            "Fitness",
            fitness
        )

    st.divider()

    st.subheader(
        "📍 Địa điểm được tìm thấy từ các tags"
    )

    display_random_places(
        places,
        destination
    )


# =====================================================
# 11. HIỂN THỊ KẾT QUẢ SCHEDULER
# =====================================================

def display_schedule_result(result):

    if not result:
        return

    if not result.get("success"):

        st.error(
            result.get(
                "message",
                "Không thể tạo lịch trình."
            )
        )

        st.json(result)
        return

    st.success(
        "Đã tạo lịch trình thành công!"
    )

    col1, col2 = st.columns(2)

    col1.metric(
        "Tổng số ngày",
        result.get("total_days", 0)
    )

    col2.metric(
        "Tổng hoạt động",
        result.get("total_activities", 0)
    )

    st.divider()

    schedule = result.get("schedule", [])

    if not schedule:
        st.warning(
            "Backend chưa trả về lịch trình."
        )
        return

    for day_index, day in enumerate(schedule, start=1):

        day_number = day.get(
            "day",
            day_index
        )

        st.markdown(
            f"### 📅 Ngày {day_number}"
        )

        activities = day.get("activities", [])

        if not activities:
            st.info(
                "Ngày này chưa có hoạt động."
            )
            continue

        for activity_index, activity in enumerate(
            activities,
            start=1
        ):

            if isinstance(activity, dict):

                activity_name = (
                    activity.get("name")
                    or activity.get("restaurant_name")
                    or activity.get("food_name")
                    or "Hoạt động chưa có tên"
                )

                activity_type = activity.get(
                    "type",
                    "Hoạt động"
                )

                activity_tags = activity.get(
                    "tags",
                    []
                )

                with st.container(border=True):

                    st.write(
                        f"**{activity_index}. {activity_name}**"
                    )

                    st.caption(
                        f"Loại: {activity_type}"
                    )

                    if activity_tags:
                        st.write(
                            "Tags:",
                            format_list(activity_tags)
                        )

                    image_url = activity.get("image_url")

                    display_safe_image(image_url)

                    location = (
                        activity.get("location")
                        or activity.get("address")
                    )

                    if location:
                        query = urllib.parse.quote(str(location))

                        map_url = (
                            "https://www.google.com/maps/search/"
                            f"?api=1&query={query}"
                        )

                        st.markdown(
                            f"[📍 Xem trên Google Maps]({map_url})"
                        )

            else:

                with st.container(border=True):
                    st.write(
                        f"**{activity_index}. {activity}**"
                    )

    remaining_places = result.get(
        "remaining_places",
        []
    )

    if remaining_places:

        st.warning(
            "Một số địa điểm chưa được xếp vào lịch trình "
            "do giới hạn số địa điểm mỗi ngày."
        )

        with st.expander(
            "Xem các địa điểm còn lại"
        ):

            for item in remaining_places:

                if isinstance(item, dict):
                    st.write(
                        item.get("name", "Chưa có tên")
                    )
                else:
                    st.write(item)


# =====================================================
# 12. HIỂN THỊ CHI TIẾT LỊCH SỬ
# =====================================================

def display_history_detail(detail):

    if not detail:
        return

    st.divider()

    st.subheader(
        "📖 Chi tiết lần tìm kiếm đã lưu"
    )

    if st.button(
        "✖ Đóng chi tiết",
        key=f"close_detail_{detail.get('id', 'unknown')}"
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

    st.write(
        f"**Loại lịch sử:** "
        f"{HISTORY_TYPE_LABELS.get(search_type, search_type)}"
    )

    request_data = detail.get("request_data", {})

    if request_data:

        with st.expander(
            "📥 Xem đầy đủ thông tin đầu vào"
        ):
            st.json(request_data)

    result_data = detail.get("result_data")

    if not result_data:

        st.warning(
            "Lịch sử này được tạo từ phiên bản cũ, "
            "chưa lưu nội dung kết quả chi tiết."
        )

        return

    st.divider()

    # -----------------------------------------
    # RANDOM CHALLENGE
    # -----------------------------------------

    if search_type == "random_challenge":

        display_random_result(result_data)

    # -----------------------------------------
    # SCHEDULER
    # -----------------------------------------

    elif search_type == "scheduler":

        display_schedule_result(result_data)

    # -----------------------------------------
    # AI RECOMMENDATION
    # -----------------------------------------

    elif search_type == "place_recommendation":

        if isinstance(result_data, dict):

            recommendation_results = result_data.get(
                "data",
                []
            )

        elif isinstance(result_data, list):

            recommendation_results = result_data

        else:

            recommendation_results = []

        display_recommendations(
            recommendation_results
        )

    else:

        st.json(result_data)


# =====================================================
# 13. TẢI DANH SÁCH ĐIỂM ĐẾN
# =====================================================

destinations = get_destinations()

recommendation_destinations = destinations or [
    "Hà Nội",
    "Đà Nẵng",
    "Thành phố Hồ Chí Minh"
]

destination_options = ["Toàn Việt Nam"] + destinations


# =====================================================
# 14. HEADER VÀ CÁC TAB
# =====================================================

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

tab_home, tab_random, tab_schedule, tab_history = st.tabs(
    [
        "Trang chủ",
        "🎲 Random Challenge",
        "Lịch trình",
        "Lịch sử"
    ]
)


# =====================================================
# 15. TAB TRANG CHỦ - AI RECOMMENDATION
# =====================================================

with tab_home:

    with st.sidebar:

        st.header(
            "Đặc điểm cá nhân nổi bật"
        )

        selected_mode = st.selectbox(
            "Bạn đi du lịch với ai?",
            options=list(MODE_OPTIONS.keys()),
            index=list(MODE_OPTIONS.values()).index(
                st.session_state.mode
            ) if st.session_state.mode in MODE_OPTIONS.values() else 0
        )

        mode = MODE_OPTIONS[selected_mode]

        hobby = st.multiselect(
            "Sở thích",
            list(HOBBY_TAGS.keys()),
            default=st.session_state.hobby
        )

        default_place = st.session_state.place

        if default_place not in recommendation_destinations:
            default_place = recommendation_destinations[0]

        place = st.selectbox(
            "Thành phố dự kiến muốn đi",
            recommendation_destinations,
            index=recommendation_destinations.index(default_place)
        )

        budget = st.number_input(
            "Ngân sách dự kiến (VNĐ)",
            min_value=100000,
            max_value=10000000,
            value=int(st.session_state.budget),
            step=100000
        )

        duration = st.number_input(
            "Thời gian dự kiến (Ngày)",
            min_value=1,
            max_value=10,
            value=int(st.session_state.duration),
            step=1
        )

        submit = st.button(
            "Tìm kiếm địa điểm AI",
            type="primary"
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
                    mode
                )

            if data is not None:

                results = data.get("data", [])

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

                # TỰ ĐỘNG LƯU LỊCH SỬ RECOMMENDATION

                saved = save_search_history(
                    keyword="Tìm kiếm địa điểm theo sở thích",
                    destination=place,
                    search_type="place_recommendation",
                    request_data={
                        "destination": place,
                        "interests": interests,
                        "mode": mode,
                        "budget": budget,
                        "duration": duration
                    },
                    result_data=data
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
                st.session_state.mode
            )
        )

        col_card, col_map = st.columns([1, 1])

        with col_map:

            st.subheader(
                "Bản đồ gợi ý"
            )

            st.info(
                "Bản đồ sẽ được tích hợp ở bước tiếp theo."
            )

        with col_card:

            display_recommendations(
                st.session_state.results
            )


# =====================================================
# 16. TAB RANDOM CHALLENGE - TV4
# =====================================================

with tab_random:

    st.title(
        "🎲 Random Challenge"
    )

    st.write(
        "Để TravelMate AI lựa chọn ngẫu nhiên "
        "các tags và tìm những địa điểm phù hợp."
    )

    st.divider()

    if destination_options:

        random_destination = st.selectbox(
            "Chọn điểm đến",
            destination_options,
            key="random_destination"
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
            unsafe_allow_html=True
        )

        if st.button(
            "🎲 BẮT ĐẦU RANDOM",
            type="primary",
            use_container_width=True
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
                unsafe_allow_html=True
            )

            result = run_random_challenge(
                random_destination
            )

            wheel_placeholder.empty()

            if result and result.get("success"):

                st.session_state.random_result = result

                # Lấy tags Backend đã random

                result_data = result.get("data", {})

                selected_tags = []

                if isinstance(result_data, dict):
                    selected_tags = result_data.get("tags", [])

                # TỰ ĐỘNG LƯU TOÀN BỘ KẾT QUẢ RANDOM

                saved = save_search_history(
                    keyword="Random Challenge",
                    destination=random_destination,
                    search_type="random_challenge",
                    request_data={
                        "destination": random_destination,
                        "selected_tags": selected_tags
                    },
                    result_data=result
                )

                if saved:

                    refresh_history_cache(
                        "random_challenge"
                    )

                    st.success(
                        "🎉 Random Challenge hoàn thành và đã lưu lịch sử!"
                    )

                else:

                    st.warning(
                        "Kết quả đã được tạo nhưng "
                        "chưa lưu được lịch sử."
                    )

            elif result:

                st.error(
                    result.get(
                        "message",
                        "Không thể tạo Random Challenge."
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


# =====================================================
# 17. TAB LỊCH TRÌNH - SCHEDULER TV4
# =====================================================

with tab_schedule:

    st.subheader(
        "🗓️ Lập lịch trình du lịch"
    )

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

        if st.button(
            "🗓️ TẠO LỊCH TRÌNH",
            type="primary",
            use_container_width=True
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


# =====================================================
# 18. TAB LỊCH SỬ
# =====================================================

with tab_history:

    st.subheader(
        "📚 Lịch sử hoạt động"
    )

    st.write(
        "Xem lại những lần tìm kiếm địa điểm, "
        "Random Challenge và tạo lịch trình trước đây."
    )

    st.caption(
        "Mỗi hoạt động được lưu thành một bản ghi riêng. "
        "Bạn có thể mở từng bản ghi để xem lại toàn bộ kết quả."
    )

    history_random, history_schedule, history_places = st.tabs(
        [
            "🎲 Random Challenge",
            "🗓️ Lịch trình",
            "📍 Tìm kiếm địa điểm"
        ]
    )

    # -------------------------------------------------
    # HÀM HIỂN THỊ DANH SÁCH LỊCH SỬ
    # -------------------------------------------------

    def display_history_list(search_type):

        # Tải dữ liệu từ Backend
        histories = get_search_history(search_type)

        st.session_state.history_by_type[search_type] = histories

        # Nút tải lại lịch sử

        if st.button(
            "🔄 Tải lại lịch sử",
            key=f"load_history_{search_type}"
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

        for index, item in enumerate(histories, start=1):

            history_id = item.get("id")

            if not history_id:
                continue

            is_selected = (
                st.session_state.selected_history_id == history_id
            )

            with st.container(border=True):

                # Tên hoạt động

                st.markdown(
                    f"**{index}. {item.get('keyword', 'Không có từ khóa')}**"
                )

                # Thời gian

                st.write(
                    f"🕒 **Thời gian:** "
                    f"{format_datetime(item.get('created_at'))}"
                )

                # Loại hoạt động

                type_label = HISTORY_TYPE_LABELS.get(
                    item.get("search_type"),
                    item.get("search_type", "Không xác định")
                )

                st.write(
                    f"📂 **Loại:** {type_label}"
                )

                # Điểm đến

                st.write(
                    f"📍 **Điểm đến:** "
                    f"{item.get('destination') or 'Không có'}"
                )

                # Thuộc tính tìm kiếm

                st.write(
                    "**🔎 Thuộc tính tìm kiếm:**"
                )

                attributes = get_history_attributes(item)

                for attribute in attributes:
                    st.caption(f"• {attribute}")

                # Nút mở / đóng chi tiết

                button_label = (
                    "▲ Thu gọn kết quả"
                    if is_selected
                    else "▼ Xem toàn bộ kết quả"
                )

                if st.button(
                    button_label,
                    key=f"detail_{search_type}_{history_id}",
                    use_container_width=True
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

            # -------------------------------------------------
            # HIỂN THỊ CHI TIẾT NGAY DƯỚI BẢN GHI ĐƯỢC CHỌN
            # -------------------------------------------------

            if (
                st.session_state.selected_history_id == history_id
                and st.session_state.selected_history_detail
            ):

                with st.container(border=True):

                    display_history_detail(
                        st.session_state.selected_history_detail
                    )

    # -------------------------------------------------
    # 3 NHÓM LỊCH SỬ
    # -------------------------------------------------

    with history_random:

        display_history_list(
            "random_challenge"
        )

    with history_schedule:

        display_history_list(
            "scheduler"
        )

    with history_places:

        display_history_list(
            "place_recommendation"
        )
