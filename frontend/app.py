
import streamlit as st
import requests

st.set_page_config(page_title="TravelMate AI", layout="wide")

API_URL = "http://127.0.0.1:8000"


# Lấy danh sách tỉnh/thành từ Backend
@st.cache_data(ttl=300)
def load_destinations():
    try:
        response = requests.get(
            f"{API_URL}/api/places/destinations",
            timeout=10
        )
        response.raise_for_status()

        data = response.json().get("data", [])
        return data if data else ["Hà Nội", "Đà Nẵng", "Thành phố Hồ Chí Minh"]

    except requests.RequestException:
        return ["Hà Nội", "Đà Nẵng", "Thành phố Hồ Chí Minh"]


# Chuyển sở thích giao diện thành tag chuẩn của Backend
HOBBY_TAGS = {
    "Đi biển": "biển đảo",
    "Leo núi": "leo núi & trekking",
    "Tham quan địa điểm lịch sử": "kiến trúc & di tích cổ",
    "Ngắm cảnh đẹp thiên nhiên": "thiên nhiên"
}


if "is_submitted" not in st.session_state:
    st.session_state.is_submitted = False

if "results" not in st.session_state:
    st.session_state.results = []


tab_home, tab_schedule, tab_history = st.tabs(
    ["Trang chủ", "Lịch trình", "Lịch sử"]
)


with tab_home:

    with st.sidebar:

        st.header("Đặc điểm cá nhân nổi bật")

        mode_options = {
            "Đi du lịch một mình": "solo",
            "Đi du lịch cùng người yêu": "couple",
            "Đi du lịch cùng gia đình": "family",
            "Để AI tự do lựa chọn": "random"
        }

        selected_mode = st.selectbox(
            "Bạn đi du lịch với ai?",
            options=list(mode_options.keys())
        )

        mode = mode_options[selected_mode]

        hobby = st.multiselect(
            "Sở thích",
            list(HOBBY_TAGS.keys())
        )

        destinations = load_destinations()

        place = st.selectbox(
            "Thành phố dự kiến muốn đi",
            destinations
        )

        budget = st.number_input(
            "Ngân sách dự kiến (VNĐ)",
            min_value=100000,
            max_value=10000000,
            step=100000
        )

        duration = st.number_input(
            "Thời gian dự kiến (Ngày)",
            min_value=1,
            max_value=10,
            step=1
        )

        submit = st.button(
            "Tạo lịch trình AI",
            type="primary"
        )

    # Xử lý khi người dùng nhấn nút
    if submit:

        if not hobby:
            st.warning("Fen hãy chọn ít nhất một sở thích nhé!")

        else:
            interests = [
                HOBBY_TAGS[item]
                for item in hobby
            ]

            payload = {
                "destination": place,
                "interests": interests,
                "top_k": 10,
                "mode": mode
            }

            try:
                with st.spinner("TravelMate đang tìm địa điểm phù hợp..."):

                    response = requests.post(
                        f"{API_URL}/api/places/recommend",
                        json=payload,
                        timeout=30
                    )

                    response.raise_for_status()

                    data = response.json()

                    st.session_state.results = data.get("data", [])
                    st.session_state.is_submitted = True

                    st.session_state.mode = mode
                    st.session_state.place = place
                    st.session_state.budget = budget
                    st.session_state.duration = duration
                    st.session_state.hobby = hobby

            except requests.RequestException as error:
                st.session_state.results = []
                st.session_state.is_submitted = False

                st.error(f"Không thể kết nối Backend: {error}")

    # Hiển thị kết quả
    if not st.session_state.is_submitted:

        st.info(
            "Chào mừng bạn đến với TravelMate AI! "
            "Vui lòng điền thông tin bên thanh sidebar để nhận gợi ý."
        )

    else:

        st.write(
            "Chế độ du lịch:",
            st.session_state.mode
        )

        col_card, col_map = st.columns([1, 1])

        with col_map:
            st.subheader("Bản đồ gợi ý")
            st.info("Bản đồ sẽ được tích hợp ở bước tiếp theo.")

        with col_card:

            st.subheader("Danh sách địa điểm gợi ý")

            results = st.session_state.results

            if not results:
                st.warning(
                    "Không tìm thấy địa điểm phù hợp. "
                    "Fen thử thay đổi sở thích nhé!"
                )

            for item in results:

                with st.container(border=True):

                    st.subheader(item.get("name", "Chưa có tên"))

                    image_url = item.get("image_url")

                    if image_url:
                        st.image(image_url, width="stretch")
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
                        ", ".join(tags)
                    )

                    score = item.get("score", 0)

                    st.write(
                        f"🎯 Điểm phù hợp: {score * 100:.1f}%"
                    )


with tab_schedule:
    st.subheader("Quản lý lịch trình chi tiết")

    if st.session_state.is_submitted:
        st.write("Điểm đến:", st.session_state.place)
        st.write("Thời gian:", st.session_state.duration, "ngày")
        st.write("Ngân sách:", st.session_state.budget, "VNĐ")


with tab_history:
    st.subheader("Lịch sử chuyến đi")
