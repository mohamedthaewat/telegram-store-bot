import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command

TOKEN = "8049523277:AAHZ8XKGEnmn2aPD1aUbfVduqAfMHZqhOm0"
ADMIN_ID = 123456789

bot = Bot(token=TOKEN)
dp = Dispatcher()

product = {
    "name": "Netflix Account",
    "price": "50 EGP"
}

accounts = [
    {"email": "test1@mail.com", "password": "123456"},
    {"email": "test2@mail.com", "password": "abcdef"},
]

pending_orders = {}

def buy_keyboard():
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="شراء 💳", callback_data="buy")]
    ])
    return kb

def admin_keyboard(user_id):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="تأكيد الدفع ✅", callback_data=f"confirm_{user_id}")]
    ])
    return kb


@dp.message(Command("start"))
async def start(msg: types.Message):
    await msg.answer(
        f"👋 اهلا بيك\n\n"
        f"📦 المنتج: {product['name']}\n"
        f"💰 السعر: {product['price']}",
        reply_markup=buy_keyboard()
    )


@dp.callback_query(lambda c: c.data == "buy")
async def buy(call: types.CallbackQuery):
    pending_orders[call.from_user.id] = True
    await call.message.answer(
        "💸 حول على InstaPay: 010XXXXXXX\n"
        "📸 وبعد التحويل ابعت اسكرين هنا"
    )


@dp.message(lambda msg: msg.photo)
async def receive_payment(msg: types.Message):
    if msg.from_user.id in pending_orders:
        await bot.send_photo(
            ADMIN_ID,
            msg.photo[-1].file_id,
            caption=f"طلب دفع من المستخدم: {msg.from_user.id}",
            reply_markup=admin_keyboard(msg.from_user.id)
        )
        await msg.answer("✅ تم ارسال طلبك للمراجعة")


@dp.callback_query(lambda c: c.data.startswith("confirm_"))
async def confirm(call: types.CallbackQuery):
    user_id = int(call.data.split("_")[1])

    if len(accounts) == 0:
        await call.message.answer("❌ مفيش حسابات متاحة")
        return

    account = accounts.pop(0)

    await bot.send_message(
        user_id,
        f"🎉 تم تأكيد الدفع\n\n"
        f"📧 Email: {account['email']}\n"
        f"🔑 Password: {account['password']}"
    )

    await call.message.answer("✅ تم التسليم")
    pending_orders.pop(user_id, None)


async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
