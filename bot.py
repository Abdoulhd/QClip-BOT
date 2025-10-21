import csv
import os
import random
import re
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

# Load the CSV data
def load_quran_data():
    verses = []
    surah_map = {}  # Maps (surah_num, ayah_num) to verse
    global_map = {}  # Maps global ayah number to verse
    page_map = {}  # Maps page numbers to list of verses
    
    with open('QClip.csv', 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            verses.append(row)
            
            # Build surah/ayah map
            surah_ayah_ref = row['SurahAyahRefNumeric']
            surah_num, ayah_num = map(int, surah_ayah_ref.split(':'))
            surah_map[(surah_num, ayah_num)] = row
            
            # Build global ayah map
            global_ayah_no = int(row['GlobalAyahNo'])
            global_map[global_ayah_no] = row
            
            # Build page map
            page_no = int(row['PageNoEnglish'])
            if page_no not in page_map:
                page_map[page_no] = []
            page_map[page_no].append(row)
    
    return verses, surah_map, global_map, page_map

# Convert Arabic-Indic numerals to Western digits
def arabic_to_western_numeral(text):
    arabic_numerals = '٠٢٢٣٤٥٦٧٨٩'
    western_numerals = '0123456789'
    
    # Create translation table
    trans_table = str.maketrans(arabic_numerals, western_numerals)
    return text.translate(trans_table)

# Format a verse for display (preview without glyphs)
def format_verse_preview(verse):
    # Surah heading (FIXED ORDER: ﴿ ... ﴾ )
    heading = f"﴿ {verse['SurahNameArabic']} || {verse['SurahAyahRefArabic']} ﴾\n"
    heading += f"【 {verse['SurahNameEnglish']} || {verse['SurahAyahRefNumeric']} 】\n\n"
    
    # Bismillah (except for Surah 9)
    surah_num = int(verse['SurahAyahRefNumeric'].split(':')[0])
    bismillah = ""
    if surah_num != 9:
        bismillah = "بِسْمِ ٱللَّهِ ٱلرَّحْمَـٰنِ ٱلرَّحِــيمِ\n\n"
    
    # Arabic text with extra line space before translation
    arabic_text = f"{verse['ArabicText']}\n\n"
    
    # Translation
    translation = f"{verse['Translation']}\n\n"
    
    # Page number
    page_line = f"📄 Page No. {verse['PageNoEnglish']} || رقم الصفحة {verse['PageNoArabic']}"
    
    return heading + bismillah + arabic_text + translation + page_line

# Format glyph display
def format_glyph_display(verse, glyph_type="V1"):
    if glyph_type == "V1":
        return verse['GlyphV1']
    else:
        return verse['GlyphV2']

# Create preview buttons with glyph options
def create_preview_buttons(global_ayah_no):
    # Glyph selection buttons
    glyph_buttons = [
        InlineKeyboardButton("Glyph V1", callback_data=f"glyph_V1_{global_ayah_no}"),
        InlineKeyboardButton("Glyph V2", callback_data=f"glyph_V2_{global_ayah_no}")
    ]
    
    # Combine all buttons
    buttons = [glyph_buttons]
    return InlineKeyboardMarkup(buttons)

# Create glyph display buttons
def create_glyph_buttons(global_ayah_no):
    # Navigation buttons
    nav_buttons = [
        InlineKeyboardButton("« Previous", callback_data=f"prev_{global_ayah_no}"),
        InlineKeyboardButton("🔎 Search Again", callback_data="home"),
        InlineKeyboardButton("Next »", callback_data=f"next_{global_ayah_no}")
    ]
    
    buttons = [nav_buttons]
    return InlineKeyboardMarkup(buttons)

# Store message IDs per chat
chat_sessions = {}  # chat_id -> { preview_msg_id, glyph_msg_id, current_global_ayah }

# Start command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_message = (
        "🌙📖✨\n\n"
        "ٱلسَّـــــــــــلَامُ عَلَيْـــــــــــكُمْ وَرَحْمَةُ ٱللَّٰهِ وَبَرَكاتُهُ ♡‎\n\n"
        "من فضلك قدّم مرجع الآية (على سبيل المثال: ٢:٢٥٥)\n"
        "Please provide a verse reference (e.g., 2:255)"
    )
    if update.message:
        await update.message.reply_text(welcome_message)

# Handle text messages (for ayah references)
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return
        
    reference = update.message.text.strip()
    
    # Show fetching message
    fetching_message = await update.message.reply_text("🌙 Fetching Ayah...")
    
    # Convert Arabic numerals to Western if needed
    reference = arabic_to_western_numeral(reference)
    
    try:
        surah_num, ayah_num = map(int, reference.split(':'))
        verse = surah_map.get((surah_num, ayah_num))
        
        if verse:
            # Show preparing message
            await fetching_message.edit_text("✨ Preparing result...")
            
            global_ayah_no = int(verse['GlobalAyahNo'])
            
            # Create preview message
            formatted_verse = format_verse_preview(verse)
            reply_markup = create_preview_buttons(global_ayah_no)
            preview_message = await update.message.reply_text(formatted_verse, reply_markup=reply_markup, parse_mode="Markdown")
            
            # Create empty glyph message
            glyph_message = await update.message.reply_text("Select Glyph V1 or V2 above to view glyph codes.")
            
            # Store message IDs in session
            if update.effective_chat:
                chat_sessions[update.effective_chat.id] = {
                    'preview_msg_id': preview_message.message_id,
                    'glyph_msg_id': glyph_message.message_id,
                    'current_global_ayah': global_ayah_no
                }
            
            # Show final message
            await fetching_message.edit_text("Here you go 🌙")
        else:
            await fetching_message.edit_text("❌ Ayah not found. Please check the Surah and Ayah numbers.")
    except ValueError:
        await fetching_message.edit_text("❌ Invalid format. Please use Surah:Ayah format (e.g., 2:255)")

# Callback query handler for navigation and glyph buttons
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.callback_query or not update.callback_query.message:
        return
        
    query = update.callback_query
    await query.answer()
    
    if not query.data:
        return
        
    data = query.data
    chat_id = update.callback_query.message.chat.id if update.callback_query.message.chat else None
    
    if not chat_id:
        return
    
    if data == "home":
        welcome_message = (
            "🌙📖✨\n\n"
            "ٱلسَّـــــــــــلَامُ عَلَيْـــــــــــكُمْ وَرَحْمَةُ ٱللَّٰهِ وَبَرَكاتُهُ ♡‎\n\n"
            "من فضلك قدّم مرجع الآية (على سبيل المثال: ٢:٢٥٥)\n"
            "Please provide a verse reference (e.g., 2:255)"
        )
        await query.edit_message_text(welcome_message)
        # Clear session for this chat
        if chat_id in chat_sessions:
            del chat_sessions[chat_id]
        return
    
    # Handle glyph buttons
    if data.startswith("glyph_"):
        parts = data.split('_')
        if len(parts) != 3:
            return
            
        glyph_type = parts[1]  # V1 or V2
        global_ayah_no = int(parts[2])
        
        # Get the verse
        verse = global_map.get(global_ayah_no)
        if not verse:
            await query.answer("❌ Could not retrieve the verse.", show_alert=True)
            return
            
        # Format glyph display
        glyph_text = format_glyph_display(verse, glyph_type)
        reply_markup = create_glyph_buttons(global_ayah_no)
        
        # Update glyph message with glyph text and navigation buttons
        if chat_id in chat_sessions:
            session = chat_sessions[chat_id]
            try:
                await context.bot.edit_message_text(
                    chat_id=chat_id,
                    message_id=session['glyph_msg_id'],
                    text=f"```{glyph_text}```",
                    reply_markup=reply_markup,
                    parse_mode="Markdown"
                )
                # Update current ayah in session
                session['current_global_ayah'] = global_ayah_no
            except Exception as e:
                # Message might have been deleted, ignore
                pass
        return
    
    # Handle navigation buttons
    # Extract action and global ayah number
    if not '_' in data:
        return
        
    action, global_ayah_str = data.split('_')
    global_ayah_no = int(global_ayah_str)
    
    # Handle navigation
    if action == "prev":
        global_ayah_no -= 1
    elif action == "next":
        global_ayah_no += 1
    
    # Check bounds
    if global_ayah_no < 1:
        global_ayah_no = 1  # First verse
    elif global_ayah_no > len(global_map):
        global_ayah_no = len(global_map)  # Last verse
    
    # Get the verse
    verse = global_map.get(global_ayah_no)
    if verse and chat_id in chat_sessions:
        session = chat_sessions[chat_id]
        
        # Update preview message
        formatted_verse = format_verse_preview(verse)
        reply_markup = create_preview_buttons(global_ayah_no)
        try:
            await context.bot.edit_message_text(
                chat_id=chat_id,
                message_id=session['preview_msg_id'],
                text=formatted_verse,
                reply_markup=reply_markup,
                parse_mode="Markdown"
            )
        except Exception as e:
            # Message might have been deleted, ignore
            pass
            
        # Update glyph message (if it exists and has been initialized)
        try:
            # Keep the same glyph type that was previously selected
            # For simplicity, we'll show V1 by default
            glyph_text = format_glyph_display(verse, "V1")
            await context.bot.edit_message_text(
                chat_id=chat_id,
                message_id=session['glyph_msg_id'],
                text=f"```{glyph_text}```",
                reply_markup=create_glyph_buttons(global_ayah_no),
                parse_mode="Markdown"
            )
        except Exception as e:
            # Message might have been deleted, ignore
            pass
            
        # Update session with new ayah number
        session['current_global_ayah'] = global_ayah_no
    elif not verse:
        await query.answer("❌ Could not retrieve the verse.", show_alert=True)

# Load data when the bot starts
verses, surah_map, global_map, page_map = load_quran_data()

# Main function to run the bot
def main():
    # Create the Application and pass it your bot's token
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "8435620553:AAFYR_qxG57zpKcLRcZ7mvBmHr4Pv44R4L8")
    
    application = (
        Application.builder()
        .token(token)
        .build()
    )
    
    # Register command handlers
    application.add_handler(CommandHandler("start", start))
    
    # Register message handler for text messages
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    
    # Register callback query handler for buttons
    application.add_handler(CallbackQueryHandler(button_handler))

    # Start the Bot
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()