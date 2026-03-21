"""
04_데이터_전처리 실습용 지저분한 CSV 데이터 생성 스크립트
실제 현업에서 흔히 마주치는 문제들을 의도적으로 포함:
- 결측치 (NaN, 빈 문자열, 다양한 패턴)
- 중복 데이터
- 타입 오류 (숫자가 문자열로 저장)
- 이상치 (비현실적 값)
- 공백/대소문자 불일치
- 날짜 형식 불일치
"""
import pandas as pd
import numpy as np

np.random.seed(42)

# ============================================================
# 1. 지저분한 고객 데이터 (dirty_customers.csv)
# ============================================================
n = 80

names = [
    "김민수", "이영희", "박철수", "최지은", "정현우", "강서연", "윤태호", "한미경",
    "오준석", "신예진", "장동건", "송혜교", "류현진", "김태희", "이승기",
    "배수지", "조인성", "한가인", "공유", "전지현", "이민호", "박보검",
    "김소현", "서강준", "남주혁", "이종석", "박서준", "김유정", "도경수", "차은우",
    "안효섭", "김세정", "황민현", "이도현", "노윤서", "고민시", "문가영", "송강",
    "김혜윤", "조보아", "이재욱", "한소희", "차주영", "고윤정", "김지원", "변우석",
    "류수영", "엄정화", "신민아", "원빈", "장원영", "카리나", "윈터", "지수",
    "제니", "로제", "리사", "아이유", "수지", "설현", "유인나", "박민영",
    "김고은", "한효주", "손예진", "공승연", "김다미", "전소니", "문소리", "이정은",
    "배두나", "전도연", "김선영", "이유미", "정호연", "김태리", "한지민", "임수정",
    "김향기", "박은빈"
]

# 이메일 - 일부는 빈값, 일부는 잘못된 형식
emails = []
for i in range(n):
    r = np.random.random()
    if r < 0.1:
        emails.append("")  # 빈 문자열
    elif r < 0.15:
        emails.append(np.nan)  # NaN
    elif r < 0.2:
        emails.append("없음")  # 잘못된 값
    else:
        emails.append(f"user{i+1}@{'gmail.com' if np.random.random() > 0.5 else 'naver.com'}")

# 연령 - 일부 이상치, 일부 결측
ages = np.random.randint(18, 65, size=n).astype(float)
ages[np.random.choice(n, 5, replace=False)] = np.nan  # 5개 결측
ages[12] = 150  # 이상치: 150세
ages[35] = -5   # 이상치: 음수
ages[50] = 0    # 이상치: 0세

# 성별 - 표기 불일치
genders = []
gender_options = ["남", "여", "남자", "여자", "M", "F", "male", "female", " 남 ", "여 "]
for _ in range(n):
    genders.append(np.random.choice(gender_options, p=[0.25, 0.25, 0.1, 0.1, 0.05, 0.05, 0.03, 0.03, 0.07, 0.07]))
# 일부 결측
for idx in np.random.choice(n, 3, replace=False):
    genders[idx] = np.nan

# 전화번호 - 형식 불일치
phones = []
for i in range(n):
    mid = np.random.randint(1000, 9999)
    last = np.random.randint(1000, 9999)
    r = np.random.random()
    if r < 0.2:
        phones.append(f"010-{mid}-{last}")
    elif r < 0.4:
        phones.append(f"010{mid}{last}")
    elif r < 0.6:
        phones.append(f"010.{mid}.{last}")
    elif r < 0.7:
        phones.append(f"010 {mid} {last}")
    elif r < 0.8:
        phones.append("")
    else:
        phones.append(f"010-{mid}-{last}")
# 몇 개는 NaN
for idx in np.random.choice(n, 4, replace=False):
    phones[idx] = np.nan

# 가입일 - 형식 불일치
join_dates = []
base_dates = pd.date_range("2021-01-01", periods=n, freq="7D")
for d in base_dates:
    r = np.random.random()
    if r < 0.3:
        join_dates.append(d.strftime("%Y-%m-%d"))       # 2021-01-01
    elif r < 0.5:
        join_dates.append(d.strftime("%Y/%m/%d"))       # 2021/01/01
    elif r < 0.7:
        join_dates.append(d.strftime("%d-%m-%Y"))       # 01-01-2021
    elif r < 0.85:
        join_dates.append(d.strftime("%Y.%m.%d"))       # 2021.01.01
    else:
        join_dates.append(d.strftime("%Y년 %m월 %d일"))  # 2021년 01월 01일
# 결측
for idx in np.random.choice(n, 3, replace=False):
    join_dates[idx] = np.nan

# 지역 - 공백, 오타
regions = np.random.choice(
    ["서울", "경기", "인천", "부산", "대구", "대전", "광주",
     "서울 ", " 경기", "서울시", "부산광역시", "seould"],
    size=n,
    p=[0.2, 0.15, 0.1, 0.08, 0.08, 0.08, 0.07,
       0.05, 0.05, 0.05, 0.04, 0.05]
)
# 결측
region_list = list(regions)
for idx in np.random.choice(n, 4, replace=False):
    region_list[idx] = np.nan

# 월소비금액 - 일부 문자열로 저장 (콤마 포함), 이상치
spend = np.random.normal(loc=200000, scale=100000, size=n).astype(int)
spend = np.clip(spend, 10000, 800000)
spend_str = []
for i, s in enumerate(spend):
    r = np.random.random()
    if r < 0.15:
        spend_str.append(f"{s:,}")  # "200,000" 콤마 포함 문자열
    elif r < 0.2:
        spend_str.append(f"{s}원")  # "200000원"
    elif r < 0.25:
        spend_str.append("")  # 빈값
    else:
        spend_str.append(str(s))
# 이상치
spend_str[20] = "99999999"  # 비현실적 고액
spend_str[45] = "-50000"    # 음수

# 중복 행 추가 (5건)
customers_data = {
    "고객ID": [f"C{str(i).zfill(3)}" for i in range(1, n+1)],
    "고객명": names[:n],
    "성별": genders,
    "연령": ages,
    "이메일": emails,
    "전화번호": phones,
    "가입일": join_dates,
    "지역": region_list,
    "월소비금액": spend_str
}
df_cust = pd.DataFrame(customers_data)

# 중복 행 5개 추가 (완전 동일 행)
dup_indices = np.random.choice(n, 5, replace=False)
df_dup = df_cust.iloc[dup_indices].copy()
df_cust = pd.concat([df_cust, df_dup], ignore_index=True)

# 부분 중복 (같은 고객ID인데 다른 정보)
partial_dup = df_cust.iloc[3:4].copy()
partial_dup["이메일"] = "changed@email.com"
df_cust = pd.concat([df_cust, partial_dup], ignore_index=True)

df_cust.to_csv("02_데이터분석/data/dirty_customers.csv", index=False, encoding="utf-8-sig")
print(f"dirty_customers.csv 생성 완료: {len(df_cust)}행")
print(f"  - 결측치 포함 컬럼: 연령, 성별, 이메일, 전화번호, 가입일, 지역")
print(f"  - 이상치: 연령(150, -5, 0), 월소비금액(99999999, -50000)")
print(f"  - 중복: 완전중복 5건, 부분중복 1건")
print(f"  - 타입문제: 월소비금액(콤마, '원' 포함), 가입일(형식 불일치)")
print(f"  - 값불일치: 성별(남/여/남자/여자/M/F/공백), 지역(공백/오타)")


# ============================================================
# 2. 지저분한 주문 데이터 (dirty_orders.csv)
# ============================================================
n_orders = 300

order_dates = pd.date_range("2024-01-01", "2024-06-30", freq="D")
selected_dates = np.random.choice(order_dates, size=n_orders)
selected_dates = np.sort(selected_dates)

product_names = ["노트북", "무선마우스", "기계식키보드", "27인치모니터", "USB허브",
                 "웹캠", "블루투스스피커", "외장SSD", "노트북거치대", "마우스패드"]
product_prices = [1350000, 35000, 89000, 450000, 25000,
                  65000, 120000, 95000, 45000, 15000]

product_idx = np.random.choice(len(product_names), size=n_orders)
quantities = np.random.choice([1, 1, 1, 2, 2, 3, 5], size=n_orders)

# 단가에 일부 오류 넣기
prices = []
for idx in product_idx:
    p = product_prices[idx]
    r = np.random.random()
    if r < 0.05:
        prices.append(0)         # 0원 (오류)
    elif r < 0.08:
        prices.append(-p)        # 음수 (환불 데이터 섞임)
    elif r < 0.12:
        prices.append(np.nan)    # 결측
    else:
        prices.append(p)

# 고객ID - 일부 존재하지 않는 ID
customer_ids = [f"C{str(np.random.randint(1, 81)).zfill(3)}" for _ in range(n_orders)]
for idx in np.random.choice(n_orders, 8, replace=False):
    customer_ids[idx] = f"C{str(np.random.randint(100, 200)).zfill(3)}"  # 없는 고객
for idx in np.random.choice(n_orders, 3, replace=False):
    customer_ids[idx] = np.nan  # 결측

orders_data = {
    "주문번호": [f"ORD{str(i).zfill(5)}" for i in range(1, n_orders + 1)],
    "주문일자": pd.Series(selected_dates).dt.strftime("%Y-%m-%d"),
    "고객ID": customer_ids,
    "상품명": [product_names[i] for i in product_idx],
    "수량": quantities,
    "단가": prices
}
df_orders = pd.DataFrame(orders_data)

# 수량에 일부 이상치
df_orders.loc[50, "수량"] = 999      # 비현실적 수량
df_orders.loc[120, "수량"] = 0       # 0개
df_orders.loc[200, "수량"] = -1      # 음수

# 결측치 추가
for col in ["수량"]:
    null_idx = np.random.choice(n_orders, 4, replace=False)
    df_orders.loc[null_idx, col] = np.nan

# 완전 중복 행 3건
dup_orders = df_orders.iloc[np.random.choice(n_orders, 3, replace=False)].copy()
df_orders = pd.concat([df_orders, dup_orders], ignore_index=True)

df_orders.to_csv("02_데이터분석/data/dirty_orders.csv", index=False, encoding="utf-8-sig")
print(f"\ndirty_orders.csv 생성 완료: {len(df_orders)}행")
print(f"  - 결측치: 고객ID, 단가, 수량")
print(f"  - 이상치: 단가(0, 음수), 수량(999, 0, -1)")
print(f"  - 존재하지 않는 고객ID 8건")
print(f"  - 완전중복 3건")


print("\n=== 전처리 실습 데이터 생성 완료 ===")
print("dirty_customers.csv: 고객 데이터 (결측치, 이상치, 중복, 타입문제, 값불일치)")
print("dirty_orders.csv: 주문 데이터 (결측치, 이상치, 중복, 무효 참조)")
