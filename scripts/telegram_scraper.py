# telegram_scraper.py

from telethon import TelegramClient
import pandas as pd
import logging
import os
import nest_asyncio
from dotenv import load_dotenv
nest_asyncio.apply()

# Setup Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
load_dotenv('.env')
API_ID = os.getenv('TG_API_ID')
API_HASH = os.getenv('TG_API_HASH')
PHONE_NUMBER =os.getenv ('phone')

# Initialize the Telegram Client
client = TelegramClient('session_name', API_ID, API_HASH)

# Connect to Telegram
async def connect_to_telegram():
    await client.start()
    logging.info("Client connected to Telegram.")

# Scrape messages from a given Telegram channel
async def scrape_telegram_channel(channel_name, limit=100):
    """
    Scrapes the given Telegram channel and returns the scraped data as a Pandas DataFrame.
    
    Parameters:
    - channel_name: The name or URL of the Telegram channel.
    - limit: The number of recent messages to scrape.
    
    Returns:
    - DataFrame containing the scraped messages.
    """
    await connect_to_telegram()
    logging.info(f"Scraping data from channel: {channel_name}")
    
    # Fetch messages
    messages = []
    async for message in client.iter_messages(channel_name, limit=limit):
        messages.append({
            'message_id': message.id,
            'sender_id': message.sender_id,
            'date': message.date,
            'message': message.message
        })

    # Convert to DataFrame
    df = pd.DataFrame(messages)
    logging.info(f"Scraped {len(messages)} messages from {channel_name}")
    await client.disconnect()
    return df

# Save the scraped data to a CSV file
def save_data_to_csv(dataframe, filename="telegram_data.csv"):
    """
    Saves the DataFrame to a CSV file.
    
    Parameters:
    - dataframe: Pandas DataFrame containing the scraped data.
    - filename: The filename for the CSV file.
    """
    dataframe.to_csv(filename, index=False)
    logging.info(f"Data saved to {filename}.")
