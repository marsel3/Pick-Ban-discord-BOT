import datetime
import random
import discord
from discord.ext import commands

TOKEN = "ODE5OTEwNDU4NTUwOTExMDI2.YEtfHg.ZfMy4G0IvqvgrZ3ZytnIi8SLgQU"   # Токен бота

# для проверки списка пользователей
intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix='//', intents=intents)

cap1_id = ''
cap2_id = ''
maps = {'🏝': 'Mirage', '☢': 'Nuke',
        '⌛': 'Dust II', '🌇': 'Inferno',
        '🚂': 'Train', '🌋': 'Vertigo',
        '🐉': 'Overpass'}    # Для отображения текста и эмодзи(можно менять)

pick_ban_maps = []  # хранение выбранных карт
order = 1           # последовательность ходов
count_of_pick = 0   # количество игр


@bot.event  # Проверка работоспособности бота
async def on_ready():
    print(f'Я готов {bot.user.name}')
    print('--------------------')


@bot.command(name='info')   # Используя эту команду, пользователи могут узнать информацию о работе бота
async def info(msg):
    await msg.channel.send(f'Задайте команду типа: \n'
                           f'"//play 1/3/5 @captain1 @captain2"\n'
                           f'Где 1 или 3 или 5 это количество карт которые будут сыграны,\n'
                           f'А @captain1 и @captain2 капитаны команд(пикают и банят карты)\n'
                           f'Если капитан(ы) не пикают и не банят, воспользуйтесь "//break" для прекращения процесса')


@bot.command(name='play', pass_context=True)   # Основная функция.
async def play(msg, *args):
    global cap1_id, cap2_id, maps, count_of_pick

    list_of_members_id = users_id()

    try:    # try, except, чтобы бота не ломали
        num, cap1, cap2 = args

        if not int(num) in [1, 3, 5]:   # Возможная ошибка №1
            await msg.channel.send('Только 1, 3 или 5 карт погут быть сыграны!')

        elif not(cap1 in list_of_members_id and cap2 in list_of_members_id):    # Возможная ошибка №2
            await msg.channel.send('Ник капитана должен начинаться с @, капитан должен быть участником сервера!')

        else:
            c = 1
            text = ''

            for emoji, map in maps.items():     # Эмодзи и текст берутся из словаря карт
                text += f'{c}.{emoji}{map}\n'
                c += 1

            message = await msg.send(text)
            for emoji, map in maps.items():
                await message.add_reaction(emoji)

            first_ban = random.choice([cap1, cap2])
            await msg.channel.send(f'Первый карту банит {first_ban}')

            count_of_pick = num
            cap1_id = cap1[3:-1]    # Оставляет только ID(цифры)
            cap2_id = cap2[3:-1]    # Оставляет только ID(цифры)
            if first_ban == cap2:   # Первыйм будет считаться капитан, который делает выбор первым
                cap1_id, cap2_id = cap2_id, cap1_id

    except:
        await msg.channel.send('Формат ввода: "//play количество\_игр @captain1 @captain2"'
                               '\nПодробнее в команде //info')


# Получение реакции на сообщение
@bot.event
async def on_raw_reaction_add(payload):
    global cap1_id, cap2_id, pick_ban_maps, order, maps, count_of_pick

    message_id = payload.message_id    # ID сообщения
    channel_id = payload.channel_id   # ID канала
    channel = bot.get_channel(channel_id)     # Получаем канал
    message = await channel.fetch_message(message_id)  # Получаем сообщение
    author = message.author    # Автор сообщения
    user_id = payload.user_id     # ID пользователя, который добавил реакцию
    user = channel.guild.get_member(user_id)  # Пользователь, который добавил реакцию

    if int(user_id) in [int(cap1_id), int(cap2_id)]:
        if order == 1:    # Обработка хода первого капитана, только в свою очередь
            if int(user_id) == int(cap1_id):
                order = 2
                await message.clear_reaction(payload.emoji)
                pick_ban_maps.append(payload.emoji)

        elif order == 2:    # Обработка хода второго капитана, только в свою очередь
            if int(user_id) == int(cap2_id):
                order = 1
                await message.clear_reaction(payload.emoji)
                pick_ban_maps.append(payload.emoji.name)

    if len(pick_ban_maps) == len(maps):     # Если число выбранных карт равно общему числу карт
        correct_map = []
        if int(count_of_pick) == 1:
            correct_map = [maps[str(pick_ban_maps[-1])]]
        elif int(count_of_pick) == 3:
            correct_map = [maps[str(pick_ban_maps[2])], maps[str(pick_ban_maps[3])], maps[str(pick_ban_maps[-1])]]
        elif int(count_of_pick) == 5:
            correct_map = [maps[str(pick_ban_maps[2])], maps[str(pick_ban_maps[3])],
             maps[str(pick_ban_maps[4])], maps[str(pick_ban_maps[5])], maps[str(pick_ban_maps[6])]]

        await channel.send('Порядок матчей:')
        c = 1
        for map in correct_map:
            await channel.send(f'{c}. {map}')
            c += 1
        # Обновление данных
        pick_ban_maps = []
        count_of_pick = 0
        order = 1


@bot.command(name='break')      # Команда для обновления данных(чтобы старые данные не ломали работоспособность бота)
async def info(msg):
    global pick_ban_maps, order, count_of_pick
    pick_ban_maps = []
    order = 1
    count_of_pick = 0


def users_id():     # Функция для получения списка пользователей
    list_of_members = []
    for guild in bot.guilds:
        for member in guild.members:
            list_of_members.append(f'<@!{member.id}>')
    return list_of_members


bot.run(TOKEN)