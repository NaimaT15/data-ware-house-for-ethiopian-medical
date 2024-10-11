from telethon import TelegramClient, errors
import pandas as pd
import logging
import os
import nest_asyncio
from dotenv import load_dotenv
import re
import asyncio

# Apply nest_asyncio to allow nested event loops in Jupyter notebooks
nest_asyncio.apply()

# Setup Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables from the .env file
load_dotenv('.env')

# Read API credentials from the .env file
API_ID = int(os.getenv('TG_API_ID'))
API_HASH = os.getenv('TG_API_HASH')
PHONE_NUMBER = os.getenv('phone')
TELEGRAM_PASSWORD = os.getenv('TELEGRAM_PASSWORD')  # Optional: Use if two-step verification is enabled

# Initialize the Telegram Client
client = TelegramClient('session_name', API_ID, API_HASH)


# Step 1: Telegram Scraping Functions

def sanitize_channel_name(channel_name):
    """Sanitize channel name to create valid folder and file paths."""
    return re.sub(r'[\\/:*?"<>|]', "_", channel_name.replace("https://t.me/", ""))


async def connect_to_telegram():
    """Connect and authenticate to Telegram."""
    await client.connect()
    if not await client.is_user_authorized():
        await client.send_code_request(PHONE_NUMBER)
        code = input("Enter the code you received on Telegram: ")
        try:
            await client.sign_in(PHONE_NUMBER, code)
        except errors.SessionPasswordNeededError:
            password = input("Enter your Telegram account password: ")
            await client.sign_in(password=password)


async def scrape_telegram_channel(channel_name, text_folder='texts', image_folder='images', limit=100):
    """
    Scrape the given Telegram channel for text messages and images.
    - channel_name: The Telegram channel name or URL.
    - text_folder: Folder to save text messages.
    - image_folder: Folder to save images.
    - limit: The number of recent messages to scrape.
    """
    await connect_to_telegram()
    sanitized_channel_name = sanitize_channel_name(channel_name)

    # Create folders for each channel's data
    text_folder_path = os.path.join(text_folder, sanitized_channel_name)
    image_folder_path = os.path.join(image_folder, sanitized_channel_name)

    if not os.path.exists(text_folder_path):
        os.makedirs(text_folder_path)
    if not os.path.exists(image_folder_path):
        os.makedirs(image_folder_path)

    messages = []
    image_count = 0

    # Fetch messages from the channel
    async for message in client.iter_messages(channel_name, limit=limit):
        messages.append({
            'message_id': message.id,
            'sender_id': message.sender_id,
            'date': message.date,
            'message': message.message
        })
        if message.photo:
            image_filename = f"{sanitized_channel_name}_{image_count}.jpg"
            await message.download_media(file=os.path.join(image_folder_path, image_filename))
            image_count += 1

    df = pd.DataFrame(messages)
    csv_filename = os.path.join(text_folder_path, f"{sanitized_channel_name}_data.csv")
    df.to_csv(csv_filename, index=False)
    await client.disconnect()
    return df, image_count


async def scrape_multiple_channels(channels, text_folder='texts', image_folder='images', limit=100):
    """
    Scrapes multiple Telegram channels and stores the combined results.
    """
    all_dataframes = []
    for channel in channels:
        df, _ = await scrape_telegram_channel(channel, text_folder=text_folder, image_folder=image_folder, limit=limit)
        df['channel'] = channel
        all_dataframes.append(df)
    combined_df = pd.concat(all_dataframes, ignore_index=True)
    return combined_df


# Step 2: Data Cleaning Functions

def load_data(file_path):
    """Load the scraped CSV data into a Pandas DataFrame."""
    return pd.read_csv(file_path)


def remove_duplicates(df):
    """Remove duplicate rows from the DataFrame."""
    return df.drop_duplicates()


def handle_missing_values(df):
    """Fill missing values in the DataFrame."""
    return df.fillna('Unknown')


def standardize_date_format(df, date_column='date'):
    """Standardize the date format to YYYY-MM-DD."""
    df[date_column] = pd.to_datetime(df[date_column], errors='coerce').dt.strftime('%Y-%m-%d')
    return df


def validate_data(df, required_columns):
    """Validate that all required columns are present in the DataFrame."""
    return all(col in df.columns for col in required_columns)


def clean_and_store_data(input_file, output_file, required_columns):
    """
    Clean the scraped data: remove duplicates, handle missing values, standardize dates, and store cleaned data.
    """
    df = load_data(input_file)
    if not validate_data(df, required_columns):
        logger.error(f"Required columns {required_columns} are missing.")
        return None
    df = remove_duplicates(df)
    df = handle_missing_values(df)
    df = standardize_date_format(df)
    df.to_csv(output_file, index=False)
    logger.info(f"Cleaned data saved to {output_file}.")
    return df


def clean_all_scraped_data(text_folder='texts', cleaned_folder='cleaned_data', required_columns=None):
    """
    Clean all scraped data files in the specified folder and store the cleaned results.
    """
    if required_columns is None:
        required_columns = ['message_id', 'sender_id', 'date', 'message']

    if not os.path.exists(cleaned_folder):
        os.makedirs(cleaned_folder)

    for root, _, files in os.walk(text_folder):
        for file in files:
            if file.endswith('_data.csv'):
                input_file = os.path.join(root, file)
                channel_name = os.path.basename(root)
                output_file = os.path.join(cleaned_folder, f"{channel_name}_cleaned_data.csv")
                clean_and_store_data(input_file, output_file, required_columns)

    logger.info(f"All scraped data has been cleaned and stored in {cleaned_folder}.")

