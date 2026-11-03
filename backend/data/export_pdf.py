import os
import subprocess
import sys

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
HTML_PATH = os.path.join(CURRENT_DIR, "DATA_SPECIFICATION.html")
PDF_PATH = os.path.join(CURRENT_DIR, "DATA_SPECIFICATION.pdf")

# Các đường dẫn trình duyệt Chromium có sẵn trên Windows
BROWSERS = [
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Google\Chrome\Application\chrome.exe"
]

def export_pdf():
    print("==================================================================")
    print("   XUẤT TÀI LIỆU DATA_SPECIFICATION THÀNH FILE PDF                ")
    print("==================================================================")

    if not os.path.exists(HTML_PATH):
        print(f"❌ Không tìm thấy file HTML: {HTML_PATH}")
        return

    # Tìm trình duyệt có sẵn trên máy
    selected_browser = None
    for b in BROWSERS:
        if os.path.exists(b):
            selected_browser = b
            break

    if not selected_browser:
        print("❌ Không tìm thấy Microsoft Edge hoặc Google Chrome trên máy.")
        return

    browser_name = os.path.basename(selected_browser)
    print(f"-> Đang sử dụng {browser_name} để render PDF chuẩn in ấn A4...")

    cmd = [
        selected_browser,
        "--headless",
        "--disable-gpu",
        "--no-pdf-header-footer",
        f"--print-to-pdf={PDF_PATH}",
        HTML_PATH
    ]

    try:
        subprocess.run(cmd, check=True)
        if os.path.exists(PDF_PATH):
            file_size_kb = round(os.path.getsize(PDF_PATH) / 1024, 1)
            print("==================================================================")
            print(f"✅ XUẤT THÀNH CÔNG FILE PDF: {file_size_kb} KB")
            print(f"📁 Vị trí lưu: {PDF_PATH}")
            print("==================================================================")
            print("👉 Bạn có thể mở File Explorer trong thư mục 'backend/data/' để xem ngay!")
        else:
            print("⚠️ Lệnh chạy xong nhưng chưa thấy file PDF được tạo.")
    except Exception as e:
        print(f"❌ Lỗi khi xuất PDF: {e}")

if __name__ == "__main__":
    export_pdf()
