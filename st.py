from telethon import TelegramClient, events
import logging
import os
import asyncio
from aiohttp import web

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Your API credentials
api_id = 22557209
api_hash = '2c2cc680074bcfa5e77f2773ff6e565b'
input_channel = -1001663891655  # Input channel ID
output_channel = -1002192323521  # Output channel ID

# Fetch port from environment variable for Render
PORT = int(os.environ.get("PORT", 8080))

# Use a saved session to avoid login each time
client = TelegramClient('bot_session', api_id, api_hash)

# Function to convert text to small caps
def to_small_caps(text):
    normal_to_small_caps = str.maketrans(
        "ABCDEFGHIJKLMNOPQRSTUVWXYZ",
        "ᴀʙᴄᴅᴇꜰɢʜɪᴊᴋʟᴍɴᴏᴘǫʀsᴛᴜᴠᴡxʏᴢ"
    )
    return text.translate(normal_to_small_caps)

@client.on(events.NewMessage(chats=input_channel))
async def signal_handler(event):
    message = event.raw_text.strip()
    
    try:
        # Handling signals
        if '💳' in message:
            # Extracting the pair from the first line of the message
            pair_line = message.split('\n')[0]
            raw_pair = pair_line.split('💳 ')[-1].strip().upper()

            # Separate pair and "OTC", ensuring it's correctly formatted
            if '-OTC' in raw_pair:
                currency_pair, otc = raw_pair.split('-OTC')
                formatted_pair = f"{to_small_caps(currency_pair[:3])}/{to_small_caps(currency_pair[3:])} OTC"
            else:
                currency_pair = raw_pair.replace('-', '/')
                formatted_pair = to_small_caps(currency_pair)
            
            time = message.split('⌛')[1].split()[0].strip()  # Extracting time
            
            # Determine direction based on the presence of "call" or "put"
            if 'put' in message.lower():
                direction = 'ᴘᴜᴛ 🟥'
            elif 'call' in message.lower():
                direction = 'ᴄᴀʟʟ 🟩'
            else:
                direction = 'UNKNOWN'
            
            # Constructing the formatted message with correct pair format and direction
            formatted_message = (
                f"📊 ᴘᴀɪʀ: {formatted_pair}\n\n"
                f"⏰ ᴛɪᴍᴇ: {time}\n\n"
                f"⏳ ᴇxᴘɪʀʏ: ᴍ𝟷 𝟷 ᴍɪɴᴜᴛᴇ\n\n"
                f"↕️ ᴅɪʀᴇᴄᴛɪᴏɴ: {direction}\n\n"
                f"✅¹ 𝟷 sᴛᴇᴘ ᴍᴛɢ ✓\n\n"
                f"🧔🏻 ᴏᴡɴᴇʀ : sᴋᴇᴘᴛɪᴄ ᴛʀᴀᴅᴇʀ"
            )
            
            # Sending the formatted message to the output channel
            await client.send_message(output_channel, formatted_message)

        # Handling result messages
        result_messages = ['win ✅', 'win ✅¹', 'win ✅²', '💔 loss']
        if any(result_message in message.lower() for result_message in result_messages):
            await client.send_message(output_channel, message)
    
    except Exception as e:
        logger.error(f"An error occurred: {e}")

# Simple HTTP server for Render port binding
async def handle(request):
    return web.Response(text="Bot is running")

async def start_server():
    app = web.Application()
    app.add_routes([web.get('/', handle)])
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', PORT)
    await site.start()

# Run both the Telegram client and the web server
async def main():
    await client.start()  # Automatically uses the saved session
    await start_server()
    await client.run_until_disconnected()

# Start the asyncio event loop
loop = asyncio.get_event_loop()
loop.run_until_complete(main())
