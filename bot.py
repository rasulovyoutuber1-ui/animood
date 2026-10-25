"""
====================================================================
KAGE DUB — RASMIY TELEGRAM ANIME BOT & BOSHQARUV TIZIMI[cite: 1]
Framework: aiogram 3.x (Asinxron va yuqori tezlikdagi Telegram Bot)[cite: 1]
O'rnatish: pip install aiogram aiohttp[cite: 1]

SOZLANGAN PARAMETRLAR:
 - Bot Egasi (Owner ID): 8318241400[cite: 1]
 - Majburiy Obuna va Post Kanali ID: -1003852596133[cite: 1]
 - Kanal Username: @kagedub1 (https://t.me/kagedub1)[cite: 1]
 - VIP & AI: Butunlay olib tashlangan (100% toza va bepul anime boti)[cite: 1]
====================================================================
"""

import asyncio
import logging
from typing import List, Dict, Set
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
BOT_TOKEN = "8732171636:AAGc0HkdTpjKOlpVjplNeRpvSZBOZa-53EM"  # @BotFather dan olingan bot tokeni[cite: 1]

# Egasi (Owner) Telegram ID
OWNER_ID = 8318241400[cite: 1]

# Majburiy obuna va postlar tashlanadigan rasmiy kanal
CHANNEL_ID = -1003852596133[cite: 1]
CHANNEL_USERNAME = "@kagedub1"[cite: 1]
CHANNEL_LINK = "https://t.me/kagedub1"[cite: 1]

CHANNELS = [
    {
        "name": "Kage Dub | Rasmiy Kanal",
        "id": CHANNEL_ID,
        "username": CHANNEL_USERNAME,
        "link": CHANNEL_LINK
    }
]

# Adminlar bazasi (RBAC) - Faqat Owner yangi admin qo'sha oladi[cite: 1]
ADMINS: Dict[int, dict] = {
    OWNER_ID: {"name": "Kage Boss (Egasi)", "role": "owner"}
}

# Bot foydalanuvchilari bazasi (xabarlarni tarqatish uchun)
BOT_USERS: Set[int] = set()

# Anime ma'lumotlar bazasi (Katalog)
ANIME_DATABASE = {
    101: {
        "title": "Yakka o'zi Daraja Oshirish (Solo Leveling)",[cite: 1]
        "genres": "Ekshn, Fentezi, Shonen, Super Kuch",[cite: 1]
        "year": 2024,[cite: 1]
        "rating": 9.2,[cite: 1]
        "dub": "Kage Dub (Alisher & Kamola)",[cite: 1]
        "desc": "Zaif ovchi Jin-Vu sirli qaltis ibodatxonadagi fojiadan so'ng tizim orqali darajasini cheksiz oshirishga kirishadi va dunyodagi eng qudratli S-darajali jangchiga aylanadi.",[cite: 1]
        "poster": "https://images.unsplash.com/photo-1578632767115-351597cf2477?w=600",[cite: 1]
        "episodes": [
            {"ep": 1, "link": "https://t.me/kagedub1/101_1"},[cite: 1]
            {"ep": 2, "link": "https://t.me/kagedub1/101_2"},[cite: 1]
            {"ep": 3, "link": "https://t.me/kagedub1/101_3"},[cite: 1]
            {"ep": 4, "link": "https://t.me/kagedub1/101_4"}[cite: 1]
        ]
    },
    102: {
        "title": "Sehrli Jang (Jujutsu Kaisen)",[cite: 1]
        "genres": "Ekshn, Sehr, Shonen",[cite: 1]
        "year": 2023,[cite: 1]
        "rating": 9.0,[cite: 1]
        "dub": "Kage Dub (Rustam & Dilshod)",[cite: 1]
        "desc": "Yuji Itadori lanatlangan qonxo'r Sukunaning barmog'ini yutib yuboradi. Gojo Satoru bilan birga la'natlar dunyosini tozalash janggiga kirishadi.",[cite: 1]
        "poster": "https://images.unsplash.com/photo-1534447677768-be436bb09401?w=600",[cite: 1]
        "episodes": [
            {"ep": 1, "link": "https://t.me/kagedub1/102_1"},[cite: 1]
            {"ep": 2, "link": "https://t.me/kagedub1/102_2"}[cite: 1]
        ]
    },
    103: {
        "title": "Iblislar Qotili (Demon Slayer: Hashira Training)",[cite: 1]
        "genres": "Ekshn, Tarixiy, Fentezi",[cite: 1]
        "year": 2024,[cite: 1]
        "rating": 8.9,[cite: 1]
        "dub": "Kage Dub (Azizbek & Farrux)",[cite: 1]
        "desc": "Tanjirou va do'stlari eng kuchli Hashiralar bilan shafqatsiz jangga tayyorgarlik ko'rish uchun mashg'ulotlarga kirishadilar.",[cite: 1]
        "poster": "https://images.unsplash.com/photo-1607604276583-eef5d076aa5f?w=600",[cite: 1]
        "episodes": [
            {"ep": 1, "link": "https://t.me/kagedub1/103_1"}[cite: 1]
        ]
    },
    104: {
        "title": "Titanlar Hujumi (Attack on Titan: The Final Season)",[cite: 1]
        "genres": "Harbiy, Psixologik, Drama",[cite: 1]
        "year": 2023,[cite: 1]
        "rating": 9.4,[cite: 1]
        "dub": "Kage Dub (Sardor & Ziyoda)",[cite: 1]
        "desc": "Eren Yeager insoniyatning ozodligi uchun halokatli devor titanlarini harakatga keltiradi.",[cite: 1]
        "poster": "https://images.unsplash.com/photo-1563089145-599997674d42?w=600",[cite: 1]
        "episodes": [
            {"ep": 1, "link": "https://t.me/kagedub1/104_1"}[cite: 1]
        ]
    },
    105: {
        "title": "O'lim Daftari (Death Note)",[cite: 1]
        "genres": "Detektiv, Psixologik, Triller",[cite: 1]
        "year": 2006,[cite: 1]
        "rating": 9.3,[cite: 1]
        "dub": "Kage Dub Klassika",[cite: 1]
        "desc": "Yagami Layt shinigami daftarini topib, jinoyatchilarni jazolab yangi dunyo xudosi bo'lishni reja qiladi. Ammo L unga qarshi chiqadi.",[cite: 1]
        "poster": "https://images.unsplash.com/photo-1518709268805-4e9042af9f23?w=600",[cite: 1]
        "episodes": [
            {"ep": 1, "link": "https://t.me/kagedub1/105_1"},[cite: 1]
            {"ep": 2, "link": "https://t.me/kagedub1/105_2"}[cite: 1]
        ]
    }
}

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# --- KLAVIATURALAR ---
def get_main_menu_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🔍 Anime Qidirish"), KeyboardButton(text="🔢 Kod orqali")],
            [KeyboardButton(text="🎲 Tasodifiy Anime"), KeyboardButton(text="🔥 Top Animelar")],
            [KeyboardButton(text="🆕 Yangi Qismlar"), KeyboardButton(text="🎭 Janrlar")],
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

# --- 1. MAJBURIY OBUNA TEKSHIRUVI (-1003852596133) ---[cite: 1]
async def check_user_subscription(user_id: int, bot_instance: Bot) -> bool:
    try:
        member = await bot_instance.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        if isinstance(member, (ChatMemberOwner, ChatMemberAdministrator, ChatMemberMember)):
            return True
        return False
    except Exception as e:
        logging.warning(f"Kanal obunasi tekshirilmadi: {e}")
        return True

# --- 2. /start KOMANDASI ---
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
        f"Kage Dub rasmiy anime botidasiz! Barcha animelarimiz mutlaqo bepul va ochiq.\n\n"
        f"🔹 <b>Qanday foydalanasiz?</b>\n"
        f"• Anime kodini yozing (masalan: <code>101</code>)\n"
        f"• Yoki pastdagi menyudan kerakli bo'limni tanlang! 👇",
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
            f"❌ Siz hali {CHANNEL_USERNAME} kanaliga a'zo emassiz! Iltimos, kanalga a'zo bo'ling.", 
            show_alert=True
        )

# --- 3. KENGAYTIRILGAN ANIME QIDIRUV (KOD: 101, 102...) ---[cite: 1]
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
        await message.answer(f"❌ <b>{code}</b>-raqamli anime bazada topilmadi. Boshqa kod kiriting.")
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
        InlineKeyboardButton(text="🚀 Do'stlarga Ulashish", url=f"https://t.me/share/url?url={CHANNEL_LINK}")
    ])

    caption = (
        f"🎬 <b>{anime['title']}</b>\n\n"
        f"🔢 <b>Kodi:</b> <code>{code}</code>\n"
        f"⭐ <b>Reyting:</b> {anime['rating']} / 10 | 📅 <b>Yili:</b> {anime['year']}\n"
        f"🎭 <b>Janrlar:</b> {anime['genres']}\n"
        f"🎙️ <b>Dublyaj:</b> {anime['dub']}\n\n"
        f"📖 <b>Mazmuni:</b> {anime['desc']}\n\n"
        f"Tomosha qilish uchun pastdagi qismlardan birini tanlang! 👇"
    )

    await message.answer_photo(
        photo=anime["poster"],
        caption=caption,
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
    )

# --- 4. TASODIFIY, TOP DAN YANGI ANIMELAR ---
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
        "🔥 <b>Kage Dub — Eng Saralangan TOP Animelar:</b>",
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
    await message.answer(
        f"📢 <b>Kage Dub Rasmiy Kanali:</b>\n\n"
        f"Eng so'nggi premyeralar va yangiliklar kanalimizda e'lon qilinadi:\n"
        f"👉 {CHANNEL_LINK}",
        parse_mode="HTML"
    )

@dp.message(F.text == "ℹ️ Bot Haqida")
async def about_bot_handler(message: types.Message):
    await message.answer(
        f"ℹ️ <b>Kage Dub Rasmiy Anime Boti</b>\n\n"
        f"🎙️ Dublyaj: Kage Dub professional ovoz ustalari\n"
        f"🌐 Kanal: {CHANNEL_USERNAME}\n"
        f"👑 Egasi ID: <code>{OWNER_ID}</code>\n\n"
        f"Barcha animelar bepul va reklamasiz taqdim etiladi!",
        parse_mode="HTML"
    )

# --- 5. RBAC ADMINLAR BOSHQARUVI (FAQAT OWNER: 8318241400) ---[cite: 1]
@dp.message(Command("addadmin"))
async def add_admin_handler(message: types.Message):
    if message.from_user.id != OWNER_ID:
        await message.answer("🚫 <b>Ruxsat berilmadi!</b> Faqat Bot Egasi (Owner: 8318241400) yangi admin tayinlashi mumkin.", parse_mode="HTML")[cite: 1]
        return

    parts = message.text.split()
    if len(parts) < 2:
        await message.answer("⚠️ Foydalanish: <code>/addadmin &lt;telegram_id&gt; [ism]</code>", parse_mode="HTML")
        return

    try:
        new_id = int(parts[1])
        name = parts[2] if len(parts) > 2 else f"Admin_{new_id}"
        ADMINS[new_id] = {"name": name, "role": "admin"}
        await message.answer(f"✅ Yangi admin tayinlandi:\nID: <code>{new_id}</code>\nIsmi: {name}", parse_mode="HTML")
    except ValueError:
        await message.answer("❌ ID raqam bo'lishi kerak!")

@dp.message(Command("deladmin"))
async def del_admin_handler(message: types.Message):
    if message.from_user.id != OWNER_ID:
        await message.answer("🚫 Faqat Bot Egasi (Owner) adminni o'chira oladi!", parse_mode="HTML")
        return

    parts = message.text.split()
    if len(parts) < 2:
        await message.answer("⚠️ Foydalanish: <code>/deladmin &lt;telegram_id&gt;</code>", parse_mode="HTML")
        return

    target_id = int(parts[1])
    if target_id == OWNER_ID:
        await message.answer("❌ Bot Egasini (Owner) o'chirib bo'lmaydi!")
        return

    if target_id in ADMINS:
        del ADMINS[target_id]
        await message.answer(f"✅ Admin <code>{target_id}</code> lavozimidan ozod qilindi.", parse_mode="HTML")
    else:
        await message.answer("❌ Bu foydalanuvchi admin emas.")

@dp.message(Command("admins"))
async def list_admins_handler(message: types.Message):
    text = "🛡️ <b>Kage Dub Bot Adminlari:</b>\n\n"
    for uid, data in ADMINS.items():
        crown = "👑 (Egasi)" if data["role"] == "owner" else "🛡️ (Yordamchi Admin)"
        text += f"• <code>{uid}</code> — {data['name']} {crown}\n"
    await message.answer(text, parse_mode="HTML")

# --- 6. POST BUILDER & BROADCAST (-1003852596133 GA JO'NATISH) ---[cite: 1]
class PostBuilderState(StatesGroup):
    waiting_for_media = State()
    waiting_for_caption = State()

@dp.message(Command("post"))
async def start_post_builder(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    if user_id not in ADMINS:
        await message.answer("🚫 Bu buyruq faqat bot adminlari uchun!")
        return

    await state.set_state(PostBuilderState.waiting_for_media)
    await message.answer(
        "📝 <b>Post Builder rejimi:</b>\n\n"
        "Post uchun rasm yuboring (yoki rasmsiz davom etish uchun <code>/skip</code> deb yozing):",
        parse_mode="HTML"
    )

@dp.message(PostBuilderState.waiting_for_media)
async def process_media(message: types.Message, state: FSMContext):
    photo_id = message.photo[-1].file_id if message.photo else None
    await state.update_data(photo=photo_id)
    await state.set_state(PostBuilderState.waiting_for_caption)
    await message.answer("✍️ Endi post matnini (HTML formatida) yuboring:")

@dp.message(PostBuilderState.waiting_for_caption)
async def process_caption(message: types.Message, state: FSMContext):
    caption = message.html_text
    data = await state.get_data()
    photo_id = data.get("photo")

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📺 Ko'rish", url=CHANNEL_LINK),
            InlineKeyboardButton(text="📥 Yuklab Olish", url=CHANNEL_LINK)
        ],
        [
            InlineKeyboardButton(text="🚀 Do'stlarga Ulashish", url=f"https://t.me/share/url?url={CHANNEL_LINK}")
        ]
    ])

    # 1. To'g'ridan-to'g'ri kanalga jo'natish (-1003852596133)[cite: 1]
    try:
        if photo_id:
            await bot.send_photo(chat_id=CHANNEL_ID, photo=photo_id, caption=caption, parse_mode="HTML", reply_markup=kb)
        else:
            await bot.send_message(chat_id=CHANNEL_ID, text=caption, parse_mode="HTML", reply_markup=kb)
        channel_status = f"✅ {CHANNEL_USERNAME} kanaliga muvaffaqiyatli joylandi!"[cite: 1]
    except Exception as err:
        channel_status = f"⚠️ Kanalga jo'natishda xatolik (botni kanalga admin qilganingizga ishonch hosil qiling): {err}"

    # 2. Barcha bot foydalanuvchilariga tarqatish
    sent_count = 0
    for uid in list(BOT_USERS):
        try:
            if photo_id:
                await bot.send_photo(chat_id=uid, photo=photo_id, caption=caption, parse_mode="HTML", reply_markup=kb)
            else:
                await bot.send_message(chat_id=uid, text=caption, parse_mode="HTML", reply_markup=kb)
            sent_count += 1
            await asyncio.sleep(0.04)
        except Exception:
            continue

    await message.answer(
        f"🎉 <b>Post tarqatish yakunlandi!</b>\n\n"
        f"📢 Kanal: {channel_status}\n"
        f"👥 Bot foydalanuvchilari: <b>{sent_count} ta</b> a'zoga yetkazildi.",
        parse_mode="HTML"
    )
    await state.clear()

# --- ISHGA TUSHIRISH ---
async def main():
    logging.basicConfig(level=logging.INFO)
    print("=" * 60)
    print("🚀 KAGE DUB TELEGRAM BOT ISHGA TUSHMOQDA...")
    print(f"👑 Owner ID: {OWNER_ID}")[cite: 1]
    print(f"📢 Kanal ID: {CHANNEL_ID} ({CHANNEL_USERNAME})")[cite: 1]
    print("=" * 60)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
