import requests
import json
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from telegram import Bot, Update
from telegram.ext import CommandHandler, ApplicationBuilder, ContextTypes

API_KEY = 'XXP1PZH3MWIZAWUUIHEU3VB9ERVR8SKTSB'
TELEGRAM_TOKEN = '7964299443:AAF2PHd147Ml5xlzGSy8ZkyILuGZy7TwByo'
CHAT_ID = '7898876090'

url = f'https://api.etherscan.io/api?module=gastracker&action=gasoracle&apikey={API_KEY}'
bot = Bot(token=TELEGRAM_TOKEN)

previous_fast_gas_price = None

async def get_gas_price():
    global previous_fast_gas_price
    try:
        print("Fetching gas price...")  # Debug print
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        print(f"API Response: {data}")  # Debug print
        
        if data['status'] == '1':
            fast_gas_price = float(data['result']['FastGasPrice'])
            gas_used_ratio = float(data['result']['gasUsedRatio'].split(',')[0])
            change = (fast_gas_price - previous_fast_gas_price) if previous_fast_gas_price is not None else 0
            previous_fast_gas_price = fast_gas_price
            
            message = f"FastGasPrice: {fast_gas_price}, GasUsedRatio: {gas_used_ratio}, Change: {change:.2f}"
            print(message)
            await bot.send_message(chat_id=CHAT_ID, text=message)
            print(f"Message sent to Telegram: {message}")  # Debug print
        else:
            print("API 호출 실패:", data['message'])

    except requests.exceptions.RequestException as e:
        print("HTTP 요청 오류:", e)
    except json.JSONDecodeError:
        print("JSON 디코딩 오류 발생")
    except Exception as e:
        print("기타 오류 발생:", e)

async def restart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global previous_fast_gas_price
    previous_fast_gas_price = None  # 변화량 초기화
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Change has been reset!")

async def main():
    print("Starting the bot...")  # Debug print
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler('restart', restart))  # /restart 명령어 핸들러 추가

    scheduler = AsyncIOScheduler()
    scheduler.add_job(get_gas_price, 'interval', seconds=10)
    scheduler.start()

    print("Initializing application...")  # Debug print
    await app.initialize()
    print("Starting application...")  # Debug print
    await app.start()
    print("Starting polling...")  # Debug print
    await app.updater.start_polling()

    try:
        print("Bot is running. Press Ctrl+C to stop.")
        # Keep the main coroutine running
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        print("Stopping the bot...")
    finally:
        await app.updater.stop()
        await app.stop()
        await app.shutdown()

if __name__ == '__main__':
    asyncio.run(main())