import streamlit as st
import pandas as pd
import yfinance as yf

# =====================================================================
# [수정] 1. 페이지 초기 설정 - 와이드 모드(wide) 적용으로 좌우 폭 확장
# =====================================================================
st.set_page_config(
    page_title="국민연금(NPS) 글로벌 자산배분 통계 시스템", 
    layout="wide",  # 화면 전체를 꽉 차게 사용하는 옵션
    initial_sidebar_state="collapsed"
)

# =====================================================================
# 데이터 및 백엔드 DB (개발자님 기존 코드 100% 보존)
# =====================================================================
NPS_TOTAL_DOMESTIC_EQUITY_KRW = 320_900_000_000_000  # 320.9조 원
NPS_TOTAL_FOREIGN_EQUITY_KRW = 446_000_000_000_000   # 446조 원

K_STOCKS = [
    {"name": "삼성전자", "ticker": "005930.KS", "code": "005930"},
    {"name": "SK하이닉스", "ticker": "000660.KS", "code": "000660"},
    {"name": "SK스퀘어", "ticker": "402340.KS", "code": "402340"},
    {"name": "현대차", "ticker": "005380.KS", "code": "005380"},
    {"name": "삼성전기", "ticker": "009150.KS", "code": "009150"},
    {"name": "LG에너지솔루션", "ticker": "373220.KS", "code": "373220"},
    {"name": "삼성생명", "ticker": "032830.KS", "code": "032830"},
    {"name": "삼성물산", "ticker": "028260.KS", "code": "028260"},
    {"name": "HD현대중공업", "ticker": "329180.KS", "code": "329180"},
    {"name": "기아", "ticker": "000270.KS", "code": "000270"},
    {"name": "삼성바이오로직스", "ticker": "207940.KS", "code": "207940"},
    {"name": "KB금융", "ticker": "105560.KS", "code": "105560"},
    {"name": "현대모비스", "ticker": "012330.KS", "code": "012330"},
    {"name": "두산에너빌리티", "ticker": "034020.KS", "code": "034020"},
    {"name": "한화에어로스페이스", "ticker": "012450.KS", "code": "012450"},
    {"name": "신한지주", "ticker": "055550.KS", "code": "055550"},
    {"name": "NAVER", "ticker": "035420.KS", "code": "035420"},
    {"name": "LG전자", "ticker": "066570.KS", "code": "066570"},
    {"name": "SK", "ticker": "034730.KS", "code": "034730"},
    {"name": "삼성SDI", "ticker": "006400.KS", "code": "006400"}
]

US_STOCKS = [
    {"name": "Microsoft", "ticker": "MSFT", "cusip": "594918104"},
    {"name": "Apple", "ticker": "AAPL", "cusip": "037833100"},
    {"name": "NVIDIA", "ticker": "NVDA", "cusip": "67066G104"},
    {"name": "Amazon", "ticker": "AMZN", "cusip": "023135106"},
    {"name": "Alphabet Class A", "ticker": "GOOGL", "cusip": "02079K305"},
    {"name": "Meta Platforms", "ticker": "META", "cusip": "30303M102"},
    {"name": "Berkshire Hathaway Class B", "ticker": "BRK.B", "cusip": "084670702"},
    {"name": "Alphabet Class C", "ticker": "GOOG", "cusip": "02079K107"},
    {"name": "Eli Lilly", "ticker": "LLY", "cusip": "532457108"},
    {"name": "Broadcom", "ticker": "AVGO", "cusip": "11135F101"},
    {"name": "Tesla", "ticker": "TSLA", "cusip": "88160R101"},
    {"name": "JPMorgan Chase", "ticker": "JPM", "cusip": "46625H100"},
    {"name": "UnitedHealth Group", "ticker": "UNH", "cusip": "91324P102"},
    {"name": "Visa", "ticker": "V", "cusip": "92826C839"},
    {"name": "Exxon Mobil", "ticker": "XOM", "cusip": "30231G102"},
    {"name": "Mastercard", "ticker": "MA", "cusip": "57636Q104"},
    {"name": "Johnson & Johnson", "ticker": "JNJ", "cusip": "478160104"},
    {"name": "Procter & Gamble", "ticker": "PG", "cusip": "742718109"},
    {"name": "Home Depot", "ticker": "HD", "cusip": "437076102"},
    {"name": "Costco", "ticker": "COST", "cusip": "22160K105"}
]

K_STOCKS_NPS_DB = {
    "005930": {"shares": 458147205, "pct": 7.68},
    "000660": {"shares": 57875116, "pct": 7.95},
    "402340": {"shares": 11141601, "pct": 8.24},
    "005380": {"shares": 16145190, "pct": 7.70},
    "009150": {"shares": 6648122, "pct": 8.90},
    "373220": {"shares": 11723400, "pct": 5.01},
    "032830": {"shares": 10420000, "pct": 5.21},
    "028260": {"shares": 12246087, "pct": 6.87},
    "329180": {"shares": 5415100, "pct": 6.10},
    "000270": {"shares": 28680000, "pct": 7.17},
    "207940": {"shares": 4341200, "pct": 6.10},
    "105560": {"shares": 33341919, "pct": 8.94},
    "012330": {"shares": 7654000, "pct": 8.12},
    "034020": {"shares": 42880000, "pct": 6.70},
    "012450": {"shares": 3750000, "pct": 7.40},
    "055550": {"shares": 41500000, "pct": 8.20},
    "035420": {"shares": 14638837, "pct": 9.24},
    "066570": {"shares": 12246087, "pct": 7.48},
    "034730": {"shares": 5910000, "pct": 8.10},
    "006400": {"shares": 5430000, "pct": 7.90}
}

US_STOCKS_NPS_DB = {
    "MSFT": {"shares": 11200000, "val_usd": 4720000000},
    "AAPL": {"shares": 12400000, "val_usd": 2550000000},
    "NVDA": {"shares": 21500000, "val_usd": 2680000000},
    "AMZN": {"shares": 11100000, "val_usd": 2100000000},
    "GOOGL": {"shares": 11500000, "val_usd": 1820000000},
    "META": {"shares": 3100000, "val_usd": 1540000000},
    "BRK.B": {"shares": 1950000, "val_usd": 820000000},
    "GOOG": {"shares": 9400000, "val_usd": 1500000000},
    "LLY": {"shares": 1100000, "val_usd": 980000000},
    "AVGO": {"shares": 850000, "val_usd": 1210000000},
    "TSLA": {"shares": 4100000, "val_usd": 710000000},
    "JPM": {"shares": 3800000, "val_usd": 740000000},
    "UNH": {"shares": 1300000, "val_usd": 670000000},
    "V": {"shares": 2300000, "val_usd": 620000000},
    "XOM": {"shares": 4500000, "val_usd": 510000000},
    "MA": {"shares": 1100000, "val_usd": 500000000},
    "JNJ": {"shares": 3100000, "val_usd": 480000000},
    "PG": {"shares": 2900000, "val_usd": 470000000},
    "HD": {"shares": 1200000, "val_usd": 440000000},
    "COST": {"shares": 520000, "val_usd": 430000000}
}

# 연산 엔진 함수들 (기존 로직 보존)
@st.cache_data(ttl=3600)
def fetch_financial_market_data():
    k_tickers = [s["ticker"] for s in K_STOCKS]
    us_tickers = [s["ticker"] for s in US_STOCKS]
    all_tickers = k_tickers + us_tickers + ["USDKRW=X"]
    prices, shares_outstanding = {}, {}
    try:
        tickers_str = " ".join(all_tickers)
        data = yf.Tickers(tickers_str)
        for t in all_tickers:
            try:
                ticker_obj = data.tickers[t]
                price = None
                fast_info = getattr(ticker_obj, 'fast_info', {})
                if fast_info:
                    price = fast_info.get('last_price', None) or fast_info.get('lastPrice', None)
                if price is None:
                    hist = ticker_obj.history(period="1d")
                    if not hist.empty: price = hist['Close'].iloc[-1]
                prices[t] = price
                if t in us_tickers:
                    shares_outstanding[t] = getattr(ticker_obj, 'info', {}).get('sharesOutstanding', None)
            except Exception:
                prices[t], shares_outstanding[t] = None, None
    except Exception:
        for t in all_tickers:
            try:
                ticker_obj = yf.Ticker(t)
                hist = ticker_obj.history(period="1d")
                prices[t] = hist['Close'].iloc[-1] if not hist.empty else None
                if t in us_tickers: shares_outstanding[t] = ticker_obj.info.get('sharesOutstanding', None)
            except Exception:
                prices[t], shares_outstanding[t] = None, None
    usdkrw_rate = prices.get("USDKRW=X", 1380.0)
    return prices, shares_outstanding, usdkrw_rate

def calculate_domestic_portfolio(prices):
    results = []
    for stock in K_STOCKS:
        code = stock["code"]
        db_info = K_STOCKS_NPS_DB.get(code, {"shares": 0, "pct": 0.0})
        shares, pct = db_info["shares"], db_info["pct"]
        curr_price = prices.get(stock["ticker"])
        eval_100m = (shares * curr_price / 100_000_000) if curr_price and shares > 0 else 0.0
        results.append({"종목명": stock["name"], "티커": code, "보유 주식수": int(shares), "평가액(억 원)": eval_100m, "지분율(%)": pct})
    df = pd.DataFrame(results)
    if not df.empty:
        total_top20 = df["평가액(억 원)"].sum()
        df["상위20 비중(%)"] = (df["평가액(억 원)"] / total_top20 * 100) if total_top20 > 0 else 0.0
        df["국민연금 전체 내 비중(%)"] = ((df["평가액(억 원)"] * 100_000_000) / NPS_TOTAL_DOMESTIC_EQUITY_KRW) * 100
        df = df.sort_values(by="평가액(억 원)", ascending=False).reset_index(drop=True)
        df.index = df.index + 1
        df.index.name = "순위"
    return df

def calculate_us_portfolio(prices, outstanding_map, exchange_rate):
    results = []
    for stock in US_STOCKS:
        ticker = stock["ticker"]
        db_info = US_STOCKS_NPS_DB.get(ticker, {"shares": 0, "val_usd": 0.0})
        shares, val_usd = db_info["shares"], db_info["val_usd"]
        curr_price = prices.get(stock["ticker"])
        if curr_price and shares > 0: val_usd = shares * curr_price
        val_100m = (val_usd * exchange_rate / 100_000_000)
        outstanding_shares = outstanding_map.get(stock["ticker"])
        pct = (shares / outstanding_shares * 100) if outstanding_shares and shares > 0 else 0.0
        results.append({"종목명": stock["name"], "티커": ticker, "보유 주식수": int(shares), "평가액(억 원)": eval_100m if 'eval_100m' in locals() else val_100m, "지분율(%)": pct})
    df = pd.DataFrame(results)
    if not df.empty:
        total_top20 = df["평가액(억 원)"].sum()
        df["상위20 비중(%)"] = (df["평가액(억 원)"] / total_top20 * 100) if total_top20 > 0 else 0.0
        df["국민연금 전체 내 비중(%)"] = ((df["평가액(억 원)"] * 100_000_000) / NPS_TOTAL_FOREIGN_EQUITY_KRW) * 100
        df = df.sort_values(by="평가액(억 원)", ascending=False).reset_index(drop=True)
        df.index = df.index + 1
        df.index.name = "순위"
    return df

# =====================================================================
# [수정] 4. 대시보드 UI 및 배치 렌더링 (와이드 스크린 최적화)
# =====================================================================
st.title("🏛️ 국민연금(NPS) 글로벌 자산배분 통계 시스템")

with st.spinner("최신 마켓 시세 및 원/달러 실시간 환율을 취합하고 있습니다..."):
    prices_map, outstanding_map, current_rate = fetch_financial_market_data()

# 상단 요약 지표 컴팩트 배치
overview_cols = st.columns(3)
with overview_cols[0]:
    st.metric(label="💵 실시간 환율 (USD/KRW)", value=f"{current_rate:,.2f} 원")
with overview_cols[1]:
    st.metric(label="📊 국내주식 총 자산 (분모)", value=f"{NPS_TOTAL_DOMESTIC_EQUITY_KRW/1_0000_0000_0000:,.1f} 조 원")
with overview_cols[2]:
    st.metric(label="🌎 해외주식 총 자산 (분모)", value=f"{NPS_TOTAL_FOREIGN_EQUITY_KRW/1_0000_0000_0000:,.1f} 조 원")

st.markdown("---")

# 데이터 연산
df_korean = calculate_domestic_portfolio(prices_map)
df_us = calculate_us_portfolio(prices_map, outstanding_map, current_rate)

# =====================================================================
# [수정] 공시 뷰어 최적화 - 컬럼별 너비(width) 고정 지정을 통해 스크롤바 제거
# =====================================================================
col_config_template = {
    "종목명": st.column_config.TextColumn("종목명", width="medium"),
    "티커": st.column_config.TextColumn("티커", width="small"),
    "보유 주식수": st.column_config.NumberColumn("보유 주식수", format="%d 주", width="medium"),
    "평가액(억 원)": st.column_config.NumberColumn("평가액(억 원)", format="%,.1f 억 원", width="medium"),
    "지분율(%)": st.column_config.NumberColumn("지분율(%)", format="%.2f %%", width="small"),
    "상위20 비중(%)": st.column_config.NumberColumn("상위20 내 비중(%)", format="%.2f %%", width="medium"),
    "국민연금 전체 내 비중(%)": st.column_config.NumberColumn("전체 자산 내 비중", format="%.4f %%", width="medium"),
}

# --- [ Section 1: 국내 주식 포트폴리오 ] ---
st.header("🇰🇷 국내 KOSPI 시총 상위 20 포트폴리오")
if not df_korean.empty:
    st.subheader(f"Top 20 투자금 총액: {df_korean['평가액(억 원)'].sum():,.1f} 억 원 (국내 자산의 {((df_korean['평가액(억 원)'].sum() * 100_000_000) / NPS_TOTAL_DOMESTIC_EQUITY_KRW) * 100:.2f}%)")
    
    # 750px 높이와 전폭 최적화 셋업 적용
    st.dataframe(
        df_korean,
        column_config=col_config_template,
        use_container_width=True,
        height=750
    )
    st.bar_chart(df_korean.set_index("종목명")["평가액(억 원)"])
else:
    st.error("국내 데이터를 연산할 수 없습니다.")

st.markdown("---")

# --- [ Section 2: 미국 주식 포트폴리오 ] ---
st.header("🇺🇸 미국 US 시총 상위 20 포트폴리오")
if not df_us.empty:
    st.subheader(f"Top 20 투자금 총액: {df_us['평가액(억 원)'].sum():,.1f} 억 원 (해외 자산의 {((df_us['평가액(억 원)'].sum() * 100_000_000) / NPS_TOTAL_FOREIGN_EQUITY_KRW) * 100:.2f}%)")
    
    # 750px 높이와 전폭 최적화 셋업 적용
    st.dataframe(
        df_us,
        column_config=col_config_template,
        use_container_width=True,
        height=750
    )
    st.bar_chart(df_us.set_index("종목명")["평가액(억 원)"])
else:
    st.error("미국 데이터를 연산할 수 없습니다.")
