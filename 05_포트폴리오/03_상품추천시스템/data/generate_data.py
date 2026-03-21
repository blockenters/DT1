"""
상품 추천 시스템 프로젝트용 데이터 생성 스크립트
- users.csv: 500명 유저
- products.csv: 100개 상품
- purchase_history.csv: 20000건 구매 이력
"""

import numpy as np
import pandas as pd
from itertools import combinations

np.random.seed(123)

DATA_DIR = "./"

# ============================================================
# 카테고리 및 상품 정의
# ============================================================
categories = ["전자", "의류", "식품", "뷰티", "생활"]

product_names = {
    "전자": [
        "무선 블루투스 이어폰", "스마트워치 프로", "보조배터리 20000mAh",
        "USB-C 고속 충전기", "노이즈캔슬링 헤드폰", "태블릿 거치대",
        "무선 마우스", "기계식 키보드", "웹캠 HD", "USB 허브 7포트",
        "블루투스 스피커", "전자책 리더기", "드론 미니", "액션캠",
        "공기청정기 필터", "로봇청소기", "스마트 체중계",
        "무선 충전패드", "포터블 모니터", "게이밍 마우스패드"
    ],
    "의류": [
        "오버핏 맨투맨", "슬림핏 청바지", "캐시미어 머플러",
        "패딩 조끼", "린넨 셔츠", "운동용 레깅스",
        "코튼 후드집업", "와이드 슬랙스", "니트 가디건",
        "방수 바람막이", "울 코트", "데님 자켓",
        "스포츠 양말 5팩", "기능성 반팔티", "조거 팬츠",
        "트레이닝 세트", "폴로 셔츠", "면 반바지",
        "플리스 집업", "경량 패딩"
    ],
    "식품": [
        "유기농 견과류 세트", "프로틴 바 12입", "수제 그래놀라",
        "콤부차 6병", "핸드드립 원두 500g", "말차 파우더",
        "건조 과일 믹스", "올리브유 1L", "꿀 500g",
        "현미 5kg", "냉동 블루베리 1kg", "아몬드 밀크",
        "단백질 쉐이크", "비타민 젤리", "오트밀 1kg",
        "녹차 티백 100입", "참치캔 12개입", "즉석밥 12입",
        "김 선물세트", "전통 된장 1kg"
    ],
    "뷰티": [
        "수분 크림 50ml", "선크림 SPF50", "클렌징 오일",
        "토너 패드 60매", "세럼 30ml", "립밤 세트",
        "시트 마스크 10매", "핸드크림 세트", "바디로션 500ml",
        "향수 50ml", "아이크림 25ml", "BB크림",
        "폼클렌저", "미스트 스프레이", "각질제거 젤",
        "헤어 에센스", "두피 샴푸", "네일 케어 세트",
        "컬러 립스틱", "메이크업 브러쉬 세트"
    ],
    "생활": [
        "스테인리스 텀블러", "접이식 우산", "아로마 디퓨저",
        "극세사 수건 세트", "무드등 조명", "다이어리 플래너",
        "에코백", "미니 가습기", "수납 바구니 3종",
        "멀티 공구 세트", "방향제 세트", "실리콘 주방매트",
        "음식물 밀폐용기 5종", "칫솔 세트", "빨래 건조대",
        "LED 스탠드", "벽걸이 시계", "쿠션 커버 2종",
        "식탁 매트 4종", "욕실 정리함"
    ],
}

# ============================================================
# 1. products.csv 생성
# ============================================================
products = []
pid = 1
for cat in categories:
    for name in product_names[cat]:
        products.append({
            "상품ID": f"P{pid:03d}",
            "상품명": name,
            "카테고리": cat,
            "가격": 0,
            "평균평점": 0.0,
        })
        pid += 1

df_products = pd.DataFrame(products)

# 카테고리별 가격 범위
price_ranges = {
    "전자": (15000, 350000),
    "의류": (12000, 180000),
    "식품": (5000, 50000),
    "뷰티": (8000, 80000),
    "생활": (5000, 60000),
}

for idx, row in df_products.iterrows():
    lo, hi = price_ranges[row["카테고리"]]
    price = int(np.round(np.random.uniform(lo, hi), -2))  # 100원 단위
    df_products.at[idx, "가격"] = price

df_products["평균평점"] = np.round(np.random.uniform(3.0, 5.0, len(df_products)), 1)

# ============================================================
# 2. users.csv 생성
# ============================================================
genders = ["남", "여"]

# 유저 그룹 정의 (협업 필터링이 잘 작동하도록)
# 각 그룹은 특정 카테고리 조합을 선호
user_groups = [
    (["전자"], 0.15),            # 전자 단독
    (["의류"], 0.10),            # 의류 단독
    (["식품"], 0.10),            # 식품 단독
    (["뷰티"], 0.10),            # 뷰티 단독
    (["생활"], 0.10),            # 생활 단독
    (["전자", "생활"], 0.10),    # 전자+생활
    (["의류", "뷰티"], 0.10),    # 의류+뷰티
    (["식품", "생활"], 0.10),    # 식품+생활
    (["전자", "의류"], 0.05),    # 전자+의류
    (["뷰티", "생활"], 0.05),    # 뷰티+생활
    (["식품", "뷰티"], 0.05),    # 식품+뷰티
]

group_prefs = [g[0] for g in user_groups]
group_probs = [g[1] for g in user_groups]

users = []
user_group_map = {}  # 유저별 그룹 인덱스

for i in range(1, 501):
    uid = f"U{i:04d}"
    gender = np.random.choice(genders)
    age = np.random.randint(18, 61)
    join_date = pd.Timestamp("2023-01-01") + pd.Timedelta(days=int(np.random.randint(0, 365)))

    # 그룹 배정
    gidx = np.random.choice(len(group_prefs), p=group_probs)
    pref_cats = group_prefs[gidx]
    user_group_map[uid] = gidx

    users.append({
        "유저ID": uid,
        "성별": gender,
        "연령": age,
        "가입일": join_date.strftime("%Y-%m-%d"),
        "선호카테고리": ",".join(pref_cats),
    })

df_users = pd.DataFrame(users)

# ============================================================
# 3. purchase_history.csv 생성
# ============================================================
# 상품 ID를 카테고리별로 분류
cat_to_pids = {}
for _, row in df_products.iterrows():
    cat = row["카테고리"]
    if cat not in cat_to_pids:
        cat_to_pids[cat] = []
    cat_to_pids[cat].append(row["상품ID"])

all_pids = df_products["상품ID"].tolist()
product_price_map = dict(zip(df_products["상품ID"], df_products["가격"]))

purchases = []
purchase_id = 1

# 유저별 구매수 할당 (총합 약 20000)
n_users = 500
target_total = 20000
mean_purchases = target_total / n_users  # 40

# 유저별 구매 수: 5~80, 평균 40
user_purchase_counts = np.clip(
    np.random.normal(mean_purchases, 12, n_users).astype(int),
    5, 80
)

# 총합 조정
diff = target_total - user_purchase_counts.sum()
if diff > 0:
    for _ in range(diff):
        idx = np.random.randint(0, n_users)
        if user_purchase_counts[idx] < 80:
            user_purchase_counts[idx] += 1
elif diff < 0:
    for _ in range(-diff):
        idx = np.random.randint(0, n_users)
        if user_purchase_counts[idx] > 5:
            user_purchase_counts[idx] -= 1

for i, (_, user_row) in enumerate(df_users.iterrows()):
    uid = user_row["유저ID"]
    pref_cats = user_row["선호카테고리"].split(",")
    n_purchases = user_purchase_counts[i]

    # 선호 카테고리 상품 목록
    pref_pids = []
    for cat in pref_cats:
        pref_pids.extend(cat_to_pids[cat])

    # 비선호 카테고리 상품 목록
    other_pids = [p for p in all_pids if p not in pref_pids]

    for _ in range(n_purchases):
        # 70% 확률로 선호 카테고리에서, 30% 비선호
        if np.random.random() < 0.70:
            pid = np.random.choice(pref_pids)
        else:
            pid = np.random.choice(other_pids)

        # 구매일: 2024-01-01 ~ 2024-12-31
        buy_date = pd.Timestamp("2024-01-01") + pd.Timedelta(
            days=int(np.random.randint(0, 366))
        )

        # 평점: 선호 카테고리 상품일수록 높은 평점 경향
        if pid in pref_pids:
            rating = np.random.choice([3, 4, 4, 5, 5], p=[0.1, 0.25, 0.25, 0.2, 0.2])
        else:
            rating = np.random.choice([1, 2, 3, 4, 5], p=[0.05, 0.15, 0.35, 0.30, 0.15])

        # 15% 확률로 평점 NaN
        if np.random.random() < 0.15:
            rating = np.nan

        price = product_price_map[pid]
        # 구매금액: 가격에 약간 변동 (할인/추가구매)
        amount = int(np.round(price * np.random.uniform(0.85, 1.15), -2))

        purchases.append({
            "구매ID": f"PU{purchase_id:06d}",
            "유저ID": uid,
            "상품ID": pid,
            "구매일": buy_date.strftime("%Y-%m-%d"),
            "평점": rating,
            "구매금액": amount,
        })
        purchase_id += 1

df_purchases = pd.DataFrame(purchases)

# ============================================================
# 저장
# ============================================================
df_users.to_csv(f"{DATA_DIR}users.csv", index=False, encoding="utf-8-sig")
df_products.to_csv(f"{DATA_DIR}products.csv", index=False, encoding="utf-8-sig")
df_purchases.to_csv(f"{DATA_DIR}purchase_history.csv", index=False, encoding="utf-8-sig")

print(f"users.csv: {len(df_users)}행")
print(f"products.csv: {len(df_products)}행")
print(f"purchase_history.csv: {len(df_purchases)}행")
print("데이터 생성 완료!")
