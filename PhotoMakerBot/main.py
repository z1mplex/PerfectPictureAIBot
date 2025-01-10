import telebot
import requests
import json
from googletrans import Translator
import time

bot = telebot.TeleBot("")
api_token = ""
url = 'https://api.vyro.ai/v1/imagine/api/generations'
feedback_file = 'feedback.json'
language_file = 'language.json'

user_language = {}
user_feedback = {}

def load_language():
    try:
        with open(language_file, 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def save_language():
    with open(language_file, 'w', encoding='utf-8') as file:
        json.dump(user_language, file, ensure_ascii=False, indent=4)

def get_translation(lang, key):
    translations = {
        'uk': {
            'welcome': "Привіт, {name}! Виберіть опцію з меню:",
            'choose_language': "Виберіть мову / Choose your language",
            'services_info': """
            🌟 Інформація про наші послуги 🌟

            1. 📸 Професійні фотосесії:
               - Індивідуальні та сімейні фотосесії.
               - Весільні та урочисті фотосесії.
               - Дитячі та новонароджені фотосесії.

            2. 🌐 Цифровий контент:
               - Створення та редагування зображень для соціальних мереж.
               - Дизайн банерів та рекламних матеріалів.

            3. 🖼️ Обробка та ретушування:
               - Професійне ретушування фотографій.
               - Виправлення кольорів та освітлення.

            4. 🎨 Графічний дизайн:
               - Розробка логотипів та брендової атрибутики.
               - Дизайн поліграфічних матеріалів (візитки, листівки, плакати).

            5. 📷 Оренда фотостудії:
               - Оренда студійного обладнання та простору для зйомок.
               - Консультації та допомога професійних фотографів.
            """,
            'website': "Відвідайте наш веб-сайт за адресою: https://linktr.ee/indigophoto",
            'apply_session': "Для подачі заявки на фотосесію, будь ласка, заповніть нашу форму за даним посиланням: https://docs.google.com/forms/d/e/1FAIpQLSenSpsNeJVz8Nmlio-27T2vzZe2JO5DrBnxzLSb-_FPdeqpPA/viewform?usp=sf_link",
            'generate_image_prompt': "Введіть, будь ласка, опис того, що хочете згенерувати.",
            'feedback_prompt': "Напишіть ваше повне ім'я.",
            'feedback_email_prompt': "Напишіть вашу електронну пошту.",
            'feedback_text_prompt': "Напишіть ваші ідеї, пропозиції або відгуки.",
            'thank_you_feedback': "Дякуємо за ваш відгук!",
            'image_gen_error': "На жаль, я поки що не вмію цього робити 😔",
            'back_to_menu': "Повертаємось до меню",
            'change_language': "Змінити мову"
        },
        'en': {
            'welcome': "Hello, {name}! Choose an option from the menu:",
            'choose_language': "Виберіть мову / Choose your language",
            'services_info': """
            🌟 Information about our services 🌟

            1. 📸 Professional Photoshoots:
               - Individual and family photoshoots.
               - Wedding and ceremonial photoshoots.
               - Children and newborn photoshoots.

            2. 🌐 Digital Content:
               - Creation and editing of images for social media.
               - Design of banners and advertising materials.

            3. 🖼️ Editing and Retouching:
               - Professional photo retouching.
               - Color and lighting correction.

            4. 🎨 Graphic Design:
               - Logo and brand identity development.
               - Design of printed materials (business cards, flyers, posters).

            5. 📷 Studio Rental:
               - Rental of studio equipment and shooting space.
               - Consultations and assistance from professional photographers.
            """,
            'website': "Visit our website at: https://linktr.ee/indigophoto",
            'apply_session': "To apply for a photo session, please fill out our form at: https://docs.google.com/forms/d/e/1FAIpQLSfoPcQKYRZHHCuxLDIbZwIWefg8yKezfKap97EGYAIA-NYO6A/viewform?usp=sf_link",
            'generate_image_prompt': "Please enter the description of what you want to generate.",
            'feedback_prompt': "Please enter your full name.",
            'feedback_email_prompt': "Please enter your email address.",
            'feedback_text_prompt': "Please enter your ideas, suggestions, or feedback.",
            'thank_you_feedback': "Thank you for your feedback!",
            'image_gen_error': "Unfortunately, I can't do that yet 😔",
            'back_to_menu': "Back to Menu",
            'change_language': "Change language"
        }
    }
    return translations[lang][key]

def get_main_menu_markup(lang):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    if lang == 'uk':
        markup.row('Інформація про послуги', 'Наш веб-сайт')
        markup.row('Подати заявку на фотосесію', 'Згенерувати зображення')
        markup.row('Зворотній зв\'язок', 'Змінити мову')
    elif lang == 'en':
        markup.row('Information about services', 'Our website')
        markup.row('Apply for a photoshoot', 'Generate an image')
        markup.row('Feedback', 'Change language')
    return markup

def get_back_to_menu_markup(lang):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    if lang == 'uk':
        markup.row("Назад до меню")
    elif lang == 'en':
        markup.row("Back to Menu")
    return markup

main_menu_markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
main_menu_markup.row('Інформація про послуги', 'Наш веб-сайт')
main_menu_markup.row('Подати заявку на фотосесію', 'Згенерувати зображення')
main_menu_markup.row('Зворотній зв\'язок', 'Змінити мову')

language_markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
language_markup.row('Українська', 'English')

@bot.message_handler(commands=["start"])
def start(message):
    user_id = message.from_user.id
    bot.send_message(message.chat.id, get_translation('uk', 'choose_language'), reply_markup=language_markup)
    bot.register_next_step_handler(message, set_language)

def set_language(message):
    user_id = message.from_user.id
    if message.text:
        if message.text.lower() == 'українська':
            user_language[user_id] = 'uk'
            save_language()
            bot.send_message(message.chat.id, "Вибрано українську мову.", reply_markup=get_main_menu_markup('uk'))
        elif message.text.lower() == 'english':
            user_language[user_id] = 'en'
            save_language()
            bot.send_message(message.chat.id, "English language selected.", reply_markup=get_main_menu_markup('en'))
        else:
            bot.send_message(message.chat.id, get_translation('uk', 'choose_language'), reply_markup=language_markup)
            return
    else:
        bot.send_message(message.chat.id, get_translation('uk', 'choose_language'), reply_markup=language_markup)
        return

@bot.message_handler(func=lambda message: message.text.lower() in ['інформація про послуги', 'information about services'])
def services_info(message):
    lang = user_language.get(message.from_user.id, 'uk')
    bot.send_message(message.chat.id, get_translation(lang, 'services_info'))

@bot.message_handler(func=lambda message: message.text.lower() in ['наш веб-сайт', 'our website'])
def our_website(message):
    lang = user_language.get(message.from_user.id, 'uk')
    bot.send_message(message.chat.id, get_translation(lang, 'website'))

@bot.message_handler(func=lambda message: message.text.lower() in ['подати заявку на фотосесію', 'apply for a photoshoot'])
def apply_photo_session(message):
    lang = user_language.get(message.from_user.id, 'uk')
    bot.send_message(message.chat.id, get_translation(lang, 'apply_session'))

@bot.message_handler(func=lambda message: message.text.lower() in ['згенерувати зображення', 'generate an image'])
def handle_generate_image_request(message):
    lang = user_language.get(message.from_user.id, 'uk')
    prompt_text = get_translation(lang, 'generate_image_prompt')
    bot.send_message(message.chat.id, prompt_text, reply_markup=get_back_to_menu_markup(lang))
    bot.register_next_step_handler(message, handle_generate_image)

@bot.message_handler(func=lambda message: message.text.lower() in ['зворотній зв\'язок', 'feedback'])
def feedback(message):
    lang = user_language.get(message.from_user.id, 'uk')
    bot.send_message(message.chat.id, get_translation(lang, 'feedback_prompt'), reply_markup=get_back_to_menu_markup(lang))
    bot.register_next_step_handler(message, get_full_name)

@bot.message_handler(func=lambda message: message.text.lower() in ['змінити мову', 'change language'])
def change_language(message):
    bot.send_message(message.chat.id, get_translation('uk', 'choose_language'), reply_markup=language_markup)
    bot.register_next_step_handler(message, set_language)

def get_full_name(message):
    user_id = message.from_user.id

    if message.text is None:
        lang = user_language.get(user_id, 'uk')
        if lang == 'en':
            response = "I don't understand your question."
        else:
            response = "Не розумію вашого запиту."
        bot.send_message(message.chat.id, response)
        return

    if message.text.lower() == 'назад до меню' or message.text.lower() == 'back to menu':
        back_to_menu_simple(message)
    else:
        user_id = message.from_user.id
        user_feedback[user_id] = {'full_name': message.text}
        lang = user_language.get(user_id, 'uk')
        bot.send_message(message.chat.id, get_translation(lang, 'feedback_email_prompt'),
                         reply_markup=get_back_to_menu_markup(lang))
        bot.register_next_step_handler(message, get_email)

def get_email(message):
    user_id = message.from_user.id

    if message.text is None:
        lang = user_language.get(user_id, 'uk')
        if lang == 'en':
            response = "I don't understand your question."
        else:
            response = "Не розумію вашого запиту."
        bot.send_message(message.chat.id, response)
        return

    if message.text.lower() == 'назад до меню' or message.text.lower() == 'back to menu':
        back_to_menu_simple(message)
    else:
        user_id = message.from_user.id
        user_feedback[user_id]['email'] = message.text
        lang = user_language.get(user_id, 'uk')
        bot.send_message(message.chat.id, get_translation(lang, 'feedback_text_prompt'),
                         reply_markup=get_back_to_menu_markup(lang))
        bot.register_next_step_handler(message, get_feedback)

def get_feedback(message):
    user_id = message.from_user.id

    if message.text is None:
        lang = user_language.get(user_id, 'uk')
        if lang == 'en':
            response = "I don't understand your question."
        else:
            response = "Не розумію вашого запиту."
        bot.send_message(message.chat.id, response)
        return

    if message.text.lower() == 'назад до меню' or message.text.lower() == 'back to menu':
        back_to_menu_simple(message)
    else:
        if user_id not in user_feedback:
            user_feedback[user_id] = {}
        user_feedback[user_id]['feedback_text'] = message.text
        save_feedback(user_feedback[user_id])
        lang = user_language.get(user_id, 'uk')
        bot.send_message(message.chat.id, get_translation(lang, 'thank_you_feedback'),
                         reply_markup=get_main_menu_markup(lang))

def handle_generate_image(message):
    user_id = message.from_user.id

    if message.text is None:
        if user_id in user_language and user_language[user_id] == 'en':
            bot.send_message(message.chat.id, "I don't understand your question.")
        else:
            bot.send_message(message.chat.id, "Не розумію вашого запиту.")
        return

    if message.text.lower() == 'назад до меню' or message.text.lower() == 'back to menu':
        back_to_menu_simple(message)
    else:
        prompt_text = message.text
        translated_text = translate_text(prompt_text)
        print(f"Переклад на англійську: {translated_text}")
        response = generate_image(translated_text)
        if response.status_code == 200:
            with open('image.jpg', 'wb') as f:
                f.write(response.content)
            bot.send_photo(message.chat.id, open('image.jpg', 'rb'))
            print('Фотографія успішно згенерована та відправлена.')
        else:
            if user_id in user_language and user_language[user_id] == 'en':
                bot.send_message(message.chat.id, "I don't understand your question.")
            else:
                bot.send_message(message.chat.id, get_translation(user_language[user_id], 'image_gen_error'))
            print('Помилка:', response.status_code)

def translate_text(text):
    translator = Translator()
    translated_text = translator.translate(text, src='auto', dest='en').text
    return translated_text


def generate_image(prompt_text):
    headers = {
        'Authorization': 'Bearer ' + api_token
    }

    payload = {
        'prompt': (None, prompt_text),
        'style_id': (None, '29')
    }

    response = requests.post(url, headers=headers, files=payload)
    return response

def save_feedback(feedback_data):
    with open(feedback_file, 'a', encoding='utf-8') as file:
        json.dump(feedback_data, file, ensure_ascii=False)
        file.write('\n')

def back_to_menu_simple(message):
    user_id = message.from_user.id
    lang = user_language.get(user_id, 'uk')
    bot.send_message(message.chat.id, get_translation(lang, 'back_to_menu'),
                     reply_markup=get_main_menu_markup(lang))

@bot.message_handler(content_types=['photo', 'video', 'audio', 'voice', 'document', 'sticker', 'location', 'contact', 'animation'])
def handle_media(message):
    lang = user_language.get(message.from_user.id, 'uk')
    if lang == 'en':
        bot.send_message(message.chat.id, "I don't understand your question. Please choose an option from the menu:",
                         reply_markup=get_main_menu_markup(lang))
    else:
        bot.send_message(message.chat.id, "Я вас не розумію, оберіть опцію з меню:",
                         reply_markup=get_main_menu_markup(lang))
    time.sleep(3)
    bot.delete_message(message.chat.id, message.message_id)



@bot.message_handler(func=lambda message: True)
def handle_text(message):
    user_id = message.from_user.id
    lang = user_language.get(user_id, 'uk')

    if message.text == get_translation(lang, 'generate_image_prompt'):
        handle_generate_image(message)
        return

    if message.text.lower() in ['назад до меню', 'back to menu']:
        back_to_menu_simple(message)
        return

    if lang == 'en':
        bot.send_message(message.chat.id, "I don't understand your question. Please choose an option from the menu:",
                         reply_markup=get_main_menu_markup(lang))
    else:
        bot.send_message(message.chat.id, "Я вас не розумію, оберіть опцію з меню:",
                         reply_markup=get_main_menu_markup(lang))
    time.sleep(3)
    bot.delete_message(message.chat.id, message.message_id)

bot.polling()
