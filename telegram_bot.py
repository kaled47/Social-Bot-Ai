import os
import logging
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from services.ai import generar_respuesta
from database import guardar_interaccion #Modifcacion 1 importamos base de datos
# ─────────────────────────────────────────────
# Configuración
# ─────────────────────────────────────────────
load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────
# Handlers
# ─────────────────────────────────────────────

async def ayuda(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Único comando disponible."""
    texto = (
        "🧭 *TravelAI — Asistente de viajes*\n\n"
        "Escríbeme directamente con cualquier pregunta sobre:\n\n"
        "• ✈️ Vuelos nacionales e internacionales\n"
        "• 🏨 Hoteles y alojamientos\n"
        "• 🌴 Paquetes vacacionales\n"
        "• 📍 Recomendaciones turísticas\n"
        "• 💰 Precios y promociones\n\n"
        "No necesitas ningún comando — solo escríbeme y te respondo al instante 😊"
    )
    await update.message.reply_text(texto, parse_mode="Markdown")


async def manejar_mensaje(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Procesa cualquier mensaje de texto y responde con Gemini AI."""
    mensaje_usuario = update.message.text
    user_id = update.effective_user.id
    username = update.effective_user.username or update.effective_user.first_name

    logger.info("Mensaje de @%s (id=%s): %s", username, user_id, mensaje_usuario)

    await update.message.chat.send_action("typing")

    try:
        respuesta = generar_respuesta(mensaje_usuario)
        logger.info("Respuesta IA para @%s: %s", username, respuesta)

        guardar_interaccion(str(username), mensaje_usuario, respuesta) #Modificacion 2 almacena los datos en SQLite

    except Exception as e:
        logger.error("Error al generar respuesta: %s", e)
        respuesta = "⚠️ El asistente está temporalmente ocupado. Por favor intenta nuevamente en unos segundos."

    await update.message.reply_text(respuesta)


async def manejar_error(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log de errores inesperados del bot."""
    logger.error("Error inesperado: %s", context.error, exc_info=context.error)


# ─────────────────────────────────────────────
# Punto de entrada
# ─────────────────────────────────────────────

def main() -> None:
    if not TELEGRAM_BOT_TOKEN:
        raise ValueError(
            "❌ No se encontró TELEGRAM_BOT_TOKEN en el archivo .env\n"
            "Agrega: TELEGRAM_BOT_TOKEN=tu_token_aqui"
        )

    logger.info("🚀 Iniciando TravelAI Telegram Bot...")

    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("ayuda", ayuda))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, manejar_mensaje))
    app.add_error_handler(manejar_error)

    logger.info("✅ Bot corriendo — esperando mensajes (Ctrl+C para detener)")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()