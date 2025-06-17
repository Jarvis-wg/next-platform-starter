import telebot
from datetime import datetime

# ====== CONFIG ======
TOKEN = '7921075085:AAGnnd2ibua_MiICxLnoQamJFAlBKCUs8us'  # Bot token
GROUP_ID = -1002818537693  # Replace with your private group ID
GROUP_LINK = 'https://t.me/+-MDPcKZ9xj9iZTk1'  # Group invite link
BOT_USERNAME = 'Desileakshub_referral_bot'  # Bot username without '@'
# =====================

bot = telebot.TeleBot(TOKEN)

referrals = {}        # {referrer_id: [user_ids]}
leaderboard = {}      # {referrer_id: count}
user_links = {}       # {user_id: referral_link}

def is_online():
    now = datetime.now()
    return 7 <= now.hour < 22  # Active 7 AM to 10 PM

@bot.message_handler(commands=['start'])
def handle_start(message):
    user_id = message.from_user.id

    # Check bot online time
    if not is_online():
        bot.reply_to(message, "⏰ Bot abhi offline hai. Yeh sirf 7AM – 10PM tak active rehta hai.")
        return

    # Group membership check
    try:
        member = bot.get_chat_member(GROUP_ID, user_id)
        if member.status not in ['member', 'administrator', 'creator']:
            raise Exception("User not in group")
    except:
        bot.send_message(user_id, f"🚫 Pehle group join kijiye tabhi referral milega.\n👉 {GROUP_LINK}")
        return

    # Generate referral link (only once per user)
    if user_id not in user_links:
        referral_link = f"https://t.me/{BOT_USERNAME}?start={user_id}"
        user_links[user_id] = referral_link
    else:
        referral_link = user_links[user_id]

    # Handle referral logic
    args = message.text.split()
    referrer_id = args[1] if len(args) > 1 else None

    if referrer_id and str(user_id) != referrer_id:
        if referrer_id not in referrals:
            referrals[referrer_id] = []
        if str(user_id) not in referrals[referrer_id]:
            referrals[referrer_id].append(str(user_id))
            leaderboard[referrer_id] = leaderboard.get(referrer_id, 0) + 1

    # Display user info
    username = message.from_user.username
    first = message.from_user.first_name or ""
    last = message.from_user.last_name or ""
    display = f"@{username}" if username else f"{first} {last}".strip()

    # Send response
    bot.send_message(
        user_id,
        f"✅ *Referral Details:*\n\n"
        f"👤 *Name:* {display}\n"
        f"🆔 *Referral Code:* {user_id}\n"
        f"🔗 *Referral Link:* [Click here]({referral_link})",
        parse_mode="Markdown"
    )

@bot.message_handler(commands=['leaderboard'])
def handle_leaderboard(message):
    if not is_online():
        bot.reply_to(message, "⏰ Bot abhi offline hai. Leaderboard sirf 7AM–10PM tak hi dikhaya jata hai.")
        return

    if not leaderboard:
        bot.send_message(message.chat.id, "📉 Koi referral data available nahi hai.")
        return

    sorted_board = sorted(leaderboard.items(), key=lambda x: x[1], reverse=True)
    msg = "🏆 *Top Referrers:*\n\n"
    for i, (uid, count) in enumerate(sorted_board[:10]):
        msg += f"{i+1}. 👤 User {uid} – 🔁 {count} referrals\n"

    bot.send_message(message.chat.id, msg, parse_mode="Markdown")

# Run the bot
bot.polling(none_stop=True)