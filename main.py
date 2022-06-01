import telebot
from telebot import types
from telebot.types import ReplyKeyboardMarkup
from telebot.types import InlineKeyboardButton
import re

token = ''
bot = telebot.TeleBot(token)

chat_id = '-680473958'

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    pay = types.KeyboardButton('Оплатить за интернет')
    add = types.KeyboardButton('Оставить заявку на добавление/изменение MAC адреса')
    check = types.KeyboardButton('Проверить статус заявки')
    report = types.KeyboardButton('Сообщить о проблеме')
    markup.add(pay, add, check, report)
    mess = f'Привет, {message.from_user.first_name}\nВыбери проблему'
    bot.send_message(message.chat.id, mess, parse_mode='html', reply_markup=markup)


@bot.message_handler(commands=['add', 'check', 'report'])
def wip(message):
    bot.send_message(message.chat.id, 'В скором времени данная функция будет добавлена')


@bot.message_handler(content_types=['text'])
def pay(message):
    if message.text == 'Оплатить за интернет':
        msg = bot.send_message(message.chat.id, 'Введите ФИО')
        bot.register_next_step_handler(msg, fio_register)
    elif message.text == 'Проверить статус заявки' or message.text == 'Сообщить о проблеме' or message.text == 'Оставить заявку на добавление/изменение MAC адреса':
        bot.send_message(message.chat.id, 'В скором времени данная функция будет добавлена')
    else:
        bot.send_message(message.chat.id, 'Я тебя не понимаю.')


def fio_register(message):
    global fio
    fio = message.text

    msg = bot.send_message(message.chat.id, 'Введите IP')
    bot.register_next_step_handler(msg, validate_ip)


def again(message):
    msg = bot.send_message(message.chat.id, 'Введите IP снова')
    bot.register_next_step_handler(msg, validate_ip)


def validate_ip(message):
    global ipp
    ipp = message.text

    if re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", message.text):
        amount_enter(message)
    else:
        msg = bot.reply_to(message, 'IP адрес должен содержать только цифры. Введите снова IP адрес')
        again(message)


def amount_enter(message):
    global ipp
    ipp = message.text

    msg = bot.send_message(message.chat.id, 'Введите сумму')
    bot.register_next_step_handler(msg, final)


def final(message):
    global amount
    amount = message.text

    markup_pay = types.InlineKeyboardMarkup()
    button_1 = types.InlineKeyboardButton("Оплатить", url="https://www.tinkoff.ru/cf/50CxiWeHAiD", callback_data='pay')
    button_2 = types.InlineKeyboardButton("Готово", callback_data='done')
    markup_pay.add(button_1, button_2)
    bot.send_message(message.chat.id, 'Выберите способ оплаты.\nПосле оплаты нажмите <b>готово</b>', parse_mode='html',
                     reply_markup=markup_pay)


@bot.callback_query_handler(func=lambda call: True)
def payment_check(call):
    if call.data == "done":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        link = types.KeyboardButton('Ссылка на чек')
        photo = types.KeyboardButton('Скриншот оплаты')
        document = types.KeyboardButton('Чек в формате pdf')
        markup.add(link, photo, document)
        msg = bot.send_message(call.from_user.id, 'Выбери способ подтверждения оплаты', reply_markup=markup)
        bot.register_next_step_handler(msg, payment_methods)


def payment_methods(message):
    if message.text == 'Ссылка на чек':
        msg = bot.send_message(message.chat.id, 'Введите ссылку на чек')
        bot.register_next_step_handler(msg, text_payment)
    elif message.text == 'Скриншот оплаты':
        msg = bot.send_message(message.chat.id, 'Пришлите фото оплаты')
        bot.register_next_step_handler(msg, photo_payment)
    elif message.text == 'Чек в формате pdf':
        msg = bot.send_message(message.chat.id, 'Отправьте чек в формате pdf')
        bot.register_next_step_handler(msg, document_payment)
    else:
        bot.send_message(message.chat.id, 'Надо выбрать один из вариантов. Попробуй еще раз.')
        return payment_check


def text_payment(message):
    global link
    link = message.text
    msg = bot.reply_to(message, 'Оплата принята. В течении 24 часов Ваш баланс будет пополнен')
    user_name = message.from_user.username
    bot.send_message(chat_id, f'@{user_name} произвел оплату.' f'\nФИО: {fio} \nIP: {ipp} \nСумма: {amount} \nСсылка: {link}', parse_mode='html')


@bot.message_handler(content_types=['photo'])
def photo_payment(message):
    global photo
    photo = message.photo[0].file_id
    bot.reply_to(message, 'Оплата принята. В течении 24 часов Ваш баланс будет пополнен')
    user_name = message.from_user.username
    msg = bot.send_photo(chat_id, photo)
    bot.reply_to(msg, f'@{user_name} произвел оплату.' f'\nФИО: {fio} \nIP: {ipp} \nСумма: {amount}', parse_mode='html')


@bot.message_handler(content_types=['document'])
def document_payment(message):
    global document
    document = message.document.file_id
    bot.reply_to(message, 'Оплата принята. В течении 24 часов Ваш баланс будет пополнен')
    user_name = message.from_user.username
    msg = bot.send_document(chat_id, document)
    bot.reply_to(msg, f'@{user_name} произвел оплату.' f'\nФИО: {fio} \nIP: {ipp} \nСумма: {amount}', parse_mode='html')


bot.infinity_polling()
