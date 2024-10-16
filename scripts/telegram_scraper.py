from telethon import TelegramClient, errors
import pandas as pd
import logging
import os
import nest_asyncio
from dotenv import load_dotenv
import re
import asyncio
from sqlalchemy import create_engine

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

# List of channels to scrape images from
image_only_channels = [
    'https://t.me/CheMed123',
    'https://t.me/lobelia4cosmetics'
]

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
    Scrape the given Telegram channel for text messages and images based on the specified channels.
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
        # Prepare message details
        message_data = {
            'channel_name': channel_name,  # Add channel name to the data
            'message_id': message.id,
            # 'sender_id': message.sender_id,
            'date': message.date,
            'message': message.message,
            'image_path': None  # Default to None unless an image is downloaded
        }

        # Download image if the channel is in the selective list
        if message.photo and channel_name in image_only_channels:
            image_filename = f"{sanitized_channel_name}_{image_count}.jpg"
            image_path = os.path.join(image_folder_path, image_filename)
            await message.download_media(file=image_path)
            message_data['image_path'] = image_path  # Store image path in the data
            image_count += 1

        messages.append(message_data)

    # Save the messages to a DataFrame and CSV file
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


def clean_all_scraped_data(text_folder='texts', cleaned_folder='cleaned_data', output_file='combined_cleaned_data.csv', required_columns=None):
    """
    Clean all scraped data files in the specified folder and store the cleaned results in a single CSV file.
    - text_folder: Folder containing the raw scraped data.
    - cleaned_folder: Folder to save the cleaned data for each channel.
    - output_file: The final combined CSV file to store all cleaned data.
    - required_columns: List of required columns to validate in the DataFrame.
    """
    if required_columns is None:
        required_columns = ['channel_name', 'message_id', 'date', 'message', 'image_path']

    if not os.path.exists(cleaned_folder):
        os.makedirs(cleaned_folder)

    combined_df = pd.DataFrame()  # Initialize an empty DataFrame for storing combined results

    for root, _, files in os.walk(text_folder):
        for file in files:
            if file.endswith('_data.csv'):
                input_file = os.path.join(root, file)
                channel_name = os.path.basename(root)
                output_file_per_channel = os.path.join(cleaned_folder, f"{channel_name}_cleaned_data.csv")
                
                # Clean the data for each channel and store it in a separate CSV
                cleaned_df = clean_and_store_data(input_file, output_file_per_channel, required_columns)
                
                if cleaned_df is not None:
                    # Append the cleaned data to the combined DataFrame
                    combined_df = pd.concat([combined_df, cleaned_df], ignore_index=True)

    # Save the combined cleaned data to a single CSV file
    combined_df.to_csv(output_file, index=False)
    print(f"All cleaned data has been combined and saved to '{output_file}'")

    return combined_df


# Store Combined Data in a Database (Optional)
def store_combined_data_in_db(combined_df, table_name, db_url):
    """
    Store the combined cleaned data into a specified database table.
    Args:
    - combined_df (pd.DataFrame): DataFrame containing combined cleaned data.
    - table_name (str): Name of the table to store data in.
    - db_url (str): Database URL for SQLAlchemy (e.g., 'postgresql://user:password@localhost:5432/mydatabase').

    Returns:
    - None
    """
    engine = create_engine(db_url)
    try:
        combined_df.to_sql(table_name, engine, if_exists='replace', index=False)
        print(f"Combined data successfully stored in table '{table_name}'")
    except Exception as e:
        print(f"Error storing combined data: {e}")

# Configure logging settings
logging.basicConfig(
    filename='scraping.log',
    filemode='a',
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

def log_scraping_activity(channel_name, message_count):
    logging.info(f"Successfully scraped {message_count} messages from {channel_name}")

# Example usage in the scrape function:
channel_name = "https://t.me/mychannel"
message_count = 100  
log_scraping_activity(channel_name, message_count)
def store_detection_results_in_db(detection_df, table_name, db_url):
    engine = create_engine(db_url)
    try:
        detection_df.to_sql(table_name, engine, if_exists='replace', index=False)
        print(f"Detection results successfully stored in table '{table_name}'")
    except Exception as e:
        print(f"Error storing detection results: {e}")
