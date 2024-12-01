import re

min_pattern = r"^\d{1,2}min$"  # 1-99min 형식
hour_pattern = r"^\d{1,2}hour$"  # 1-99hour 형식
day_pattern = r"^\d{1,2}day$"  # 1-99day 형식


def validate_interval(interval: str):
    if not any(
        [
            re.match(min_pattern, interval),
            re.match(hour_pattern, interval),
            re.match(day_pattern, interval),
            interval == "1min",
        ]
    ):
        raise ValueError(f"잘못된 시간 간격 형식입니다: {interval}")
