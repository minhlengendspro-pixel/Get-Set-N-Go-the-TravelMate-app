INPUT TAG SPECIFICATION 
Module: 1 - Input and Context

1. Mục tiêu:
Chuẩn hoá sở thích của người dùng thành các tag tương thích với trường tags trong dataset
- Sử dụng tags làm nguồn đối chiếu chính
- Sử dụng original_tags để tham khảo cách diễn đạt
- Tách địa phương vào destination
- Không tự tạo tag nằm ngoài danh mục hỗ trợ

2. Danh mục 21 tag đã lựa chọn:
* Địa hình:
- biển đảo
- núi rừng
- sông nước
- làng quê & đồng bằng
- đô thị
* Thể loại:
- thiên nhiên
- văn hoá - lịch sử
- nghỉ dưỡng
- ẩm thực
- vui chơi giải trí
* Ẩm thực & trải nghiệm:
- hải sản tươi sống
- ẩm thực đường phố
- cà phê & trà
- đặc sản địa phương
- kiến trúc & di tích cổ
- du lịch tâm linh
- check-in sống ảo
- tắm biển & lặn ngắm san hô
- leo núi & trekking
- ngắm hoàng hôn & bình minh
- lễ hội dân gian

3. Ánh xạ đề xuất:
- đi biển, du lịch biển -> biển đảo
- khám phá rừng núi -> núi rừng
- ngắm cảnh thiên nhiên -> thiên nhiên
- đi chợ nổi, du ngoạn sông -> sông nước
- khám phá làng quê -> làng quê & đồng bằng
- khám phá thành phố -> đô thị
- thư giãn, nghỉ ngơi -> nghỉ dưỡng
- khám phá văn hoá, tìm hiểu lịch sử -> văn hoá - lịch sử
- tham quan di tích, khám phá kiến trúc cổ -> kiến trúc & di tích cổ
- khám phá ẩm thực -> ẩm thực
- ăn hải sản -> hải sản tươi sống
- ăn đặc sản -> đặc sản địa phương
- ăn vặt đường phố -> ẩm thực đường phố
- uống cà phê, uống trà -> cà phê & trà
- trò chơi giải trí, đi công viên giải trí -> vui chơi giải trí
- chụp ảnh check-in, sống ảo -> check-in sống ảo
- lặn ngắm san hô, tắm biển -> tắm biển & lặn ngắm san hô
- tham gia lễ hội -> lễ hội dân gian
- leo núi, trekking -> leo núi & trekking
- ngắm hoàng hôn, ngắm bình minh -> ngắm hoàng hôn & bình minh
- hành hương, đi chùa, viếng đền -> du lịch tâm linh

4. Quy tắc xử lý:
- Một câu có thể chứa nhiều sở thích và tạo ra nhiều tag
- Loại bỏ tag trùng trong kết quả
- Không tự động tạo tag mới từ văn bản người dùng nhập
- Không coi tên địa phương là tag sở thích
