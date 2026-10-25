import os
import asyncio
import logging
from typing import Dict, Set
from aiohttp import web
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, CommandStart
from aiogram.types import (
    InlineKeyboardMarkup, 
    InlineKeyboardButton, 
    ReplyKeyboardMarkup, 
    KeyboardButton,
    ChatMemberOwner,
    ChatMemberAdministrator,
    ChatMemberMember
)
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

# ==================== SOZLAMALAR ====================
BOT_TOKEN = "8783907306:AAF0Apxpq6DdEf5H34gY8s0-daZUNRbMuuI"

OWNER_ID = 8318241400
CHANNEL_ID = -1003852596133
CHANNEL_USERNAME = "@kagedub1"
CHANNEL_LINK = "https://t.me/kagedub1"

CHANNELS = [
    {
        "name": "Kage Dub | Rasmiy Kanal",
        "id": CHANNEL_ID,
        "username": CHANNEL_USERNAME,
        "link": CHANNEL_LINK
    }
]

ADMINS: Dict[int, dict] = {
    OWNER_ID: {"name": "Kage Boss (Egasi)", "role": "owner"}
}

BOT_USERS: Set[int] = set()

ANIME_DATABASE = {
    101: {
        "title": "Yakka o'zi Daraja Oshirish (Solo Leveling)",
        "genres": "Ekshn, Fentezi, Shonen, Super Kuch",
        "year": 2024,
        "rating": 9.2,
        "dub": "Kage Dub (Alisher & Kamola)",
        "desc": "Zaif ovchi Jin-Vu sirli qaltis ibodatxonadagi fojiadan so'ng tizim orqali darajasini cheksiz oshirishga kirishadi va dunyodagi eng qudratli S-darajali jangchiga aylanadi.",
        "poster": "https://images.unsplash.com/photo-1578632767115-351597cf2477?w=600",
        "episodes": [
            {"ep": 1, "link": "https://t.me/kagedub1/101_1"},
            {"ep": 2, "link": "https://t.me/kagedub1/101_2"},
            {"ep": 3, "link": "https://t.me/kagedub1/101_3"},
            {"ep": 4, "link": "https://t.me/kagedub1/101_4"}
        ]
    },
    102: {
        "title": "Sehrli Jang (Jujutsu Kaisen)",
        "genres": "Ekshn, Sehr, Shonen",
        "year": 2023,
        "rating": 9.0,
        "dub": "Kage Dub (Rustam & Dilshod)",
        "desc": "Yuji Itadori lanatlangan qonxo'r Sukunaning barmog'ini yutib yuboradi. Gojo Satoru bilan birga la'natlar dunyosini tozalash janggiga kirishadi.",
        "poster": "https://images.unsplash.com/photo-1534447677768-be436bb09401?w=600",
        "episodes": [
            {"ep": 1, "link": "https://t.me/kagedub1/102_1"},
            {"ep": 2, "link": "https://t.me/kagedub1/102_2"}
        ]
    },
    103: {
        "title": "Iblislar Qotili (Demon Slayer)",
        "genres": "Ekshn, Tarixiy, Fentezi",
        "year": 2024,
        "rating": 8.9,
        "dub": "Kage Dub (Azizbek & Farrux)",
        "desc": "Tanjirou va do'stlari eng kuchli Hashiralar bilan shafqatsiz jangga tayyorgarlik ko'rish uchun mashg'ulotlarga kirishadilar.",
        "poster": "https://images.unsplash.com/photo-1607604276583-eef5d076aa5f?w=600",
        "episodes": [
            {"ep": 1, "link": "https://t.me/kagedub1/103_1"}
        ]
    }
}

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

def get_main_menu_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🔍 Anime Qidirish"), KeyboardButton(text="🔢 Kod orqali")],
            [KeyboardButton(text="🎲 Tasodifiy Anime"), KeyboardButton(text="🔥 Top Animelar")],
            [KeyboardButton(text="📢 Rasmiy Kanal"), KeyboardButton(text="ℹ️ Bot Haqida")]
        ],
        resize_keyboard=True
    )

def get_sub_channels_keyboard():
    buttons = [
        [InlineKeyboardButton(text="📢 Kage Dub Rasmiy Kanal", url=CHANNEL_LINK)],
        [InlineKeyboardButton(text="✅ Obunani Tekshirish", callback_data="check_subscription")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

async def check_user_subscription(user_id: int, bot_instance: Bot) -> bool:
    try:
        member = await bot_instance.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        if isinstance(member, (ChatMemberOwner, ChatMemberAdministrator, ChatMemberMember)):
            return True
        return False
    except Exception as e:
        logging.warning(f"Kanal obunasi tekshirilmadi: {e}")
        return True

@dp.message(CommandStart())
async def command_start_handler(message: types.Message):
    user_id = message.from_user.id
    BOT_USERS.add(user_id)

    is_sub = await check_user_subscription(user_id, bot)
    if not is_sub:
        await message.answer(
            f"Assalomu alaykum, <b>{message.from_user.full_name}</b>! 🌟\n\n"
            f"⚠️ <b>DIQQAT:</b> Botdan to'liq foydalanish va animelarni bepul tomosha qilish uchun "
            f"rasmiy kanalimiz {CHANNEL_USERNAME} ga obuna bo'lishingiz shart!\n\n"
            f"Obuna bo'lib, pastdagi <b>«Tekshirish ✅»</b> tugmasini bosing:",
            parse_mode="HTML",
            reply_markup=get_sub_channels_keyboard()
        )
        return

    await message.answer(
        f"🎉 <b>Xush kelibsiz, {message.from_user.full_name}!</b>\n\n"
        f"Kage Dub rasmiy anime botidasiz! Anime kodini yozing (masalan: <code>101</code>):",
        parse_mode="HTML",
        reply_markup=get_main_menu_keyboard()
    )

@dp.callback_query(F.data == "check_subscription")
async def verify_sub_callback(query: types.CallbackQuery):
    user_id = query.from_user.id
    is_sub = await check_user_subscription(user_id, bot)

    if is_sub:
        try:
            await query.message.delete()
        except Exception:
            pass
        await query.message.answer(
            "✅ <b>Obuna muvaffaqiyatli tasdiqlandi!</b> Barcha animelar ochildi.",
            parse_mode="HTML",
            reply_markup=get_main_menu_keyboard()
        )
    else:
        await query.answer(
            f"❌ Siz hali {CHANNEL_USERNAME} kanaliga a'zo emassiz!", 
            show_alert=True
        )

@dp.message(F.text.regexp(r"^\d{2,4}$"))
async def code_search_handler(message: types.Message):
    user_id = message.from_user.id
    BOT_USERS.add(user_id)

    if not await check_user_subscription(user_id, bot):
        await message.answer(
            f"⚠️ Botdan foydalanish uchun {CHANNEL_USERNAME} kanaliga obuna bo'ling!",
            reply_markup=get_sub_channels_keyboard()
        )
        return

    code = int(message.text)
    anime = ANIME_DATABASE.get(code)

    if not anime:
        await message.answer(f"❌ <b>{code}</b>-raqamli anime bazada topilmadi.")
        return

    buttons = []
    ep_row = []
    for ep in anime.get("episodes", []):
        ep_row.append(InlineKeyboardButton(text=f"▶️ {ep['ep']}-qism", url=ep["link"]))
        if len(ep_row) == 2:
            buttons.append(ep_row)
            ep_row = []
    if ep_row:
        buttons.append(ep_row)

    buttons.append([
        InlineKeyboardButton(text="📢 Rasmiy Kanal", url=CHANNEL_LINK),
        InlineKeyboardButton(text="🚀 Ulashish", url=f"https://t.me/share/url?url={CHANNEL_LINK}")
    ])

    caption = (
        f"🎬 <b>{anime['title']}</b>\n\n"
        f"🔢 <b>Kodi:</b> <code>{code}</code>\n"
        f"⭐ <b>Reyting:</b> {anime['rating']} / 10 | 📅 <b>Yili:</b> {anime['year']}\n"
        f"🎭 <b>Janrlar:</b> {anime['genres']}\n"
        f"🎙️ <b>Dublyaj:</b> {anime['dub']}\n\n"
        f"📖 <b>Mazmuni:</b> {anime['desc']}"
    )

    await message.answer_photo(
        photo=anime["poster"],
        caption=caption,
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
    )

@dp.message(F.text == "🎲 Tasodifiy Anime")
async def random_anime_handler(message: types.Message):
    import random
    code = random.choice(list(ANIME_DATABASE.keys()))
    message.text = str(code)
    await code_search_handler(message)

@dp.message(F.text == "🔥 Top Animelar")
async def top_anime_handler(message: types.Message):
    buttons = []
    for code, a in sorted(ANIME_DATABASE.items(), key=lambda x: x[1]["rating"], reverse=True)[:5]:
        buttons.append([InlineKeyboardButton(text=f"⭐ {a['rating']} | [{code}] {a['title']}", callback_data=f"anime_{code}")])

    await message.answer(
        "🔥 <b>Kage Dub — Saralangan TOP Animelar:</b>",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
    )

@dp.callback_query(F.data.startswith("anime_"))
async def anime_callback_handler(query: types.CallbackQuery):
    code = int(query.data.split("_")[1])
    query.message.text = str(code)
    await code_search_handler(query.message)

@dp.message(F.text == "📢 Rasmiy Kanal")
async def channel_info_handler(message: types.Message):
    await message.answer(f"📢 Rasmiy kanal: {CHANNEL_LINK}")

@dp.message(F.text == "ℹ️ Bot Haqida")
async def about_bot_handler(message: types.Message):
    await message.answer("ℹ️ Kage Dub Rasmiy Anime Boti. Barcha animelar bepul!")

@dp.message(Command("admins"))
async def list_admins_handler(message: types.Message):
    if message.from_user.id != OWNER_ID:
        return
    text = "🛡️ <b>Adminlar:</b>\n"
    for uid, data in ADMINS.items():
        text += f"• <code>{uid}</code> — {data['name']}\n"
    await message.answer(text, parse_mode="HTML")

# --- HEALTH CHECK SERVER ---
async def health_check_handler(request):
    return web.Response(text="Bot is running smoothly!", status=200)

async def start_web_server():
    app = web.Application()
    app.router.add_get("/", health_check_handler)
    app.router.add_get("/health", health_check_handler)
    
    port = int(os.environ.get("PORT", 10000))
    runner = web.AppRunner(app)
    await runner.setup()
    await web.TCPSite(runner, "0.0.0.0", port).start()
    logging.info(f"Render Web Service serveri {port}-portda ishga tushdi!")

async def main():
    logging.basicConfig(level=logging.INFO)
    print("🚀 KAGE DUB TELEGRAM BOT ISHGA TUSHMOQDA...")
    
    await start_web_server()
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Bot to'xtatildi!")
