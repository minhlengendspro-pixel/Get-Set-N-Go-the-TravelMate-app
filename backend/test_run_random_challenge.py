
from services.random_challenge import run_random_challenge


# Dataset giả lập gồm 5 địa điểm
TEST_PLACES = [
    {
        "name": "Bãi Dài",
        "tags": ["biển", "check-in", "thiên nhiên"]
    },
    {
        "name": "Hòn Chồng",
        "tags": ["biển", "thiên nhiên", "tham quan"]
    },
    {
        "name": "Tháp Bà Ponagar",
        "tags": ["văn hóa", "tham quan", "check-in"]
    },
    {
        "name": "VinWonders",
        "tags": ["check-in", "tham quan", "giải trí"]
    },
    {
        "name": "Viện Hải dương học",
        "tags": ["tham quan", "thiên nhiên"]
    }
]


def test_run_random_challenge():
    print("===== TEST RUN RANDOM CHALLENGE =====")

    result = run_random_challenge(TEST_PLACES)

    print("\n1. Tags được chọn:")
    print(result["tags"])

    print("\n2. Fitness:")
    print(result["fitness"])

    print("\n3. Các địa điểm phù hợp:")

    for place in result["places"]:
        print(
            f'{place["name"]} | '
            f'Matched tags: {place["matched_tags"]} | '
            f'Match count: {place["match_count"]}'
        )

    # Kiểm tra cấu trúc kết quả
    assert isinstance(result, dict)
    assert "tags" in result
    assert "fitness" in result
    assert "places" in result

    # Kiểm tra số lượng tags
    assert 2 <= len(result["tags"]) <= 4

    # Kiểm tra Fitness
    assert 0 <= result["fitness"] <= 1

    # Kiểm tra danh sách địa điểm
    assert isinstance(result["places"], list)
    assert len(result["places"]) <= 5

    print("\nTEST RUN RANDOM CHALLENGE: PASSED!")


if __name__ == "__main__":
    test_run_random_challenge()
