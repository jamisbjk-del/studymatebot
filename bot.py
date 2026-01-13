from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from fpdf import FPDF
import os
import pytesseract
import cv2
import yt_dlp
import whisper
import requests

TOKEN = os.getenv("BOT_TOKEN")

# ========= 1. رسالة الترحيب =========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🌟 أهلاً وسهلاً! أنا بوت StudyMate.\n"
        "أقدر ألخص النصوص، أحولها PDF، أفرغ الصوت، أقرأ المحاضرات بخط اليد، أنشئ صور، وأحمل من السوشيال.\n"
        "✨ جرب أي أمر من الأوامر التالية:\n"
        "/ocr (صورة)\n/stt (صوت)\n/summarize (نص)\n/pdf (نص)\n/image (وصف)\n/download (رابط)"
    )

# ========= 2. تلخيص النصوص =========
async def summarize(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if len(text) < 100:
        await update.message.reply_text("✍️ أرسل لي نص أطول عشان أقدر ألخصه بشكل مفيد.")
        return
    summary = text[:100] + "...\n\n🔑 للحصول على التلخيص الكامل، تواصل معنا للاشتراك 💳"
    await update.message.reply_text(summary)

# ========= 3. تحويل النص إلى PDF =========
async def to_pdf(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.replace("/pdf ", "")
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, text)
    pdf.output("output.pdf")
    await update.message.reply_document(open("output.pdf", "rb"))

# ========= 4. OCR للمحاضرات بخط اليد =========
async def ocr(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo = await update.message.photo[-1].get_file()
    file_path = await photo.download_to_drive("lecture.jpg")
    img = cv2.imread("lecture.jpg")
    text = pytesseract.image_to_string(img, lang="ara")
    await update.message.reply_text("📖 النص المستخرج:\n" + text[:200] + "...\n\n✨ أرسل /summarize للتلخيص")

# ========= 5. تحويل الصوت إلى نص =========
async def stt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    voice = await update.message.voice.get_file()
    file_path = await voice.download_to_drive("audio.ogg")
    model = whisper.load_model("base")
    result = model.transcribe("audio.ogg")
    await update.message.reply_text("🎙️ النص المستخرج:\n" + result["text"])

# ========= 6. توليد الصور =========
async def image_gen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    desc = update.message.text.replace("/image ", "")
    await update.message.reply_text(f"🖼️ (هنا يتم توليد صورة من الوصف: {desc})")

# ========= 7. تحميل من السوشيال =========
async def download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.replace("/download ", "")
    ydl_opts = {"outtmpl": "downloaded.%(ext)s"}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    await update.message.reply_text("✅ تم التحميل، الملف محفوظ.")

# ========= 8. الرد على الكلمات المفتاحية =========
async def keyword_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()
    if "مرحبا" in text:
        await update.message.reply_text("🌹 مرحباً بك! كيف أقدر أساعدك اليوم؟")
    elif "ملخص" in text:
        await update.message.reply_text("📚 أرسل لي النص وأنا ألخصه لك.")
    elif "pdf" in text:
        await update.message.reply_text("📝 أرسل لي النص مع كلمة /pdf وأنا أحوله لك إلى ملف.")

# ========= 9. تشغيل البوت =========
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("pdf", to_pdf))
    app.add_handler(CommandHandler("ocr", ocr))
    app.add_handler(CommandHandler("stt", stt))
    app.add_handler(CommandHandler("image", image_gen))
    app.add_handler(CommandHandler("download", download))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), summarize))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), keyword_reply))

    app.run_polling()

if __name__ == "__main__":
    main()
