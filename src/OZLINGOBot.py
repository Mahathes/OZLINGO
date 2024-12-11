import boto3
from aiogram import Bot, Dispatcher, filters, types
from aiogram.types import Message
import io
import speech_recognition as sr
import librosa
import csv
import logging
from pydub import AudioSegment
import soundfile as sf

# from aiogram import Bot, Dispatcher, types

logging.basicConfig(level=logging.INFO)

# AWS credentials
AWS_REGION = 'us-west-2'
AWS_ACCESS_KEY = 'AWS_ACCESS_KEY'
AWS_SECRET_KEY = 'AWS_SECRET_KEY'
S3_BUCKET_NAME = 'S3_BUCKET_NAME'
WELCOME_IMAGE_KEY = 'WelcomeAus.png'
AUSSIE_SLANG_IMAGE_KEY = 'AussieSlang.png'
CSV_FILE_KEY = 'aussie_slang.csv'

# Telegram Bot
bot = Bot(token="BOT_TOKEN")
dp = Dispatcher(bot)

# S3 client
s3 = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET_KEY)
# Initialize Textract client
textract = boto3.client('textract', region_name=AWS_REGION, aws_access_key_id=AWS_ACCESS_KEY,
                        aws_secret_access_key=AWS_SECRET_KEY)

# Dictionary to store user-specific data
user_sessions = {}

# Initialize lists for the first and second columns
slangList = []
meaningList = []
usageList = []

# Read CSV file from S3
try:
    response = s3.get_object(Bucket=S3_BUCKET_NAME, Key=CSV_FILE_KEY)
    csv_data = response['Body'].read().decode('utf-8')
    csv_rows = csv_data.splitlines()

    # Parse CSV data, skipping the first row
    for row in csv.reader(csv_rows[1:]):  # Skip the first row
        slangList.append(row[0].lower())
        meaningList.append(row[1].lower())
        usageList.append(row[2].lower())

except Exception as e:
    print(f"Error reading data: {e}")

slangmean = dict(zip(slangList, meaningList))
slangUsage = dict(zip(slangList, usageList))


# Handler for /start command
@dp.message_handler(commands=['start'])
async def start_command(message: Message):
    user_id = message.from_user.id

    # Check if user already has a session
    if user_id not in user_sessions:
        user_sessions[user_id] = {}

    # Send the welcome image from S3 bucket
    try:
        image_stream = io.BytesIO()
        s3.download_fileobj(S3_BUCKET_NAME, WELCOME_IMAGE_KEY, image_stream)
        image_stream.seek(0)
        await bot.send_photo(message.chat.id, photo=image_stream)
    except Exception as e:
        print("Failed to send image:", e)

    await message.answer("""🇦🇺Hello! Welcome to \"New to Aussie\" OZLINGO Translator.🇦🇺

🦘Your go to place to find meanings for the 
Aussie words that you hear or want to learn.🦘

📖Our dictionary consists of 90+ Aussie words for you to learn and explore

🚀To get Started: 

🔊Type /voice to activate Aussie Slang Speech to English Text Translator.

📝Use /text for Aussie Slang Text to English Text Translator.
🔡Make sure the spelling is correct
💡Input example: /text Let's go to Barbie party
💡Output example: Barbie means Barbecue

📸Use /photo for Aussie Slang Detector from Pictures
Just upload the picture that contains Aussie Slang text and see the Magic

❓If you need /help don't be hesitant to type it.""")


# Handler for /help command
@dp.message_handler(commands=['help'])
async def help_command(message: Message):
    await message.answer("""Did you know that OZZIE is the Australian Slang for Australian

🚀Type /start to get started.
Gives you basic instructions on how to get started with OZLINGO

🔊Type /voice to use our Speech Translation feature
This feature allows you to convert your Speech to Text 
Which helps to find the Aussie Slang words from your Speech
We use exact matching algorithm which means you have to make sure the spellings are 
correct
Input Example:🔊 Let's go to Barbie party
Output Example: 
Recognised Text: Let's go to Barbie Party
Australian slang phrases found ini your message:
Barbie means Barbecue
Usage: Just Getting A Few Mates Together For ....

📝Use /text for Aussie Slang Text to English Text Translator.
🔡Make sure the spelling is correct
💡Input example: /text Welcome to OZZIE
💡Output example: 
Australian slang phrases found ini your message:
Barbie means Barbecue
Usage: Just Getting A Few Mates Together For ....

📸Use /photo for Aussie Slang Detector from Pictures
For accurate results make sure the text part is cropped 
from the picture
Just upload the picture that contains Aussie Slang text and see the Magic
""")


# Handler for /voice command
@dp.message_handler(commands=['voice'])
async def voice_command(message: Message):
    # Send the welcome image from S3 bucket
    try:
        image_stream = io.BytesIO()
        s3.download_fileobj(S3_BUCKET_NAME, AUSSIE_SLANG_IMAGE_KEY, image_stream)
        image_stream.seek(0)
        await bot.send_photo(message.chat.id, photo=image_stream)
    except Exception as e:
        print("Failed to send image:", e)

    await message.answer("""Make sure you are in a Quiet Environment

Click the mic button to record audio! and speak clearly
Usage example: Let's go to Barbie party!""")


@dp.message_handler(content_types=['voice'])
async def handle_voice(message: Message):
    voice = message.voice
    voice_file = await voice.get_file()

    try:
        # Download the voice file
        voice_data = await bot.download_file_by_id(voice_file.file_id)

        y, sr = librosa.load(voice_data)
        samples_cut = y[0:]
        sf.write('processed' + str(voice_file.file_id) + '.wav', samples_cut, sr, 'PCM_16')
        voice_data_name = 'processed' + str(voice_file.file_id) + '.wav'

        # Convert audio data to text
        voice_text = speech_to_text(voice_data_name)

        # Respond with the converted text
        await message.answer(f"Recognized text: {voice_text.title()}")

        voice_txt = voice_text.lower()
        slang_phrases_in_voice_text = \
            [voice_phrase.lower() for voice_phrase in slangList if voice_phrase.lower() in voice_txt]

        # Send a message containing the Australian slang phrases found in the user's input
        if slang_phrases_in_voice_text:
            response_text = f"Australian slang phrases found in your message:\n"
            # await message.answer(response_text)
            for i in slang_phrases_in_voice_text:
                response_text += f"🔹*{i.title()}* means *{slangmean[i].title()}*\n"
                slangUsage[i] = slangUsage[i].replace('"', '')
                response_text += f"*Usage:* {slangUsage[i].title()}\n\n"
            await message.answer(response_text, parse_mode="Markdown")
        else:
            await message.answer("🚫 No Australian slang phrases found in your message.")

    except Exception as e:
        await message.answer(f"Failed to process voice message: {e}")


def speech_to_text(audio_file):
    recognizer = sr.Recognizer()

    with sr.AudioFile(audio_file) as source:
        print("Processing audio file:", audio_file)
        audio = recognizer.listen(source)

    try:
        print("Processing...")
        text = recognizer.recognize_google(audio)
        print("Converted text:", text)
        return text
    except sr.UnknownValueError:
        print("Speech recognition could not understand audio")
    except sr.RequestError as e:
        print("Could not request results from Google Speech Recognition service; {0}".format(e))

# Handler for /text command
@dp.message_handler(commands=['text'])
async def text_command(message: Message):
    # Extract the text from the message
    text_with_command = message.text

    # Remove the '/text' command from the text
    text_without_command = text_with_command.lower().replace('/text', '', 1).strip()

    tetext_without_command = text_without_command.lower()
    slang_phrases_in_text = [phrase.lower() for phrase in slangList if phrase.lower() in text_without_command]

    # Send a message containing the Australian slang phrases found in the user's input
    if slang_phrases_in_text:
        response_text = f"Australian slang phrases found in your message:\n"
        # await message.answer(response_text)
        for i in slang_phrases_in_text:
            response_text += f"🔹*{i.title()}* means *{slangmean[i].title()}*\n"
            slangUsage[i] = slangUsage[i].replace('"', '')
            response_text += f"*Usage:* {slangUsage[i].title()}\n\n"
        await message.answer(response_text, parse_mode="Markdown")
    else:
        await message.answer("🚫 No Australian slang phrases found in your message.")


# Handler for processing the /photo command
@dp.message_handler(commands=['photo'])
async def handle_photo_command(message: types.Message):
    await message.answer("📸 Kindly upload a picture by clicking on the "
                         "attachments sign at the bottom left corner")


@dp.message_handler(content_types=['photo'])
async def handle_voice(message: Message):
    try:
        # Get the photo file ID
        photo_id = message.photo[-1].file_id

        # Download the photo file
        photo_file = await bot.download_file_by_id(photo_id)

        # Detect text from the photo using AWS Textract
        text = await detect_text_from_photo(photo_file)

        photo_text = text.lower()
        slang_phrases_in_photo = [phrase.lower() for phrase in slangList if phrase.lower() in photo_text]

        # Send a message containing the Australian slang phrases found in the user's input
        if slang_phrases_in_photo:
            response_text = f"Australian slang phrases found in your Picture:\n"
            # await message.answer(response_text)
            for i in slang_phrases_in_photo:
                response_text += f"🔹*{i.title()}* means *{slangmean[i].title()}*\n"
                slangUsage[i] = slangUsage[i].replace('"', '')
                response_text += f"*Usage:* {slangUsage[i].title()}\n\n"
            await message.answer(response_text, parse_mode="Markdown")
        else:
            await message.answer("🚫 No Australian slang phrases found in your message.")

        # await message.reply(text)

    except Exception as e:
        print("Error:", e)


async def detect_text_from_photo(photo_file):
    try:
        # Upload the photo file to S3 (optional)
        # You can skip this step if you prefer to process the photo without uploading it to S3

        # Call Textract to detect text in the photo
        response = textract.detect_document_text(
            Document={
                'Bytes': photo_file.getvalue()  # Pass the bytes of the photo file
            }
        )

        # Extract the detected text
        detected_text = ''
        for item in response['Blocks']:
            if item['BlockType'] == 'LINE':
                detected_text += item['Text'] + '\n'

        return detected_text

    except Exception as e:
        return str(e)


# Handler for new users
@dp.message_handler()
async def new_user_handler(message: Message):
    user_id = message.from_user.id

    # Check if the user has interacted with the bot before
    if user_id not in user_sessions:
        await start_command(message)


if __name__ == "__main__":
    import asyncio
    from aiogram import executor

    loop = asyncio.get_event_loop()
    executor.start_polling(dp, loop=loop, skip_updates=True)
