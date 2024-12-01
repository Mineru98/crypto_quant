import polars as pl

from trading.utils.validation import validate_interval


def search_db_data(
    conn,
    start_date: str,
    end_date: str,
    interval: str = "1min",
    table_name: str = "KRW-BTC",
) -> pl.DataFrame:
    """특정 기간의 데이터를 DB에서 로드하는 함수

    Args:
        start_date (str): 시작일자 (YYYY-MM-DD)
        end_date (str): 종료일자 (YYYY-MM-DD)
        interval (str, optional): 데이터 주기. Defaults to "1min".

    Returns:
        pl.DataFrame: 필터링된 데이터프레임
    """
    validate_interval(interval)
    try:
        if interval == "1min":
            query = f"""
                SELECT 
                    date as Date,
                    open,
                    high,
                    low,
                    close,
                    volume
                FROM \"{table_name}\" 
                WHERE DATE(date) BETWEEN %s AND %s
                ORDER BY date
            """
        else:
            # 시간 간격 문자열 파싱 및 변환
            if interval.endswith("min"):
                minutes = int(interval[:-3])  # "min" 제거하고 숫자만 추출
                time_bucket = f"{minutes} minutes" if 2 <= minutes <= 59 else "1 day"
            elif interval.endswith("hour"):
                hours = int(interval[:-4])  # "hour" 제거하고 숫자만 추출
                time_bucket = f"{hours} hours"
            elif interval.endswith("day"):
                days = int(interval[:-3])  # "day" 제거하고 숫자만 추출
                time_bucket = f"{days} days" if 1 <= days <= 6 else "1 day"
            else:
                time_bucket = "1 day"

            query = f"""
                SELECT 
                    time_bucket('{time_bucket}', date) as Date,
                    FIRST(open, date) as open,
                    MAX(high) as high,
                    MIN(low) as low, 
                    LAST(close, date) as close,
                    SUM(volume) as volume
                FROM \"{table_name}\"
                WHERE DATE(date) BETWEEN %s AND %s
                GROUP BY 1
                ORDER BY 1
            """

        with conn.cursor() as cur:
            cur.execute(query, (start_date, end_date))
            data = cur.fetchall()
            df = pl.DataFrame(
                [
                    (
                        row[0],
                        float(row[1]) if row[1] else None,
                        float(row[2]) if row[2] else None,
                        float(row[3]) if row[3] else None,
                        float(row[4]) if row[4] else None,
                        row[5],
                    )
                    for row in data
                ],
                schema=["Date", "open", "high", "low", "close", "volume"],
                orient="row",
            )

        return df
    finally:
        conn.close()
