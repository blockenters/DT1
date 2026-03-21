"""
03_Pandas_핵심 실습용 CSV 데이터 생성 스크립트
실행: python 02_데이터분석/data/generate_csv.py
"""
import pandas as pd
import numpy as np

np.random.seed(42)

# ============================================================
# 1. 고객 마스터 (customers.csv)
# ============================================================
n_customers = 50
customers = pd.DataFrame({
    "고객ID": [f"C{str(i).zfill(3)}" for i in range(1, n_customers + 1)],
    "고객명": np.random.choice([
        "김민수", "이영희", "박철수", "최지은", "정현우", "강서연", "윤태호", "한미경",
        "오준석", "신예진", "장동건", "송혜교", "류현진", "김태희", "이승기",
        "배수지", "조인성", "한가인", "공유", "전지현", "이민호", "박보검",
        "김소현", "서강준", "남주혁", "이종석", "박서준", "김유정", "도경수", "차은우",
        "안효섭", "김세정", "황민현", "이도현", "노윤서", "고민시", "문가영", "송강",
        "김혜윤", "조보아", "이재욱", "한소희", "차주영", "고윤정", "김지원", "변우석",
        "류수영", "엄정화", "신민아", "원빈"
    ], size=n_customers, replace=False),
    "성별": np.random.choice(["남", "여"], size=n_customers),
    "연령": np.random.randint(20, 60, size=n_customers),
    "지역": np.random.choice(["서울", "경기", "인천", "부산", "대구", "대전", "광주"], size=n_customers, p=[0.3, 0.25, 0.1, 0.1, 0.08, 0.09, 0.08]),
    "가입일": pd.date_range("2022-01-01", periods=n_customers, freq="5D").strftime("%Y-%m-%d").tolist(),
    "회원등급": np.random.choice(["일반", "실버", "골드", "VIP"], size=n_customers, p=[0.4, 0.3, 0.2, 0.1])
})
customers.to_csv("02_데이터분석/data/customers.csv", index=False, encoding="utf-8-sig")
print("customers.csv 생성 완료")

# ============================================================
# 2. 상품 마스터 (products.csv)
# ============================================================
products = pd.DataFrame({
    "상품코드": ["P001", "P002", "P003", "P004", "P005", "P006", "P007", "P008", "P009", "P010",
                "P011", "P012", "P013", "P014", "P015"],
    "상품명": ["노트북", "무선마우스", "기계식키보드", "27인치모니터", "USB허브",
              "웹캠", "블루투스스피커", "외장SSD", "노트북거치대", "마우스패드",
              "충전케이블", "보조배터리", "이어폰", "태블릿", "스마트워치"],
    "카테고리": ["컴퓨터", "주변기기", "주변기기", "컴퓨터", "주변기기",
               "주변기기", "음향", "저장장치", "주변기기", "주변기기",
               "액세서리", "액세서리", "음향", "컴퓨터", "웨어러블"],
    "단가": [1350000, 35000, 89000, 450000, 25000,
            65000, 120000, 95000, 45000, 15000,
            12000, 38000, 55000, 680000, 320000]
})
products.to_csv("02_데이터분석/data/products.csv", index=False, encoding="utf-8-sig")
print("products.csv 생성 완료")

# ============================================================
# 3. 주문 내역 - 1분기 (orders_q1.csv)
# ============================================================
def generate_orders(n_orders, start_date, end_date, start_id):
    dates = pd.date_range(start_date, end_date, freq="D")
    order_dates = np.random.choice(dates, size=n_orders)
    order_dates = np.sort(order_dates)

    return pd.DataFrame({
        "주문번호": [f"ORD{str(i).zfill(5)}" for i in range(start_id, start_id + n_orders)],
        "주문일자": pd.Series(order_dates).dt.strftime("%Y-%m-%d"),
        "고객ID": np.random.choice(customers["고객ID"].values, size=n_orders),
        "상품코드": np.random.choice(products["상품코드"].values, size=n_orders,
                                   p=[0.08, 0.12, 0.10, 0.06, 0.08, 0.05, 0.07, 0.08, 0.06, 0.07,
                                      0.06, 0.05, 0.04, 0.04, 0.04]),
        "수량": np.random.choice([1, 1, 1, 1, 2, 2, 3, 5], size=n_orders)
    })

orders_q1 = generate_orders(150, "2024-01-01", "2024-03-31", 1)
orders_q1.to_csv("02_데이터분석/data/orders_q1.csv", index=False, encoding="utf-8-sig")
print("orders_q1.csv 생성 완료")

# ============================================================
# 4. 주문 내역 - 2분기 (orders_q2.csv)
# ============================================================
orders_q2 = generate_orders(180, "2024-04-01", "2024-06-30", 151)
orders_q2.to_csv("02_데이터분석/data/orders_q2.csv", index=False, encoding="utf-8-sig")
print("orders_q2.csv 생성 완료")

# ============================================================
# 5. 주문 내역 - 3분기 (orders_q3.csv)
# ============================================================
orders_q3 = generate_orders(200, "2024-07-01", "2024-09-30", 331)
orders_q3.to_csv("02_데이터분석/data/orders_q3.csv", index=False, encoding="utf-8-sig")
print("orders_q3.csv 생성 완료")

# ============================================================
# 6. 주문 내역 - 4분기 (orders_q4.csv)
# ============================================================
orders_q4 = generate_orders(220, "2024-10-01", "2024-12-31", 531)
orders_q4.to_csv("02_데이터분석/data/orders_q4.csv", index=False, encoding="utf-8-sig")
print("orders_q4.csv 생성 완료")

print("\n=== 전체 데이터 요약 ===")
print(f"고객: {len(customers)}명")
print(f"상품: {len(products)}개")
print(f"주문: Q1={len(orders_q1)}, Q2={len(orders_q2)}, Q3={len(orders_q3)}, Q4={len(orders_q4)}")
print(f"총 주문: {len(orders_q1) + len(orders_q2) + len(orders_q3) + len(orders_q4)}건")
