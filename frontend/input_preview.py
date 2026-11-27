import streamlit as st
from input_form import render_input_form
from backend.config.tag_config import SUPPORTED_TAGS
from input_api import validate_input_api, InputAPIError

st.set_page_config(
    page_title="TravelMate - Input Preview",
    layout="wide"
)
destinations = [
    "Hà Nội",
    "Đà Nẵng",
    "Thành phố Hồ Chí Minh"
]
tag_options = sorted(SUPPORTED_TAGS)
st.title("TravelMate AI")
if "module1_confirmed_payload" not in st.session_state:
    st.session_state["module1_confirmed_payload"] = None
if "module1_input_response" not in st.session_state:
    st.session_state["module1_input_response"] = None
if "module1_api_error" not in st.session_state:
    st.session_state["module1_api_error"] = None
with st.sidebar:
    submitted, payload = render_input_form(
        destinations,
        tag_options
    )
if submitted:
    st.session_state["module1_confirmed_payload"] = payload
    st.session_state["module1_input_response"] = None
    st.session_state["module1_api_error"] = None
    if payload is not None:
        try:
            with st.spinner("Đang xử lý thông tin..."):
                result = validate_input_api(payload)
            st.session_state["module1_input_response"] = result
        except InputAPIError as error:
            st.session_state["module1_api_error"] = str(error)
confirmed_payload = st.session_state["module1_confirmed_payload"]
st.subheader("Dữ liệu chuyến đi đã xác nhận")
if confirmed_payload is None:
    st.info(
        "Vui lòng nhập thông tin hợp lệ và xác nhận biểu mẫu! "
    )
else:
    st.success("Đã có dữ liệu chuyến đi được xác nhận!")
    st.caption(
        "Đây là dữ liệu từ lần xác nhận thành công gần nhất. "
        "Các thay đổi mới chỉ được cập nhật khi xác nhận lại."
    )
    st.json(confirmed_payload)
st.divider()
st.subheader("Kết quả trả về từ Backend")
input_response = st.session_state["module1_input_response"]
api_error = st.session_state["module1_api_error"]
if api_error is not None:
    st.error(api_error)
elif input_response is None:
    st.info("Chưa có kết quả xử lý từ Backend.")
elif input_response["success"] is not True:
    st.error("Backend chưa xác nhận dữ liệu hợp lệ.")
else:
    data = input_response["data"]
    destination = data["destination"]
    mode = data["mode"]
    tags = data["tags"]
    tag_weights = data["tag_weights"]
    budget = data["budget"]
    duration = data["duration"]
    allergies = data["allergies"]
    st.success("Thông tin đã được xác nhận tại Frontend!")

    col1, col2, col3 = st.columns(3)
    col1.metric("Điểm đến", destination)
    col2.metric("Thời gian", f"{duration} ngày")
    if budget is None:
        budget_display = "Chưa xác định"
    else:
        budget_display = f"{budget:,} VNĐ"
    col3.metric("Ngân sách", budget_display)
    st.subheader("Sở thích sau khi chuẩn hóa")
    if len(tags) == 0:
        st.info("Không có tag sở thích được nhận diện.")
    else:
        st.write(", ".join(tags))
    weight_rows = []
    for tag, weight in tag_weights.items():
        row = {
            "Tag sở thích": tag,
            "Trọng số ưu tiên": weight
        }
        weight_rows.append(row)
    st.subheader("Trọng số ưu tiên theo mode")
    st.write("Mode:", mode)
    if len(tag_weights) == 0:
        st.info("Không có trọng số tag để hiển thị.")
    else:
        st.table(weight_rows)
        st.bar_chart(
            weight_rows,
            x="Tag sở thích",
            y="Trọng số ưu tiên"
            )
    st.subheader("Thực phẩm dị ứng đã khai báo")
    if len(allergies) == 0:
        st.write("Không có thông tin dị ứng được khai báo.")
    else:
        st.write(", ".join(allergies))
    with st.expander("Xem JSON Response gốc"):
        st.json(input_response)