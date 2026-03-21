import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import os

np.random.seed(42)

SAVE_DIR = os.path.dirname(os.path.abspath(__file__))

# ============================================================
# 1. customers.csv (800 customers)
# ============================================================

n_customers = 800
customer_ids = [f"CU{str(i).zfill(5)}" for i in range(1, n_customers + 1)]

# 성별 - with intentional dirty values
genders_clean = np.random.choice(["남", "여"], size=n_customers, p=[0.55, 0.45])
genders = genders_clean.copy()
dirty_idx = np.random.choice(n_customers, size=30, replace=False)
for i in dirty_idx[:8]:
    genders[i] = "남자" if genders[i] == "남" else "여자"
for i in dirty_idx[8:16]:
    genders[i] = "M" if genders[i] == "남" else "F"
for i in dirty_idx[16:]:
    genders[i] = np.nan

# 연령 - with NaN and outliers
ages = np.random.randint(20, 66, size=n_customers).astype(float)
nan_age_idx = np.random.choice(n_customers, size=15, replace=False)
ages[nan_age_idx] = np.nan
ages[np.random.randint(0, n_customers)] = -1
ages[np.random.randint(0, n_customers)] = 200

# 지역 - with dirty values
regions_clean = ["서울", "경기", "인천", "부산", "대구", "대전", "광주", "기타"]
regions_prob = [0.30, 0.25, 0.10, 0.10, 0.07, 0.06, 0.05, 0.07]
regions = np.random.choice(regions_clean, size=n_customers, p=regions_prob)
regions = regions.astype(object)
dirty_region_idx = np.random.choice(n_customers, size=20, replace=False)
for i in dirty_region_idx[:10]:
    regions[i] = regions[i] + " "  # trailing space
for i in dirty_region_idx[10:15]:
    if regions[i] == "서울":
        regions[i] = "서울특별시"
    elif regions[i] == "부산":
        regions[i] = "부산광역시"
    elif regions[i] == "대구":
        regions[i] = "대구광역시"
    elif regions[i] == "인천":
        regions[i] = "인천광역시"
    elif regions[i] == "대전":
        regions[i] = "대전광역시"

# 가입일 - mixed date formats
start_date = datetime(2021, 1, 1)
end_date = datetime(2024, 6, 30)
date_range_days = (end_date - start_date).days
join_dates = [start_date + timedelta(days=np.random.randint(0, date_range_days)) for _ in range(n_customers)]

join_date_strs = []
for i, d in enumerate(join_dates):
    r = np.random.random()
    if r < 0.6:
        join_date_strs.append(d.strftime("%Y-%m-%d"))
    elif r < 0.8:
        join_date_strs.append(d.strftime("%Y/%m/%d"))
    elif r < 0.9:
        join_date_strs.append(d.strftime("%Y.%m.%d"))
    else:
        join_date_strs.append(d.strftime("%d-%m-%Y"))

# 요금제
plans = np.random.choice(["베이직", "스탠다드", "프리미엄"], size=n_customers, p=[0.40, 0.35, 0.25])
plan_price_map = {"베이직": 9900, "스탠다드": 14900, "프리미엄": 19900}

# 가입경로
channels = np.random.choice(["검색", "SNS광고", "지인추천", "앱스토어", "기타"],
                             size=n_customers, p=[0.30, 0.25, 0.20, 0.15, 0.10])

# 이탈여부 - 30% churn, realistic patterns later
churn_labels = np.zeros(n_customers, dtype=int)
churn_idx = np.random.choice(n_customers, size=int(n_customers * 0.30), replace=False)
churn_labels[churn_idx] = 1

# 이탈일 - only for churned, between join_date and 2024-06-30
churn_dates = [None] * n_customers
for i in churn_idx:
    earliest_churn = join_dates[i] + timedelta(days=30)
    latest_churn = datetime(2024, 6, 30)
    if earliest_churn >= latest_churn:
        earliest_churn = join_dates[i] + timedelta(days=7)
    days_range = (latest_churn - earliest_churn).days
    if days_range > 0:
        churn_dates[i] = earliest_churn + timedelta(days=np.random.randint(0, days_range))
    else:
        churn_dates[i] = latest_churn

churn_date_strs = [d.strftime("%Y-%m-%d") if d else np.nan for d in churn_dates]

# 월평균결제액 - based on plan with variation, some dirty
payments = []
for i in range(n_customers):
    base = plan_price_map[plans[i]]
    variation = np.random.normal(0, base * 0.1)
    pay = max(0, round(base + variation, -2))
    payments.append(pay)

payments = np.array(payments, dtype=object)
# Add comma-formatted values
comma_idx = np.random.choice(n_customers, size=25, replace=False)
for i in comma_idx:
    payments[i] = f"{int(payments[i]):,}"
# Add NaN
nan_pay_idx = np.random.choice(n_customers, size=12, replace=False)
for i in nan_pay_idx:
    payments[i] = np.nan

customers_df = pd.DataFrame({
    "고객ID": customer_ids,
    "성별": genders,
    "연령": ages,
    "지역": regions,
    "가입일": join_date_strs,
    "요금제": plans,
    "이탈여부": churn_labels,
    "이탈일": churn_date_strs,
    "월평균결제액": payments,
    "가입경로": channels,
})

customers_df.to_csv(os.path.join(SAVE_DIR, "customers.csv"), index=False, encoding="utf-8-sig")

# ============================================================
# 2. usage_2023.csv
# ============================================================

usage_2023_rows = []
months_2023 = [f"2023-{str(m).zfill(2)}" for m in range(1, 13)]

for i in range(n_customers):
    cid = customer_ids[i]
    is_churned = churn_labels[i]
    join_d = join_dates[i]
    churn_d = churn_dates[i]

    # Determine which months this customer was active in 2023
    for m_idx, ym in enumerate(months_2023):
        year, month = 2023, m_idx + 1
        month_start = datetime(year, month, 1)
        month_end = datetime(year, month, 28)

        if join_d > month_end:
            continue
        if churn_d and churn_d < month_start:
            continue

        # Skip some months randomly (~5% chance) to create incomplete records
        if np.random.random() < 0.05:
            continue

        if is_churned:
            # Churned customers trend downward
            if churn_d:
                months_until_churn = (churn_d.year - year) * 12 + (churn_d.month - month)
                if months_until_churn < 0:
                    months_until_churn = 0
                decay = max(0.2, 1.0 - (1.0 - months_until_churn / 24.0) * 0.6) if months_until_churn < 12 else 1.0
            else:
                decay = 0.5
            usage_count = max(0, int(np.random.poisson(8) * decay))
        else:
            usage_count = max(0, int(np.random.poisson(15)))

        usage_minutes = max(0, int(usage_count * np.random.uniform(10, 40) + np.random.normal(0, 10)))

        row = {"고객ID": cid, "연월": ym, "이용횟수": usage_count, "이용시간(분)": usage_minutes}

        # Add some NaN
        if np.random.random() < 0.02:
            row["이용횟수"] = np.nan
        if np.random.random() < 0.02:
            row["이용시간(분)"] = np.nan

        usage_2023_rows.append(row)

usage_2023_df = pd.DataFrame(usage_2023_rows)
usage_2023_df.to_csv(os.path.join(SAVE_DIR, "usage_2023.csv"), index=False, encoding="utf-8-sig")

# ============================================================
# 3. usage_2024.csv (2024-01 ~ 2024-06)
# ============================================================

usage_2024_rows = []
months_2024 = [f"2024-{str(m).zfill(2)}" for m in range(1, 7)]

for i in range(n_customers):
    cid = customer_ids[i]
    is_churned = churn_labels[i]
    join_d = join_dates[i]
    churn_d = churn_dates[i]

    for m_idx, ym in enumerate(months_2024):
        year, month = 2024, m_idx + 1
        month_start = datetime(year, month, 1)
        month_end = datetime(year, month, 28)

        if join_d > month_end:
            continue
        if churn_d and churn_d < month_start:
            continue

        if np.random.random() < 0.05:
            continue

        if is_churned:
            if churn_d:
                months_until_churn = (churn_d.year - year) * 12 + (churn_d.month - month)
                if months_until_churn < 0:
                    months_until_churn = 0
                decay = max(0.1, 1.0 - (1.0 - months_until_churn / 12.0) * 0.7) if months_until_churn < 6 else 0.8
            else:
                decay = 0.4
            usage_count = max(0, int(np.random.poisson(6) * decay))
        else:
            usage_count = max(0, int(np.random.poisson(15)))

        usage_minutes = max(0, int(usage_count * np.random.uniform(10, 40) + np.random.normal(0, 10)))

        row = {"고객ID": cid, "연월": ym, "이용횟수": usage_count, "이용시간(분)": usage_minutes}

        if np.random.random() < 0.02:
            row["이용횟수"] = np.nan
        if np.random.random() < 0.02:
            row["이용시간(분)"] = np.nan

        usage_2024_rows.append(row)

usage_2024_df = pd.DataFrame(usage_2024_rows)
usage_2024_df.to_csv(os.path.join(SAVE_DIR, "usage_2024.csv"), index=False, encoding="utf-8-sig")

# ============================================================
# 4. campaigns.csv (10 campaigns)
# ============================================================

campaign_data = {
    "캠페인ID": [f"CAM{str(i).zfill(3)}" for i in range(1, 11)],
    "캠페인명": [
        "여름맞이 할인",
        "신규가입 프로모션",
        "추석 감사 이벤트",
        "겨울 특별 혜택",
        "봄맞이 리텐션 캠페인",
        "프리미엄 업그레이드 할인",
        "친구 초대 이벤트",
        "1주년 기념 할인",
        "블랙프라이데이 특가",
        "연말 감사 쿠폰",
    ],
    "시작일": [
        "2023-06-01", "2023-03-01", "2023-09-15", "2023-12-01", "2024-03-01",
        "2023-07-15", "2023-05-01", "2023-10-01", "2023-11-20", "2023-12-20",
    ],
    "종료일": [
        "2023-06-30", "2023-03-31", "2023-10-05", "2023-12-31", "2024-03-31",
        "2023-08-15", "2023-05-31", "2023-10-31", "2023-11-30", "2024-01-05",
    ],
    "채널": ["이메일", "앱푸시", "SMS", "이메일", "SNS", "앱푸시", "SNS", "이메일", "SMS", "앱푸시"],
    "예산(만원)": [500, 800, 600, 700, 1000, 400, 900, 550, 1200, 650],
    "대상고객수": [300, 500, 350, 400, 450, 200, 600, 280, 550, 380],
}

campaigns_df = pd.DataFrame(campaign_data)
campaigns_df.to_csv(os.path.join(SAVE_DIR, "campaigns.csv"), index=False, encoding="utf-8-sig")

# ============================================================
# 5. campaign_responses.csv (~3000 rows with some duplicates)
# ============================================================

campaign_starts = {row["캠페인ID"]: datetime.strptime(row["시작일"], "%Y-%m-%d")
                   for _, row in campaigns_df.iterrows()}
campaign_ends = {row["캠페인ID"]: datetime.strptime(row["종료일"], "%Y-%m-%d")
                 for _, row in campaigns_df.iterrows()}
campaign_targets = {row["캠페인ID"]: row["대상고객수"] for _, row in campaigns_df.iterrows()}

response_rows = []

for _, camp in campaigns_df.iterrows():
    cam_id = camp["캠페인ID"]
    n_target = camp["대상고객수"]
    start_d = campaign_starts[cam_id]
    end_d = campaign_ends[cam_id]
    days_range = max(1, (end_d - start_d).days)

    target_customers = np.random.choice(customer_ids, size=n_target, replace=False)

    for cid in target_customers:
        send_date = start_d + timedelta(days=np.random.randint(0, days_range))

        opened = np.random.random() < 0.45
        clicked = opened and np.random.random() < 0.30
        converted = clicked and np.random.random() < 0.25

        row = {
            "캠페인ID": cam_id,
            "고객ID": cid,
            "발송일": send_date.strftime("%Y-%m-%d"),
            "오픈여부": "Y" if opened else "N",
            "클릭여부": "Y" if clicked else "N",
            "전환여부": "Y" if converted else "N",
            "전환금액": round(np.random.uniform(5000, 50000), -2) if converted else np.nan,
        }
        response_rows.append(row)

responses_df = pd.DataFrame(response_rows)

# Add 4 duplicate rows
dup_indices = np.random.choice(len(responses_df), size=4, replace=False)
duplicates = responses_df.iloc[dup_indices].copy()
responses_df = pd.concat([responses_df, duplicates], ignore_index=True)
responses_df = responses_df.sample(frac=1, random_state=42).reset_index(drop=True)

responses_df.to_csv(os.path.join(SAVE_DIR, "campaign_responses.csv"), index=False, encoding="utf-8-sig")

# ============================================================
# Summary
# ============================================================

print("=" * 60)
print("데이터 생성 완료!")
print("=" * 60)

for name, df in [
    ("customers.csv", customers_df),
    ("usage_2023.csv", usage_2023_df),
    ("usage_2024.csv", usage_2024_df),
    ("campaigns.csv", campaigns_df),
    ("campaign_responses.csv", responses_df),
]:
    print(f"\n--- {name} ---")
    print(f"  행: {len(df):,}, 열: {len(df.columns)}")
    print(f"  컬럼: {list(df.columns)}")
    null_counts = df.isnull().sum()
    nulls = null_counts[null_counts > 0]
    if len(nulls) > 0:
        print(f"  결측치: {dict(nulls)}")
    else:
        print(f"  결측치: 없음")

print(f"\n저장 경로: {SAVE_DIR}")
print("=" * 60)
