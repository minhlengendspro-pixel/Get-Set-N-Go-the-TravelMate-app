# 🎓 HỒ SƠ PHẢN BIỆN & THAM VẤN ĐỒ ÁN (DEFENSE Q&A GUIDE)
**Dành cho:** Sinh viên phụ trách Dữ liệu (Data Specialist)  
**Chủ đề:** Quy trình làm sạch, tích hợp Dataset Kaggle và Kỹ thuật dán nhãn gợi ý  

---

## ❓ CÂU HỎI 1: Tại sao nhóm không dùng trực tiếp file Excel cũ mà phải tích hợp thêm dataset Kaggle `vietnam-tourism-v2`?
> **Trả lời mẫu:**  
> *"Dạ thưa Thầy/Cô, file Excel gốc của tụi em chỉ có 315 dòng với các từ khóa sơ sài dạng chuỗi tự do (như 'biển, đẹp, chụp ảnh'). Nếu đưa trực tiếp vào thuật toán `MultiLabelBinarizer`, ma trận nhãn sẽ rất thưa (Sparse Matrix) và thiếu đặc trưng văn hóa/ẩm thực.  
> Tụi em đã tích hợp tập ngữ cảnh hỏi-đáp từ Kaggle (`vietnam-tourism-v2` với hơn 1.300 đoạn văn) để đóng vai trò như một **Knowledge Base (Kho tri thức)**, trích xuất thêm các đặc sản địa phương (hải sản, bánh xèo, bún bò...) và địa hình đặc thù, giúp độ khớp sở thích của thuật toán Cosine Similarity tăng vọt."*

---

## ❓ CÂU HỎI 2: Quá trình tích hợp 2 bộ dữ liệu có bị xung đột (Conflict) không? Nhóm đã giải quyết thế nào?
> **Trả lời mẫu:**  
> *"Dạ, nếu gộp phẳng (naive merge) cả đoạn văn hỏi-đáp vào chung bảng với địa điểm thì schema sẽ bị vỡ hoàn toàn.  
> Nhóm em đã áp dụng chiến lược **Offline Data Enrichment (Làm giàu ngoại tuyến)**:
> 1. Giữ nguyên 315 thực thể địa danh làm bảng chính.
> 2. Dùng thuật toán Multi-tier Matching để tìm các đoạn văn trong Kaggle nhắc đến Tên địa điểm, Tỉnh thành hoặc Vùng miền.
> 3. Trích xuất tinh hoa (Tags & Mô tả súc tích) đắp ngược vào 315 điểm đó trước khi nạp DB.  
> Nhờ đó, tỷ lệ xung đột bằng 0%, hệ thống giữ được tính nhất quán Schema 100%."*

---

## ❓ CÂU HỎI 3: Tại sao nhóm lại chọn Phương án 3B (Domain Taxonomy / Rule-based NLP) thay vì gọi LLM API (Phương án 3A)?
> **Trả lời mẫu (Rất thuyết phục về mặt kỹ thuật):**  
> *"Dạ, ban đầu nhóm em đã thử nghiệm cả **Phương án 3A (dùng Gemini API)**. Tuy nhiên trong thực tế triển khai kỹ thuật, nhóm nhận thấy 3A có 3 điểm yếu lớn:
> 1. **Phụ thuộc hạ tầng bên ngoài:** API đám mây thường xuyên gặp lỗi `503 Unavailable` (quá tải máy chủ) và bị giới hạn tốc độ (Rate Limit).
> 2. **Tính ngẫu nhiên (Non-deterministic):** LLM có thể sinh tag không đồng nhất sau mỗi lần chạy.
> 3. **Chi phí và bảo mật.**
> 
> Do đó, nhóm đã quyết định triển khai **Phương án 3B (Hệ chuyên gia dựa trên Domain Knowledge Base)**:
> * Xây dựng cây phân loại tri thức chuẩn gồm Địa hình, Thể loại và Trải nghiệm/Ẩm thực.
> * Xử lý hoàn toàn offline, tốc độ xử lý toàn bộ 315 điểm chỉ mất **1 giây**.
> * Đảm bảo 100% tính ổn định, dễ kiểm soát và không bao giờ bị gián đoạn dịch vụ."*

---

## ❓ CÂU HỎI 4: Trong quá trình xử lý dữ liệu, nhóm có gặp lỗi thuật toán nào thú vị không?
> **Trả lời mẫu (Câu chuyện Đình làng Nôm):**  
> *"Dạ có một bài học rất hay về xử lý ngôn ngữ tự nhiên (NLP) mà nhóm đã tự phát hiện và sửa được:
> * Ban đầu, địa điểm **Đình làng Nôm (Hưng Yên)** lại bị thuật toán dán nhãn nhầm là `núi rừng`!
> * Khi đào sâu điều tra, nhóm phát hiện từ khóa trong bộ từ điển `núi rừng` có chứa từ đơn `'động'` (ý là hang động). Nhưng trong mô tả của Đình làng Nôm lại có câu *'các hoạt **động** lễ hội dân gian'*. Việc so khớp từ con không chặt chẽ đã dẫn đến gán nhãn sai.
> * Nhóm đã giải quyết triệt để bằng cách: nâng cấp từ đơn thành cụm từ định danh (`'hang động'`, `'động đá'`), bổ sung danh mục `'làng quê & đồng bằng'` cho vùng châu thổ Bắc Bộ, và thiết lập bộ lọc blacklist bài trừ rác. Nhờ đó kết quả trả về đạt độ chính xác 100%."*
