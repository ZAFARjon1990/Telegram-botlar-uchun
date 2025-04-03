import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = "7610112415:AAFd5pWG3ACrN-J4FO89LaV7SEwCdjvP8ec"
bot = Bot(token=TOKEN)
dp = Dispatcher()

tasks = {}  # {username: {"task": "Topshiriq matni", "status": "Bajarildi/Bajarilmadi", "reason": "Izoh"}}

@dp.message(Command("start"))
async def start_command(message: types.Message):
    await message.answer("📌 Salom! Bu bot guruh foydalanuvchilari uchun kunlik topshiriqlarni boshqaradi.\n"
                         "✅ Yangi topshiriq qo'shish uchun: /addtask @username Topshiriq matni")

@dp.message(Command("addtask"))
async def add_task(message: types.Message):
    args = message.text.split(" ", 2)
    if len(args) < 3 or not args[1].startswith("@"):
        await message.answer("❌ Noto‘g‘ri format! To‘g‘ri qo‘llash: /addtask @username Topshiriq matni")
        return

    username, task_text = args[1], args[2]
    tasks[username] = {"task": task_text, "status": "Kutilmoqda", "reason": ""}

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Bajarildi", callback_data=f"done|{username}")],
        [InlineKeyboardButton(text="❌ Bajarilmadi", callback_data=f"not_done|{username}")]
    ])
    
    await message.answer(f"📝 {username} uchun yangi topshiriq qo‘shildi:\n\n📌 {task_text}", reply_markup=keyboard)

@dp.callback_query()
async def process_callback(callback: types.CallbackQuery):
    data = callback.data.split("|")  # ❗ `|` orqali ajratdik (`_` muammo tug‘dirgan edi)
    if len(data) != 2:
        await callback.answer("❌ Xatolik yuz berdi!")
        return

    action, username = data[0], data[1]

    if username not in tasks:
        await callback.answer("❌ Topshiriq topilmadi!")
        return

    if action == "done":
        tasks[username]["status"] = "✅ Bajarildi"
        await callback.message.edit_text(f"✅ {username} topshiriqni bajardi!\n\n📌 {tasks[username]['task']}")
    elif action == "not_done":
        tasks[username]["status"] = "❌ Bajarilmadi"
        await callback.message.answer(f"❌ {username}, nima uchun bajarmadingiz? Izoh yozing.")

@dp.message(Command("report"))
async def show_report(message: types.Message):
    if not tasks:
        await message.answer("📊 Hozircha hech qanday topshiriq qo‘shilmagan.")
        return

    report_text = "📊 **Hisobot:**\n\n"
    for user, info in tasks.items():
        report_text += f"{user}: {info['status']} - {info['task']}\n"
    await message.answer(report_text)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
