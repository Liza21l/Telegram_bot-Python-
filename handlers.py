
from aiogram import Router

from aiogram import Bot, Dispatcher, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery, BotCommand, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext

from commands import FILMS_COMMAND
from data import get_films, add_film, delete_film_by_name, update_film_description, update_film_rating
from keyboards import films_keyboard_markup, FilmCallback
from state_group import FilmForm, MovieStates, MovieRatingStates



from commands import (
   FILMS_COMMAND,
   START_COMMAND,
   FILM_CREATE_COMMAND,
   BOT_COMMANDS,
)
from models import Film
from aiogram.types import URLInputFile

# Bot token can be obtained via https://t.me/BotFather
# TOKEN = getenv("BOT_TOKEN")

# All handlers should be attached to the Router (or Dispatcher)


router = Router()

@router.message(Command('search_movie'))
async def search_movie(message: Message, state: FSMContext):
    await message.reply("Введіть назву фільму для пошуку:")
    await state.set_state(MovieStates.search_query)

@router.message(MovieStates.search_query)
async def get_search_query(message: Message, state: FSMContext):
    query = message.text.lower()
    films_data = get_films()
    results = [film for film in films_data if query in film['name'].lower()]
    
    if results:
        for film in results:
            await message.reply(f"Знайдено: {film['name']} - {film['description']}")
    else:
        await message.reply("Фільм не знайдено.")
    
    await state.clear()

@router.message(Command('filter_actor'))
async def filter_actor(message: Message, state: FSMContext):
    await message.reply("Введіть ім'я актора")
    await state.set_state(MovieStates.filter_actor)

@router.message(MovieStates.filter_actor)
async def get_search_actor(message: Message, state: FSMContext):
    """
    Пошук фільма за актором
    """
    filmActor = message.text
    films_data = get_films()
    result = [film for film in films_data if any(filmActor in actor for actor in film['actors'])]
    
    if result:
        for film in result:
           await message.reply(f"Знайдено: {film['name']} - {film['description']} - {film['actors']}")
    else:
        await message.reply("Фільм не знайдено.")

# Фільтрація фільмів за жанром або роком
@router.message(Command('filter_movies'))
async def filter_movies(message: Message, state: FSMContext):
    await message.reply("Введіть жанр або рік випуску для фільтрації:")
    await state.set_state(MovieStates.filter_criteria)

@router.message(MovieStates.filter_criteria)
async def get_filter_criteria(message: Message, state: FSMContext):
    criteria = message.text.lower()
    films_data = get_films()
    filtered = list(filter(lambda film: criteria in film['genre'].lower() or criteria in str(film['year']) == criteria, films_data))
    
    if filtered:
        for film in filtered:
            await message.reply(f"Знайдено: {film['name']} - {film['description']}")
    else:
        await message.reply("Фільм не знайдено за цими критеріями.")
    
    await state.clear()

# Видалення фільму за назвою
@router.message(Command('delete_movie'))
async def delete_movie(message: Message, state: FSMContext):
    await message.reply("Введіть назву фільму, який бажаєте видалити:")
    await state.set_state(MovieStates.delete_query)

@router.message(MovieStates.delete_query)
async def get_delete_query(message: Message, state: FSMContext):
    film_to_delete = message.text
    if delete_film_by_name(film_to_delete):
        await message.reply(f"Фільм '{film_to_delete}' видалено.")
        await state.clear()
        return
    await message.reply("Фільм не знайдено.")
    await state.clear()

# Редагування опису фільму за назвою
@router.message(Command('edit_movie'))
async def edit_movie(message: Message, state: FSMContext):
    await message.reply("Введіть назву фільму, який бажаєте редагувати:")
    await state.set_state(MovieStates.edit_query)

@router.message(MovieStates.edit_query)
async def get_edit_query(message: Message, state: FSMContext):
    film_to_edit = message.text.lower()
    films = get_films()
    for film in films:
        if film_to_edit == film['name'].lower():
            await state.update_data(film_name=film['name'])
            await message.reply("Введіть новий опис фільму:")
            await state.set_state(MovieStates.edit_description)
            return
    await message.reply("Фільм не знайдено.")
    await state.clear()

# Команда для отримання рекомендованого фільму
@router.message(Command('recommend_movie'))
async def recommend_movie(message: Message):
    films = get_films()
    rated_films = [film for film in films if film.get('rating') is not None]
    if rated_films:
        recommended = max(rated_films, key=lambda film: film['rating'])
        await message.reply(f"Рекомендуємо переглянути: {recommended['name']} - {recommended['description']} (Рейтинг: {recommended['rating']})")
    else:
        await message.reply("Немає фільмів з рейтингом для рекомендації.")


# Команда для оцінювання фільму
@router.message(Command('rate_movie'))
async def rate_movie(message: Message, state: FSMContext):
    await message.reply("Введіть назву фільму, щоб оцінити:")
    await state.set_state(MovieRatingStates.rate_query)

@router.message(MovieRatingStates.rate_query)
async def get_rate_query(message: Message, state: FSMContext):
    film_to_rate = message.text.lower()
    films_data = get_films()
    for film in films_data:
        if film_to_rate == film['name'].lower():
            await state.update_data(film_name=film['name'])
            await message.reply("Введіть рейтинг від 1 до 10:")
            await state.set_state(MovieRatingStates.set_rating)
            return
    await message.reply("Фільм не знайдено.")
    await state.clear()

@router.message(MovieRatingStates.set_rating)
async def set_rating(message: Message, state: FSMContext):
    data = await state.get_data()
    film = data['film_name']
    
    try:
        rating = int(message.text)
        if 1 <= rating <= 10:
            update_film_rating(film, rating)
            await message.reply(f"Рейтинг для '{film}' оновлено на {rating}.")
            await state.clear()
        else:
            await message.reply("Введіть рейтинг від 1 до 10.")
    except ValueError:
        await message.reply("Введіть число.")


@router.message(MovieStates.edit_description)
async def update_description(message: Message, state: FSMContext):
    data = await state.get_data()
    film = data['film_name']
    if update_film_description(film, message.text):
        await message.reply(f"Фільм '{film}' оновлено.")
        await state.clear()
        return
    await message.reply("Виникла помилка...")
    await state.clear()


@router.message(FilmForm.poster)
async def film_poster(message: Message, state: FSMContext) -> None:
   data = await state.update_data(poster=message.text)
   film = Film(**data)
   add_film(film.model_dump())
   await state.clear()
@router.message(FILM_CREATE_COMMAND)
async def film_create(message: Message, state: FSMContext) -> None:
   await state.set_state(FilmForm.name)
   await message.answer(
       f"Введіть назву фільму.",
       reply_markup=ReplyKeyboardRemove(),
   )

@router.message(FilmForm.name)
async def film_name(message: Message, state: FSMContext) -> None:
   await state.update_data(name=message.text)
   await state.set_state(FilmForm.description)
   await message.answer(
       f"Введіть опис фільму.",
       reply_markup=ReplyKeyboardRemove(),
   )


@router.message(FilmForm.description)
async def film_description(message: Message, state: FSMContext) -> None:
   await state.update_data(description=message.text)
   await state.set_state(FilmForm.rating)
   await message.answer(
       f"Вкажіть рейтинг фільму від 0 до 10.",
       reply_markup=ReplyKeyboardRemove(),
   )


@router.message(FilmForm.rating)
async def film_rating(message: Message, state: FSMContext) -> None:
   await state.update_data(rating=float(message.text))
   await state.set_state(FilmForm.genre)
   await message.answer(
       f"Введіть жанр фільму.",
       reply_markup=ReplyKeyboardRemove(),
   )


@router.message(FilmForm.genre)
async def film_genre(message: Message, state: FSMContext) -> None:
   await state.update_data(genre=message.text)
   await state.set_state(FilmForm.actors)
   await message.answer(
       text=f"Введіть акторів фільму через роздільник ', '\n"
       + html.bold("Обов'язкова кома та відступ після неї."),
       reply_markup=ReplyKeyboardRemove(),
   )


@router.message(FilmForm.actors)
async def film_actors(message: Message, state: FSMContext) -> None:
   await state.update_data(actors=[x for x in message.text.split(", ")])
   await state.set_state(FilmForm.poster)
   await message.answer(
       f"Введіть посилання на постер фільму.",
       reply_markup=ReplyKeyboardRemove(),
   )


@router.message(FilmForm.poster)
async def film_poster(message: Message, state: FSMContext) -> None:
   data = await state.update_data(poster=message.text)
   film = Film(**data)
   add_film(film.model_dump())
   await state.clear()
   await message.answer(
       f"Фільм {film.name} успішно додано!",
       reply_markup=ReplyKeyboardRemove(),
   )
@router.callback_query(FilmCallback.filter())
async def callb_film(callback: CallbackQuery, callback_data: FilmCallback) -> None:
    film_id = callback_data.id
    film_data = get_films(film_id=film_id)
    film = Film(**film_data)

    text = f"Фільм: {film.name}\n" \
           f"Опис: {film.description}\n" \
           f"Рік: {film.year}\n"\
           f"Рейтинг: {film.rating}\n" \
           f"Жанр: {film.genre}\n" \
           f"Актори: {', '.join(film.actors)}\n"
   
    await callback.message.answer_photo(
        caption=text,
        photo=URLInputFile(
            film.poster,
            filename=f"{film.name}_poster.{film.poster.split('.')[-1]}"
        )
    )

@router.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """
    This handler receives messages with `/start` command
    """
    # Most event objects have aliases for API methods that can be called in events' context
    # For example if you want to answer to incoming message you can use `message.answer(...)` alias
    # and the target chat will be passed to :ref:`aiogram.methods.send_message.SendMessage`
    # method automatically or call API method directly via
    # Bot instance: `bot.send_message(chat_id=message.chat.id, ...)`
    await message.answer(f"Hello, {html.bold(message.from_user.full_name)}! Я Telegram Bot Film помічник.")


@router.message(Command("start"))
async def echo_handler(message: Message) -> None:
    """
    Handler will forward receive a message back to the sender

    By default, message handler will handle all message types (like a text, photo, sticker etc.)
    """
    try:
        # Send a copy of the received message
        await message.send_copy(chat_id=message.chat.id)
    except TypeError:
        # But not all the types is supported to be copied so need to handle it
        await message.answer("Nice try!")

@router.message(FILMS_COMMAND)
async def films(message: Message) -> None:
    data = get_films()
    markup = films_keyboard_markup(films_list=data)
    await message.answer(
        f"Перелік фільмів. Натисніть на назву фільму для отримання деталей.",
        reply_markup=markup
    )
