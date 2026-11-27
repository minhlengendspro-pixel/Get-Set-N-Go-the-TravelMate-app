import streamlit as st

MODE_OPTIONS = {
    "Đi du lịch một mình": "solo",
    "Đi du lịch cùng người yêu": "couple",
    "Đi du lịch cùng gia đình": "family",
    "Để AI tự do lựa chọn": "random"
}
MODE_DESCRIPTIONS = {
    "solo": "Hãy lựa chọn những trải nghiệm phù hợp với sở thích cá nhân của bạn.",
    "couple": "Bạn có thể mô tả những sở thích chung của cả hai người.",
    "family": "Hãy bổ sung những nhu cầu và sở thích của các thành viên trong gia đình.",
    "random": "Bạn có thể lựa chọn sở thích hoặc mô tả thêm mong muốn của mình.",
}

def render_input_form(destinations, tag_options):
    st.header("Thông tin chuyến đi")
    selected_mode = st.selectbox(
        "Bạn đi du lịch với ai?",
        options=list(MODE_OPTIONS.keys())
    )
    mode = MODE_OPTIONS[selected_mode]
    st.info(MODE_DESCRIPTIONS[mode])
    has_budget = st.checkbox(
        "Tôi đã xác định ngân sách",
        value=True
    )
    # Tạo biểu mẫu tĩnh
    with st.form(
        key="travel_input_form",
        clear_on_submit=False
    ):
        destination = st.selectbox(
        "Bạn muốn đi du lịch ở đâu?",
        options=destinations
        )
        interests = st.multiselect(
        "Bạn yêu thích những trải nghiệm nào?",
        options=tag_options
        )
        if has_budget:
            budget = st.number_input(
                "Ngân sách dự kiến (VNĐ)",
                min_value=0,
                value=3000000,
                step=100000
            )
        else:
            budget = None
        duration = st.number_input(
            "Thời gian du lịch (ngày)",
            min_value=1,
            max_value=30,
            value=3,
            step=1
        )
        allergies_text = st.text_input(
            "Bạn bị dị ứng với thực phẩm nào?",
            placeholder="Ví dụ: tôm, cua, lạc"
        )
        user_text = st.text_area(
            "Mô tả thêm sở thích của bạn (Nếu cần)",
            placeholder="Ví dụ: Mình thích đi biển và nghỉ ngơi"
        )
        st.caption("Nội dung tối đa 30 từ.")
        submitted = st.form_submit_button(
            "Xác nhận thông tin",
            type="primary"
        )
    if not submitted:
        return False, None
    word_count = len(user_text.split())
    st.caption(f"Số từ: {word_count}/30")
    if word_count > 30:
        st.warning("Nội dung không được vượt quá 30 từ.")
        return True, None
    allergies = []
    for allergy in allergies_text.split(","):
        allergy = allergy.strip()
        if allergy != "" and allergy not in allergies:
            allergies.append(allergy)
    payload = {
        "destination": destination,
        "mode": mode,
        "interests": interests,
        "budget": budget,
        "duration": duration,
        "allergies": allergies,
        "user_text": user_text
    }
    return True, payload