import streamlit as st
st.set_page_config(page_title = "TravelMate AI", layout = "wide") #Setup cấu hình trang web
if "is_submitted" not in st.session_state: #Ktra phiên đã được xác nhận chưa
    st.session_state.is_submitted = False
tab_home, tab_schedule, tab_history = st.tabs(["Trang chủ", "Lịch trình", "Lịch sử"]) #Tạo thanh tab đầu trang

with tab_home:  #Chỉ áp dụng cho tab trang chủ
    with st.sidebar: #Tạo sidebar nhỏ bên trái màn hình
        st.header("Đặc điểm cá nhân nổi bật")

        hobby = st.multiselect("Sở thích", ["Đi biển", "Leo núi", "Tham quan địa điểm lịch sử", "Ngắm cảnh đẹp thiên nhiên"])
        place = st.selectbox("Thành phố dự kiến muốn đi ", ["Hà Nội", "Đà Nẵng", "Thành phố Hồ Chí Minh", "Toàn Việt Nam"])
        budget = st.number_input("Ngân sách dự kiến (VNĐ)", min_value = 100000, max_value = 10000000, step = 100000)
        duration = st.number_input("Thời gian dự kiến (Ngày)", min_value = 1, max_value = 10, step = 1)

        if st.button("Tạo lịch trình AI", type = "primary"): #Tạo nút xác nhận nổi bật, bấm vào thì cập nhật trạng thái
            st.session_state.is_submitted = True
            st.session_state.hobby = hobby
            st.session_state.place = place
            st.session_state.budget = budget
            st.session_state.duration = duration
            st.session_state.is_submitted = True
    if not st.session_state.is_submitted: #Nếu chưa xác nhận thì hiển thị thông báo
        st.info("Chào mừng bạn đến với TravelMate AI! Vui lòng điền đầy đủ thông tin bên thanh sidebar để được cung cấp lịch trình gợi ý!")
    else: 
        col_card, col_map = st.columns([1, 1]) #Tạo 2 cột map và card địa điểm chia đôi màn hình

        with col_map: #Chỉ áp dụng cho cột map
            st.subheader("Bản đồ gợi ý")
        with col_card: #Chỉ áp dụng cho cột card địa điểm
            st.subheader("Danh sách địa điểm gợi ý")
            st.checkbox("Lăng Bác (Hà Nội)")
            st.checkbox("Phố cổ (Hà Nội)")

with tab_schedule: #Chỉ áp dụng cho tab lịch trình
    st.subheader("Quản lý lịch trình chi tiết")

with tab_history: #Chỉ áp dụng cho tab lịch sử
    st.subheader("Lịch sử chuyến đi")

