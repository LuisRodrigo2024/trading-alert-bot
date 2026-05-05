import os
import logging
import yfinance as yf
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
# MARKET DATA (LIGHT)
# =========================

def get_price_change(symbol):
    try:
        stock = yf.Ticker(symbol)
        hist = stock.history(period="2d")

        if len(hist) < 2:
            return 0

        last = hist["Close"].iloc[-1]
        prev = hist["Close"].iloc[-2]

        return ((last - prev) / prev) * 100

    except:
        return 0

# =========================
# NEWS SENTIMENT (ULTRA LIGHT)
# =========================

def get_sentiment(symbol):
    try:
        # News RSS simplificado (sin IA)
        import requests

        url = f"https://news.google.com/rss/search?q={symbol}+stock"
        r = requests.get(url, timeout=5)

        text = r.text.lower()

        positive = ["growth", "profit", "upgrade", "strong", "beats"]
        negative = ["loss", "drop", "weak", "lawsuit", "decline"]

        score = 0

        for w in positive:
            if w in text:
                score += 0.3

        for w in negative:
            if w in text:
                score -= 0.3

        return score

    except:
        return 0

# =========================
# DECISION ENGINE
# =========================

def decision_engine(price_change, sentiment):

    expected_profit = abs(price_change) * 10

    # 💰 filtro comisión
    if expected_profit < COMMISSION:
        return "HOLD", "No cubre comisión ($20)"

    score = price_change + (sentiment * 5)

    if score > 3:
        return "BUY", f"Momentum + Sentimiento positivo ({score:.2f})"

    if score < -3:
        return "SELL", f"Caída + noticias negativas ({score:.2f})"

    return "HOLD", f"Sin señal clara ({score:.2f})"

# =========================
# TELEGRAM
# =========================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🚀 Trading Bot LIGERO activo")

async def scan(update: Update, context: ContextTypes.DEFAULT_TYPE):

    messages = []

    for stock in STOCKS:

        price = get_price_change(stock)
        sentiment = get_sentiment(stock)

        signal, reason = decision_engine(price, sentiment)

        msg = (
            f"📊 {stock}\n"
            f"📈 Cambio: {price:.2f}%\n"
            f"🧠 Sentimiento: {sentiment:.2f}\n"
            f"🤖 Señal: {signal}\n"
            f"📌 {reason}\n"
            "--------------------"
        )

        messages.append(msg)

    await update.message.reply_text("\n".join(messages))

# =========================
# MAIN
# =========================

def main():

    if not TOKEN:
        print("❌ TOKEN no configurado")
        return

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("scan", scan))

    print("🚀 Bot ligero corriendo...")
    app.run_polling()

if __name__ == "__main__":
    main()
