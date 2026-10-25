# ====================================================================
# KAGE DUB — RASMIY TELEGRAM ANIME BOT & BOSHQARUV TIZIMI
# Framework: aiogram 3.x (Asinxron va yuqori tezlikdagi Telegram Bot)
# O'rnatish: pip install -r requirements.txt
#
# RENDER SOZLAMALARI:
#  - Build Command: pip install -r requirements.txt
#  - Start Command: python bot.py
# ====================================================================

import asyncio
import logging
import os
import random
from typing import List, Dict, Set
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
# Render muhitidan tokenni o'qish uchun:
BOT_TOKEN = os.environ.get("BOT_TOKEN")

# Egasi (Owner) Telegram ID
OWNER_ID = 8318241400

# Majburiy obuna va postlar tashlanadigan rasmiy kanal
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

# Adminlar ro'yxati (RBAC) - Faqat Owner yangi admin qo'sha yoki o'chira oladi
ADMINS: Dict[int, dict] = {
    OWNER_ID: {"name": "Kage Boss (Egasi)", "role": "owner"}
}

# Bot foydalanuvchilari ID lari (post tarqatish uchun)
BOT_USERS: Set[int] = set()

# Anime ma'lumotlar bazasi (Katalog)
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
        "title": "Iblislar Qotili (Demon Slayer: Hashira Training)",
        "genres": "Ekshn, Tarixiy, Fentezi",
        "year": 2024,
        "rating": 8.9,
        "dub": "Kage Dub (Azizbek & Farrux)",
        "desc": "Tanjirou va do'stlari eng kuchli Hashiralar bilan shafqatsiz jangga tayyorgarlik ko'rish uchun mashg'ulotlarga kirishadilar.",
        "poster": "https://images.unsplash.com/photo-1607604276583-eef5d076aa5f?w=600",
        "episodes": [
            {"ep": 1, "link": "https://t.me/kagedub1/103_1"}
        ]
    },
    104: {
        "title": "Titanlar Hujumi (Attack on Titan: The Final Season)",
        "genres": "Harbiy, Psixologik, Drama",
        "year": 2023,
        "rating": 9.4,
        "dub": "Kage Dub (Sardor & Ziyoda)",
        "desc": "Eren Yeager insoniyatning ozodligi uchun halokatli devor titanlarini harakatga keltiradi.",
        "poster": "https://images.unsplash.com/photo-1563089145-599997674d42?w=600",
        "episodes": [
            {"ep": 1, "link": "https://t.me/kagedub1/104_1"}
        ]
    },
    105: {
        "title": "Bleach: Ming Yillik Qonli Urush (Thousand-Year Blood War)",
        "genres": "Ekshn, Shonen, G'ayritabiiy",
        "year": 2024,
        "rating": 9.1,
        "dub": "Kage Dub (Temur & Shahnoza)",
        "desc": "Qadimgi dushman Kvinsilar Yaxve boshchiligida Ruhlar Jamiyatiga misli ko'rilmagan hujum boshlaydilar.",
        "poster": "https://images.unsplash.com/photo-1534447677768-be436bb09401?w=600",
        "episodes": [
            {"ep": 1, "link": "https://t.me/kagedub1/105_1"}
        ]
    }
}

# ==================== BOT VA DISPATCHER ====================
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# ==================== FSM HOLATLAR ====================
class PostStates(StatesGroup):
    waiting_for_content = State()
    waiting_for_buttons = State()
    confirm_broadcast = State()

class SearchStates(StatesGroup):
    waiting_for_name = State()

# ==================== YORDAMCHI FUNKSIYALAR ====================
async def check_user_subscription(user_id: int) -> bool:
    if user_id == OWNER_ID or user_id in ADMINS:
        return True

    for ch in CHANNELS:
        try:
            member = await bot.get_chat_member(chat_id=ch["id"], user_id=user_id)
            if not isinstance(member, (ChatMemberOwner, ChatMemberAdministrator, ChatMemberMember)):
                return False
        except Exception as e:
            logging.error(f"Kanal obunasini tekshirishda xato ({ch['id']}): {e}")
            continue
    return True

def get_subscription_keyboard() -> InlineKeyboardMarkup:
    buttons = []
    for ch in CHANNELS:
        buttons.append([InlineKeyboardButton(text=f"📢 {ch['name']} ga a'zo bo'lish", url=ch["link"])])
    
    buttons.append([InlineKeyboardButton(text="🔄 Obunani Tekshirish", callback_data="verify_subscription")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_main_keyboard(user_id: int) -> ReplyKeyboardMarkup:
    kb = [
        [KeyboardButton(text="🔍 Anime Qidirish"), KeyboardButton(text="🎲 Tasodifiy Anime")],
        [KeyboardButton(text="🔥 Top Animelar"), KeyboardButton(text="📂 Janrlar")],
        [KeyboardButton(text="ℹ️ Bot Haqida")]
    ]
    if user_id == OWNER_ID or user_id in ADMINS:
        kb.append([KeyboardButton(text="⚙️ Admin Panel"), KeyboardButton(text="📢 Post Tayyorlash")])
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

def get_anime_card_keyboard(code: int) -> InlineKeyboardMarkup:
    anime = ANIME_DATABASE.get(code)
    buttons = []
    
    if anime and "episodes" in anime:
        ep_buttons = []
        for ep in anime["episodes"][:4]:
            ep_buttons.append(InlineKeyboardButton(text=f"▶️ {ep['ep']}-qism", url=ep["link"]))
        if ep_buttons:
            buttons.append(ep_buttons)
            
    buttons.append([
        InlineKeyboardButton(text="📺 Kanalda Ko'rish", url=CHANNEL_LINK),
        InlineKeyboardButton(text="📥 Barcha Qismlar", url=f"{CHANNEL_LINK}/{code}")
    ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

# ==================== HANDLERLAR (BOT BUYRUQLARI) ====================

@dp.message(CommandStart())
async def cmd_start(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    BOT_USERS.add(user_id)
    await state.clear()

    # 1. Majburiy obunani tekshirish
    is_subscribed = await check_user_subscription(user_id)
    if not is_subscribed:
        await message.answer(
            f"Salom, <b>{message.from_user.full_name}</b>!\n\n"
            f"🎬 <b>Kage Dub</b> rasmiy anime botiga xush kelibsiz.\n\n"
            f"⚠️ Botdan to'liq foydalanish uchun rasmiy kanalimizga a'zo bo'ling:\n"
            f"👉 <b>{CHANNEL_USERNAME}</b>\n\n"
            f"A'zo bo'lgach, quyidagi <b>'Obunani Tekshirish'</b> tugmasini bosing:",
            parse_mode="HTML",
            reply_markup=get_subscription_keyboard()
        )
        return

    role_badge = "👑 Bot Egasi (Owner)" if user_id == OWNER_ID else ("⚡ Admin" if user_id in ADMINS else "👤 Muxlis")
    
    await message.answer(
        f"Xush kelibsiz, <b>{message.from_user.full_name}</b>!\n"
        f"Maqomingiz: <b>{role_badge}</b>\n\n"
        f"Kage Dub boti orqali eng sara animelarni o'zbek tilida yuqori sifatda tomosha qiling va yuklab oling.\n\n"
        f"👇 Anime topish uchun anime kodi (masalan: <code>101</code>) yoki quyidagi menyudan foydalaning:",
        parse_mode="HTML",
        reply_markup=get_main_keyboard(user_id)
    )

@dp.callback_query(F.data == "verify_subscription")
async def callback_verify_sub(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    is_sub = await check_user_subscription(user_id)
    
    if is_sub:
        await callback.message.delete()
        await callback.message.answer(
            "🎉 <b>Tabriklaymiz! Obuna tasdiqlandi.</b>\n\nEndi botning barcha imkoniyatlaridan bemalol foydalanishingiz mumkin!",
            parse_mode="HTML",
            reply_markup=get_main_keyboard(user_id)
        )
    else:
        await callback.answer("❌ Hali kanalimizga obuna bo'lmadingiz! Iltimos, oldin kanalga a'zo bo'ling.", show_alert=True)

@dp.message(F.text.regexp(r'^\d{3,4}$'))
async def handle_anime_code(message: types.Message):
    user_id = message.from_user.id
    if not await check_user_subscription(user_id):
        await message.answer("⚠️ Botdan foydalanish uchun rasmiy kanalga a'zo bo'ling!", reply_markup=get_subscription_keyboard())
        return

    code = int(message.text.strip())
    anime = ANIME_DATABASE.get(code)
    
    if not anime:
        await message.answer(
            f"❌ <b>{code}</b> raqamli anime ma'lumotlar bazasida topilmadi!\n"
            f"Iltimos, kodni to'g'ri kiritganingizga ishonch hosil qiling.",
            parse_mode="HTML"
        )
        return

    caption = (
        f"🎬 <b>{anime['title']}</b>\n"
        f"🔢 Kod: <code>{code}</code>\n"
        f"⭐ Reyting: <b>{anime['rating']} / 10</b>\n"
        f"📅 Yil: {anime['year']}\n"
        f"🎭 Janrlar: {anime['genres']}\n"
        f"🎙️ Dublyaj: <b>{anime['dub']}</b>\n\n"
        f"📝 <i>{anime['desc']}</i>\n\n"
        f"📢 Rasmiy kanal: {CHANNEL_USERNAME}"
    )

    try:
        await message.answer_photo(
            photo=anime["poster"],
            caption=caption,
            parse_mode="HTML",
            reply_markup=get_anime_card_keyboard(code)
        )
    except Exception:
        await message.answer(
            caption,
            parse_mode="HTML",
            reply_markup=get_anime_card_keyboard(code)
        )

@dp.message(F.text == "🔍 Anime Qidirish")
async def menu_search(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    if not await check_user_subscription(user_id):
        await message.answer("⚠️ Botdan foydalanish uchun kanalga a'zo bo'ling!", reply_markup=get_subscription_keyboard())
        return

    await state.set_state(SearchStates.waiting_for_name)
    await message.answer("🔎 Qidirayotgan anime nomini yoki kalit so'zni yozib yuboring (yoki bekor qilish uchun /cancel):")

@dp.message(SearchStates.waiting_for_name)
async def process_search_name(message: types.Message, state: FSMContext):
    query = message.text.lower().strip()
    await state.clear()
    
    matches = []
    for code, anime in ANIME_DATABASE.items():
        if query in anime["title"].lower() or query in anime["genres"].lower():
            matches.append((code, anime))
            
    if not matches:
        await message.answer(f"❌ '{message.text}' so'rovi bo'yicha hech qanday anime topilmadi.")
        return

    kb_buttons = []
    text = f"🔎 <b>'{message.text}'</b> bo'yicha topilgan animelar:\n\n"
    for code, anime in matches[:10]:
        text += f"🔹 <b>{anime['title']}</b> (Kod: <code>{code}</code>)\n"
        kb_buttons.append([InlineKeyboardButton(text=f"🎬 {anime['title']} (Kod: {code})", callback_data=f"show_anime_{code}")])

    await message.answer(text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(inline_keyboard=kb_buttons))

@dp.callback_query(F.data.startswith("show_anime_"))
async def callback_show_anime(callback: types.CallbackQuery):
    code = int(callback.data.replace("show_anime_", ""))
    anime = ANIME_DATABASE.get(code)
    if not anime:
        await callback.answer("Anime topilmadi!", show_alert=True)
        return

    caption = (
        f"🎬 <b>{anime['title']}</b>\n"
        f"🔢 Kod: <code>{code}</code>\n"
        f"⭐ Reyting: <b>{anime['rating']} / 10</b>\n"
        f"📅 Yil: {anime['year']}\n"
        f"🎙️ Dublyaj: <b>{anime['dub']}</b>\n\n"
        f"📝 <i>{anime['desc']}</i>"
    )
    await callback.message.answer_photo(
        photo=anime["poster"],
        caption=caption,
        parse_mode="HTML",
        reply_markup=get_anime_card_keyboard(code)
    )
    await callback.answer()

@dp.message(F.text == "🎲 Tasodifiy Anime")
async def menu_random_anime(message: types.Message):
    user_id = message.from_user.id
    if not await check_user_subscription(user_id):
        await message.answer("⚠️ Botdan foydalanish uchun kanalga a'zo bo'ling!", reply_markup=get_subscription_keyboard())
        return

    code = random.choice(list(ANIME_DATABASE.keys()))
    anime = ANIME_DATABASE[code]
    
    caption = (
        f"🎲 <b>Tasodifiy Anime:</b>\n\n"
        f"🎬 <b>{anime['title']}</b>\n"
        f"🔢 Kod: <code>{code}</code>\n"
        f"⭐ Reyting: <b>{anime['rating']} / 10</b>\n"
        f"🎙️ Dub: <b>{anime['dub']}</b>\n\n"
        f"📝 <i>{anime['desc']}</i>"
    )
    await message.answer_photo(
        photo=anime["poster"],
        caption=caption,
        parse_mode="HTML",
        reply_markup=get_anime_card_keyboard(code)
    )

@dp.message(F.text == "🔥 Top Animelar")
async def menu_top_anime(message: types.Message):
    sorted_animes = sorted(ANIME_DATABASE.items(), key=lambda x: x[1]["rating"], reverse=True)
    text = "🔥 <b>KAGE DUB — ENG REYTINGI BALAND ANIMELAR:</b>\n\n"
    buttons = []
    
    for idx, (code, anime) in enumerate(sorted_animes[:5], 1):
        text += f"{idx}. <b>{anime['title']}</b>\n   ⭐ {anime['rating']} | Kod: <code>{code}</code> | {anime['genres']}\n\n"
        buttons.append([InlineKeyboardButton(text=f"{idx}. {anime['title']} (Kod: {code})", callback_data=f"show_anime_{code}")])

    await message.answer(text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))

@dp.message(F.text == "📂 Janrlar")
async def menu_genres(message: types.Message):
    genres = ["Ekshn", "Shonen", "Fentezi", "Sehr", "Psixologik", "Drama"]
    buttons = []
    for g in genres:
        buttons.append([InlineKeyboardButton(text=f"📁 {g}", callback_data=f"genre_{g}")])
        
    await message.answer("📂 <b>Quyidagi janrlardan birini tanlang:</b>", parse_mode="HTML", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))

@dp.callback_query(F.data.startswith("genre_"))
async def callback_genre(callback: types.CallbackQuery):
    genre = callback.data.replace("genre_", "")
    matches = [(c, a) for c, a in ANIME_DATABASE.items() if genre.lower() in a["genres"].lower()]
    
    if not matches:
        await callback.answer(f"{genre} janrida anime hozircha yo'q", show_alert=True)
        return

    buttons = []
    text = f"📁 <b>{genre}</b> janridagi animelar:\n\n"
    for code, anime in matches:
        text += f"🔹 {anime['title']} (Kod: <code>{code}</code>)\n"
        buttons.append([InlineKeyboardButton(text=f"🎬 {anime['title']}", callback_data=f"show_anime_{code}")])
        
    await callback.message.edit_text(text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))
    await callback.answer()

@dp.message(F.text == "ℹ️ Bot Haqida")
async def menu_about(message: types.Message):
    await message.answer(
        f"🎙️ <b>Kage Dub</b> — Rasmiy Anime & Ovoz berish platformasi boti.\n\n"
        f"👑 <b>Bot Egasi (Owner):</b> {OWNER_ID}\n"
        f"📢 <b>Rasmiy Kanal:</b> {CHANNEL_USERNAME} ({CHANNEL_ID})\n"
        f"⚡ <b>Tezkor Kod Qidiruvi:</b> Har qanday anime kodini botga yuboring (masalan: 101)\n\n"
        f"Biz bilan eng so'nggi animelarni o'zbek tilida yuqori sifatda tomosha qiling!",
        parse_mode="HTML"
    )

# ==================== RBAC: ADMIN VA OWNER BOSHQARUVI ====================

@dp.message(Command("admins"))
async def cmd_admins(message: types.Message):
    if message.from_user.id != OWNER_ID:
        await message.answer("❌ Bu buyruq faqat Bot Egasiga (Owner) tegishli!")
        return

    text = "👑 <b>KAGE DUB BOT MA'MURIYATI (RBAC):</b>\n\n"
    text += f"👑 <b>Owner:</b> <code>{OWNER_ID}</code> (Kage Boss)\n\n"
    text += "⚡ <b>Yordamchi Adminlar:</b>\n"
    
    admin_count = 0
    for uid, info in ADMINS.items():
        if uid != OWNER_ID:
            admin_count += 1
            text += f"{admin_count}. {info['name']} — ID: <code>{uid}</code>\n"
            
    if admin_count == 0:
        text += "<i>Hozircha yordamchi adminlar belgilanmagan.</i>\n"

    text += "\n💡 Admin qo'shish uchun: <code>/addadmin TELEGRAM_ID Ismi</code>\n"
    text += "💡 Adminni bo'shatish uchun: <code>/deladmin TELEGRAM_ID</code>"

    await message.answer(text, parse_mode="HTML")

@dp.message(Command("addadmin"))
async def cmd_addadmin(message: types.Message):
    if message.from_user.id != OWNER_ID:
        await message.answer("❌ Faqat Bot Egasi (Owner) yangi admin tayinlashi mumkin!")
        return

    parts = message.text.split(maxsplit=2)
    if len(parts) < 2:
        await message.answer("⚠️ Foydalanish: <code>/addadmin TELEGRAM_ID Ismi</code>\nMisol: <code>/addadmin 123456789 Ali</code>", parse_mode="HTML")
        return

    try:
        new_id = int(parts[1])
        name = parts[2] if len(parts) > 2 else f"Admin {new_id}"
        ADMINS[new_id] = {"name": name, "role": "admin"}
        await message.answer(f"✅ Yangi admin tayinlandi:\n👤 <b>{name}</b> (ID: <code>{new_id}</code>)", parse_mode="HTML")
    except ValueError:
        await message.answer("❌ Xatolik: Telegram ID faqat sonlardan iborat bo'lishi kerak!")

@dp.message(Command("deladmin"))
async def cmd_deladmin(message: types.Message):
    if message.from_user.id != OWNER_ID:
        await message.answer("❌ Faqat Bot Egasi (Owner) adminlarni o'chira oladi!")
        return

    parts = message.text.split()
    if len(parts) < 2:
        await message.answer("⚠️ Foydalanish: <code>/deladmin TELEGRAM_ID</code>", parse_mode="HTML")
        return

    try:
        target_id = int(parts[1])
        if target_id == OWNER_ID:
            await message.answer("❌ Bot Egasini (Owner) o'chirib bo'lmaydi!")
            return
        if target_id in ADMINS:
            del ADMINS[target_id]
            await message.answer(f"✅ <code>{target_id}</code> IDli admin bo'shatildi.", parse_mode="HTML")
        else:
            await message.answer("❌ Bunday admin topilmadi.")
    except ValueError:
        await message.answer("❌ ID noto'g'ri kiritildi.")

# ==================== POST BUILDER ====================

@dp.message(F.text == "📢 Post Tayyorlash")
@dp.message(Command("post"))
async def start_post_builder(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    if user_id != OWNER_ID and user_id not in ADMINS:
        await message.answer("❌ Faqat adminlar post tayyorlay oladi!")
        return

    await state.set_state(PostStates.waiting_for_content)
    await message.answer(
        "📝 <b>PROFESSIONAL POST TAYYORLASH (Post Builder):</b>\n\n"
        "1-qadam: Kanalga va bot a'zolariga yuboriladigan postni (Rasm/Video bilan yoki oddiy matn shaklida) yuboring.\n\n"
        "<i>Bekor qilish uchun /cancel deb yozing.</i>",
        parse_mode="HTML"
    )

@dp.message(Command("cancel"))
async def cancel_handler(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("❌ Amaliyot bekor qilindi.", reply_markup=get_main_keyboard(message.from_user.id))

@dp.message(PostStates.waiting_for_content)
async def process_post_content(message: types.Message, state: FSMContext):
    data = {}
    if message.photo:
        data["type"] = "photo"
        data["file_id"] = message.photo[-1].file_id
        data["caption"] = message.caption or ""
    elif message.video:
        data["type"] = "video"
        data["file_id"] = message.video.file_id
        data["caption"] = message.caption or ""
    else:
        data["type"] = "text"
        data["text"] = message.text

    await state.update_data(post_data=data)
    await state.set_state(PostStates.waiting_for_buttons)
    
    await message.answer(
        "2-qadam: Post ostiga Inline tugmalar qo'shasizmi?\n\n"
        "Agar tugma qo'shmoqchi bo'lsangiz quyidagi formatda yozing:\n"
        "<code>Ko'rish 📺 | https://t.me/kagedub1\nYuklab olish 📥 | https://t.me/kagedub1</code>\n\n"
        "Agar tugma kerak bo'lmasa <b>'Yo'q'</b> deb yozing.",
        parse_mode="HTML"
    )

@dp.message(PostStates.waiting_for_buttons)
async def process_post_buttons(message: types.Message, state: FSMContext):
    reply_text = message.text.strip()
    inline_buttons = []
    
    if reply_text.lower() != "yo'q" and "|" in reply_text:
        lines = reply_text.split("\n")
        for line in lines:
            if "|" in line:
                btn_name, btn_url = line.split("|", 1)
                inline_buttons.append([InlineKeyboardButton(text=btn_name.strip(), url=btn_url.strip())])

    await state.update_data(inline_buttons=inline_buttons)
    await state.set_state(PostStates.confirm_broadcast)
    
    user_data = await state.get_data()
    post_data = user_data["post_data"]
    kb = InlineKeyboardMarkup(inline_keyboard=inline_buttons) if inline_buttons else None
    
    await message.answer("👀 <b>POSTINGIZ KO'RINISHI (PREVIEW):</b>", parse_mode="HTML")
    
    if post_data["type"] == "photo":
        await message.answer_photo(photo=post_data["file_id"], caption=post_data.get("caption"), reply_markup=kb)
    elif post_data["type"] == "video":
        await message.answer_video(video=post_data["file_id"], caption=post_data.get("caption"), reply_markup=kb)
    else:
        await message.answer(text=post_data.get("text", ""), reply_markup=kb)

    confirm_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📢 Kanalga Jo'natish", callback_data="send_to_channel")],
        [InlineKeyboardButton(text="👥 Barcha Bot Foydalanuvchilariga Tarqatish", callback_data="broadcast_users")],
        [InlineKeyboardButton(text="🚀 Kanal va Foydalanuvchilarga Tarqatish", callback_data="send_both")],
        [InlineKeyboardButton(text="❌ Bekor Qilish", callback_data="cancel_post")]
    ])
    
    await message.answer("Qayerga tarqatmoqchisiz?", reply_markup=confirm_kb)

@dp.callback_query(PostStates.confirm_broadcast, F.data == "cancel_post")
async def callback_cancel_post(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.delete()
    await callback.message.answer("❌ Post bekor qilindi.")

@dp.callback_query(PostStates.confirm_broadcast, F.data.in_(["send_to_channel", "broadcast_users", "send_both"]))
async def callback_execute_post(callback: types.CallbackQuery, state: FSMContext):
    action = callback.data
    user_data = await state.get_data()
    post_data = user_data.get("post_data")
    buttons = user_data.get("inline_buttons", [])
    kb = InlineKeyboardMarkup(inline_keyboard=buttons) if buttons else None
    
    await callback.message.delete()
    status_msg = await callback.message.answer("⏳ Post jo'natilmoqda...")

    if action in ["send_to_channel", "send_both"]:
        try:
            if post_data["type"] == "photo":
                await bot.send_photo(chat_id=CHANNEL_ID, photo=post_data["file_id"], caption=post_data.get("caption"), reply_markup=kb)
            elif post_data["type"] == "video":
                await bot.send_video(chat_id=CHANNEL_ID, video=post_data["file_id"], caption=post_data.get("caption"), reply_markup=kb)
            else:
                await bot.send_message(chat_id=CHANNEL_ID, text=post_data.get("text"), reply_markup=kb)
        except Exception as e:
            logging.error(f"Kanalga jo'natishda xatolik: {e}")

    if action in ["broadcast_users", "send_both"]:
        success_count = 0
        for uid in list(BOT_USERS):
            try:
                if post_data["type"] == "photo":
                    await bot.send_photo(chat_id=uid, photo=post_data["file_id"], caption=post_data.get("caption"), reply_markup=kb)
                elif post_data["type"] == "video":
                    await bot.send_video(chat_id=uid, video=post_data["file_id"], caption=post_data.get("caption"), reply_markup=kb)
                else:
                    await bot.send_message(chat_id=uid, text=post_data.get("text"), reply_markup=kb)
                success_count += 1
                await asyncio.sleep(0.04)
            except Exception:
                pass

    await status_msg.edit_text("✅ <b>Post muvaffaqiyatli tarqatildi!</b>", parse_mode="HTML")
    await state.clear()

# ==================== RENDER WEB SERVICE PORT SERVERI ====================
async def health_check_handler(request):
    return web.Response(text="Kage Dub Telegram Bot is running! Status: OK 200")

async def start_render_health_server():
    port_env = os.environ.get("PORT")
    if port_env:
        try:
            port = int(port_env)
            app = web.Application()
            app.router.add_get("/", health_check_handler)
            app.router.add_get("/health", health_check_handler)
            runner = web.AppRunner(app)
            await runner.setup()
            site = web.TCPSite(runner, "0.0.0.0", port)
            await site.start()
            print(f"🌐 Render Web Service serveri {port}-portda muvaffaqiyatli ishga tushdi!")
        except Exception as e:
            logging.warning(f"Render port serveri ochilmadi: {e}")

# ==================== ASOSIY MAIN FUNKSIYASI ====================
async def main():
    logging.basicConfig(level=logging.INFO)
    print("=" * 60)
    print("🚀 KAGE DUB TELEGRAM BOT ISHGA TUSHMOQDA...")
    print(f"👑 Owner ID: {OWNER_ID}")
    print(f"📢 Kanal ID: {CHANNEL_ID} ({CHANNEL_USERNAME})")
    print("=" * 60)

    await start_render_health_server()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
