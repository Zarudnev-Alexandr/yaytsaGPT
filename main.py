from discord.ext import commands
import g4f
import discord
import asyncio
import re

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='/', intents=intents)

ban_words = ["Здравствуйте, это Bing.", "Bing", "bing"]

# Dictionary to store settings for each server
server_settings = {}


def gpt(query: str):
    response = g4f.ChatCompletion.create(
        model=g4f.models.gpt_4,
        messages=[{"role": "user", "content": query}],
    )
    return response


def filter_response(response):
    # Убираем запрещенные слова и фразы
    for word in ban_words:
        response = response.replace(word.lower(), "")
    return response


def split_message(text, max_length):
    # Разбиваем текст на части по максимальной длине
    return [text[i:i + max_length] for i in range(0, len(text), max_length)]


def remove_links(text):
    # Используем регулярное выражение для поиска и удаления ссылок
    return re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)


def remove_square_bracket_content(text):
    # Используем регулярное выражение для поиска и удаления текста в квадратных скобках
    text = re.sub(r'\[[^\]]+\]', '', text)
    # Удаляем строки вроде " :  "" и ((("
    text = re.sub(r'\s*[:\(\-]+\s*["\(]*\s*', '', text)
    return text


@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')


@bot.command(name='меню')
async def menu(ctx):

    if ctx.guild is None:
        await ctx.reply("Команда доступна только на серверах, а не в личных сообщениях.")
        return

    await ctx.send(
        "**📃меню арбузера📃**\n\n1)/распетляй {запрос} - запрос к ГПТшнику\n2)/настройка - нут, тут все понятно\n3)/изменить - описание команды в /настройка")


@bot.command(name='настройка')
async def settings(ctx):

    if ctx.guild is None:
        await ctx.reply("Команда доступна только на серверах, а не в личных сообщениях.")
        return

    guild_id = ctx.guild.id
    if guild_id not in server_settings:
        server_settings[guild_id] = {"enable_link_insertion": False}

    enable_link_insertion = server_settings[guild_id]["enable_link_insertion"]

    await ctx.send(f"**⚙настройки арбузера⚙**\n\n1 (вставка ссылок) - " + (
        "выключено⛔" if enable_link_insertion else "включено✅") + "\n\nЧтобы изменить настройку, напиши: /изменить {номер параметра}")


@bot.command(name='изменить')
async def change_setting(ctx, setting_number: int):

    if ctx.guild is None:
        await ctx.reply("Команда доступна только на серверах, а не в личных сообщениях.")
        return

    guild_id = ctx.guild.id
    if guild_id not in server_settings:
        server_settings[guild_id] = {"enable_link_insertion": False}

    if setting_number == 1:
        server_settings[guild_id]["enable_link_insertion"] = not server_settings[guild_id]["enable_link_insertion"]
        await ctx.send("Вставка ссылок теперь " + (
            "выключена💀" if server_settings[guild_id]["enable_link_insertion"] else "включена🔥"))
    else:
        await ctx.send("Неправильный номер параметра.")


@bot.command(name='распетляй')
async def generate_response(ctx, *, query: str):

    if ctx.guild is None:
        await ctx.reply("Команда доступна только на серверах, а не в личных сообщениях.")
        return

    query = query.strip()
    if not query:
        await ctx.reply("Самый умный?🤡 А ввести запрос?")
        return
    generating_message = await ctx.reply("Генерирую ответ⌛")

    guild_id = ctx.guild.id
    if guild_id not in server_settings:
        server_settings[guild_id] = {"enable_link_insertion": False}

    enable_link_insertion = server_settings[guild_id]["enable_link_insertion"]

    response = await asyncio.to_thread(gpt, query)
    filtered_response = filter_response(response.lower())
    if enable_link_insertion:
        filtered_response = remove_links(filtered_response)
        filtered_response = remove_square_bracket_content(filtered_response)
    for chunk in split_message(filtered_response, max_length=2000):
        print(chunk)
        await ctx.reply(chunk)
    await generating_message.delete()


bot.run('')
