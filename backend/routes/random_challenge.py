
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from services.place_data import get_places_by_destination
from services.random_challenge import run_random_challenge


router = APIRouter(
    prefix="/api/random-challenge",
    tags=["Random Challenge"]
)


class RandomChallengeRequest(BaseModel):
    destination: str = Field(min_length=1)


@router.post("/")
def generate_random_challenge(
    request: RandomChallengeRequest
):
    try:
        # 1. Lấy danh sách địa điểm theo tỉnh/thành
        places = get_places_by_destination(
            request.destination
        )
        print("Destination:", request.destination)
        print("So dia diem truy van:", len(places))
        print("Ten dia diem:", [p.get("name") for p in places])
        for place in places:
             print(
               "Name:", place.get("name"),
              "| Tags:", place.get("tags")
            )

        if not places:
            raise HTTPException(
                status_code=404,
                detail="Không tìm thấy địa điểm phù hợp"
            )

        # 2. Chạy thuật toán Random Challenge
        result = run_random_challenge(places)

        # 3. Trả kết quả cho frontend
        return {
            "success": True,
            "destination": request.destination,
            "total": len(result["places"]),
            "data": {
                "tags": result["tags"],
                "fitness": result["fitness"],
                "places": result["places"]
            }
        }

    except HTTPException:
        raise

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    except Exception as error:
        print(f"Random Challenge API error: {error}")

        raise HTTPException(
            status_code=500,
            detail="Lỗi khi thực hiện Random Challenge"
        )
