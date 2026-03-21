import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import os

np.random.seed(2024)

SAVE_DIR = os.path.dirname(os.path.abspath(__file__))

# ============================================================
# 1. stores.csv (100 stores)
# ============================================================

store_name_pool = {
    "치킨": ["황금올리브치킨", "네네치킨", "교촌치킨", "BHC치킨", "굽네치킨", "호식이두마리치킨",
             "페리카나치킨", "처갓집양념치킨", "노랑통닭", "맘스터치치킨", "바른치킨", "또래오래치킨"],
    "피자": ["도미노피자", "피자헛", "파파존스", "미스터피자", "피자마루", "7번가피자",
            "피자알볼로", "고피자", "반올림피자", "오구피자"],
    "중식": ["홍콩반점", "짬뽕지존", "만리장성", "북경", "용문각", "취향저격중화요리",
            "미스터차이나", "동보성", "진짜루", "중화명가"],
    "한식": ["한솥도시락", "본죽", "김밥천국", "백반의민족", "시골밥상", "엄마손맛집",
            "정든집", "고향집", "미소가든", "한일관", "도담도담", "가마솥설렁탕"],
    "분식": ["엽기떡볶이", "신전떡볶이", "죠스떡볶이", "동대문엽기떡볶이", "국대떡볶이",
            "청년다방", "봉구스밥버거", "김가네", "오봉집", "스쿨푸드"],
    "일식": ["스시로", "하남돼지집", "규카츠", "돈카츠전문점", "미소야라멘",
            "이치란라멘", "삼첩분식", "온센", "사무라이돈부리", "하코야"],
    "카페/디저트": ["스타벅스", "투썸플레이스", "이디야커피", "메가커피", "컴포즈커피",
                 "빽다방", "설빙", "배스킨라빈스", "파리바게뜨", "뚜레쥬르"],
    "야식": ["자담치킨", "신포차", "포장마차", "야식의민족", "호프집",
            "야식천국", "불야성", "한잔의추억", "달빛포차", "야식공작소"],
    "패스트푸드": ["맥도날드", "버거킹", "롯데리아", "KFC", "서브웨이",
               "쉐이크쉑", "맘스터치", "노브랜드버거", "이삭토스트", "에그드랍"],
    "샐러드": ["샐러디", "프레시코드", "서브웨이샐러드", "피그인더가든", "그리너리",
             "샐러드판다", "닥터로빈", "포케올데이", "위샐러드", "그린랩"]
}

업종_list = list(store_name_pool.keys())
지역_list = ["강남구", "서초구", "마포구", "송파구", "영등포구", "종로구", "성동구", "관악구"]

stores = []
for i in range(100):
    sid = f"STR{i+1:03d}"
    업종 = np.random.choice(업종_list)
    가게명 = np.random.choice(store_name_pool[업종]) + f" {np.random.choice(['본점','역삼점','강남점','신촌점','홍대점','잠실점','선릉점','사당점'])}"
    지역 = np.random.choice(지역_list)

    # Dirty: trailing spaces, abbreviated name
    if i in [3, 15, 27, 45, 60]:
        지역 = 지역 + "  "  # trailing spaces
    if i in [8, 22, 50, 78]:
        지역 = 지역.replace("구", "")  # e.g., "강남" instead of "강남구"

    avg_delivery = np.random.randint(20, 51)
    rating = round(np.random.uniform(3.0, 5.0), 1)

    # Some NaN ratings
    if i in [5, 18, 33, 67, 89]:
        rating = np.nan

    stores.append([sid, 가게명, 업종, 지역, avg_delivery, rating])

df_stores = pd.DataFrame(stores, columns=["가게ID", "가게명", "업종", "지역", "평균배달시간(분)", "가게평점"])
df_stores.to_csv(os.path.join(SAVE_DIR, "stores.csv"), index=False, encoding="utf-8-sig")

# ============================================================
# 2. customers.csv (500 customers)
# ============================================================

customers = []
for i in range(500):
    cid = f"CUST{i+1:04d}"

    # Gender with dirty values
    gender_roll = np.random.random()
    if gender_roll < 0.45:
        gender = "남"
    elif gender_roll < 0.90:
        gender = "여"
    elif gender_roll < 0.93:
        gender = "남자"
    elif gender_roll < 0.96:
        gender = "M"
    else:
        gender = np.nan

    # Age with issues
    age = int(np.random.randint(18, 61))
    if i == 77:
        age = 0
    elif i == 233:
        age = 150
    if i in [10, 55, 130, 299, 410]:
        age = np.nan

    지역 = np.random.choice(지역_list)

    # Mixed date formats
    start_date = datetime(2022, 1, 1)
    end_date = datetime(2024, 6, 30)
    days_range = (end_date - start_date).days
    join_date = start_date + timedelta(days=int(np.random.randint(0, days_range + 1)))

    fmt_roll = np.random.random()
    if fmt_roll < 0.7:
        join_str = join_date.strftime("%Y-%m-%d")
    elif fmt_roll < 0.95:
        join_str = join_date.strftime("%Y/%m/%d")
    else:
        join_str = np.nan

    등급 = np.random.choice(["일반", "실버", "골드", "VIP"], p=[0.5, 0.25, 0.15, 0.1])

    customers.append([cid, gender, age, 지역, join_str, 등급])

df_customers = pd.DataFrame(customers, columns=["고객ID", "성별", "연령", "지역", "가입일", "등급"])
df_customers.to_csv(os.path.join(SAVE_DIR, "customers.csv"), index=False, encoding="utf-8-sig")

# ============================================================
# 3. orders.csv (5000 orders)
# ============================================================

menu_pool = {
    "치킨": ["후라이드치킨", "양념치킨", "간장치킨", "마늘치킨", "반반치킨", "순살치킨", "치킨텐더"],
    "피자": ["페퍼로니피자", "콤비네이션피자", "불고기피자", "하와이안피자", "고구마피자", "치즈피자"],
    "중식": ["짜장면", "짬뽕", "탕수육", "볶음밥", "마파두부", "깐풍기"],
    "한식": ["된장찌개", "김치찌개", "불고기", "비빔밥", "제육볶음", "갈비탕", "설렁탕"],
    "분식": ["떡볶이", "순대", "튀김", "김밥", "라볶이", "오뎅"],
    "일식": ["초밥세트", "돈카츠", "라멘", "우동", "규동", "오꼬노미야끼"],
    "카페/디저트": ["아메리카노", "카페라떼", "케이크", "빙수", "크로플", "마카롱세트"],
    "야식": ["닭발", "곱창", "족발", "보쌈", "오돌뼈", "닭볶음탕"],
    "패스트푸드": ["빅맥세트", "와퍼세트", "치킨버거", "감자튀김", "너겟세트", "불고기버거"],
    "샐러드": ["닭가슴살샐러드", "연어샐러드", "포케보울", "시저샐러드", "그릭샐러드", "퀴노아샐러드"]
}

price_range = {
    "치킨": (18000, 25000),
    "피자": (15000, 35000),
    "중식": (6000, 18000),
    "한식": (7000, 15000),
    "분식": (3000, 12000),
    "일식": (8000, 25000),
    "카페/디저트": (3000, 15000),
    "야식": (15000, 35000),
    "패스트푸드": (5000, 12000),
    "샐러드": (8000, 16000)
}

# Build store lookup
store_업종 = dict(zip(df_stores["가게ID"], df_stores["업종"]))
valid_store_ids = df_stores["가게ID"].tolist()
valid_customer_ids = df_customers["고객ID"].tolist()

def generate_order_datetime():
    """Generate realistic order datetime with time patterns."""
    date = datetime(2024, 1, 1) + timedelta(days=int(np.random.randint(0, 366)))

    # Time distribution: lunch peak, dinner peak, late night
    roll = np.random.random()
    if roll < 0.30:  # lunch 11-13
        hour = np.random.randint(11, 14)
    elif roll < 0.70:  # dinner 17-20
        hour = np.random.randint(17, 21)
    elif roll < 0.90:  # late night 21-24
        hour = np.random.randint(21, 24)
    else:  # other times
        hour = np.random.choice([9, 10, 14, 15, 16])

    minute = np.random.randint(0, 60)
    second = np.random.randint(0, 60)
    return date.replace(hour=hour, minute=minute, second=second)

orders = []
for i in range(4995):  # 4995 + 5 duplicates = 5000
    oid = f"ORD{i+1:05d}"
    order_dt = generate_order_datetime()
    order_dt_str = order_dt.strftime("%Y-%m-%d %H:%M:%S")

    # Customer ID: mostly valid, some NaN, some invalid
    if i in [100, 500, 1200, 2500, 3800]:
        cid = np.nan
    elif i in [200, 700, 1500, 2800, 3300, 4100, 4500]:
        cid = f"CUST9{np.random.randint(100,999)}"
    else:
        cid = np.random.choice(valid_customer_ids)

    sid = np.random.choice(valid_store_ids)
    업종 = store_업종[sid]
    menu = np.random.choice(menu_pool[업종])

    # Price with dirty values
    lo, hi = price_range[업종]
    price = int(np.round(np.random.randint(lo, hi + 1), -2))

    if i in [50, 300, 888, 1234, 2000, 3456]:
        price_val = f"{price:,}"  # string with commas
    elif i in [150, 600, 999, 2222]:
        price_val = f"{price}원"
    elif i in [400, 1800, 3000]:
        price_val = np.nan
    elif i in [250, 2600]:
        price_val = -abs(price)  # negative
    else:
        price_val = price

    # Quantity
    qty_roll = np.random.random()
    if qty_roll < 0.75:
        qty = 1
    elif qty_roll < 0.92:
        qty = 2
    elif qty_roll < 0.98:
        qty = 3
    else:
        qty = np.random.choice([0, 99])

    # Delivery time
    delivery_time = int(np.random.randint(15, 61))
    if i in [80, 500, 1600, 2900]:
        delivery_time = np.nan
    elif i in [120, 2100]:
        delivery_time = 0
    elif i in [350, 3700]:
        delivery_time = 180

    payment = np.random.choice(["카드", "간편결제", "현금"], p=[0.5, 0.4, 0.1])
    coupon = np.random.choice(["Y", "N"], p=[0.3, 0.7])

    # Order status
    status_roll = np.random.random()
    if status_roll < 0.85:
        status = "배달완료"
    elif status_roll < 0.95:
        status = "취소"
    else:
        status = "배달중"

    # Rating only for completed orders, and not all of them
    if status == "배달완료" and np.random.random() < 0.7:
        rating = int(np.random.choice([1, 2, 3, 4, 5], p=[0.05, 0.08, 0.17, 0.35, 0.35]))
    else:
        rating = np.nan

    orders.append([oid, order_dt_str, cid, sid, menu, price_val, qty, delivery_time, payment, coupon, rating, status])

# Add 5 duplicate rows
dup_indices = np.random.choice(len(orders), 5, replace=False)
for idx in dup_indices:
    orders.append(orders[idx].copy())

df_orders = pd.DataFrame(orders, columns=[
    "주문ID", "주문일시", "고객ID", "가게ID", "메뉴", "주문금액", "수량",
    "배달소요시간(분)", "결제방법", "쿠폰사용여부", "평점", "주문상태"
])
df_orders.to_csv(os.path.join(SAVE_DIR, "orders.csv"), index=False, encoding="utf-8-sig")

# ============================================================
# 4. weather.csv (366 days of 2024 - leap year)
# ============================================================

# Seoul monthly average temperatures (approx)
monthly_temp = {
    1: (-5, 3), 2: (-3, 5), 3: (2, 12), 4: (8, 18),
    5: (13, 24), 6: (18, 28), 7: (22, 32), 8: (23, 33),
    9: (17, 27), 10: (9, 20), 11: (2, 12), 12: (-4, 4)
}

weather_data = []
date = datetime(2024, 1, 1)
end = datetime(2024, 12, 31)

while date <= end:
    month = date.month
    lo, hi = monthly_temp[month]
    temp = round(np.random.uniform(lo, hi), 1)

    # Precipitation: seasonal
    if month in [6, 7, 8]:  # summer rainy season
        rain_prob = 0.35
        rain_amount = np.random.exponential(20) if np.random.random() < rain_prob else 0
    elif month in [12, 1, 2]:  # winter
        rain_prob = 0.15
        rain_amount = np.random.exponential(5) if np.random.random() < rain_prob else 0
    else:
        rain_prob = 0.2
        rain_amount = np.random.exponential(10) if np.random.random() < rain_prob else 0

    rain_amount = round(rain_amount, 1)

    if rain_amount > 0:
        if month in [12, 1, 2] and temp < 2:
            weather = "눈"
        else:
            weather = "비"
    else:
        weather = np.random.choice(["맑음", "흐림"], p=[0.65, 0.35])

    weather_data.append([date.strftime("%Y-%m-%d"), temp, rain_amount, weather])
    date += timedelta(days=1)

df_weather = pd.DataFrame(weather_data, columns=["날짜", "기온", "강수량(mm)", "날씨"])
df_weather.to_csv(os.path.join(SAVE_DIR, "weather.csv"), index=False, encoding="utf-8-sig")

# ============================================================
# Summary
# ============================================================

print("=" * 60)
print("데이터 생성 완료!")
print("=" * 60)

print(f"\n[1] stores.csv ({len(df_stores)}개 가게)")
print(df_stores.head())
print(f"  - 결측치:\n{df_stores.isnull().sum().to_string()}")

print(f"\n[2] customers.csv ({len(df_customers)}명 고객)")
print(df_customers.head())
print(f"  - 결측치:\n{df_customers.isnull().sum().to_string()}")

print(f"\n[3] orders.csv ({len(df_orders)}건 주문)")
print(df_orders.head())
print(f"  - 결측치:\n{df_orders.isnull().sum().to_string()}")
print(f"  - 주문상태 분포:\n{df_orders['주문상태'].value_counts().to_string()}")

print(f"\n[4] weather.csv ({len(df_weather)}일 날씨)")
print(df_weather.head())
print(f"  - 날씨 분포:\n{df_weather['날씨'].value_counts().to_string()}")

print(f"\n저장 경로: {SAVE_DIR}")
print("=" * 60)
