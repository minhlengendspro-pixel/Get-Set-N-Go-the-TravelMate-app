import requests
from pydantic import ValidationError
from backend.models.input_context import InputContextResponse

API_BASE_URL = "http://127.0.0.1:8000"
INPUT_API_URL = f"{API_BASE_URL}/api/input/validate"

HTTP_ERRORS = {
    404: "Lỗi 404: Không tìm thấy Input API.",
    405: "Lỗi 405: Input API yêu cầu phương thức POST."
}

class InputAPIError(Exception):
    pass

def get_validation_error(response): # Đọc thông báo lỗi 422
    default_message = "Dữ liệu đầu vào không hợp lệ."
    try:
        error_data = response.json()
    except ValueError:
        return default_message
    if not isinstance(error_data, dict):
        return default_message
    detail = error_data.get("detail")
    if isinstance(detail, str):
        return detail
    if isinstance(detail, list):
        messages = []
        for item in detail:
            if isinstance(item, dict):
                message = item.get("msg")
                if isinstance(message, str):
                    messages.append(message)
        if len(messages) > 0:
            return "; ".join(messages)
    return default_message

def check_input_response(result): # Kiểm tra cấu trúc Response
    if not isinstance(result, dict):
        raise InputAPIError(
            "Response không phải dictionary."
        )
    if result.get("success") is not True:
        raise InputAPIError(
            "Backend chưa xác nhận dữ liệu hợp lệ."
        )
    if not isinstance(result.get("message"), str):
        raise InputAPIError(
            "Response thiếu thông báo hợp lệ."
        )
    data = result.get("data")
    if not isinstance(data, dict):
        raise InputAPIError(
            "Response thiếu dữ liệu chuyến đi."
        )
    for field in InputContextResponse.model_fields:
        if field not in data:
            raise InputAPIError(
                f"Response thiếu trường {field}."
            )
    try:
        InputContextResponse.model_validate(
            data,
            strict=True
        )
    except ValidationError:
        raise InputAPIError(
            "Dữ liệu Backend trả về không đúng cấu trúc."
        )

def validate_input_api(payload): # Gửi Request đến Backend
    try:
        response = requests.post(
            INPUT_API_URL,
            json = payload,
            timeout=10,
        )
    except requests.exceptions.Timeout:
        raise InputAPIError(
            "Backend phản hồi quá chậm. Vui lòng thử lại."
        )
    except requests.exceptions.ConnectionError:
        raise InputAPIError(
            "Không thể kết nối Backend. "
            "Hãy kiểm tra FastAPI đã được khởi động chưa."
        )
    except requests.exceptions.RequestException:
        raise InputAPIError(
            "Đã xảy ra lỗi khi gửi yêu cầu đến Backend."
        )
    # Kiểm tra HTTP status code
    status_code = response.status_code
    if status_code in HTTP_ERRORS:
        raise InputAPIError(HTTP_ERRORS[status_code])
    elif status_code == 422:
        detail = get_validation_error(response)
        raise InputAPIError(f"Lỗi 422: {detail}")
    elif status_code >= 500:
        raise InputAPIError(
            f"Lỗi {status_code}: Backend gặp lỗi nội bộ."
            )
    elif status_code != 200:
        raise InputAPIError(
            f"Input API trả về mã HTTP {status_code}."
            )
    try: # Đọc json
        result = response.json()
    except ValueError:
        raise InputAPIError(
            "Backend không trả về JSON hợp lệ."
        )
    check_input_response(result)
    return result
