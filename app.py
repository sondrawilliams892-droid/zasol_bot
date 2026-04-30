"""
Zasol Bot — MVP v1.0
Dead simple. Works immediately. No package magic.
"""
import asyncio
import logging
import os

from aiogram import Bot, Dispatcher, Router, F
from aiogram.enums import ParseMode
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message, CallbackQuery
from dotenv import load_dotenv

from aiogram.client.default import DefaultBotProperties

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

# ═══════ BOT ═══════
bot = Bot(token=os.getenv("BOT_TOKEN"), default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=MemoryStorage())

# ═══════ ROUTER ═══════
router = Router()

# ═══════ FSM STATES ═══════
class BestEggStates(StatesGroup):
    email = State()
    dob = State()
    zip_code = State()
    confirm = State()

# ═══════ HANDLERS ═══════

@router.message(Command("start"))
async def cmd_start(message: Message) -> None:
    await message.answer(
        "<b>🥚 Zasol Bot — MVP</b>\n\n"
        "Commands:\n"
        "/bestegg — check real credit score on Best Egg\n"
        "/help — show help"
    )

@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    await message.answer(
        "<b>📋 Help</b>\n\n"
        "/bestegg — Best Egg credit score lookup\n"
        "Flow: email → DOB (MM/DD/YYYY) → ZIP → result"
    )

@router.message(Command("bestegg"))
async def cmd_bestegg(message: Message, state: FSMContext) -> None:
    await state.set_state(BestEggStates.email)
    await message.answer("<b>🥚 Best Egg Credit Score</b>\n\nEnter your <b>email</b>:")

@router.message(StateFilter(BestEggStates.email))
async def bestegg_email(message: Message, state: FSMContext) -> None:
    if not message.text or "@" not in message.text:
        await message.answer("❌ Enter a valid email.")
        return
    await state.update_data(email=message.text.strip().lower())
    await state.set_state(BestEggStates.dob)
    await message.answer(
        "<b>📅 Date of Birth</b>\n"
        "Format: <code>MM/DD/YYYY</code>\n"
        "<i>Example: 03/26/1979</i>"
    )

@router.message(StateFilter(BestEggStates.dob))
async def bestegg_dob(message: Message, state: FSMContext) -> None:
    import re
    dob = message.text.strip()
    if not re.match(r"^\d{2}/\d{2}/\d{4}$", dob):
        await message.answer("❌ Format: <code>MM/DD/YYYY</code>")
        return
    await state.update_data(dob=dob)
    await state.set_state(BestEggStates.zip_code)
    await message.answer("<b>📍 ZIP Code</b>\n<i>Example: 64089</i>")

@router.message(StateFilter(BestEggStates.zip_code))
async def bestegg_zip(message: Message, state: FSMContext) -> None:
    zip_code = message.text.strip()
    if not zip_code.isdigit() or len(zip_code) != 5:
        await message.answer("❌ Enter 5-digit ZIP.")
        return
    await state.update_data(zip_code=zip_code)
    data = await state.get_data()
    
    await state.set_state(BestEggStates.confirm)
    await message.answer(
        f"<b>🥚 Confirm</b>\n\n"
        f"📧 <code>{data['email']}</code>\n"
        f"📅 <code>{data['dob']}</code>\n"
        f"📍 <code>{data['zip_code']}</code>\n\n"
        f"Send <b>yes</b> to proceed or <b>/cancel</b> to abort."
    )

@router.message(StateFilter(BestEggStates.confirm), F.text.lower() == "yes")
async def bestegg_submit(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    email = data.get("email")
    dob = data.get("dob")
    zip_code = data.get("zip_code")

    await message.answer(
        "<b>🥚 Best Egg</b>\n\n"
        "⏳ Checking credit score...\n"
        "<i>This may take 20-40 seconds (browser automation)...</i>"
    )

    # SIMPLIFIED MVP: direct message without Playwright for now
    # We'll add Playwright engine in v2 after this MVP works
    await message.answer(
        f"<b>🥚 Best Egg Result</b>\n\n"
        f"📧 <code>{email}</code>\n"
        f"📅 <code>{dob}</code>\n"
        f"📍 <code>{zip_code}</code>\n\n"
        f"<i>MVP mode: Playwright engine will be added in next version.</i>\n"
        f"<i>Bot is running correctly! ✅</i>"
    )
    await state.clear()

@router.message(StateFilter(BestEggStates.confirm), F.text.lower() == "/cancel")
async def bestegg_cancel(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer("❌ Cancelled.")

@router.message(Command("cancel"))
async def cmd_cancel(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer("❌ State cleared.")

# ═══════ MAIN ═══════
async def main() -> None:
    logger.info("🚀 Bot starting...")
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
