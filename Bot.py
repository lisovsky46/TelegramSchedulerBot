from concurrent.futures import thread
from datetime import date, datetime, timedelta
from operator import mod
import threading
from time import time
import telebot
import Db
import settings




# commands
set_required_votes_count_cmd = 'set_required_votes_count'
start_cmd = 'start'
stop_cmd = 'stop'
hit_on_sat_cmd = 'hit_me_on_saturday'
hit_me_now_cmd = 'hit_me_right_now'
schedule_cmd = 'schedule'

commands = [
    telebot.types.BotCommand(set_required_votes_count_cmd, 'set_required_votes_count'),
    telebot.types.BotCommand(start_cmd, 'start'),
    telebot.types.BotCommand(schedule_cmd, 'schedule'),
    # telebot.types.BotCommand(hit_on_sat_cmd, 'do saturday polls'),
    telebot.types.BotCommand(hit_me_now_cmd, 'poll now')
]
# commands



subscribers = list[int]()
polls = dict[int, telebot.types.Poll]()

# init
db = Db.bot_db()
db.connect()
db.try_create()
db_chats = list(db.get_all_chats())
db_polls = dict(db.get_all_polls())

bot = telebot.TeleBot(settings.API_KEY)
bot.set_my_commands(commands)
# init




@bot.message_handler(commands=[start_cmd])
def start(message:telebot.types.Message):
    chat_id = message.chat.id
    if any(chat_id == db_chat.chat_id for db_chat in db_chats):
        print('nope')
    else:
        members_count = bot.get_chat_member_count(chat_id) - 1
        db.add_chat(chat_id, message.chat.title, members_count)
        reload_chats()




@bot.message_handler(commands=[stop_cmd])
def stop(message:telebot.types.Message):
    chat_id = message.chat.id
    db.delete_chat(chat_id)
    reload_chats()



@bot.message_handler(commands=[set_required_votes_count_cmd])
def update_members_count(message:telebot.types.Message):
    chat_id = message.chat.id
    count = message.text.split(' ')[1]
    db.update_user_count(chat_id, count)
    reload_chats()

    

@bot.message_handler(commands=[hit_on_sat_cmd])
def subscribe( message:telebot.types.Message):
    subscribers.append(message.chat.id)
    bot.reply_to(message, 'You got it')



@bot.message_handler(commands=[hit_me_now_cmd])
def subscribe( message:telebot.types.Message):
    invite(message.chat.id, 'sup everyone, wanna do some stuff?')



def poll_filter(message):
    return True

@bot.poll_handler(poll_filter)
def handle_poll_update(poll:telebot.types.Poll):
    chat_id = db_polls[poll.id]
    chat = next ((chat for chat in db_chats if chat.chat_id == str(chat_id)), None)
    max_votes = max(poll.voter_count for poll in poll.options)
    options = list[telebot.types.PollOption]()
    message = str()
    if (poll.total_voter_count == chat.members_count):
        for option in poll.options:
            if (option.voter_count == max_votes):
                options.append(option)
                message += option.text + ' '
    

        # date_str = options[0].text.split(' ')[1]
        # time_str = '19:00'
        # time_now = datetime.utcnow() + timedelta(minutes=1)
        # time_str = time_now.time().strftime('%H:%M')
        # datetime_str = ' '.join([date_str, time_str])
        # date_to_schedule = datetime.strptime(datetime_str, '%d.%m %H:%M')
        # delay = date_to_schedule - datetime.utcnow()

        sent_msg = bot.send_message(chat_id, "it's over Anakin, your option(s): " + message)
        bot.pin_chat_message(chat_id, sent_msg.id)
        #bot.unpin_chat_message todo

        # t = threading.Timer(delay.seconds, send_reminder, args=(chat_id, message))
        # t.start()


# def schedule_reminder(chat_id, message):
#     date_str = options[0].text.split(' ')[1]
#     # time_str = '19:00'
#     time_now = datetime.utcnow() + timedelta(minutes=1)
#     time_str = time_now.time().strftime('%H:%M')
#     datetime_str = ' '.join([date_str, time_str])
#     date_to_schedule = datetime.strptime(datetime_str, '%d.%m %H:%M')
#     delay = date_to_schedule - datetime.utcnow()

def send_reminder(chat_id, message):
    bot.send_message(chat_id, "reminder: " + message)

@bot.poll_answer_handler()
def handle_poll_answer( answer:telebot.types.PollAnswer):
    # if (answer.poll_id)
    pass


def saturday_invitation():
    for subscriber in subscribers:
        message = 'sup everyone, wanna do some stuff next week?'
        invite(subscriber, message)


def invite(chat_id:int, message):
    
    today = datetime.today()
    days_offset = (8 - today.isoweekday()) % 7

    days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
    options = []

    for day in days:
        date_str = (today + timedelta(days_offset)).strftime('%d.%m')
        option = ' '.join([day, date_str])
        options.append(option) 
        days_offset += 1


    msg = bot.send_poll(chat_id, message, options, True, allows_multiple_answers=True)
    poll:telebot.types.Poll = msg.poll
    db.add_poll(chat_id, poll.id)
    db_polls[poll.id] = chat_id
    polls[poll.id] = poll



def reload_chats():
    db_chats = list(db.get_all_chats())
    pass




def start_polling():
    bot.polling()
