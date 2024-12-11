# OZLINGO
A chatbot that could serve as a useful language-learning assistant tailored for Australian English (OZLINGO)

## OZLINGO: Australian Slang Translator Bot

OZLINGO is a Telegram bot designed to help users understand Australian slang through various interactive features. It leverages AWS services and libraries like Aiogram to provide functionalities for text, speech, and image-based translation of Aussie slang.

---

## **Features**

### 🦘 **Aussie Slang Translator**
- **/start**: Provides an introduction and instructions for using the bot.
- **/help**: Offers guidance on the bot's commands and features.

### 🔊 **Speech-to-Text Translation**
- Converts voice messages into text and identifies Aussie slang phrases in the speech.
- **Command:** `/voice`

### 📝 **Text Translation**
- Translates text messages to identify and explain Aussie slang terms.
- **Command:** `/text [your message]`

### 📸 **Image Translation**
- Analyzes uploaded images for text containing Aussie slang and translates it.
- **Command:** `/photo`

---

## **Setup Instructions**

### 1. **Clone the Repository**
```bash
git clone https://github.com/yourusername/ozlingo-bot.git
cd ozlingo-bot
```

### 2. **Install Dependencies**
Ensure you have Python 3.8+ installed. Run the following command to install required libraries:
```bash
pip install -r requirements.txt
```

### 3. **Configure Environment Variables**
Create a `.env` file and set up the required variables:
```env
AWS_ACCESS_KEY=your_aws_access_key
AWS_SECRET_KEY=your_aws_secret_key
AWS_REGION=your_aws_region
S3_BUCKET_NAME=your_s3_bucket_name
CSV_FILE_KEY=your_csv_file_key
BOT_TOKEN=your_telegram_bot_token
```

### 4. **Upload Resources to S3**
- Place your Aussie slang CSV file, `WelcomeAus.png`, and `AussieSlang.png` in the specified S3 bucket.

### 5. **Run the Bot**
Start the bot locally:
```bash
python ozlingo_bot.py
```

---

## **Usage**

### Start the Bot
- Send `/start` to the bot for an introduction and instructions.

### Speech Translation
- Use `/voice` to send voice messages for Aussie slang translation.

### Text Translation
- Use `/text [your message]` to translate written text for Aussie slang.

### Image Translation
- Use `/photo` to upload an image containing Aussie slang text.

---

## **Technical Overview**

### **Libraries and Tools**
- **Aiogram**: For Telegram bot development.
- **AWS S3**: For storing resources like images and the slang CSV file.
- **AWS Textract**: For extracting text from uploaded images.
- **SpeechRecognition**: For converting speech to text.
- **Librosa** and **Pydub**: For processing audio files.

### **File Structure**
```
.
├── ozlingo_bot.py         # Main bot script
├── requirements.txt       # Python dependencies
├── README.md              # Documentation
└── .env                   # Environment variables
```

---

## **Contributing**
Contributions are welcome! Feel free to open issues or submit pull requests.

---

## **License**
This project is licensed under the MIT License. See `LICENSE` for details.

---

## **Future Enhancements**
- Expand the Aussie slang dictionary.
- Add support for additional languages.
- Improve error handling and user experience.

