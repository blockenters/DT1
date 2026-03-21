"""
매출/수요 예측 프로젝트 - 데이터 생성 스크립트
2023-01-01 ~ 2024-12-31 (730일) 기준
"""

import numpy as np
import pandas as pd
from pathlib import Path

np.random.seed(42)

DATA_DIR = Path(__file__).parent
date_range = pd.date_range("2023-01-01", "2024-12-31", freq="D")
n_days = len(date_range)

# ============================================================
# 공휴일 목록 (대한민국)
# ============================================================
holidays = [
    # 2023
    "2023-01-01", "2023-01-21", "2023-01-22", "2023-01-23", "2023-01-24",
    "2023-03-01", "2023-05-05", "2023-05-27", "2023-06-06",
    "2023-08-15", "2023-09-28", "2023-09-29", "2023-09-30",
    "2023-10-03", "2023-10-09", "2023-12-25",
    # 2024
    "2024-01-01", "2024-02-09", "2024-02-10", "2024-02-11", "2024-02-12",
    "2024-03-01", "2024-05-05", "2024-05-15", "2024-06-06",
    "2024-08-15", "2024-09-16", "2024-09-17", "2024-09-18",
    "2024-10-03", "2024-10-09", "2024-12-25",
]
holiday_set = set(pd.to_datetime(holidays))

# ============================================================
# 1. daily_sales.csv (730 rows)
# ============================================================
day_of_week = date_range.dayofweek.to_numpy()  # 0=Mon ... 6=Sun
month = date_range.month.to_numpy()

# 계절성 factor (여름/겨울 높음, 봄/가을 보통)
seasonal = 1.0 + 0.15 * np.sin(2 * np.pi * (date_range.dayofyear.to_numpy() / 365 - 0.05))

# 주말 여부
is_weekend = (day_of_week >= 5).astype(int)

# 공휴일
is_holiday = np.array([1 if d in holiday_set else 0 for d in date_range])

# 이벤트 (월 2~3회)
is_event = np.zeros(n_days, dtype=int)
for y in [2023, 2024]:
    for m in range(1, 13):
        month_mask = (date_range.year == y) & (date_range.month == m)
        idx = np.where(month_mask)[0]
        n_events = np.random.choice([2, 3])
        event_idx = np.random.choice(idx, size=n_events, replace=False)
        is_event[event_idx] = 1

# 매출액 (만원)
base_sales = np.where(is_weekend, np.random.uniform(300, 700, n_days),
                      np.random.uniform(200, 500, n_days))
sales = base_sales * seasonal
sales += is_holiday * np.random.uniform(50, 150, n_days)
sales += is_event * np.random.uniform(30, 100, n_days)
# 연말 부스트
year_end = ((month == 11) | (month == 12)).astype(int)
sales += year_end * np.random.uniform(30, 80, n_days)
sales = np.round(sales, 1)

# 객단가 (만원)
avg_price = np.round(np.random.uniform(2.5, 6.5, n_days), 2)

# 주문건수
order_count = np.round(sales / avg_price).astype(int)

# 요일 이름
weekday_names = ["월", "화", "수", "목", "금", "토", "일"]
weekday_kr = [weekday_names[d] for d in day_of_week]

# 결측 삽입 (매출액에 약 3%)
nan_idx = np.random.choice(n_days, size=int(n_days * 0.03), replace=False)
sales_with_nan = sales.astype(float).copy()
sales_with_nan[nan_idx] = np.nan

df_sales = pd.DataFrame({
    "날짜": date_range.strftime("%Y-%m-%d"),
    "매출액": sales_with_nan,
    "주문건수": order_count,
    "객단가": avg_price,
    "요일": weekday_kr,
    "공휴일여부": is_holiday,
    "이벤트여부": is_event,
})
df_sales.to_csv(DATA_DIR / "daily_sales.csv", index=False, encoding="utf-8-sig")
print(f"daily_sales.csv: {len(df_sales)} rows")

# ============================================================
# 2. weather_daily.csv (730 rows) - 서울 현실적 기온
# ============================================================
# 서울 월별 평균 기온 (근사)
monthly_temp = {1: -2.4, 2: 0.4, 3: 5.7, 4: 12.5, 5: 17.8, 6: 22.2,
                7: 24.9, 8: 25.7, 9: 21.2, 10: 14.8, 11: 7.2, 12: 0.4}

temp = np.array([monthly_temp[m] + np.random.normal(0, 3) for m in month])
temp = np.round(temp, 1)

# 강수량
precip = np.zeros(n_days)
for i in range(n_days):
    m = month[i]
    if m in [6, 7, 8]:  # 여름 장마
        if np.random.random() < 0.35:
            precip[i] = np.random.exponential(15)
    elif m in [12, 1, 2]:  # 겨울
        if np.random.random() < 0.10:
            precip[i] = np.random.exponential(3)
    else:
        if np.random.random() < 0.20:
            precip[i] = np.random.exponential(8)
precip = np.round(precip, 1)

# 습도
humidity = np.clip(
    np.where(np.isin(month, [6, 7, 8]),
             np.random.normal(75, 8, n_days),
             np.random.normal(55, 10, n_days)),
    20, 100).round(0).astype(int)

# 날씨
weather_list = []
for i in range(n_days):
    if precip[i] > 0:
        if temp[i] <= 0:
            weather_list.append("눈")
        else:
            weather_list.append("비")
    else:
        weather_list.append(np.random.choice(["맑음", "흐림"], p=[0.65, 0.35]))

df_weather = pd.DataFrame({
    "날짜": date_range.strftime("%Y-%m-%d"),
    "기온": temp,
    "강수량": precip,
    "습도": humidity,
    "날씨": weather_list,
})
df_weather.to_csv(DATA_DIR / "weather_daily.csv", index=False, encoding="utf-8-sig")
print(f"weather_daily.csv: {len(df_weather)} rows")

# ============================================================
# 3. products_daily.csv (7300 rows = 730일 x 10카테고리)
# ============================================================
categories = ["식품", "의류", "전자", "뷰티", "생활", "스포츠", "가구", "도서", "완구", "반려"]

# 카테고리별 기본 매출 비중
base_share = {
    "식품": 0.18, "의류": 0.14, "전자": 0.15, "뷰티": 0.10,
    "생활": 0.12, "스포츠": 0.08, "가구": 0.07, "도서": 0.05,
    "완구": 0.06, "반려": 0.05,
}

rows = []
for i, date in enumerate(date_range):
    m = date.month
    total = sales[i]  # 결측 없는 원본 사용

    # 계절별 가중치 조정
    share = dict(base_share)
    if m in [6, 7, 8]:  # 여름
        share["스포츠"] *= 1.6
        share["의류"] *= 1.4
        share["식품"] *= 0.9
        share["가구"] *= 0.8
    elif m in [12, 1, 2]:  # 겨울
        share["식품"] *= 1.4
        share["가구"] *= 1.3
        share["스포츠"] *= 0.7
        share["의류"] *= 0.9
    if m in [11, 12]:  # 연말
        share["전자"] *= 1.5
        share["완구"] *= 1.8
        share["도서"] *= 1.2

    # 정규화
    total_share = sum(share.values())
    for cat in categories:
        share[cat] /= total_share

    for cat in categories:
        cat_sales = round(total * share[cat] * np.random.uniform(0.85, 1.15), 1)
        cat_orders = max(1, int(cat_sales / np.random.uniform(2, 8)))
        rows.append({
            "날짜": date.strftime("%Y-%m-%d"),
            "카테고리": cat,
            "카테고리매출": cat_sales,
            "카테고리주문수": cat_orders,
        })

df_products = pd.DataFrame(rows)
df_products.to_csv(DATA_DIR / "products_daily.csv", index=False, encoding="utf-8-sig")
print(f"products_daily.csv: {len(df_products)} rows")

print("\n데이터 생성 완료!")
