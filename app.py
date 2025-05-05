import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta

st.set_page_config(page_title="Stock Analyzer", layout="wide")
st.title("📈 Stock Analyzer with Buy/Sell Signal + Option Trade Suggestion")

symbol = st.text_input("Enter Stock Symbol (e.g., AAPL, TSLA):", "AAPL").upper()

if symbol:
    try:
        ticker = yf.Ticker(symbol)
        df = ticker.history(period="6mo", interval="1d")

        if df.empty:
            st.warning("No data found. Check the symbol.")
        else:
            df.ta.sma(length=50, append=True)
            df.ta.ema(length=20, append=True)
            df.ta.rsi(length=14, append=True)
            df.ta.macd(append=True)
            df.ta.adx(append=True)

            latest = df.iloc[-1]
            indicators = {
                "SMA 50": latest["SMA_50"],
                "EMA 20": latest["EMA_20"],
                "RSI": latest["RSI_14"],
                "MACD": latest["MACD_12_26_9"],
                "ADX": latest["ADX_14"]
            }

            # Simple scoring system
            score = 0
            if latest["SMA_50"] > latest["Close"]: score += 1
            if latest["EMA_20"] > latest["Close"]: score += 1
            if latest["RSI_14"] < 30: score += 1
            if latest["MACD_12_26_9"] < 0: score += 1
            if latest["ADX_14"] > 25: score += 1

            if score <= 1:
                recommendation = "🟢 BUY"
            elif score >= 4:
                recommendation = "🔴 SELL"
            else:
                recommendation = "🟡 NEUTRAL"

            # Show output
            st.subheader(f"📌 Analysis for {symbol}")
            st.metric("Current Price", round(latest["Close"], 2))
            st.metric("Recommendation", recommendation)

            st.subheader("📊 Technical Indicators")
            st.dataframe(pd.DataFrame(indicators, index=["Latest"]).T)

            # Option suggestion
            expiries = ticker.options
            if expiries:
                expiry = expiries[0]
                options = ticker.option_chain(expiry)
                current_price = latest["Close"]
                calls = options.calls
                calls["diff"] = abs(calls["strike"] - current_price)
                best_call = calls.loc[calls["diff"].idxmin()]

                st.subheader("💡 Single-Leg Option Suggestion")
                st.write(f"**{symbol} {expiry} CALL {best_call['strike']}**")
                st.write(f"Last Price: ${best_call['lastPrice']} | Volume: {best_call['volume']} | Open Interest: {best_call['openInterest']}")
            else:
                st.warning("Options data not available.")
    except Exception as e:
        st.error(f"Error: {e}")
