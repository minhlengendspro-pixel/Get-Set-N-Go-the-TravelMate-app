
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

RANDOM_API = f"{API_BASE_URL}/api/random-challenge/"
HISTORY_API = f"{API_BASE_URL}/api/search-history/"
DESTINATIONS_API = f"{API_BASE_URL}/api/places/destinations"


# =====================================================
# 2. SESSION STATE
# =====================================================

if "is_submitted" not in st.session_state:
    st.session_state.is_submitted = False

if "random_result" not in st.session_state:
    st.session_state.random_result = None

if "history" not in st.session_state:
    st.session_state.history = []

if "history_loaded" not in st.session_state:
    st.session_state.history_loaded = False

if "hobby" not in st.session_state:
    st.session_state.hobby = []

if "place" not in st.session_state:
    st.session_state.place = "Hà Nội"

if "budget" not in st.session_state:
    st.session_state.budget = 100000

if "duration" not in st.session_state:
    st.session_state.duration = 1


# =====================================================
# 3. CSS GIAO DIỆN
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
# 4. BACKEND API FUNCTIONS
# =====================================================

# Lấy danh sách tỉnh/thành từ MongoDB thông qua Backend
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
        st.error(
            f"Không thể tải danh sách tỉnh/thành: {error}"
        )
        return []


# Gọi API Random Challenge
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
# 5. HIỂN THỊ ĐỊA ĐIỂM RANDOM
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
                        use_container_width=True
                    )

                else:
                    st.caption("Địa điểm chưa có ảnh.")

            # Thông tin địa điểm
            with col_info:

                st.markdown(
                    f"### {index}. {name}"
                )

                # Rating
                rating = item.get("rating")

                if rating is not None:

                    st.write(
                        f"⭐ Rating: {rating}"
                    )

                # Tags gốc của địa điểm
                place_tags = item.get("tags", [])

                st.write("**Tags của địa điểm:**")

                if place_tags:

                    st.write(
                        ", ".join(place_tags)
                    )

                else:
                    st.write("Không có thông tin tags.")

                # Tags trùng khớp
                matched_tags = item.get(
                    "matched_tags",
                    []
                )

                st.write("**Tags khớp với thử thách:**")

                if matched_tags:

                    st.success(
                        ", ".join(matched_tags)
                    )

                else:

                    st.write(
                        "Không có thông tin tags khớp."
                    )

                # Số tags khớp
                match_count = item.get(
                    "match_count",
                    len(matched_tags)
                )

                st.write(
                    f"**Số tags khớp:** {match_count}"
                )

                # Tỷ lệ khớp
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
# 6. HIỂN THỊ TOÀN BỘ KẾT QUẢ RANDOM CHALLENGE
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
        st.session_state.get("place", "")
    )

    tags = data.get("tags", [])
    fitness = data.get("fitness")
    places = data.get("places", [])

    st.divider()

    st.markdown(
        '<div class="random-heading">🎉 KẾT QUẢ RANDOM CHALLENGE</div>',
        unsafe_allow_html=True
    )

    st.write(
        f"**Điểm đến:** {destination}"
    )

    # Tags được thuật toán lựa chọn
    st.subheader("🎯 Tags ngẫu nhiên được lựa chọn")

    if tags:

        tag_columns = st.columns(len(tags))

        for index, tag in enumerate(tags):

            with tag_columns[index]:

                st.info(
                    f"🏷️ {tag}"
                )

    else:

        st.warning(
            "Backend chưa trả về tags."
        )

    # Fitness
    if fitness is not None:

        st.metric(
            "Fitness",
            fitness
        )

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
# 7. TẢI DANH SÁCH ĐIỂM ĐẾN
# =====================================================

destinations = get_destinations()

# Thêm lựa chọn toàn quốc
destination_options = ["Toàn Việt Nam"] + destinations


# =====================================================
# 8. HEADER VÀ CÁC TAB
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
# 9. TAB TRANG CHỦ
# =====================================================

with tab_home:

    with st.sidebar:

        st.header(
            "Đặc điểm cá nhân nổi bật"
        )

        hobby = st.multiselect(
            "Sở thích",
            [
                "Đi biển",
                "Leo núi",
                "Tham quan địa điểm lịch sử",
                "Ngắm cảnh đẹp thiên nhiên"
            ],
            default=st.session_state.hobby
        )

        # Chọn điểm đến động từ MongoDB
        if destination_options:

            default_place = st.session_state.place

            if default_place not in destination_options:
                default_place = destination_options[0]

            place = st.selectbox(
                "Thành phố dự kiến muốn đi",
                destination_options,
                index=destination_options.index(default_place)
            )

        else:

            st.warning(
                "Chưa tải được danh sách tỉnh/thành."
            )

            place = st.session_state.place

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

        if st.button(
            "Tạo lịch trình AI",
            type="primary"
        ):

            st.session_state.is_submitted = True

            st.session_state.hobby = hobby

            st.session_state.place = place

            st.session_state.budget = budget

            st.session_state.duration = duration

    # Nội dung trang chủ
    if not st.session_state.is_submitted:

        st.info(
            "Chào mừng bạn đến với TravelMate AI! "
            "Vui lòng điền đầy đủ thông tin bên thanh sidebar "
            "để được cung cấp lịch trình gợi ý!"
        )

    else:

        col_card, col_map = st.columns([1, 1])

        with col_map:

            st.subheader(
                "Bản đồ gợi ý"
            )

            st.info(
                "Bản đồ sẽ được bổ sung khi hoàn thiện phần "
                "hiển thị dữ liệu địa điểm."
            )

        with col_card:

            st.subheader(
                "Danh sách địa điểm gợi ý"
            )

            # Giữ lại phần hiển thị mẫu từ code gốc
            st.checkbox(
                "Lăng Bác (Hà Nội)"
            )

            st.checkbox(
                "Phố cổ (Hà Nội)"
            )


# =====================================================
# 10. TAB RANDOM CHALLENGE
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

    # Chọn Destination từ MongoDB
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

        # Nút bắt đầu Random
        if st.button(
            "🎲 BẮT ĐẦU RANDOM",
            type="primary",
            use_container_width=True
        ):

            st.session_state.random_result = None

            wheel_placeholder = st.empty()

            # Hiệu ứng vòng quay
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
                        "Kết quả đã được tạo nhưng chưa lưu được lịch sử."
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
# 11. TAB LỊCH TRÌNH
# =====================================================

with tab_schedule:

    st.subheader(
        "Quản lý lịch trình chi tiết"
    )

    st.info(
        "Khu vực này sẽ hiển thị lịch trình nhiều ngày "
        "sau khi hoàn thiện kết nối API Scheduler với dữ liệu TV1, TV2 và TV3."
    )

    if st.session_state.is_submitted:

        st.write(
            f"**Điểm đến:** {st.session_state.place}"
        )

        st.write(
            f"**Số ngày:** {st.session_state.duration}"
        )

        st.write(
            f"**Sở thích:** "
            f"{', '.join(st.session_state.hobby)}"
        )


# =====================================================
# 12. TAB LỊCH SỬ
# =====================================================

with tab_history:

    st.subheader(
        "Lịch sử chuyến đi"
    )

    if st.button(
        "🔄 Tải lịch sử tìm kiếm"
    ):

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

        st.info(
            "Chưa có lịch sử tìm kiếm."
        )
