import pandas as pd
import re
from pathlib import Path

# 1. Đọc Excel
BASE_DIR = Path(__file__).resolve().parent
FILE_PATH = BASE_DIR / "DataSet.xlsx"

df = pd.read_excel(FILE_PATH)

# 2. Chuẩn hóa tên cột
df.columns = df.columns.str.strip()

# 3. Đổi tên cột Excel sang tên trong PlaceSchema
df = df.rename(columns={
    "STT": "id",
    "Tên địa điểm": "name",
    "Vị trí": "destination",
    "Mô tả": "description",
    "Đánh giá": "rating",
    "Ảnh": "image_url",
    "Từ Khóa": "tags"
})

raw_rating = df["rating"].copy()
raw_tags = df["tags"].copy()
raw_destination = df["destination"].copy()

# 4. Chuẩn hóa Rating
def clean_tags(value):
    if pd.isna(value):
        return []

    # Tách các từ khóa bằng dấu phẩy
    tags = re.split(r",", str(value))

    cleaned_tags = []

    for tag in tags:
        # Loại bỏ khoảng trắng và dấu ngoặc kép
        tag = tag.strip().strip('"').strip("'").strip()

        # Chuẩn hóa chữ thường
        tag = tag.casefold()

        if tag:
            cleaned_tags.append(tag)

    # Loại bỏ tag trùng nhưng giữ nguyên thứ tự
    return list(dict.fromkeys(cleaned_tags))
def clean_rating(value):
    if pd.isna(value):
        return 0.0

    value = str(value).strip()
    value = value.split("/")[0]
    value = value.replace(",", ".")

    return float(value)

# 6. Áp dụng chuyển đổi
df["id"] = df["id"].astype(int).astype(str)
df["rating"] = df["rating"].apply(clean_rating)
df["tags"] = df["tags"].apply(clean_tags)

# 7. Kiểm tra kết quả
records = df.to_dict(orient="records")

# 8. Kiểm tra chất lượng dữ liệu

print("\n========== DATA QUALITY CHECK ==========")

# Kiểm tra ID trùng
print("ID trùng:", df["id"].duplicated().sum())

# Kiểm tra địa điểm thiếu tên
print("Thiếu tên:", df["name"].isna().sum())

# Kiểm tra địa điểm thiếu tỉnh/thành
print("Thiếu destination:", df["destination"].isna().sum())

# Kiểm tra rating ngoài khoảng 0-5
invalid_rating = df[
    (df["rating"] < 0) | (df["rating"] > 5)
]
print("Rating không hợp lệ:", len(invalid_rating))

# Kiểm tra tags rỗng
empty_tags = df[
    df["tags"].apply(lambda tags: len(tags) == 0)
]
print("Địa điểm không có tags:", len(empty_tags))

# Kiểm tra tên địa điểm trùng trong cùng tỉnh/thành
duplicate_places = df[
    df.duplicated(
        subset=["name", "destination"],
        keep=False
    )
]
print("Địa điểm trùng tên và tỉnh:", len(duplicate_places))

# Thống kê số lượng địa điểm theo tỉnh
print("\nSố địa điểm theo tỉnh:")
print(df["destination"].value_counts())

print("\n========== CHECK COMPLETED ==========")

print("Số lượng địa điểm:", len(records))
print("\nDữ liệu sau chuẩn hóa:")
for record in records[:3]:
    print(record)

print("\n========== CHI TIẾT DỮ LIỆU LỖI ==========")

# 1. Xem Rating không hợp lệ
invalid_rating = df[
    (df["rating"] < 0) | (df["rating"] > 5)
]

print("\nRating không hợp lệ:")
for index in invalid_rating.index:
    print(
        "Dòng:", index + 2,
        "| Tên:", df.loc[index, "name"],
        "| Rating gốc:", raw_rating.loc[index],
        "| Rating sau xử lý:", df.loc[index, "rating"]
    )

# 2. Xem 10 địa điểm đầu tiên không có Tags
empty_tags = df[
    df["tags"].apply(lambda tags: len(tags) == 0)
]

print("\n10 địa điểm đầu tiên không có Tags:")
for index in empty_tags.index[:10]:
    print(
        "Dòng:", index + 2,
        "| Tên:", df.loc[index, "name"],
        "| Tags gốc:", repr(raw_tags.loc[index])
    )

# 3. Kiểm tra tên tỉnh bị trùng do cách viết
print("\nCác giá trị Destination:")
print(raw_destination.value_counts().to_string())

DESTINATION_MAPPING = {
    "quang ninh": "Quảng Ninh"
}

df["destination"] = (
    df["destination"]
    .astype(str)
    .str.strip()
    .apply(
        lambda x: DESTINATION_MAPPING.get(
            x.casefold(), x
        )
    )
)
print(df["destination"].value_counts())