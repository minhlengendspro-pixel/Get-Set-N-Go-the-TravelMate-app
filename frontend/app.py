
import streamlit as st
import requests
import urllib.parse


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


# =====================================================
# 2. SESSION STATE
# =====================================================

default_states = {
    "is_submitted": False,
    "results": [],
    "random_result": None,
    "history": [],
    "history_loaded": False,
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
# 3. DỮ LIỆU GIAO DIỆN AI RECOMMENDATION
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
# 5. BACKEND API FUNCTIONS
# =====================================================

# Lấy danh sách tỉnh/thành từ MongoDB
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

    except requests.RequestException as error:
        return []


# AI Recommendation
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
        st.error(f"Không thể kết nối API Recommendation: {error}")
        return None


# Random Challenge
def run_random_challenge(destination):

    try:
        response = requests.post(
            RANDOM_API,
            json={
                "destination": destination
            },
            timeout=60
        )

        if response.status_code == 200:
            return response.json()

        st.error(
            f"Random Challenge thất bại: HTTP {response.status_code}"
        )

        st.code(response.text)

        return None

    except requests.RequestException as error:

        st.error(
            f"Không thể kết nối Backend: {error}"
        )

        return None


# Lưu lịch sử tìm kiếm
def save_search_history(destination):

    try:
        response = requests.post(
            HISTORY_API,
            json={
                "keyword": "Random Challenge",
                "destination": destination,
                "search_type": "random_challenge"
            },
            timeout=15
        )

        return response.status_code in [200, 201]

    except requests.RequestException:
        return False


# Lấy lịch sử tìm kiếm
def get_search_history():

    try:
        response = requests.get(
            HISTORY_API,
            timeout=15
        )

        if response.status_code != 200:
            return []

        result = response.json()

        if isinstance(result, list):
            return result

        if isinstance(result, dict):
            data = result.get("data", [])

            if isinstance(data, list):
                return data

        return []

    except requests.RequestException:

        st.error(
            "Không thể kết nối API Search History."
        )

        return []


# =====================================================
# 6. HIỂN THỊ KẾT QUẢ AI RECOMMENDATION
# =====================================================

def display_recommendations(results):

    st.subheader("Danh sách địa điểm gợi ý")

    if not results:
        st.warning(
            "Không tìm thấy địa điểm phù hợp. "
            "Bạn thử thay đổi sở thích nhé!"
        )
        return

    for item in results:

        with st.container(border=True):

            st.subheader(
                item.get("name", "Chưa có tên")
            )

            image_url = item.get("image_url")

            if image_url:
                st.image(
                    image_url,
                    width="stretch"
                )
            else:
                st.caption("Chưa có hình ảnh địa điểm.")

            rating = item.get("rating", 0)

            st.write(f"⭐ Đánh giá: {rating}/5")

            st.write(
                item.get("description") or "Chưa có mô tả."
            )

            tags = item.get("tags", [])

            st.write(
                "🏷️ Sở thích phù hợp:",
                ", ".join(tags) if tags else "Chưa có tags"
            )

            score = item.get("score", 0)

            st.write(
                f"🎯 Điểm phù hợp: {score * 100:.1f}%"
            )


# =====================================================
# 7. HIỂN THỊ ĐỊA ĐIỂM RANDOM
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

        name = item.get(
            "name",
            "Địa điểm chưa có tên"
        )

        image_url = item.get("image_url")

        with st.container(border=True):

            col_image, col_info = st.columns([1, 2])

            # Hình ảnh địa điểm
            with col_image:

                if image_url:

                    st.image(
                        image_url,
                        width="stretch"
                    )

                else:
                    st.caption("Địa điểm chưa có ảnh.")

            # Thông tin địa điểm
            with col_info:

                st.markdown(
                    f"### {index}. {name}"
                )

                rating = item.get("rating")

                if rating is not None:
                    st.write(f"⭐ Rating: {rating}")

                place_tags = item.get("tags", [])

                st.write("**Tags của địa điểm:**")

                if place_tags:
                    st.write(", ".join(place_tags))
                else:
                    st.write("Không có thông tin tags.")

                matched_tags = item.get(
                    "matched_tags",
                    []
                )

                st.write("**Tags khớp với thử thách:**")

                if matched_tags:
                    st.success(", ".join(matched_tags))
                else:
                    st.write("Không có thông tin tags khớp.")

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

                # Google Maps
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
# 8. HIỂN THỊ TOÀN BỘ KẾT QUẢ RANDOM CHALLENGE
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
        '<div class="random-heading">🎉 KẾT QUẢ RANDOM CHALLENGE</div>',
        unsafe_allow_html=True
    )

    st.write(f"**Điểm đến:** {destination}")

    # Tags được thuật toán lựa chọn
    st.subheader("🎯 Tags ngẫu nhiên được lựa chọn")

    if tags:

        tag_columns = st.columns(len(tags))

        for index, tag in enumerate(tags):

            with tag_columns[index]:
                st.info(f"🏷️ {tag}")

    else:
        st.warning("Backend chưa trả về tags.")

    # Fitness
    if fitness is not None:
        st.metric("Fitness", fitness)

    st.divider()

    # Danh sách địa điểm
    st.subheader(
        "📍 Địa điểm được tìm thấy từ các tags"
    )

    display_random_places(
        places,
        destination
    )


# =====================================================
# 9. TẢI DANH SÁCH ĐIỂM ĐẾN
# =====================================================

destinations = get_destinations()

# Danh sách cho AI Recommendation
# Không thêm "Toàn Việt Nam" vào đây vì chưa xác nhận
# API Recommendation hỗ trợ lựa chọn này.
recommendation_destinations = destinations or [
    "Hà Nội",
    "Đà Nẵng",
    "Thành phố Hồ Chí Minh"
]

# Danh sách cho Random Challenge
destination_options = ["Toàn Việt Nam"] + destinations


# =====================================================
# 10. HEADER VÀ CÁC TAB
# =====================================================

st.markdown(
    '<div class="main-title">✈️ TravelMate AI</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="sub-title">Your AI-powered travel companion</div>',
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
# 11. TAB TRANG CHỦ - AI RECOMMENDATION
# =====================================================

with tab_home:

    with st.sidebar:

        st.header("Đặc điểm cá nhân nổi bật")

        selected_mode = st.selectbox(
            "Bạn đi du lịch với ai?",
            options=list(MODE_OPTIONS.keys())
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
            value=st.session_state.budget,
            step=100000
        )

        duration = st.number_input(
            "Thời gian dự kiến (Ngày)",
            min_value=1,
            max_value=10,
            value=st.session_state.duration,
            step=1
        )

        submit = st.button(
            "Tạo lịch trình AI",
            type="primary"
        )

    # Xử lý khi người dùng nhấn nút
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

                st.session_state.results = data.get(
                    "data",
                    []
                )

                st.session_state.is_submitted = True

                st.session_state.mode = mode
                st.session_state.place = place
                st.session_state.budget = budget
                st.session_state.duration = duration
                st.session_state.hobby = hobby

    # Hiển thị kết quả
    if not st.session_state.is_submitted:

        st.info(
            "Chào mừng bạn đến với TravelMate AI! "
            "Vui lòng điền thông tin bên thanh sidebar "
            "để nhận gợi ý."
        )

    else:

        st.write(
            "**Chế độ du lịch:**",
            st.session_state.mode
        )

        col_card, col_map = st.columns([1, 1])

        with col_map:

            st.subheader("Bản đồ gợi ý")

            st.info(
                "Bản đồ sẽ được tích hợp ở bước tiếp theo."
            )

        with col_card:

            display_recommendations(
                st.session_state.results
            )


# =====================================================
# 12. TAB RANDOM CHALLENGE - TV4
# =====================================================

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

            # Gọi Backend thuật toán thật
            result = run_random_challenge(
                random_destination
            )

            wheel_placeholder.empty()

            if result and result.get("success"):

                st.session_state.random_result = result

                # Lưu lịch sử
                saved = save_search_history(
                    random_destination
                )

                st.success(
                    "🎉 Random Challenge hoàn thành!"
                )

                if not saved:

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

    # Hiển thị kết quả
    if st.session_state.random_result:

        display_random_result(
            st.session_state.random_result
        )


# =====================================================
# 13. TAB LỊCH TRÌNH
# =====================================================

with tab_schedule:

    st.subheader("Quản lý lịch trình chi tiết")

    st.info(
        "Khu vực này sẽ hiển thị lịch trình nhiều ngày "
        "sau khi hoàn thiện kết nối API Scheduler "
        "với dữ liệu TV1, TV2 và TV3."
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
            f"**Chế độ du lịch:** {st.session_state.mode}"
        )

        st.write(
            f"**Sở thích:** "
            f"{', '.join(st.session_state.hobby)}"
        )


# =====================================================
# 14. TAB LỊCH SỬ
# =====================================================

with tab_history:

    st.subheader("Lịch sử chuyến đi")

    if st.button("🔄 Tải lịch sử tìm kiếm"):

        st.session_state.history = get_search_history()

        st.session_state.history_loaded = True

    if not st.session_state.history_loaded:

        st.info(
            "Nhấn Tải lịch sử tìm kiếm để xem dữ liệu."
        )

    elif st.session_state.history:

        for item in st.session_state.history:

            with st.container(border=True):

                st.write(
                    f"**Từ khóa:** "
                    f"{item.get('keyword', 'Không có')}"
                )

                st.write(
                    f"**Destination:** "
                    f"{item.get('destination', 'Không có')}"
                )

                st.write(
                    f"**Loại tìm kiếm:** "
                    f"{item.get('search_type', 'Không có')}"
                )

                st.caption(
                    f"Thời gian: "
                    f"{item.get('created_at', 'Không có')}"
                )

    else:

        st.info("Chưa có lịch sử tìm kiếm.")
