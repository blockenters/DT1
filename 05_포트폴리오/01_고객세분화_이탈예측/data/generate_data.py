"""
고객 세분화 & 이탈 예측 프로젝트 - 데이터 생성 스크립트
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta

np.random.seed(2024)

DATA_DIR = "./"

# ============================================================
# 1. customers.csv (2000명)
# ============================================================

n_customers = 2000
customer_ids = [f"C{str(i).zfill(5)}" for i in range(1, n_customers + 1)]

# 성별 (일부 dirty)
clean_genders = np.random.choice(["남", "여"], size=n_customers, p=[0.52, 0.48])
dirty_indices = np.random.choice(n_customers, size=40, replace=False)
dirty_values = np.random.choice(["남자", "여자", "M", "F", "male", "female"], size=40)
genders = clean_genders.copy()
for idx, val in zip(dirty_indices, dirty_values):
    genders[idx] = val

# 연령 (20~65, 일부 NaN)
ages = np.random.randint(20, 66, size=n_customers).astype(float)
nan_age_idx = np.random.choice(n_customers, size=60, replace=False)
ages[nan_age_idx] = np.nan

# 지역 (8개)
regions = np.random.choice(
    ["서울", "경기", "인천", "부산", "대구", "대전", "광주", "제주"],
    size=n_customers,
    p=[0.28, 0.22, 0.10, 0.10, 0.08, 0.08, 0.07, 0.07]
)

# 가입일 (2020-01 ~ 2024-06, mixed formats)
start_date = datetime(2020, 1, 1)
end_date = datetime(2024, 6, 30)
days_range = (end_date - start_date).days
join_dates_raw = [start_date + timedelta(days=np.random.randint(0, days_range)) for _ in range(n_customers)]

join_dates = []
for i, d in enumerate(join_dates_raw):
    r = np.random.random()
    if r < 0.6:
        join_dates.append(d.strftime("%Y-%m-%d"))
    elif r < 0.8:
        join_dates.append(d.strftime("%Y/%m/%d"))
    elif r < 0.9:
        join_dates.append(d.strftime("%d-%m-%Y"))
    else:
        join_dates.append(d.strftime("%Y.%m.%d"))

# 요금제
plans = np.random.choice(
    ["베이직", "스탠다드", "프리미엄"],
    size=n_customers,
    p=[0.45, 0.35, 0.20]
)

# 이탈여부 (28% churn)
churn = np.random.choice([0, 1], size=n_customers, p=[0.72, 0.28])

# 월평균결제액 (이탈 고객은 낮은 경향, 일부 콤마 포함)
monthly_pay = []
for i in range(n_customers):
    if plans[i] == "베이직":
        base = np.random.normal(15000, 5000)
    elif plans[i] == "스탠다드":
        base = np.random.normal(30000, 8000)
    else:
        base = np.random.normal(50000, 12000)
    if churn[i] == 1:
        base *= np.random.uniform(0.5, 0.9)
    base = max(5000, base)
    monthly_pay.append(base)

# 일부에 콤마 형식 적용
monthly_pay_str = []
for i, val in enumerate(monthly_pay):
    val_int = int(round(val))
    if np.random.random() < 0.15:
        monthly_pay_str.append(f"{val_int:,}")
    else:
        monthly_pay_str.append(str(val_int))

# 가입경로
channels = np.random.choice(
    ["검색", "SNS", "지인추천", "앱스토어"],
    size=n_customers,
    p=[0.35, 0.25, 0.20, 0.20]
)

customers_df = pd.DataFrame({
    "고객ID": customer_ids,
    "성별": genders,
    "연령": ages,
    "지역": regions,
    "가입일": join_dates,
    "요금제": plans,
    "이탈여부": churn,
    "월평균결제액": monthly_pay_str,
    "가입경로": channels
})

customers_df.to_csv(f"{DATA_DIR}customers.csv", index=False, encoding="utf-8-sig")
print(f"customers.csv: {len(customers_df)} rows saved")

# ============================================================
# 2. transactions.csv (15000 rows)
# ============================================================

n_transactions = 15000
churned_ids = [cid for cid, c in zip(customer_ids, churn) if c == 1]
active_ids = [cid for cid, c in zip(customer_ids, churn) if c == 0]

tx_start = datetime(2023, 1, 1)
tx_end = datetime(2024, 6, 30)
tx_days = (tx_end - tx_start).days

# 이탈 고객: 최근 거래 적음 -> 날짜 분포를 앞쪽으로 편향
tx_customer_ids = []
tx_dates = []
tx_amounts = []
tx_categories = []
tx_methods = []

categories = ["식품", "의류", "전자", "뷰티", "생활"]
methods = ["카드", "간편결제", "현금"]

# 활성 고객 거래 (~70%)
n_active_tx = int(n_transactions * 0.70)
for _ in range(n_active_tx):
    cid = np.random.choice(active_ids)
    tx_customer_ids.append(cid)
    day_offset = np.random.randint(0, tx_days)
    tx_dates.append((tx_start + timedelta(days=day_offset)).strftime("%Y-%m-%d"))
    tx_amounts.append(float(np.random.randint(1000, 500001)))
    tx_categories.append(np.random.choice(categories))
    tx_methods.append(np.random.choice(methods, p=[0.45, 0.40, 0.15]))

# 이탈 고객 거래 (~30%) - 최근 거래 줄어듦
n_churn_tx = n_transactions - n_active_tx
for _ in range(n_churn_tx):
    cid = np.random.choice(churned_ids)
    tx_customer_ids.append(cid)
    # 베타 분포로 앞쪽에 편향 (최근 거래 적음)
    day_offset = int(np.random.beta(2, 5) * tx_days)
    tx_dates.append((tx_start + timedelta(days=day_offset)).strftime("%Y-%m-%d"))
    tx_amounts.append(float(np.random.randint(1000, 300001)))
    tx_categories.append(np.random.choice(categories))
    tx_methods.append(np.random.choice(methods, p=[0.45, 0.40, 0.15]))

# 일부 거래금액 NaN
tx_amounts = np.array(tx_amounts, dtype=float)
nan_tx_idx = np.random.choice(n_transactions, size=200, replace=False)
tx_amounts[nan_tx_idx] = np.nan

tx_ids = [f"T{str(i).zfill(6)}" for i in range(1, n_transactions + 1)]

transactions_df = pd.DataFrame({
    "거래ID": tx_ids,
    "고객ID": tx_customer_ids,
    "거래일": tx_dates,
    "거래금액": tx_amounts,
    "카테고리": tx_categories,
    "결제방법": tx_methods
})

# 셔플
transactions_df = transactions_df.sample(frac=1, random_state=2024).reset_index(drop=True)
transactions_df["거래ID"] = [f"T{str(i).zfill(6)}" for i in range(1, n_transactions + 1)]

transactions_df.to_csv(f"{DATA_DIR}transactions.csv", index=False, encoding="utf-8-sig")
print(f"transactions.csv: {len(transactions_df)} rows saved")

# ============================================================
# 3. service_usage.csv (~20000 rows, monthly)
# ============================================================

months = pd.date_range("2023-01", "2024-06", freq="MS")  # 18 months
month_strs = [m.strftime("%Y-%m") for m in months]

usage_rows = []
churn_set = set(churned_ids)

for cid in customer_ids:
    # 각 고객이 모든 월에 데이터가 있지는 않음 (일부 빠짐)
    n_months = np.random.randint(8, 19)  # 8~18개월
    selected_months = sorted(np.random.choice(range(len(month_strs)), size=min(n_months, len(month_strs)), replace=False))

    is_churned = cid in churn_set

    for idx, m_idx in enumerate(selected_months):
        month = month_strs[m_idx]
        progress = idx / max(len(selected_months) - 1, 1)  # 0~1

        if is_churned:
            # 이탈 고객: 시간 지남에 따라 로그인/이용 감소, 불만 증가
            login = max(0, int(np.random.normal(40 - 30 * progress, 8)))
            usage_time = max(0, int(np.random.normal(2000 - 1500 * progress, 300)))
            inquiry = max(0, min(10, int(np.random.normal(2 + 4 * progress, 2))))
            complaint = max(0, min(5, int(np.random.normal(0.5 + 3 * progress, 1))))
        else:
            login = max(0, int(np.random.normal(35, 10)))
            usage_time = max(0, int(np.random.normal(1500, 400)))
            inquiry = max(0, min(10, int(np.random.normal(2, 1.5))))
            complaint = max(0, min(5, int(np.random.normal(0.5, 0.8))))

        usage_rows.append({
            "고객ID": cid,
            "연월": month,
            "로그인횟수": login,
            "서비스이용시간(분)": usage_time,
            "문의횟수": inquiry,
            "불만횟수": complaint
        })

usage_df = pd.DataFrame(usage_rows)
print(f"service_usage.csv: {len(usage_df)} rows saved")

usage_df.to_csv(f"{DATA_DIR}service_usage.csv", index=False, encoding="utf-8-sig")

# Summary
print("\n=== 데이터 생성 완료 ===")
print(f"customers.csv: {len(customers_df)} rows, 이탈률: {churn.mean():.1%}")
print(f"transactions.csv: {len(transactions_df)} rows")
print(f"service_usage.csv: {len(usage_df)} rows")
