import streamlit as st
import importlib
import services.api_client
import services.places_service
importlib.reload(services.api_client)
importlib.reload(services.places_service)
from services.api_client import fetch_safe_restaurants, check_backend_connection
from services.places_service import get_featured_places

# ==============================================================================
# 1. CẤU HÌNH TRANG VÀ THIẾT KẾ PHONG CÁCH ATLAS EDITORIAL
# ==============================================================================
st.set_page_config(
    page_title="Get, Set N Go - TravelMate AI",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Khởi tạo trạng thái phiên làm việc (Session State Guard)
if "is_submitted" not in st.session_state:
    st.session_state.is_submitted = False
if "safe_dining_data" not in st.session_state:
    st.session_state.safe_dining_data = None
if "api_error" not in st.session_state:
    st.session_state.api_error = None
if "destination" not in st.session_state:
    st.session_state.destination = "Đà Nẵng"
if "group_allergens" not in st.session_state:
    st.session_state.group_allergens = ["tôm"]
if "max_budget_per_meal" not in st.session_state:
    st.session_state.max_budget_per_meal = 120000
if "group_size" not in st.session_state:
    st.session_state.group_size = 4
if "travel_mode" not in st.session_state:
    st.session_state.travel_mode = "Gia đình"
if "selected_itinerary_places" not in st.session_state:
    st.session_state.selected_itinerary_places = []
if "selected_dining_places" not in st.session_state:
    st.session_state.selected_dining_places = []

# ==============================================================================
# 2. INJECT CSS TÙY BIẾN THEO BẢN MẪU ATLAS TRAVEL GUIDE (KHÔNG ICON)
# ==============================================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,500;0,600;0,700;1,400&family=Plus+Jakarta+Sans:wght@400;500;600;700&family=Space+Mono:wght@400;700&display=swap');

    /* Tông màu nền chính toàn trang */
    .stApp {
        background-color: #fcfdfd;
        font-family: 'Plus Jakarta Sans', sans-serif;
    }

    /* Tùy biến thanh Sidebar màu xanh Navy đậm */
    [data-testid="stSidebar"] {
        background-color: #0b1e2d !important;
        color: #ffffff !important;
    }
    [data-testid="stSidebar"] * {
        color: #cbd5e1;
    }
    [data-testid="stSidebar"] label {
        color: #ffffff !important;
        font-weight: 600 !important;
        font-size: 0.88rem !important;
        letter-spacing: 0.3px;
    }
    [data-testid="stSidebar"] .stSelectbox, 
    [data-testid="stSidebar"] .stMultiSelect, 
    [data-testid="stSidebar"] .stNumberInput {
        margin-bottom: 12px;
    }

    /* Logo thương hiệu thanh bên */
    .sidebar-brand {
        font-family: 'Playfair Display', Georgia, serif;
        font-size: 1.65rem;
        font-weight: 700;
        color: #ffffff !important;
        letter-spacing: -0.5px;
        margin-bottom: 2px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .sidebar-brand-sub {
        font-family: 'Space Mono', monospace;
        font-size: 0.68rem;
        color: #64748b !important;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        margin-bottom: 20px;
    }
    .sidebar-section-header {
        font-family: 'Space Mono', monospace;
        font-size: 0.72rem;
        color: #94a3b8 !important;
        text-transform: uppercase;
        letter-spacing: 1.2px;
        border-bottom: 1px solid #1e3a52;
        padding-bottom: 6px;
        margin-top: 18px;
        margin-bottom: 12px;
    }

    /* Banner chính phong cách Cẩm nang Khám phá (The Explorer's Atlas) */
    .atlas-hero-banner {
        background: linear-gradient(135deg, #eaf2f8 0%, #e2edf6 100%);
        border: 1px solid #cbdde9;
        border-radius: 18px;
        padding: 36px 40px;
        margin-bottom: 30px;
        position: relative;
        overflow: hidden;
    }
    .atlas-hero-category {
        font-family: 'Space Mono', monospace;
        font-size: 0.75rem;
        font-weight: 700;
        color: #3b6b88;
        text-transform: uppercase;
        letter-spacing: 2px;
        margin-bottom: 8px;
    }
    .atlas-hero-title {
        font-family: 'Playfair Display', Georgia, serif;
        font-size: 2.7rem;
        font-weight: 700;
        color: #0f2b48;
        line-height: 1.15;
        margin-bottom: 10px;
    }
    .atlas-hero-subtitle {
        color: #526b7d;
        font-size: 1.05rem;
        margin-bottom: 20px;
        max-width: 650px;
    }

    /* Thanh tìm kiếm nhanh dạng thẻ pill */
    .hero-search-pill-box {
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
        background-color: #ffffff;
        padding: 10px 16px;
        border-radius: 30px;
        border: 1px solid #c7dceb;
        max-width: 600px;
        box-shadow: 0 4px 12px rgba(15, 43, 72, 0.05);
    }
    .pill-item {
        font-size: 0.82rem;
        font-weight: 600;
        color: #1e3a56;
        background-color: #f0f6fa;
        padding: 5px 14px;
        border-radius: 20px;
        border: 1px solid #d4e4f0;
    }

    /* Thẻ phong cách du lịch (Travel Mode Cards) */
    .mode-card {
        background: linear-gradient(145deg, #1b4965 0%, #0c2b44 100%);
        border-radius: 14px;
        padding: 22px 20px;
        color: #ffffff;
        min-height: 135px;
        position: relative;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        border: 1px solid #235c7f;
    }
    .mode-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 20px rgba(12, 43, 68, 0.25);
    }
    .mode-title {
        font-family: 'Playfair Display', Georgia, serif;
        font-size: 1.45rem;
        font-weight: 700;
        color: #ffffff;
        margin-bottom: 4px;
    }
    .mode-desc {
        font-size: 0.82rem;
        color: #94b8d2;
        line-height: 1.35;
    }
    .mode-tag {
        font-family: 'Space Mono', monospace;
        font-size: 0.65rem;
        color: #72a2c6;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 6px;
    }

    /* Thẻ Quán ăn An toàn (Safe Dining Card) - Module 2 */
    .dining-card {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 22px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.04);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .dining-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.08);
        border-color: #cbd5e1;
    }
    .dining-location {
        font-family: 'Space Mono', monospace;
        font-size: 0.72rem;
        font-weight: 700;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        margin-bottom: 4px;
    }
    .dining-name {
        font-family: 'Playfair Display', Georgia, serif;
        font-size: 1.6rem;
        font-weight: 700;
        color: #0f2b48;
        margin-bottom: 6px;
    }
    .dining-address {
        font-size: 0.88rem;
        color: #64748b;
        margin-bottom: 14px;
    }

    /* Huy hiệu trạng thái an toàn theo chuẩn WCAG */
    .badge-safe {
        background-color: #ecfdf5;
        color: #065f46;
        border: 1px solid #a7f3d0;
        padding: 5px 12px;
        border-radius: 8px;
        font-size: 0.82rem;
        font-weight: 700;
        letter-spacing: 0.5px;
        display: inline-block;
    }
    .badge-conditional {
        background-color: #fffbeb;
        color: #92400e;
        border: 1px solid #fde68a;
        padding: 5px 12px;
        border-radius: 8px;
        font-size: 0.82rem;
        font-weight: 700;
        letter-spacing: 0.5px;
        display: inline-block;
    }

    /* Thẻ Điểm đến tham quan (Places Collection Card - Người 3) */
    .place-collection-card {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 16px;
        padding: 16px;
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.03);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .place-collection-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 10px 20px rgba(0, 0, 0, 0.07);
        border-color: #cbd5e1;
    }
    .place-card-category {
        font-family: 'Space Mono', monospace;
        font-size: 0.68rem;
        font-weight: 700;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 1.2px;
        margin-bottom: 4px;
    }
    .place-card-title {
        font-family: 'Playfair Display', Georgia, serif;
        font-size: 1.35rem;
        font-weight: 700;
        color: #0f2b48;
        line-height: 1.25;
        margin-bottom: 8px;
    }
    .place-card-desc {
        font-size: 0.86rem;
        color: #475569;
        line-height: 1.45;
        margin-bottom: 14px;
        flex-grow: 1;
    }

    /* Hộp cảnh báo y tế */
    .warning-box {
        background-color: #fff8f1;
        border-left: 4px solid #ea580c;
        border-radius: 6px;
        padding: 10px 14px;
        font-size: 0.86rem;
        color: #9a3412;
        margin-top: 12px;
        margin-bottom: 12px;
    }

    /* Hộp tóm tắt bộ lọc trên trang chính */
    .filter-summary-bar {
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 16px 20px;
        margin-bottom: 24px;
    }

    /* Khung nhãn phân định trách nhiệm thành viên */
    .role-boundary-pill {
        font-family: 'Space Mono', monospace;
        font-size: 0.68rem;
        background-color: #f1f5f9;
        color: #475569;
        padding: 3px 8px;
        border-radius: 4px;
        border: 1px solid #cbd5e1;
        display: inline-block;
        margin-left: 8px;
        vertical-align: middle;
    }
</style>
""", unsafe_allow_html=True)


# ==============================================================================
# 3. HỘP THOẠI CHI TIẾT ĐỊA ĐIỂM (BỐ CỤC 2 CỘT EDITORIAL & ẢNH HD SẮC NÉT)
# ==============================================================================
@st.dialog("Chi tiết điểm đến tham quan", width="large")
def show_place_detail_dialog(place: dict):
    """
    Hien thi trang mo ta chi tiet thuc su cua dia diem duoc click tu The Collection.
    Ket hop Giai phap 1 (Bo cuc 2 cot 48/52) va Giai phap 2 (Anh HD 1200x800 sac net).
    """
    name = place.get("name", "Điểm đến tham quan")
    destination = place.get("destination", "Việt Nam")
    rating = place.get("rating", "4.5/5")
    category = place.get("category", "sightseeing")
    desc = place.get("description") or place.get("original_description", "Thông tin điểm đến đang được cập nhật.")
    ref_context = place.get("reference_context", "")
    tags = place.get("tags") or place.get("original_tags", [])
    image_url = place.get("image", "")

    # BỐ CỤC 2 CỘT: Cột ảnh (48%) và Cột nội dung (52%)
    col_img, col_content = st.columns([48, 52], gap="large")

    with col_img:
        # 1. Hiển thị ảnh HD sắc nét trong khung bo góc
        if image_url:
            st.image(image_url, caption=f"Toàn cảnh: {name} ({destination})", use_container_width=True)

        # 2. Khung thông tin vắn tắt (Quick Facts Card)
        st.markdown(f"""
        <div style="background-color: #f8fafc; border: 1px solid #e2e8f0; border-radius: 12px; padding: 14px; margin-top: 10px;">
            <div style="font-family: 'Space Mono', monospace; font-size: 0.72rem; color: #64748b; text-transform: uppercase; margin-bottom: 6px;">THÔNG TIN ĐIỂM ĐẾN</div>
            <div style="font-size: 0.88rem; color: #1e293b; line-height: 1.6;">
                • <strong>Mã định danh:</strong> <code>{place.get('id', 'POI-000')}</code><br/>
                • <strong>Đánh giá thực khách:</strong> ★ {rating}<br/>
                • <strong>Phân loại:</strong> {category.capitalize()}<br/>
                • <strong>Tỉnh / Thành phố:</strong> {destination}
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_content:
        # Tiêu đề danh lam phong cách tạp chí
        st.markdown(f'<div style="font-family: Space Mono, monospace; font-size: 0.75rem; color: #64748b; text-transform: uppercase;">{destination.upper()} • PHÂN LOẠI: {category.upper()}</div>', unsafe_allow_html=True)
        st.markdown(f'<h2 style="font-family: Playfair Display, serif; color: #0f2b48; margin-top: 0; margin-bottom: 12px; font-size: 1.9rem;">{name}</h2>', unsafe_allow_html=True)

        st.markdown("#### Mô tả tổng quan")
        st.write(desc)

        # Bối cảnh văn hóa lịch sử từ tập dữ liệu làm giàu Kaggle
        if ref_context and len(ref_context) > 20:
            st.markdown("#### Bối cảnh Văn hóa & Lịch sử")
            st.info(ref_context)

        # Nhãn phân tầng trải nghiệm
        if tags:
            st.markdown("#### Đặc trưng & Trải nghiệm")
            tag_pills = " ".join([f"`{t}`" for t in tags[:6]])
            st.markdown(tag_pills)

        st.markdown("---")
        # Nút hành động tương tác (Điểm khớp nối Người 4)
        col_btn_add, col_btn_close = st.columns([6, 4])
        with col_btn_add:
            if st.button(f"Thêm {name} vào lịch trình (Hook Người 4)", type="primary", use_container_width=True):
                if name not in st.session_state.selected_itinerary_places:
                    st.session_state.selected_itinerary_places.append(name)
                st.toast(f"Đã lưu {name} vào danh sách chờ xếp lịch trình của Người 4!")
        with col_btn_close:
            if st.button("Đóng", use_container_width=True):
                st.rerun()


@st.dialog("Hồ sơ Kiểm định An toàn Y tế & Thực đơn", width="large")
def show_restaurant_detail_dialog(restaurant: dict):
    """
    Hien thi ho so y te chi tiet cua nha hang duoc chon tu Section 02.
    Bao gom phan tich nguy co di ung cheo, danh sach mon an toan va cam ket ve sinh.
    """
    name = restaurant.get("name", "Quán ăn ẩm thực")
    address = restaurant.get("address", "Đang cập nhật địa chỉ")
    cost = restaurant.get("avg_cost_per_person", 0)
    rating = restaurant.get("rating", 4.5)
    is_100_safe = restaurant.get("is_100_percent_safe", False)
    warning_note = restaurant.get("warning_note", "")
    safe_dishes = restaurant.get("safe_dishes", [])
    unsafe_dishes = restaurant.get("unsafe_dishes", [])
    dest = restaurant.get("destination", st.session_state.destination)
    source = restaurant.get("source", "")

    badge_html = (
        '<span class="badge-safe" style="font-size: 0.9rem;">[100% AN TOÀN Y TẾ]</span>'
        if is_100_safe
        else '<span class="badge-conditional" style="font-size: 0.9rem;">[AN TOÀN CÓ ĐIỀU KIỆN]</span>'
    )
    source_html = f'<div style="font-size: 0.85rem; color: #0369a1; margin-bottom: 14px; background: #f0f9ff; padding: 6px 12px; border-radius: 6px; border: 1px solid #bae6fd;">• <strong>Nguồn kiểm chứng thực tế:</strong> {source}</div>' if source else ''

    st.markdown(f'<div style="font-family: Space Mono, monospace; font-size: 0.75rem; color: #64748b; text-transform: uppercase;">{dest.upper()} • HỒ SƠ KIỂM ĐỊNH Y TẾ MODULE 2</div>', unsafe_allow_html=True)
    st.markdown(f'<h2 style="font-family: Playfair Display, serif; color: #0f2b48; margin-top: 0; margin-bottom: 6px; font-size: 1.85rem;">{name}</h2>', unsafe_allow_html=True)
    st.markdown(f'<div style="margin-bottom: 12px;">{badge_html} &nbsp;&nbsp; <span style="color: #64748b; font-size: 0.9rem;">Địa chỉ: {address}</span></div>', unsafe_allow_html=True)
    if source_html:
        st.markdown(source_html, unsafe_allow_html=True)

    c_cost, c_rate, c_safe, c_unsafe = st.columns(4)
    with c_cost:
        st.metric("Chi phí ước tính", f"{cost:,} VNĐ")
    with c_rate:
        st.metric("Đánh giá thực khách", f"★ {rating}/5.0")
    with c_safe:
        st.metric("Món an toàn đề xuất", f"{len(safe_dishes)} món")
    with c_unsafe:
        st.metric("Món cần kiêng cữ", f"{len(unsafe_dishes)} món")

    st.markdown("---")

    if warning_note:
        st.markdown(f"""
        <div class="warning-box" style="margin-bottom: 16px;">
            <strong>LƯU Ý Y TẾ QUAN TRỌNG TỪ HỆ THỐNG:</strong><br/>
            {warning_note}
        </div>
        """, unsafe_allow_html=True)

    col_s, col_u = st.columns(2)
    with col_s:
        st.markdown("#### Món ăn an toàn (Được phép phục vụ)")
        if safe_dishes:
            for d in safe_dishes:
                st.markdown(f"• **{d.get('dish_name')}** — `{d.get('price', 0):,} VNĐ`")
        else:
            st.write("Không có món an toàn nào được ghi nhận.")

    with col_u:
        st.markdown("#### Món cần kiêng cữ (Tránh tiếp xúc)")
        if unsafe_dishes:
            for d in unsafe_dishes:
                raw_matched = d.get("matched_allergens", [])
                matched_detail = ", ".join(raw_matched) if raw_matched else "thành phần dị ứng trùng lặp của đoàn"
                st.markdown(f"• <span style='color: #b91c1c; font-weight: 600;'>{d.get('dish_name')}</span> — `{d.get('price', 0):,} VNĐ`<br/><span style='font-size: 0.8rem; color: #dc2626; margin-left: 12px;'>→ Chứa chất dị ứng của đoàn: {matched_detail}</span>", unsafe_allow_html=True)
        else:
            st.info("Thực đơn không có món nào xung đột với danh mục dị ứng của đoàn.")

    st.markdown("---")
    col_btn_add, col_btn_close = st.columns([6, 4])
    with col_btn_add:
        is_sel = name in st.session_state.selected_dining_places
        btn_txt = f"Bỏ chọn {name}" if is_sel else f"Chọn {name} cho lịch trình đoàn (Hook Người 4)"
        if st.button(btn_txt, type="primary", key=f"dlg_add_{restaurant.get('restaurant_id', '0')}", use_container_width=True):
            if is_sel:
                st.session_state.selected_dining_places.remove(name)
                st.toast(f"Đã bỏ {name} khỏi danh sách ẩm thực đoàn.")
            else:
                st.session_state.selected_dining_places.append(name)
                st.toast(f"Đã thêm {name} vào danh sách địa điểm ăn uống an toàn cho Người 4!")
            st.rerun()
    with col_btn_close:
        if st.button("Đóng hồ sơ", key=f"dlg_close_{restaurant.get('restaurant_id', '0')}", use_container_width=True):
            st.rerun()


# ==============================================================================
# 4. THANH BÊN (SIDEBAR): BỘ LỌC CHUYẾN ĐI & AN TOÀN Y TẾ
# ==============================================================================
with st.sidebar:
    st.markdown('<div class="sidebar-brand">Get, Set N Go.</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-brand-sub">HỆ THỐNG LẬP KẾ HOẠCH DU LỊCH & BẢO VỆ Y TẾ</div>', unsafe_allow_html=True)

    with st.form(key="travel_filter_form"):
        # ----------------------------------------------------------------------
        # PHẦN 1: THÔNG TIN CHUYẾN ĐI (CHUNG CHO CẢ NHÓM: NGƯỜI 1, 3, 4)
        # ----------------------------------------------------------------------
        st.markdown('<div class="sidebar-section-header">01. Thông tin chuyến đi</div>', unsafe_allow_html=True)

        place = st.selectbox(
            "Điểm đến dự kiến",
            ["Đà Nẵng", "Hà Nội", "TP. Hồ Chí Minh", "Khánh Hòa", "Lâm Đồng", "Quảng Ninh", "Quảng Nam", "Ninh Bình"],
            index=0
        )

        hobbies = st.multiselect(
            "Phong cách & Sở thích chuyến đi",
            ["Thiên nhiên", "Lịch sử & Văn hóa", "Ẩm thực địa phương", "Nghỉ dưỡng & Thư giãn", "Phiêu lưu mạo hiểm", "Check-in ngắm cảnh"],
            default=["Thiên nhiên", "Ẩm thực địa phương"]
        )

        col_days, col_budget = st.columns(2)
        with col_days:
            duration = st.number_input("Thời gian (Ngày)", min_value=1, max_value=30, value=3, step=1)
        with col_budget:
            total_budget = st.number_input("Tổng ngân sách (VNĐ)", min_value=500000, max_value=100000000, value=6000000, step=500000)

        # ----------------------------------------------------------------------
        # PHẦN 2: RÀNG BUỘC AN TOÀN Y TẾ & NGÂN SÁCH (MODULE 2 - NGƯỜI 2)
        # ----------------------------------------------------------------------
        st.markdown('<div class="sidebar-section-header">02. An toàn Y tế & Ẩm thực (Module 2)</div>', unsafe_allow_html=True)

        group_size = st.number_input(
            "Quy mô đoàn (Số thành viên)",
            min_value=1,
            max_value=50,
            value=4,
            step=1,
            help="Cây quyết định nhóm sẽ đối soát thực đơn để bảo đảm mọi thành viên đều có món ăn an toàn."
        )

        allergen_list = [
            "tôm",
            "cua",
            "hải sản",
            "đậu phộng",
            "trứng",
            "sữa",
            "thịt bò",
            "thịt gà",
            "gluten"
        ]

        group_allergens = st.multiselect(
            "Khai báo dị ứng thực phẩm của đoàn",
            options=allergen_list,
            default=["tôm"],
            help="Hệ thống loại bỏ triệt để các quán ăn phục vụ 100% món ăn dính chất dị ứng của đoàn."
        )

        # Công thức quy đổi trần chi phí 1 bữa ăn từ tổng ngân sách chuyến đi
        computed_meal_budget = int((total_budget * 0.35) / (duration * 2 * group_size)) if duration and group_size else 120000
        computed_meal_budget = max(40000, round(computed_meal_budget, -3))

        max_meal_budget = st.number_input(
            "Trần ngân sách / người / bữa (VNĐ)",
            min_value=30000,
            max_value=2000000,
            value=int(computed_meal_budget),
            step=10000,
            help="Các nhà hàng có mức giá vượt qua giới hạn này sẽ bị cắt tỉa theo luật Hard Pruning."
        )

        # Nút xác nhận toàn bộ bộ lọc
        btn_submit = st.form_submit_button("XÁC NHẬN & LỌC QUÁN ĂN AN TOÀN", type="primary")

    # Xử lý sự kiện Submit
    if btn_submit:
        st.session_state.is_submitted = True
        st.session_state.destination = place
        st.session_state.group_allergens = group_allergens
        st.session_state.max_budget_per_meal = max_meal_budget
        st.session_state.group_size = group_size
        st.session_state.duration = duration
        st.session_state.total_budget = total_budget

        # Kiểm tra kết nối Backend và gọi API
        if not check_backend_connection():
            st.session_state.api_error = (
                "Máy chủ Backend chưa được khởi động tại cổng 8000. "
                "Vui lòng chạy lệnh: cd backend; uvicorn main:app --reload"
            )
            st.session_state.safe_dining_data = None
        else:
            st.session_state.api_error = None
            with st.spinner("Hệ thống đang kết nối cơ sở dữ liệu và đánh giá rủi ro y tế..."):
                res = fetch_safe_restaurants(
                    destination=place,
                    group_allergens=group_allergens,
                    max_budget_per_person=max_meal_budget,
                    group_size=group_size
                )
                if res["success"]:
                    st.session_state.safe_dining_data = res["data"]
                else:
                    st.session_state.api_error = res["error"]
                    st.session_state.safe_dining_data = None


# ==============================================================================
# 5. KHU VỰC NỘI DUNG CHÍNH (MAIN EDITORIAL CANVAS)
# ==============================================================================

# ------------------------------------------------------------------------------
# HERO BANNER: THE EXPLORER'S ATLAS
# ------------------------------------------------------------------------------
st.markdown("""
<div class="atlas-hero-banner">
    <div class="atlas-hero-category">CẨM NANG KHÁM PHÁ - THE EXPLORER'S ATLAS</div>
    <div class="atlas-hero-title">Lên Kế Hoạch Cho Chuyến Đi Hoàn Hảo</div>
    <div class="atlas-hero-subtitle">
        Khám phá điểm đến theo phong cách riêng của bạn. Định tuyến thông minh, tối ưu chi phí và kiểm soát an toàn tuyệt đối cho cả đoàn.
    </div>
    <div class="hero-search-pill-box">
        <span class="pill-item">Thiên nhiên</span>
        <span class="pill-item">Lịch sử & Di sản</span>
        <span class="pill-item">Ẩm thực bản địa</span>
        <span class="pill-item">Nghỉ dưỡng & Chill</span>
    </div>
</div>
""", unsafe_allow_html=True)


# ------------------------------------------------------------------------------
# PHẦN 01: PHONG CÁCH DU LỊCH (NHIỆM VỤ NGƯỜI 1: BỘ TRỌNG SỐ NGỮ CẢNH)
# ------------------------------------------------------------------------------
st.markdown("""
<div style="margin-bottom: 8px;">
    <span style="font-family: 'Space Mono', monospace; font-size: 0.72rem; color: #64748b; letter-spacing: 1.5px; text-transform: uppercase;">01 - TRAVEL STYLE</span>
    <span class="role-boundary-pill">Khu vực Người 1: Nhận diện chế độ & sinh trọng số</span>
    <h2 style="font-family: 'Playfair Display', Georgia, serif; font-size: 1.85rem; color: #0f2b48; margin-top: 2px; margin-bottom: 16px;">Chọn Phong Cách Du Lịch Của Bạn</h2>
</div>
""", unsafe_allow_html=True)

col_m1, col_m2, col_m3, col_m4 = st.columns(4)

with col_m1:
    st.markdown("""
    <div class="mode-card">
        <div class="mode-tag">01 / CÁ NHÂN</div>
        <div class="mode-title">Độc hành</div>
        <div class="mode-desc">Tự do khám phá theo nhịp độ riêng, linh hoạt và chủ động.</div>
    </div>
    """, unsafe_allow_html=True)

with col_m2:
    st.markdown("""
    <div class="mode-card">
        <div class="mode-tag">02 / CẶP ĐÔI</div>
        <div class="mode-title">Cặp đôi</div>
        <div class="mode-desc">Không gian lãng mạn, ẩm thực tinh tế và trải nghiệm gắn kết.</div>
    </div>
    """, unsafe_allow_html=True)

with col_m3:
    st.markdown("""
    <div class="mode-card" style="border: 2px solid #60a5fa;">
        <div class="mode-tag" style="color: #93c5fd;">03 / ĐOÀN ĐÔNG [ĐANG CHỌN]</div>
        <div class="mode-title">Gia đình & Bạn bè</div>
        <div class="mode-desc">Cân bằng sở thích nhiều thế hệ, kiểm soát dị ứng y tế và ngân sách.</div>
    </div>
    """, unsafe_allow_html=True)

with col_m4:
    st.markdown("""
    <div class="mode-card">
        <div class="mode-tag">04 / BẤT NGỜ</div>
        <div class="mode-title">Ngẫu hứng</div>
        <div class="mode-desc">Để thuật toán mở đường cho những khám phá mới lạ bất ngờ.</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br/>", unsafe_allow_html=True)


# ------------------------------------------------------------------------------
# PHẦN 02: QUÁN ĂN AN TOÀN Y TẾ & ẨM THỰC (MODULE 2 CỦA BẠN - NGƯỜI 2)
# ------------------------------------------------------------------------------
st.markdown("""
<div style="margin-bottom: 8px;">
    <span style="font-family: 'Space Mono', monospace; font-size: 0.72rem; color: #64748b; letter-spacing: 1.5px; text-transform: uppercase;">02 - SAFE DINING & GASTRONOMY</span>
    <span class="role-boundary-pill" style="background-color: #ecfdf5; color: #065f46; border-color: #a7f3d0; font-weight: 700;">Nhiệm vụ Người 2 (Bạn): Cắt tỉa An toàn Y tế & Ngân sách</span>
    <h2 style="font-family: 'Playfair Display', Georgia, serif; font-size: 1.85rem; color: #0f2b48; margin-top: 2px; margin-bottom: 16px;">Quán Ăn An Toàn Y Tế & Ẩm Thực Đoàn</h2>
</div>
""", unsafe_allow_html=True)

if not st.session_state.is_submitted:
    st.info(
        "Chào mừng bạn đến với TravelMate AI! "
        "Vui lòng thiết lập thông tin chuyến đi và các chất dị ứng của đoàn ở thanh bên trái, "
        "sau đó bấm 'XÁC NHẬN & LỌC QUÁN ĂN AN TOÀN' để nhận danh sách đề xuất đạt chuẩn y tế."
    )
else:
    # Hộp thông tin tóm tắt bộ lọc ràng buộc
    allergens_text = ", ".join(st.session_state.group_allergens) if st.session_state.group_allergens else "Không có khai báo dị ứng"
    st.markdown(f"""
    <div class="filter-summary-bar">
        <div style="font-family: 'Space Mono', monospace; font-size: 0.72rem; color: #475569; letter-spacing: 1.2px; text-transform: uppercase; margin-bottom: 4px;">
            THÔNG SỐ RÀNG BUỘC ĐANG THI HÀNH (MODULE 2)
        </div>
        <div style="font-size: 0.92rem; color: #1e293b; line-height: 1.6;">
            • <strong>Điểm đến khảo sát:</strong> {st.session_state.destination} &nbsp;|&nbsp; 
            • <strong>Quy mô đoàn:</strong> {st.session_state.group_size} người &nbsp;|&nbsp; 
            • <strong>Dị ứng cần phòng ngừa:</strong> <span style="color: #b91c1c; font-weight: 600;">{allergens_text}</span> &nbsp;|&nbsp; 
            • <strong>Trần ngân sách bữa ăn:</strong> <strong>{st.session_state.max_budget_per_meal:,} VNĐ</strong> / người / bữa
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Xử lý kết quả trả về từ Backend
    if st.session_state.api_error:
        st.error(f"[LỖI KẾT NỐI HỆ THỐNG]: {st.session_state.api_error}")
    elif st.session_state.safe_dining_data:
        data = st.session_state.safe_dining_data
        
        # Bảng 4 chỉ số thống kê (Metrics Dashboard)
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.metric("Tổng số quán tại khu vực", f"{data.get('total_candidates', 0)} quán")
        with c2:
            st.metric("Vượt qua an toàn (Pass)", f"{data.get('passed_count', 0)} quán")
        with c3:
            st.metric("Loại bỏ do nguy cơ dị ứng", f"{data.get('pruned_unsafe_count', 0)} quán")
        with c4:
            st.metric("Loại bỏ do vượt ngân sách", f"{data.get('pruned_overbudget_count', 0)} quán")

        st.markdown("<br/>", unsafe_allow_html=True)

        # Danh sách thẻ nhà hàng an toàn được đề xuất
        safe_list = data.get("safe_restaurants", [])
        if not safe_list:
            st.markdown(f"""
            <div style="background-color: #fff8f1; border: 1px solid #fed7aa; border-radius: 16px; padding: 24px; text-align: center; margin-top: 14px;">
                <div style="font-family: 'Space Mono', monospace; font-size: 0.72rem; color: #c2410c; font-weight: 700; text-transform: uppercase; margin-bottom: 6px;">
                    THÔNG BÁO TỐI ƯU HÓA RÀNG BUỘC (MODULE 2)
                </div>
                <h3 style="font-family: 'Playfair Display', serif; color: #9a3412; margin-top: 0; margin-bottom: 8px;">
                    Không tìm thấy quán ăn nào thỏa mãn đồng thời cả 2 điều kiện
                </h3>
                <p style="font-size: 0.92rem; color: #431407; max-width: 620px; margin: 0 auto 14px auto; line-height: 1.6;">
                    Mức trần ngân sách <strong>{st.session_state.max_budget_per_meal:,} VNĐ</strong> hoặc danh mục dị ứng <strong>{allergens_text}</strong> quá nghiêm ngặt đối với mặt bằng giá tại <strong>{st.session_state.destination}</strong>.
                </p>
                <div style="font-size: 0.86rem; color: #7c2d12;">
                    <strong>Gợi ý khắc phục:</strong> Tăng trần ngân sách bữa ăn ở thanh bên Sidebar hoặc rà soát lại các chất dị ứng ít nguy cơ để hệ thống mở rộng phạm vi tìm kiếm quán an toàn.
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            # Bộ lọc phân loại mức độ an toàn (Tier Filter)
            col_tier, col_count = st.columns([7, 3])
            with col_tier:
                tier_filter = st.pills(
                    "Phân loại an toàn y tế",
                    ["Tất cả quán đạt chuẩn", "100% An toàn tuyệt đối", "An toàn có điều kiện kiêng món"],
                    default="Tất cả quán đạt chuẩn",
                    label_visibility="collapsed"
                )
            
            # Lọc danh sách theo tier_filter
            filtered_list = safe_list
            if tier_filter == "100% An toàn tuyệt đối":
                filtered_list = [r for r in safe_list if r.get("is_100_percent_safe")]
            elif tier_filter == "An toàn có điều kiện kiêng món":
                filtered_list = [r for r in safe_list if not r.get("is_100_percent_safe")]

            with col_count:
                st.markdown(f'<div style="text-align: right; font-family: \'Space Mono\', monospace; font-size: 0.75rem; color: #64748b; padding-top: 8px;">HIỂN THỊ: <strong>{len(filtered_list)} / {len(safe_list)}</strong> QUÁN ĐẠT CHUẨN</div>', unsafe_allow_html=True)

            if not filtered_list:
                st.info(f"Không có nhà hàng nào thuộc phân nhóm '{tier_filter}' tại {st.session_state.destination}.")
            else:
                for idx, r in enumerate(filtered_list):
                    name = r.get("name", "Quán ăn ẩm thực")
                    address = r.get("address", "Đang cập nhật địa chỉ")
                    cost = r.get("avg_cost_per_person", 0)
                    rating = r.get("rating", 4.5)
                    is_100_safe = r.get("is_100_percent_safe", False)
                    warning_note = r.get("warning_note")
                    safe_dishes = r.get("safe_dishes", [])
                    unsafe_dishes = r.get("unsafe_dishes", [])
                    r_id = r.get("restaurant_id", f"R_{idx}")

                    # Badge trạng thái tuân thủ WCAG (Dual-channel)
                    badge_html = (
                        '<span class="badge-safe">[100% AN TOÀN Y TẾ]</span>'
                        if is_100_safe
                        else '<span class="badge-conditional">[AN TOÀN CÓ ĐIỀU KIỆN]</span>'
                    )

                    source = r.get("source", "")
                    source_line = f'<div style="font-size: 0.8rem; color: #0284c7; margin-top: 4px; font-style: italic;">• Nguồn dữ liệu: {source}</div>' if source else ''

                    st.markdown(f"""
                    <div class="dining-card">
                        <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                            <div>
                                <div class="dining-location">{st.session_state.destination.upper()} • ĐỊA ĐIỂM ẨM THỰC #{idx+1:02d}</div>
                                <div class="dining-name">{name}</div>
                                <div class="dining-address">{address}</div>
                                {source_line}
                            </div>
                            <div>
                                {badge_html}
                            </div>
                        </div>
                        <div style="display: flex; gap: 24px; font-size: 0.92rem; color: #334155; margin-bottom: 6px;">
                            <span><strong>Mức chi phí ước tính:</strong> {cost:,} VNĐ / người</span>
                            <span><strong>Đánh giá thực khách:</strong> ★ {rating}/5.0</span>
                            <span><strong>Món an toàn đề xuất:</strong> {len(safe_dishes)} món</span>
                        </div>
                    """, unsafe_allow_html=True)

                    if warning_note:
                        st.markdown(f"""
                        <div class="warning-box">
                            <strong>Lưu ý y tế quan trọng:</strong> {warning_note}
                        </div>
                        """, unsafe_allow_html=True)

                    # Khối mở rộng bóc tách chi tiết thực đơn
                    with st.expander(f"Xem thực đơn chi tiết của {name} ({len(safe_dishes)} món an toàn đề xuất)"):
                        col_safe, col_unsafe = st.columns([1, 1])
                        with col_safe:
                            st.markdown("**Món ăn an toàn cho người dị ứng:**")
                            for d in safe_dishes:
                                st.write(f"• **{d.get('dish_name')}** — {d.get('price', 0):,} VNĐ")
                        with col_unsafe:
                            if unsafe_dishes:
                                st.markdown("**Món cần kiêng (chứa chất dị ứng của đoàn):**")
                                for d in unsafe_dishes:
                                    raw_matched = d.get("matched_allergens", [])
                                    matched_text = f"chứa: {', '.join(raw_matched)}" if raw_matched else "chứa thành phần dị ứng của đoàn"
                                    st.write(f"• <span style='color: #b91c1c; font-weight: 500;'>{d.get('dish_name')}</span> *({matched_text})*", unsafe_allow_html=True)
                            else:
                                st.write("• Thực đơn không có món nào xung đột với danh mục dị ứng của đoàn.")

                    # Cụm nút hành động tương tác (Điểm khớp nối Người 4 và Modal hồ sơ y tế)
                    st.markdown("<div style='margin-top: 14px;'></div>", unsafe_allow_html=True)
                    col_btn_sel, col_btn_det = st.columns([6, 4])
                    with col_btn_sel:
                        is_selected = name in st.session_state.selected_dining_places
                        btn_label = f"Đã chọn {name} [Bỏ chọn]" if is_selected else f"Chọn {name} cho đoàn (Hook Người 4)"
                        btn_type = "secondary" if is_selected else "primary"
                        if st.button(btn_label, key=f"btn_dining_sel_{r_id}", type=btn_type, use_container_width=True):
                            if is_selected:
                                st.session_state.selected_dining_places.remove(name)
                                st.toast(f"Đã bỏ {name} khỏi danh sách ẩm thực đoàn.")
                            else:
                                st.session_state.selected_dining_places.append(name)
                                st.toast(f"Đã lưu {name} vào danh sách ẩm thực an toàn của đoàn!")
                            st.rerun()

                    with col_btn_det:
                        if st.button("Hồ sơ y tế chi tiết →", key=f"btn_dining_view_{r_id}", use_container_width=True):
                            show_restaurant_detail_dialog(r)

                    st.markdown("</div>", unsafe_allow_html=True)

            # Khung tổng kết các nhà hàng an toàn đã chọn bàn giao cho Người 4
            if st.session_state.selected_dining_places:
                selected_str = " • ".join(st.session_state.selected_dining_places)
                st.markdown(f"""
                <div style="background-color: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 12px; padding: 14px 18px; margin-top: 16px;">
                    <div style="font-family: 'Space Mono', monospace; font-size: 0.72rem; color: #166534; font-weight: 700; text-transform: uppercase; margin-bottom: 4px;">
                        DANH SÁCH QUÁN ĂN AN TOÀN ĐÃ CHỌN (SẴN SÀNG BÀN GIAO CHO NGƯỜI 4 LẬP LỊCH ĂN UỐNG)
                    </div>
                    <div style="font-size: 0.92rem; color: #15803d; line-height: 1.5;">
                        • <strong>Số lượng đã lưu:</strong> {len(st.session_state.selected_dining_places)} quán &nbsp;|&nbsp; 
                        • <strong>Chi tiết:</strong> {selected_str}
                    </div>
                </div>
                """, unsafe_allow_html=True)


# ------------------------------------------------------------------------------
# PHẦN 03: THE COLLECTION - ĐỊA ĐIỂM NỔI BẬT (NHIỆM VỤ NGƯỜI 3: CHẤM ĐIỂM & GỢI Ý POI)
# ------------------------------------------------------------------------------
st.markdown("---")
st.markdown(f"""
<div style="margin-bottom: 8px;">
    <span style="font-family: 'Space Mono', monospace; font-size: 0.72rem; color: #64748b; letter-spacing: 1.5px; text-transform: uppercase;">03 - THE COLLECTION</span>
    <span class="role-boundary-pill">Điểm khớp nối Người 3: Dữ liệu 315 điểm đến & Thuật toán Cosine/Jaccard</span>
    <h2 style="font-family: 'Playfair Display', Georgia, serif; font-size: 1.85rem; color: #0f2b48; margin-top: 2px; margin-bottom: 6px;">Điểm Đến Tham Quan Nổi Bật</h2>
    <p style="font-size: 0.92rem; color: #64748b; margin-bottom: 18px;">
        Khám phá các danh thắng tiêu biểu tại <strong>{st.session_state.destination}</strong>. Bấm nút <strong>'Xem chi tiết'</strong> trên từng thẻ để mở thông tin văn hóa, hình ảnh HD và lịch sử.
    </p>
</div>
""", unsafe_allow_html=True)

# Lấy danh sách địa điểm thực tế từ tập 315 POIs đã làm giàu qua places_service
featured_places = get_featured_places(st.session_state.destination, limit=3)

if not featured_places:
    st.info(f"Đang đồng bộ dữ liệu điểm tham quan cho khu vực {st.session_state.destination}...")
else:
    cols_places = st.columns(len(featured_places))
    for idx, p in enumerate(featured_places):
        with cols_places[idx]:
            p_name = p.get("name", "Địa điểm tham quan")
            p_desc = p.get("description") or p.get("original_description", "")
            p_dest = p.get("destination", st.session_state.destination)
            p_rating = p.get("rating", "4.5/5")
            p_tags = p.get("tags") or p.get("original_tags", [])
            p_img = p.get("image_data_uri") or p.get("image", "")
            tag_display = p_tags[1] if len(p_tags) > 1 else (p_tags[0] if p_tags else "Tham quan")

            # Ảnh thumbnail xem trước sắc nét trên thẻ Card (khớp bản mẫu Atlas)
            img_html = f'<div style="height: 180px; overflow: hidden; border-radius: 12px; margin-bottom: 12px; background: #e2e8f0;"><img src="{p_img}" style="width: 100%; height: 100%; object-fit: cover;" /></div>' if p_img else ''

            st.markdown(f"""
            <div class="place-collection-card">
                <div>
                    {img_html}
                    <div class="place-card-category">{p_dest.upper()} • ĐÁNH GIÁ: {p_rating}</div>
                    <div class="place-card-title">{p_name}</div>
                    <div class="place-card-desc">{p_desc[:110]}...</div>
                    <div style="margin-bottom: 14px;">
                        <span class="pill-item" style="font-size: 0.72rem;">{tag_display}</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Nút tương tác bấm vào để mở Hộp thoại chi tiết (st.dialog)
            if st.button(f"Xem chi tiết {p_name} →", key=f"btn_detail_place_{p.get('id', idx)}", use_container_width=True):
                show_place_detail_dialog(p)

# Footer phong cách cẩm nang xuất bản
st.markdown("<br/><br/>", unsafe_allow_html=True)
st.markdown("""
<div style="display: flex; justify-content: space-between; border-top: 1px solid #e2e8f0; padding-top: 15px; font-family: 'Space Mono', monospace; font-size: 0.7rem; color: #94a3b8;">
    <span>GET, SET N GO — HỆ THỐNG GỢI Ý DU LỊCH & AN TOÀN Y TẾ</span>
    <span>FIELD GUIDE / VOL. 01 — PHIÊN BẢN 2026</span>
</div>
""", unsafe_allow_html=True)
