import asyncio
import os
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
TOKEN = os.environ["BOT_TOKEN"]
GROUP_CHAT_ID = int(os.environ.get("GROUP_CHAT_ID", "-1004380028697"))
bot = Bot(token=TOKEN)
dp = Dispatcher()
class ReviewState(StatesGroup):
    waiting_for_feedback = State()
def get_rating_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="⭐ 1", callback_data="rate_1"),
        InlineKeyboardButton(text="⭐ 2", callback_data="rate_2"),
        InlineKeyboardButton(text="⭐ 3", callback_data="rate_3"),
        InlineKeyboardButton(text="⭐ 4", callback_data="rate_4"),
        InlineKeyboardButton(text="⭐ 5", callback_data="rate_5"),
    ]])
@dp.message(CommandStart())
async def start_cmd(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Тебя приветствует бот SmartDesign! Большое спасибо за выбор наших услуг! Оцените наше качество работы ниже.", reply_markup=get_rating_keyboard())
@dp.callback_query(F.data.in_({"rate_1", "rate_2", "rate_3"}))
async def process_low_rating(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    rating_map = {"rate_1": "⭐ (1/5)", "rate_2": "⭐⭐ (2/5)", "rate_3": "⭐⭐⭐ (3/5)"}
    await state.update_data(rating=rating_map[callback.data])
    await callback.message.answer("Нам очень жаль, что вам не понравились наши услуги! Настоятельно просим описать наши ошибки, чтобы мы обязательно исправились. Не забудьте указать имя перед отзывом, Пример: [Имя: Текст]")
    await state.set_state(ReviewState.waiting_for_feedback)
@dp.callback_query(F.data.in_({"rate_4", "rate_5"}))
async def process_high_rating(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    rating_map = {"rate_4": "⭐⭐⭐⭐ (4/5)", "rate_5": "⭐⭐⭐⭐⭐ (5/5)"}
    await state.update_data(rating=rating_map[callback.data])
    await callback.message.answer("Большое спасибо за ваш отзыв! Не забудьте написать что именно вас впечатлило, а также укажите имя перед отзывом. Пример: [Имя: Текст]")
    await state.set_state(ReviewState.waiting_for_feedback)
@dp.message(ReviewState.waiting_for_feedback)
async def process_feedback_text(message: Message, state: FSMContext):
    user_data = await state.get_data()
    user_rating = user_data.get("rating", "Не указана")
    username = f"@{message.from_user.username}" if message.from_user.username else message.from_user.full_name
    group_message = f"📩 *Новый отзыв!*\n\n👤 *От кого:* {username}\n📊 *Оценка:* {user_rating}\n\n💬 *Текст отзыва:*\n{message.text}"
    try:
        await bot.send_message(chat_id=GROUP_CHAT_ID, text=group_message, parse_mode="Markdown")
    except Exception as e:
        print(f"Ошибка: {e}")
    await message.answer("Спасибо за отзыв! Мы обязательно его рассмотрим с улыбкой на лице! Почаще выбирайте наши услуги, мы не подведем!)")
    await state.clear()
async def main():
    print("Бот SmartDesign запущен...")
    await dp.start_polling(bot)
if __name__ == "__main__":
    asyncio.run(main())
