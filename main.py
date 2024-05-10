import telebot
from config import TOKEN
from question import Question
from pathlib import Path
import yaml
from random import choice

bot = telebot.TeleBot(TOKEN)

START_MESSAGE = ("🚉 *Приветствуем вас!*\n\nСегодня мы предлагаем вам пройти квиз, посвященный истории единственного "
                 "железнодорожного вокзала в Перми - Пермь II.\nОн имеет богатую историю и играет важную роль в "
                 "развитии железнодорожного транспорта в регионе.\nВас ждут 10 вопросов, которые позволят определить "
                 "насколько вы усвоили информацию.\nОценка за ваши ответы будет зависеть от количества правильных "
                 "решений:\n\n🥉 1-4 правильных ответа - _оценка 2_\n🥈 5-6 правильных ответов - _оценка 3_\n🥇 7-8 "
                 "правильных ответов - _оценка 4_\n🏆 9-10 правильных ответов - _оценка 5_\n\nГотовы ли вы проверить "
                 "свои знания о вокзале *Пермь II*?\nТогда давайте начнем! 🌟")

AUTHORIZED_USERS = []
STARTED_QUIZ_USERS = {}

QUESTIONS = {q['id']: Question(q['id'], q['q'], q['a']) for q in
             yaml.load(Path('questions.yaml').read_text(encoding='utf-8'), Loader=yaml.FullLoader)}


@bot.message_handler(commands=['start'])
def start_message(message):
    user_id = message.chat.id
    if user_id not in AUTHORIZED_USERS:
        print(f'User {user_id} started the bot')
        AUTHORIZED_USERS.append(user_id)
        keyboard = telebot.types.InlineKeyboardMarkup()
        keyboard.add(telebot.types.InlineKeyboardButton(text="🧠 Начать квиз!", callback_data="start"))
        bot.send_message(user_id, START_MESSAGE, reply_markup=keyboard, parse_mode="Markdown")
    else:
        bot.send_message(user_id, "Вы уже запустили бота")


@bot.message_handler(commands=['restart_quiz'])
def restart_message(message):
    user_id = message.chat.id
    if user_id not in AUTHORIZED_USERS:
        bot.send_message(user_id, "Напишите команду /start, чтобы начать")
        return
    STARTED_QUIZ_USERS[user_id] = {'questions': list(QUESTIONS.keys()),
                                   'correct_answers': 0,
                                   'answers': {},
                                   'current_question': None,
                                   'current_q_num': 1}
    print(f'User {user_id} restarted the quiz')
    bot.send_message(user_id, "Начинаем квиз заново...")
    if len(STARTED_QUIZ_USERS[user_id]['questions']) > 0:
        question_id = choice(STARTED_QUIZ_USERS[user_id]['questions'])
        STARTED_QUIZ_USERS[user_id]['current_question'] = question_id
        question = QUESTIONS[question_id]
        keyboard = telebot.types.InlineKeyboardMarkup()
        buts = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣']
        row = []
        for i in range(len(question.answers)):
            row.append(telebot.types.InlineKeyboardButton(text=buts[i], callback_data=f'a_{i + 1}'))
        keyboard.row(*row)
        out_message = (f"*Вопрос №{STARTED_QUIZ_USERS[user_id]['current_q_num']}*.\n\n{question.text}\n\nВарианты "
                       f"ответа:\n") + \
                      '\n'.join([f"{i + 1}. {question.answers[i]}" for i in range(len(question.answers))])
        bot.send_message(user_id, out_message, reply_markup=keyboard, parse_mode="Markdown")


@bot.callback_query_handler(func=lambda call: True)
def handle_call(call):
    user_id = call.message.chat.id
    message_id = call.message.message_id
    if user_id not in AUTHORIZED_USERS:
        return
    if call.data == 'start':
        if user_id not in STARTED_QUIZ_USERS:
            STARTED_QUIZ_USERS[user_id] = {'questions': list(QUESTIONS.keys()),
                                           'correct_answers': 0,
                                           'answers': {},
                                           'current_question': None,
                                           'current_q_num': 1}
            print(f'User {user_id} started the quiz')
            bot.edit_message_reply_markup(user_id, message_id, reply_markup=None)

    if call.data in [f'a_{'123456789'[i]}' for i in range(9)]:
        answer_id = int(call.data[2:]) - 1
        question_id = STARTED_QUIZ_USERS[user_id]['current_question']
        question = QUESTIONS[question_id]
        if answer_id < len(question.answers):
            STARTED_QUIZ_USERS[user_id]['answers'][question_id] = answer_id
            if answer_id == question.correct:
                print(f'User {user_id} answered correctly')
                STARTED_QUIZ_USERS[user_id]['correct_answers'] += 1

    if len(STARTED_QUIZ_USERS[user_id]['questions']) > 0:
        question_id = choice(STARTED_QUIZ_USERS[user_id]['questions'])
        STARTED_QUIZ_USERS[user_id]['current_question'] = question_id
        question = QUESTIONS[question_id]
        keyboard = telebot.types.InlineKeyboardMarkup()
        buts = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣']
        row = []
        for i in range(len(question.answers)):
            row.append(telebot.types.InlineKeyboardButton(text=buts[i], callback_data=f'a_{i + 1}'))
        keyboard.row(*row)
        out_message = f"*Вопрос №{STARTED_QUIZ_USERS[user_id]['current_q_num']}*.\n\n{question.text}\n\nВарианты ответа:\n" + \
                      '\n'.join([f"{i + 1}. {question.answers[i]}" for i in range(len(question.answers))])
        if call.data == 'start':
            bot.send_message(user_id, out_message, reply_markup=keyboard, parse_mode="Markdown")
        elif call.data in [f'a_{'123456789'[i]}' for i in range(9)]:
            bot.edit_message_text(out_message, user_id, message_id, reply_markup=keyboard, parse_mode="Markdown")

        STARTED_QUIZ_USERS[user_id]['current_q_num'] += 1
        STARTED_QUIZ_USERS[user_id]['questions'].remove(question_id)
    else:
        correct_answers = STARTED_QUIZ_USERS[user_id]['correct_answers']
        match correct_answers:
            case 1 | 2 | 3 | 4:
                grade = 2
                grade_txt = "🥉\nК сожалению, вы плохо знакомы с историей Перми II, в канале [Пермь 2 | История Станции](https://t.me/perm2_zaimka) есть много информации! Дерзайте!"
            case 5 | 6:
                grade = 3
                grade_txt = "🥈\nВы... молодец. Но, мы верим, вы сможете больше.\nПереходите в канал [Пермь 2 | История Станции](https://t.me/perm2_zaimka), изучайте информацию, и результат будет лучше"
            case 7 | 8:
                grade = 4
                grade_txt = "🥇\nПоздравляем!\nВы хорошо знакомы с историей Перми II, но немножко все-таки не дотянули.\nПереходите в канал [Пермь 2 | История Станции](https://t.me/perm2_zaimka) добирайте информацию и возвращайтесь!"
            case 9 | 10:
                grade = 5
                grade_txt = "🏆\nТроекратно поздравляем! Вы идеально знаете историю Перми II.\nЕсли захотите освежить в памяти свои знания, переходите в канал [Пермь 2 | История Станции](https://t.me/perm2_zaimka)!"
        del STARTED_QUIZ_USERS[user_id]
        bot.delete_message(user_id, message_id)
        keyboard = telebot.types.InlineKeyboardMarkup()
        keyboard.add(telebot.types.InlineKeyboardButton(text="🧠 Начать квиз заново!", callback_data="start"))
        bot.send_message(user_id, f"{grade_txt}\n\nПравильных ответов: {correct_answers}\n\n*Оценка: {grade}*",
                         reply_markup=keyboard, parse_mode="Markdown")
        print(f'User {user_id} finished the quiz')


bot.polling(none_stop=True)
