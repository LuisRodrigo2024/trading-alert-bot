import os
import time
import requests
import logging
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

COMMISSION = 20  # $10 buy + $10 sell

logging.basicConfig(level=logging.INFO)

# =========================
# DATA LAYER (SIMPLIFIED)
# =========================

def get_price_change(symbol):
    """
    Simulación simple de movimiento de precio.
    En producción puedes reemplazar con Yahoo Finance / Finnhub / AlphaVantage.
    """
    try:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
        r = requests.get(url)
        data = r.json()

        result = data["chart"]["result"][0]
        meta = result["meta"]

        current = meta["regularMarketPrice"]
        previous = meta["previousClose"]

        change_pct = ((current - previous) / previous) * 100
        return change_pct
    except:
        return 0


def get_news_sentiment(symbol):
    """
    Simulación simple de sentimiento de noticias.
    (en producción: NLP real o API de noticias)
    """
    try:
        url = f"https://news.google.com/rss/search?q={symbol}+stock"
        r = requests.get(url)

        text = r.text.lower()

        positive_words = ["upgrade", "growth", "profit", "beats", "strong"]
        negative_words = ["loss", "drop", "lawsuit", "decline", "weak"]

        score = 0

        for w in positive_words:
            if w in text:
                score += 0.3

        for w in negative_words:
            if w in text:
                score -= 0.3

        return score
    except:
        return 0


# =========================
# DECISION ENGINE
# =========================

def decision_engine(price_change, sentiment_score, expected_profit):

    if expected_profit < COMMISSION:
        return {
            "signal": "HOLD",
            "reason": "Ganancia no cubre comisión ($20)"
        }

    if price_change > 2 and sentiment_score > 0.2:
        return {
            "signal": "BUY",
            "reason": "Tendencia alcista + noticias positivas"
        }

    if price_change < -2 and sentiment_score < -0.2:
        return {
            "signal": "SELL",
            "reason": "Caída + noticias negativas"
        }

    return {
        "signal": "HOLD",
        "reason": "Sin señal clara"
    }


# =========================
# TELEGRAM COMMANDS
# =========================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🚀 Trading Alert Bot activo\nUsa /scan para analizar mercado"
    )


async def scan(update: Update, context: ContextTypes.DEFAULT_TYPE):

    messages = []

    for stock in STOCKS:

        price_change = get_price_change(stock)
        sentiment = get_news_sentiment(stock)

        # estimación simple de profit (modelo simplificado)
        expected_profit = abs(price_change) * 10

        decision = decision_engine(price_change, sentiment, expected_profit)

        msg = (
            f"📊 {stock}\n"
            f"📈 Cambio: {price_change:.2f}%\n"
            f"🧠 Sentimiento: {sentiment:.2f}\n"
            f"💰 Est. Profit: ${expected_profit:.2f}\n"
            f"🤖 Señal: {decision['signal']}\n"
            f"📌 {decision['reason']}\n"
            "----------------------"
        )

        messages.append(msg)

    await update.message.reply_text("\n".join(messages))


# =========================
# LOOP AUTOMÁTICO (TIME REAL)
# =========================

def background_loop(app):

    while True:
        try:
            for stock in STOCKS:

                price_change = get_price_change(stock)
                sentiment = get_news_sentiment(stock)
                expected_profit = abs(price_change) * 10

                decision = decision_engine(price_change, sentiment, expected_profit)

                if decision["signal"] in ["BUY", "SELL"]:

                    message = (
                        f"🚨 ALERTA {stock}\n"
                        f"Señal: {decision['signal']}\n"
                        f"Motivo: {decision['reason']}\n"
                        f"📈 Cambio: {price_change:.2f}%\n"
                        f"🧠 Sentimiento: {sentiment:.2f}"
                    )

                    # enviar a chat principal (si tienes chat_id puedes fijarlo)
                    for chat in app.chat_data.values():
                        pass

        except Exception as e:
            logging.error(e)

        time.sleep(60)


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

    print("🤖 Bot corriendo...")

    app.run_polling()


if __name__ == "__main__":
    main()
