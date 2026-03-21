"""
머신러닝 실습용 데이터셋 생성 스크립트
- house_prices.csv: 아파트 매매가 예측 (회귀)
- customer_churn.csv: 고객 이탈 예측 (분류)
- customer_rfm.csv: 고객 세분화 (클러스터링)
- user_ratings.csv: 추천 시스템용 평점
- products_catalog.csv: 추천 시스템 상품 정보
"""

import numpy as np
import pandas as pd
import os
from datetime import datetime, timedelta

np.random.seed(2024)

SAVE_DIR = os.path.dirname(os.path.abspath(__file__))

# ============================================================
# 1. house_prices.csv (2000 rows) - 아파트 매매가 예측용 (회귀)
# ============================================================
n_house = 2000

지역목록 = ['강남', '서초', '마포', '송파', '영등포', '성동', '관악', '노원']
지역계수 = {'강남': 1.8, '서초': 1.6, '마포': 1.2, '송파': 1.4,
           '영등포': 1.0, '성동': 1.1, '관악': 0.8, '노원': 0.7}

면적 = np.clip(np.random.normal(75, 25, n_house), 30, 150).round(1)
층 = np.random.randint(1, 31, n_house)
건축년도 = np.random.randint(1990, 2024, n_house)
역세권 = np.random.randint(1, 31, n_house)
편의시설수 = np.random.randint(0, 16, n_house)
지역 = np.random.choice(지역목록, n_house)

# 매매가 계산: 면적*지역계수*층보정 + 역세권영향 + 건축년도보정 + 편의시설 + 노이즈
매매가 = np.zeros(n_house)
for i in range(n_house):
    base = 면적[i] * 지역계수[지역[i]] * 80  # 기본 평당가
    층보정 = 1.0 + (층[i] - 15) * 0.008  # 고층 프리미엄
    역세권영향 = max(0, (30 - 역세권[i]) * 150)  # 가까울수록 비쌈
    년도보정 = (건축년도[i] - 1990) * 50  # 신축 프리미엄
    편의시설영향 = 편의시설수[i] * 200
    노이즈 = np.random.normal(0, 2000)
    매매가[i] = base * 층보정 + 역세권영향 + 년도보정 + 편의시설영향 + 노이즈

매매가 = np.clip(매매가, 3000, 150000).astype(int)

df_house = pd.DataFrame({
    '면적(㎡)': 면적,
    '층': 층,
    '건축년도': 건축년도,
    '역세권(분)': 역세권,
    '편의시설수': 편의시설수,
    '지역': 지역,
    '매매가(만원)': 매매가
})

# 결측치 삽입 (~3%)
for col in ['면적(㎡)', '층', '역세권(분)', '편의시설수']:
    mask = np.random.random(n_house) < 0.03
    df_house.loc[mask, col] = np.nan

# 이상치 삽입 (~1%)
outlier_idx = np.random.choice(n_house, 20, replace=False)
df_house.loc[outlier_idx[:10], '면적(㎡)'] = np.random.uniform(200, 300, 10).round(1)
df_house.loc[outlier_idx[10:], '매매가(만원)'] = np.random.randint(160000, 300000, 10)

df_house.to_csv(os.path.join(SAVE_DIR, 'house_prices.csv'), index=False, encoding='utf-8-sig')

# ============================================================
# 2. customer_churn.csv (1500 rows) - 고객 이탈 예측용 (분류)
# ============================================================
n_churn = 1500

고객ID = [f'C{str(i+1).zfill(5)}' for i in range(n_churn)]
성별 = np.random.choice(['남', '여'], n_churn)
연령 = np.random.randint(20, 66, n_churn)
요금제 = np.random.choice(['베이직', '스탠다드', '프리미엄'], n_churn, p=[0.4, 0.35, 0.25])

요금제금액 = {'베이직': 9900, '스탠다드': 14900, '프리미엄': 24900}
월이용금액 = np.array([요금제금액[p] + np.random.normal(0, 2000) for p in 요금제])
월이용금액 = np.clip(월이용금액, 5000, 40000).astype(int)

가입기간 = np.random.randint(1, 61, n_churn)

# 이탈 여부 결정 (25%)
이탈확률 = np.full(n_churn, 0.15)
이탈확률[가입기간 < 6] += 0.15  # 짧은 가입기간 -> 이탈 높음
이탈확률[연령 < 25] += 0.05
이탈확률[np.array([p == '베이직' for p in 요금제])] += 0.08
이탈여부 = (np.random.random(n_churn) < 이탈확률).astype(int)

# 이탈/비이탈에 따라 행동 패턴 생성
월이용횟수 = np.zeros(n_churn, dtype=int)
최근접속일수 = np.zeros(n_churn, dtype=int)
불만접수횟수 = np.zeros(n_churn, dtype=int)
쿠폰사용횟수 = np.zeros(n_churn, dtype=int)

for i in range(n_churn):
    if 이탈여부[i] == 1:
        월이용횟수[i] = max(0, int(np.random.normal(8, 5)))
        최근접속일수[i] = max(1, int(np.random.normal(45, 20)))
        불만접수횟수[i] = max(0, int(np.random.normal(4, 2)))
        쿠폰사용횟수[i] = max(0, int(np.random.normal(3, 2)))
    else:
        월이용횟수[i] = max(0, int(np.random.normal(25, 10)))
        최근접속일수[i] = max(1, int(np.random.normal(5, 5)))
        불만접수횟수[i] = max(0, int(np.random.normal(1, 1)))
        쿠폰사용횟수[i] = max(0, int(np.random.normal(10, 5)))

월이용횟수 = np.clip(월이용횟수, 0, 50)
최근접속일수 = np.clip(최근접속일수, 1, 120)
불만접수횟수 = np.clip(불만접수횟수, 0, 10)
쿠폰사용횟수 = np.clip(쿠폰사용횟수, 0, 20)

df_churn = pd.DataFrame({
    '고객ID': 고객ID,
    '성별': 성별,
    '연령': 연령,
    '요금제': 요금제,
    '월이용금액': 월이용금액,
    '가입기간(월)': 가입기간,
    '월이용횟수': 월이용횟수,
    '최근접속일수': 최근접속일수,
    '불만접수횟수': 불만접수횟수,
    '쿠폰사용횟수': 쿠폰사용횟수,
    '이탈여부': 이탈여부
})

# 결측치 삽입 (~2%)
for col in ['연령', '월이용금액', '월이용횟수', '최근접속일수']:
    mask = np.random.random(n_churn) < 0.02
    df_churn.loc[mask, col] = np.nan

df_churn.to_csv(os.path.join(SAVE_DIR, 'customer_churn.csv'), index=False, encoding='utf-8-sig')

# ============================================================
# 3. customer_rfm.csv (800 rows) - 고객 세분화용 (클러스터링)
# ============================================================
n_rfm = 800

고객ID_rfm = [f'R{str(i+1).zfill(5)}' for i in range(n_rfm)]

# 클러스터별 할당
cluster_labels = np.random.choice(
    ['VIP', '일반', '이탈위험', '신규'],
    n_rfm,
    p=[0.15, 0.40, 0.25, 0.20]
)

최근구매일 = np.zeros(n_rfm, dtype=int)
구매횟수 = np.zeros(n_rfm, dtype=int)
총구매금액 = np.zeros(n_rfm, dtype=int)

for i in range(n_rfm):
    cl = cluster_labels[i]
    if cl == 'VIP':
        최근구매일[i] = max(1, int(np.random.normal(10, 8)))
        구매횟수[i] = max(1, int(np.random.normal(70, 15)))
        총구매금액[i] = max(10000, int(np.random.normal(3500000, 800000)))
    elif cl == '일반':
        최근구매일[i] = max(1, int(np.random.normal(90, 50)))
        구매횟수[i] = max(1, int(np.random.normal(30, 12)))
        총구매금액[i] = max(10000, int(np.random.normal(1000000, 400000)))
    elif cl == '이탈위험':
        최근구매일[i] = max(1, int(np.random.normal(280, 50)))
        구매횟수[i] = max(1, int(np.random.normal(8, 5)))
        총구매금액[i] = max(10000, int(np.random.normal(200000, 100000)))
    else:  # 신규
        최근구매일[i] = max(1, int(np.random.normal(20, 15)))
        구매횟수[i] = max(1, int(np.random.normal(5, 3)))
        총구매금액[i] = max(10000, int(np.random.normal(150000, 80000)))

최근구매일 = np.clip(최근구매일, 1, 365)
구매횟수 = np.clip(구매횟수, 1, 100)
총구매금액 = np.clip(총구매금액, 10000, 5000000)

df_rfm = pd.DataFrame({
    '고객ID': 고객ID_rfm,
    '최근구매일(일전)': 최근구매일,
    '구매횟수': 구매횟수,
    '총구매금액': 총구매금액
})

df_rfm.to_csv(os.path.join(SAVE_DIR, 'customer_rfm.csv'), index=False, encoding='utf-8-sig')

# ============================================================
# 5. products_catalog.csv (50 rows) - 추천 시스템 상품 정보
# (4번보다 먼저 생성: 4번에서 카테고리 정보 활용)
# ============================================================
카테고리목록 = ['전자기기', '의류', '식품', '뷰티', '생활용품']

상품명_pool = {
    '전자기기': ['무선 이어폰', '블루투스 스피커', '스마트워치', '보조배터리', '무선 충전기',
                '태블릿 거치대', 'USB 허브', '웹캠', '기계식 키보드', '게이밍 마우스'],
    '의류': ['캐시미어 니트', '데님 자켓', '면 티셔츠', '조거 팬츠', '패딩 조끼',
            '린넨 셔츠', '후드 집업', '치노 팬츠', '트렌치코트', '양털 플리스'],
    '식품': ['프리미엄 견과류', '유기농 꿀', '수제 그래놀라', '단백질 바', '냉동 블루베리',
            '올리브오일', '현미 크래커', '아몬드 밀크', '곡물 시리얼', '녹차 티백'],
    '뷰티': ['수분 크림', '선크림 SPF50', '클렌징 오일', '비타민C 세럼', '립밤 세트',
            '헤어 에센스', '시트 마스크팩', '아이크림', '톤업 크림', '미스트 토너'],
    '생활용품': ['텀블러', '에코백', '무드등', '방향제', '미니 가습기',
               '수건 세트', '정리함', '쿠션', '독서등', '물티슈']
}

가격범위 = {
    '전자기기': (15000, 89000),
    '의류': (19000, 129000),
    '식품': (5000, 35000),
    '뷰티': (8000, 55000),
    '생활용품': (5000, 39000)
}

상품목록 = []
item_idx = 0
for cat in 카테고리목록:
    for name in 상품명_pool[cat]:
        low, high = 가격범위[cat]
        price = int(np.random.uniform(low, high) / 100) * 100  # 100원 단위
        상품목록.append({
            '상품ID': f'ITEM{str(item_idx + 1).zfill(3)}',
            '상품명': name,
            '카테고리': cat,
            '가격': price
        })
        item_idx += 1

df_products = pd.DataFrame(상품목록)
df_products.to_csv(os.path.join(SAVE_DIR, 'products_catalog.csv'), index=False, encoding='utf-8-sig')

# ============================================================
# 4. user_ratings.csv (10000 rows) - 추천 시스템용
# ============================================================
n_ratings = 10000
n_users = 200
n_items = 50

유저목록 = [f'USER{str(i+1).zfill(3)}' for i in range(n_users)]
상품ID목록 = [f'ITEM{str(i+1).zfill(3)}' for i in range(n_items)]

# 카테고리별 상품 인덱스
cat_items = {}
for idx, row in df_products.iterrows():
    cat = row['카테고리']
    if cat not in cat_items:
        cat_items[cat] = []
    cat_items[cat].append(idx)

# 유저별 카테고리 선호도 생성
user_cat_pref = {}
for u in range(n_users):
    prefs = {}
    fav_cats = np.random.choice(카테고리목록, size=np.random.randint(1, 3), replace=False)
    for cat in 카테고리목록:
        if cat in fav_cats:
            prefs[cat] = np.random.uniform(3.5, 5.0)
        else:
            prefs[cat] = np.random.uniform(1.5, 3.5)
    user_cat_pref[u] = prefs

# 평점 생성
ratings_data = []
start_date = datetime(2024, 1, 1)
end_date = datetime(2024, 12, 31)
date_range_days = (end_date - start_date).days

for u in range(n_users):
    n_items_rated = np.random.randint(5, 51)
    rated_items = np.random.choice(n_items, n_items_rated, replace=False)
    for item_idx in rated_items:
        item_cat = df_products.iloc[item_idx]['카테고리']
        base_rating = user_cat_pref[u][item_cat]
        rating = int(np.clip(np.round(base_rating + np.random.normal(0, 0.7)), 1, 5))
        rand_day = np.random.randint(0, date_range_days + 1)
        purchase_date = start_date + timedelta(days=rand_day)
        ratings_data.append({
            '유저ID': 유저목록[u],
            '상품ID': 상품ID목록[item_idx],
            '평점': rating,
            '구매일자': purchase_date.strftime('%Y-%m-%d')
        })

# 10000개로 조정
if len(ratings_data) > n_ratings:
    ratings_data = list(np.random.choice(ratings_data, n_ratings, replace=False))
elif len(ratings_data) < n_ratings:
    # 부족분 추가 생성
    while len(ratings_data) < n_ratings:
        u = np.random.randint(0, n_users)
        item_idx = np.random.randint(0, n_items)
        item_cat = df_products.iloc[item_idx]['카테고리']
        base_rating = user_cat_pref[u][item_cat]
        rating = int(np.clip(np.round(base_rating + np.random.normal(0, 0.7)), 1, 5))
        rand_day = np.random.randint(0, date_range_days + 1)
        purchase_date = start_date + timedelta(days=rand_day)
        ratings_data.append({
            '유저ID': 유저목록[u],
            '상품ID': 상품ID목록[item_idx],
            '평점': rating,
            '구매일자': purchase_date.strftime('%Y-%m-%d')
        })

df_ratings = pd.DataFrame(ratings_data[:n_ratings])
df_ratings.to_csv(os.path.join(SAVE_DIR, 'user_ratings.csv'), index=False, encoding='utf-8-sig')

# ============================================================
# Summary
# ============================================================
print("=" * 60)
print("  머신러닝 실습 데이터셋 생성 완료")
print("=" * 60)

print(f"\n저장 경로: {SAVE_DIR}\n")

datasets = [
    ('house_prices.csv', df_house, '아파트 매매가 예측 (회귀)'),
    ('customer_churn.csv', df_churn, '고객 이탈 예측 (분류)'),
    ('customer_rfm.csv', df_rfm, '고객 세분화 (클러스터링)'),
    ('user_ratings.csv', df_ratings, '추천 시스템 평점'),
    ('products_catalog.csv', df_products, '추천 시스템 상품 정보'),
]

for fname, df, desc in datasets:
    fpath = os.path.join(SAVE_DIR, fname)
    size_kb = os.path.getsize(fpath) / 1024
    print(f"  {fname}")
    print(f"    용도: {desc}")
    print(f"    크기: {size_kb:.1f} KB | 행: {len(df)} | 열: {len(df.columns)}")
    print(f"    컬럼: {', '.join(df.columns)}")
    n_missing = df.isnull().sum().sum()
    if n_missing > 0:
        print(f"    결측치: {n_missing}개")
    print()

print("=" * 60)
