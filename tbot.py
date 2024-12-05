import telebot
from telebot import types
import sqlite3
import configparser

config = configparser.ConfigParser()
config.read(r'../telegram.ini')
token = config.get('Telegram', 'token')


conn = sqlite3.connect('komandor.db')
cursor = conn.cursor()
cursor.execute('CREATE TABLE IF NOT EXISTS sales (id INTEGER PRIMARY KEY AUTOINCREMENT, product TEXT NOT NULL, cnt INTEGER)')
conn.commit()
# cursor.execute('INSERT INTO sales (product) VALUES (?)',['Водка', 20])
# conn.commit()
conn.close()

bot = telebot.TeleBot(token, parse_mode=None)

def get_count(message):
    product = message.text
    message = bot.send_message(message.chat.id, 'Введите количество')
    bot.register_next_step_handler(message, add_data, product)

def add_data(message, product):
    try:
        with sqlite3.connect('komandor.db') as conn:
            cursor = conn.cursor()
            cursor.execute('INSERT INTO sales (product, cnt) VALUES (?, ?)',
                        [product,message.text])
            conn.commit()
        bot.send_message(message.chat.id, 'Данные сохранены')
    except:
        bot.send_message(message.chat.id, 'Ошибка сохранения')    

def get_data(message):
    with sqlite3.connect('komandor.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM sales'.format(message.from_user.id))
        data = []
        for val in cursor.fetchall(): 
            data.append(f"{val[0]} {val[1]} {val[2]}")
        if len(data)>0:
            return "\n".join(data)
        else:
            return "Данные отсутствуют"
        
def clear_data(message):
    with sqlite3.connect('komandor.db') as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM sales')
        conn.commit()
    return "Данные удалены"

@bot.message_handler(commands=['start']) 
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    send_message = (f'<b>Привет {message.from_user.first_name} {message.from_user.last_name} </b>')
    bot.send_message(message.chat.id, send_message, parse_mode='html', reply_markup=markup)

@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)

    if message.text == "Добавить товар":
        message = bot.send_message(message.chat.id, 'Введите название товара', reply_markup=None)
        bot.register_next_step_handler(message, get_count)

    if message.text == "Выбрать товары":
        bot.send_message(message.from_user.id, get_data(message), reply_markup=markup)

    if message.text == "Очистить базу":
        bot.send_message(message.from_user.id, clear_data(message), reply_markup=markup)

    btn1 = types.KeyboardButton("Добавить товар")
    btn2 = types.KeyboardButton('Выбрать товары')
    btn3 = types.KeyboardButton('Очистить базу')
    markup.add(btn1, btn2)
    bot.send_message(message.from_user.id, "Выберите действие", reply_markup=markup)

if __name__ == "__main__":
    bot.polling(none_stop=True)