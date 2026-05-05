import os
import logging
import yfinance as yf
import torch
from transformers import pipeline
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# =========================
# CONFIG
# =========================

TOKEN = os.getenv("TOKEN")

STOCKS = [
    "AAPL", "MSFT", "NVDA", "AMZN", "GOOGL",
    "META", "AMD", "AVGO", "MU", "QCOM"
]

COMMISSION = 20

logging.basicConfig(level=logging.INFO)

# =========================
# IA SENTIMENT MODEL
# =========================

sentiment_model = pipeline(
    "sentiment-analysis",
    model="ProsusAI/finbert"
)

# =========================
# MARKET DATA
# =========================

def get_market_data(symbol):
    try:
        stock = yf.Ticker(symbol)
        hist = stock.history(period="2d")

        if len(hist) < 2:
            return 0

        last_close = hist["Close"].iloc[-1]
        prev_close = hist["Close"].iloc[-2]

        change_pct = ((last_close - prev_close) / prev_close) * 100
        return float(change_pct)

    except:
        return 0

# =========================
# NEWS (SIMULADO + REAL FEED READY)
# =========================

def get_news_text(symbol):
    """
    En versión pro real:
    aquí conectarías NewsAPI / Yahoo / RSS
    """
    return f"{symbol} company earnings strong growth innovation AI expansion"

# =========================
# IA SENTIMENT ANALYSIS
# =========================

def analyze_sentiment(text):
    try:
        result = sentiment_model(text)[0]

        label = result["label"]
        score = result["score"]

        if label.lower() == "positive":
            return score
        elif label.lower() == "negative":
            return -score
        else:
            return 0

    except:
        return 0

# =========================
# DECISION ENGINE PRO
# =========================

def decision_engine(price_change, sentiment_score):

    expected_profit = abs(price_change) * 12

    # 💰 filtro comisión
    if expected_profit < COMMISSION:
        return "HOLD", "No cubre comisión ($20)"

    score = price_change + (sentiment_score * 5)

    if score > 3:
        return "BUY", f"Score positivo ({score:.2f})"

    if score < -3:
        return "SELL", f"Score negativo ({score:.2f})"

    return "HOLD", f"Sin señal clara ({score:.2f})"

# =========================
# TELEGRAM COMMANDS
# =========================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🚀 PRO Trading AI Bot activo"
    )

async def scan(update: Update, context: ContextTypes.DEFAULT_TYPE):

    messages = []

    for stock in STOCKS:

        price_change = get_market_data(stock)

        news_text = get_news_text(stock)
        sentiment = analyze_sentiment(news_text)

        signal, reason = decision_engine(price_change, sentiment)

        msg = (
            f"📊 {stock}\n"
            f"📈 Precio: {price_change:.2f}%\n"
            f"🧠 Sentimiento AI: {sentiment:.2f}\n"
            f"🤖 Señal: {signal}\n"
            f"📌 {reason}\n"
            "----------------------"
        )

        messages.append(msg)

    await update.message.reply_text("\n".join(messages))

# =========================
# MAIN
# =========================

def main():

    if not TOKEN:
        print("TOKEN missing")
        return

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("scan", scan))

    print("🚀 PRO AI Bot running...")
    app.run_polling()

if __name__ == "__main__":
    main()
