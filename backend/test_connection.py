
print("===== BAT DAU KIEM TRA =====")

from database import check_connection, DATABASE_NAME

result = check_connection()

if result:
    print("Database:", DATABASE_NAME)
    print("KET NOI THANH CONG!")
else:
    print("KET NOI THAT BAI!")

print("===== KET THUC KIEM TRA =====")
