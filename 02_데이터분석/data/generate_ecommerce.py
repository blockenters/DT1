"""
06_EDA 실습용 이커머스 거래 데이터 생성
실제 현업과 유사한 복합 데이터셋 (적당히 지저분하게)
"""
import pandas as pd
import numpy as np

np.random.seed(2024)

n = 2000

# 날짜: 2023-01-01 ~ 2024-12-31 (2년치)
dates = pd.date_range("2023-01-01", "2024-12-31", freq="D")
order_dates = np.sort(np.random.choice(dates, size=n))

# 고객 ID (200명 중 반복 구매)
customer_ids = [f"CUST{np.random.randint(1, 201):04d}" for _ in range(n)]

# 성별
genders = np.random.choice(["남", "여"], size=n, p=[0.45, 0.55])
# 일부 결측
for idx in np.random.choice(n, 30, replace=False):
    genders[idx] = np.nan

# 연령 (20~60)
ages = np.random.normal(loc=35, scale=10, size=n).astype(int)
ages = np.clip(ages, 18, 65)
# 일부 결측
ages = ages.astype(float)
for idx in np.random.choice(n, 25, replace=False):
    ages[idx] = np.nan

# 지역
regions = np.random.choice(
    ["서울", "경기", "인천", "부산", "대구", "대전", "광주", "세종", "제주"],
    size=n, p=[0.28, 0.22, 0.1, 0.08, 0.07, 0.06, 0.05, 0.04, 0.1]
)

# 유입채널
channels = np.random.choice(
    ["검색", "SNS", "직접방문", "이메일", "제휴"],
    size=n, p=[0.35, 0.25, 0.2, 0.12, 0.08]
)

# 상품 카테고리 + 상품명 + 단가
products = {
    "의류": {"상품": ["티셔츠", "청바지", "원피스", "패딩", "니트"], "가격범위": (15000, 120000)},
    "전자기기": {"상품": ["이어폰", "보조배터리", "충전기", "스피커", "스마트워치"], "가격범위": (10000, 350000)},
    "식품": {"상품": ["견과류", "커피세트", "건강즙", "과일선물세트", "차세트"], "가격범위": (15000, 80000)},
    "뷰티": {"상품": ["스킨케어세트", "립스틱", "선크림", "향수", "마스크팩"], "가격범위": (8000, 150000)},
    "생활용품": {"상품": ["수건세트", "텀블러", "방향제", "쿠션", "조명"], "가격범위": (10000, 60000)},
}

categories = []
product_names = []
prices = []

# 계절성 반영
for d in order_dates:
    month = pd.Timestamp(d).month
    if month in [11, 12, 1, 2]:
        cat_probs = [0.3, 0.25, 0.15, 0.15, 0.15]  # 겨울: 의류↑
    elif month in [6, 7, 8]:
        cat_probs = [0.2, 0.15, 0.2, 0.25, 0.2]    # 여름: 뷰티↑
    else:
        cat_probs = [0.2, 0.2, 0.2, 0.2, 0.2]       # 기본 균등

    cat = np.random.choice(list(products.keys()), p=cat_probs)
    prod = np.random.choice(products[cat]["상품"])
    low, high = products[cat]["가격범위"]
    price = int(np.random.uniform(low, high) // 1000 * 1000)

    categories.append(cat)
    product_names.append(prod)
    prices.append(price)

prices = np.array(prices, dtype=float)
# 일부 결측
for idx in np.random.choice(n, 15, replace=False):
    prices[idx] = np.nan

# 수량
quantities = np.random.choice([1, 1, 1, 1, 2, 2, 3], size=n)

# 할인율 (0%, 5%, 10%, 15%, 20%, 30%)
discounts = np.random.choice([0, 0, 0, 0.05, 0.1, 0.1, 0.15, 0.2, 0.3], size=n)

# 결제방법
payments = np.random.choice(
    ["신용카드", "간편결제", "계좌이체", "포인트"],
    size=n, p=[0.4, 0.35, 0.15, 0.1]
)

# 배송여부 (일부 취소/반품)
statuses = np.random.choice(
    ["배송완료", "배송완료", "배송완료", "배송완료", "배송완료",
     "배송완료", "배송완료", "배송완료", "배송중", "취소", "반품"],
    size=n
)

# 평점 (1~5) - 배송완료만
ratings = []
for s in statuses:
    if s == "배송완료":
        r = np.random.choice([3, 4, 4, 4, 5, 5, 5, np.nan], p=[0.05, 0.15, 0.15, 0.15, 0.15, 0.15, 0.1, 0.1])
        ratings.append(r)
    else:
        ratings.append(np.nan)

ecommerce = pd.DataFrame({
    "주문ID": [f"ORD{i+1:05d}" for i in range(n)],
    "주문일자": pd.Series(order_dates).dt.strftime("%Y-%m-%d"),
    "고객ID": customer_ids,
    "성별": genders,
    "연령": ages,
    "지역": regions,
    "유입채널": channels,
    "카테고리": categories,
    "상품명": product_names,
    "단가": prices,
    "수량": quantities,
    "할인율": discounts,
    "결제방법": payments,
    "주문상태": statuses,
    "평점": ratings
})

ecommerce.to_csv("02_데이터분석/data/ecommerce.csv", index=False, encoding="utf-8-sig")

print(f"ecommerce.csv 생성 완료: {len(ecommerce)}행 × {len(ecommerce.columns)}열")
print(f"\n컬럼: {ecommerce.columns.tolist()}")
print(f"\n결측치:\n{ecommerce.isna().sum()}")
print(f"\n주문상태:\n{ecommerce['주문상태'].value_counts()}")
print(f"\n기간: {ecommerce['주문일자'].min()} ~ {ecommerce['주문일자'].max()}")
