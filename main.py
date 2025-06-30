import telebot
from telebot import types
import sqlite3 # import essentials

connection = sqlite3.connect('data.db', check_same_thread=False) # connecting to database
cursor = connection.cursor() # create a cursor for database

cursor.execute('''
CREATE TABLE IF NOT EXISTS data (
    user_id INTEGER,
    note TEXT
)
''') # create a database
connection.commit() # commit changes

API = '' # YOUR API-token for bot
bot = telebot.TeleBot(API) # create a bot class

@bot.message_handler(commands=['start'])
def start(message): # start function
    check_user_id(message.from_user.id)
    bot.send_message(message.from_user.id, f"👋 Hi, {message.from_user.first_name} {message.from_user.last_name}!\nThere you can make a note for yourself")
    main(message) 

def main(message): # main menu function 
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button_actual_note = types.KeyboardButton("My note 📄")
    button_create_note = types.KeyboardButton("Create task 💼")
    markup.add(button_actual_note, button_create_note)

    bot.send_message(message.from_user.id, "Choose the action:", reply_markup=markup)
    bot.register_next_step_handler(message, user_choice)

def user_choice(message): # function where is checking the user's choice
    answer = message.text
    
    if answer == "My note 📄":
        get_user_task(message, message.from_user.id)
    else:
        bot_takes_user_note(message, message.from_user.id)
    
def check_user_note(user_id): # function checks if user has any notes (True if yes, False if not)
    cursor.execute('SELECT note FROM data WHERE user_id=?', (user_id,))
    result = cursor.fetchone()
    if result[0] is None:
        return False
    else:
        return True

def update_user_note(message, user_id): # Updating user's note
    user_note = message.text
    check_result = check_user_note(user_id)
    
    if check_result == True:
        bot.send_message(user_id, "At first, complete your previous task.")
        main(message)
    else:
        cursor.execute('UPDATE data SET note=? WHERE user_id=?', (user_note, user_id,))
        connection.commit()
        bot.send_message(user_id, "✅ Successful!")
        main(message)

def bot_takes_user_note(message, user_id):
    bot.send_message(user_id, "✍️ Send me your note:")
    bot.register_next_step_handler(message, lambda m: update_user_note(m, user_id))

def action_with_task(message, user_id): # If user completed task, then bot delete his note. If not, then bot doesn't delete it
    answer = message.text

    if answer == "Yes ✅":
        cursor.execute('UPDATE data SET note=? WHERE user_id=?', (None, user_id,))
        connection.commit()

        bot.send_message(user_id, "Good job! See you later! 🚀")
        main(message)
    else:
        bot.send_message(user_id, "Good luck with it! 🚀")
        main(message)

def get_user_task(message, user_id): # function for checking user's note
    cursor.execute('SELECT note FROM data WHERE user_id=?', (user_id,))
    result = cursor.fetchone()
    if result[0] is None:
        bot.send_message(user_id, "❌ You don't have any notes yet.")
        main(message)
    if result[0] is not None:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        button_yes = types.KeyboardButton("Yes ✅")
        button_no = types.KeyboardButton("No ❌")
        markup.add(button_yes, button_no)
        bot.send_message(user_id, f"📄 Your actual note:\n\n{result[0]}\n\nHave you done this task?", reply_markup=markup)
        bot.register_next_step_handler(message, lambda m: action_with_task(m, user_id))

def check_user_id(user_id): # function for checking user id
    cursor.execute('SELECT * FROM data WHERE user_id=?', (user_id,))
    result = cursor.fetchone()
    if result is None:
        cursor.execute('INSERT INTO data (user_id) VALUES (?)', (user_id,))
        connection.commit()
   
bot.polling() # compile bot