# import asyncio
# import nest_asyncio
# from telegram import Update
# from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler

# # Apply nest_asyncio to allow nested event loops
# nest_asyncio.apply()

# TOKEN = '7340296579:AAHAMBovnW_CE1NX7HQ1lgiswR_ZEbFLjks'

# # Define states for the conversation
# TEXT, NAME, SPEED = range(3)

# async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
#     await update.message.reply_text('سلام عزیز دلم. متنتو برام میفرستی؟')
#     return TEXT

# async def receive_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
#     user_data = context.user_data
#     user_data['text'] = update.message.text
#     await update.message.reply_text('اسم صداتو برام میفرستی؟')
#     return NAME

# async def receive_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
#     user_data = context.user_data
#     user_data['name'] = update.message.text
#     await update.message.reply_text('سرعت وویستو میفرستی؟')
#     return SPEED

# async def receive_speed(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
#     user_data = context.user_data
#     user_data['speed'] = update.message.text
#     await update.message.reply_text('حالا یک کوچولو صبر کن وویسو برات میفرستم')
    
#     # This is where you would add code to process or send the voice message
#     # For now, we're just sending a placeholder message
#     await update.message.reply_text('وویس آماده است!')

#     return ConversationHandler.END

# async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
#     await update.message.reply_text('فرآیند کنسل شد.')
#     return ConversationHandler.END

# async def main() -> None:
#     application = Application.builder().token(TOKEN).build()

#     conv_handler = ConversationHandler(
#         entry_points=[CommandHandler('start', start)],
#         states={
#             TEXT: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_text)],
#             NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_name)],
#             SPEED: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_speed)],
#         },
#         fallbacks=[CommandHandler('cancel', cancel)],
#     )
    
#     application.add_handler(conv_handler)
#     await application.run_polling()

# if __name__ == '__main__':
#     asyncio.run(main())
import asyncio
import nest_asyncio
from telegram import Update, InputFile
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
import azure.cognitiveservices.speech as speechsdk

# Apply nest_asyncio to allow nested event loops
nest_asyncio.apply()

TOKEN = '7340296579:AAHAMBovnW_CE1NX7HQ1lgiswR_ZEbFLjks'

# Define states for the conversation
TEXT, NAME, SPEED = range(3)

class VoiceObject:
    def __init__(self, text, style, speaking_rate):
        self.text = text
        self.style = style
        self.speaking_rate = speaking_rate

class SpeechSynthesizer:
    def __init__(self, speech_key, service_region):
        self.speech_key = speech_key
        self.service_region = service_region

    def save_as_mp3(self, voice_obj, file_path):
        if voice_obj.text is not None:
            ssml_text = f"""
            <speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="fa-IR">
              <voice name="{voice_obj.style}">
                <prosody rate="{voice_obj.speaking_rate}">
                  {voice_obj.text}
                </prosody>
              </voice>
            </speak>
            """
            speech_config = speechsdk.SpeechConfig(subscription=self.speech_key, region=self.service_region)
            synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config)
            result = synthesizer.speak_ssml_async(ssml_text).get()
            if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
                print("Speech synthesized successfully.")
                with open(file_path, "wb") as file:
                    file.write(result.audio_data)
                    print(f"Speech saved as {file_path}")
                return file_path
            elif result.reason == speechsdk.ResultReason.Canceled:
                cancellation_details = result.cancellation_details
                print(f"Speech synthesis canceled: {cancellation_details.reason}")
                if cancellation_details.reason == speechsdk.CancellationReason.Error:
                    print(f"Error details: {cancellation_details.error_details}")
                return None

class VoiceProcessor:
    def __init__(self):
        self.speech_synthesizer = SpeechSynthesizer("d010ee6cf4854c79a069e74d63a0d943", "westus")

    async def generate_voices(self, text, style, speaking_rate, file_path):
        voice_obj = VoiceObject(text, style, speaking_rate)
        return self.speech_synthesizer.save_as_mp3(voice_obj, file_path)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text('سلام عزیز دلم. متنتو برام میفرستی؟')
    return TEXT

async def receive_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_data = context.user_data
    user_data['text'] = update.message.text
    await update.message.reply_text('اسم صداتو برام میفرستی؟')
    return NAME

async def receive_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_data = context.user_data
    user_data['name'] = update.message.text
    await update.message.reply_text('سرعت وویستو میفرستی؟')
    return SPEED

async def receive_speed(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_data = context.user_data
    user_data['speed'] = update.message.text
    await update.message.reply_text('حالا یک کوچولو صبر کن وویسو برات میفرستم')
    
    text = user_data.get('text')
    style = user_data.get('name')
    speaking_rate = user_data.get('speed')
    
    voice_processor = VoiceProcessor()
    file_path = 'demoVoice.mp3'
    generated_file_path = await voice_processor.generate_voices(text, style, speaking_rate, file_path)
    
    if generated_file_path:
        with open(generated_file_path, 'rb') as audio_file:
            await update.message.reply_audio(audio_file)
    else:
        await update.message.reply_text('متاسفانه مشکلی پیش آمده است.')

    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text('فرآیند کنسل شد.')
    return ConversationHandler.END

async def main() -> None:
    application = Application.builder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            TEXT: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_text)],
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_name)],
            SPEED: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_speed)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )
    
    application.add_handler(conv_handler)
    await application.run_polling()

if __name__ == '__main__':
    asyncio.run(main())
