# Quran Telegram Bot

This is a Telegram bot that provides access to the Quran through a simple and elegant interface. It reads from a CSV file containing Quran verses and allows users to search and navigate through the verses.

## Features

- Retrieve specific verses by Surah and Ayah number (e.g., 2:255)
- Clean, modern welcome interface with minimal UI
- Dynamic messages for natural interaction ("Fetching Ayah...", "Preparing result...", "Here you go 🌙")
- Two separate dynamic messages:
  1. Preview message with verse text and translation
  2. Glyph message showing only glyph codes
- Navigation buttons:
  - « Previous - Go to the previous verse
  - 🔎 Search Again - Return to input prompt
  - Next » - Go to the next verse

## Setup

1. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Run the bot:
   ```
   python bot.py
   ```

## Usage

1. Start the bot by sending `/start`
2. Enter a verse reference in the format Surah:Ayah (e.g., `2:255` or `٢:٢٥٥`)
3. The bot will display two separate messages:
   - **Preview Message**: Contains verse with Arabic text, translation, and page number
   - **Glyph Message**: Initially shows "Select Glyph V1 or V2 above to view glyph codes."
4. Select "Glyph V1" or "Glyph V2" in the preview message to update the glyph message
5. While viewing glyphs, use navigation buttons to browse through verses

## Deployment

### Deploying to Railway (Recommended)

1. Sign up for a [Railway](https://railway.app) account
2. Fork this repository to your GitHub account
3. Create a new project in Railway
4. Select "Worker" as the service type (for long-polling bots)
5. Connect your GitHub repository
6. Configure environment variables:
   - `TELEGRAM_BOT_TOKEN`: Your Telegram bot token
7. Deploy the application

### Environment Variables

- `TELEGRAM_BOT_TOKEN`: Telegram bot token (required)

## Supported Input Formats

- Surah:Ayah reference (Western digits): e.g. 2:255
- Surah:Ayah reference (Arabic-Indic digits): e.g. ٢:٢٥٥

## Data Source

The bot reads from `QClip.csv` which contains:
- GlobalAyahNo
- SurahNameEnglish
- SurahNameArabic
- SurahAyahRefNumeric
- SurahAyahRefArabic
- ArabicText
- Translation
- GlyphV1
- GlyphV2
- PageNoEnglish
- PageNoArabic

## Interface Flow

1. **Start Screen**:
   ```
   ٱلسَّـــــــــــلَامُ عَلَيْـــــــــــكُمْ وَرَحْمَةُ ٱللَّٰهِ وَبَرَكاتُهُ ♡‎

   من فضلك قدّم مرجع الآية (على سبيل المثال: ٢:٢٥٥)
   Please provide a verse reference (e.g., 2:255)
   ```

2. **Preview Message**:
   ```
   ﴿ سُورَةُ البَقَرَةِ || ٢:٢٥٥ ﴾
   【 Surah Al-Baqarah || 2:255 】

   بِسْمِ ٱللَّهِ ٱلرَّحْمَـٰنِ ٱلرَّحِــيمِ 𑁍

   ٱللَّهُ لَآ إِلَـٰهَ إِلَّا هُوَ ...
   Allah! There is no god ˹worthy of worship˺ except Him ...

   📄 Page No. 42 || رقم الصفحة ٤٢

   [Glyph V1] [Glyph V2]
   ```

3. **Glyph Message** (after selection):
   ```
   ۀہہہہھھھھےےۓۓڭ
   [« Previous] [Search Again] [Next »]
   ```

4. **Navigation Example**:
   ```
   ۀہہہہھھھھےےۓۓڭ
   [« Previous] [Search Again] [Next »]
   ```

## Technical Implementation

- **Two Separate Messages**: Preview and Glyph messages are maintained independently
- **Session Management**: Each chat session stores both message IDs for updates
- **Dynamic Updates**: Both messages can be updated independently through navigation
- **State Preservation**: Navigation updates both messages while preserving their distinct content

## Testing

To verify that the data is loaded correctly, you can run:
```
python test_data.py
```

This will show statistics about the loaded data and test some specific lookups.