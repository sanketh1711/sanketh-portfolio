import os
import telebot
from google import genai
from dotenv import load_dotenv

load_dotenv()
gemini_key = os.getenv("MY_GEMINI_KEY")
telegram_token = os.getenv("MY_TELEGRAM_TOKEN")

if not telegram_token or not gemini_key:
    raise SystemExit("Ensure MY_TELEGRAM_TOKEN and MY_GEMINI_KEY are in your .env file.")

client = genai.Client(api_key=gemini_key)
bot = telebot.TeleBot(telegram_token)

user_data = {}

# Helper function to prevent KeyError crashes
def check_user(message):
    if message.chat.id not in user_data:
        bot.send_message(message.chat.id, "Session expired. Please type /start again.")
        return False
    return True

@bot.message_handler(commands=['start', 'gift'])
def start_survey(message):
    user_data[message.chat.id] = [] 
    msg = bot.reply_to(message, "🎁 Let's find a gift! \n1. Who is the gift for?")
    bot.register_next_step_handler(msg, process_q1)

def process_q1(message):
    if not check_user(message): return
    user_data[message.chat.id].append(message.text)
    msg = bot.send_message(message.chat.id, "2. What is the occasion?")
    bot.register_next_step_handler(msg, process_q2)

def process_q2(message):
    if not check_user(message): return
    user_data[message.chat.id].append(message.text)
    msg = bot.send_message(message.chat.id, "3. What are their interests?")
    bot.register_next_step_handler(msg, process_q3)

def process_q3(message):
    if not check_user(message): return
    user_data[message.chat.id].append(message.text)
    msg = bot.send_message(message.chat.id, "4. What is your budget?")
    bot.register_next_step_handler(msg, process_q4)

def process_q4(message):
    if not check_user(message): return
    user_data[message.chat.id].append(message.text)
    msg = bot.send_message(message.chat.id, "5. Anything they dislike?")
    bot.register_next_step_handler(msg, final_gemini_call)

def final_gemini_call(message):
    if not check_user(message): return
    user_data[message.chat.id].append(message.text)
    answers = user_data.pop(message.chat.id) # Use .pop() to get data and clear it at once
    
    bot.send_message(message.chat.id, "🔍 Consulting the gift experts...")
    
    prompt = f"""
    Suggest 10 gifts based on:
    Target: {answers[0]} | Occasion: {answers[1]} | Interests: {answers[2]} | Budget: {answers[3]} | Dislikes: {answers[4]}
    Output ONLY a numbered list of gift names. No descriptions.
    """
    
    try:
        # Note: model name might need '-latest' suffix depending on library version
        response = client.models.generate_content(
            model="gemini-2.5-flash", 
            contents=prompt
        )
        bot.reply_to(message, response.text)
    except Exception as e:
        print(f"Gemini Error: {e}")
        bot.reply_to(message, "Sorry, I hit a limit or the AI is busy. Try again in 30 seconds.")

bot.polling(none_stop=True)
