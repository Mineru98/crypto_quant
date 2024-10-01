# -*- coding:utf-8 -*-
import csv
from datetime import datetime
from multiprocessing.dummy import freeze_support

import pyupbit
import redis

r = redis.Redis(host="localhost", port=6379, db=0, password="test1234!")


# CSV 파일에서 데이터를 읽어 Redis에 저장하는 함수
import multiprocessing


def process_row(row):
    timestamp = int(datetime.strptime(row["Date"], "%Y-%m-%d %H:%M:%S").timestamp())
    r.zadd("btc", {str(row): timestamp})


def load_csv_to_redis(file_path):
    with open(file_path, "r", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        csvfile.seek(0)  # 파일 포인터를 처음으로 되돌림
        next(reader)  # 헤더를 건너뜀

        with multiprocessing.Pool() as pool:
            for index, row in enumerate(reader):
                pool.apply_async(process_row, (row,))
            pool.close()
            pool.join()


# 특정 기간의 데이터를 Redis에서 조회하는 함수
def get_data_by_date_range(start_date, end_date):
    start_timestamp = int(datetime.strptime(start_date, "%Y-%m-%d").timestamp())
    end_timestamp = int(datetime.strptime(end_date, "%Y-%m-%d").timestamp())
    return r.zrangebyscore("btc", start_timestamp, end_timestamp)


if __name__ == "__main__":
    freeze_support()
    # 사용 예시
    load_csv_to_redis("notebooks/krw-btc-201709-202409.csv")
    # result = get_data_by_date_range("2023-01-01", "2023-12-31")
    # for item in result:
    #     print(eval(item))
