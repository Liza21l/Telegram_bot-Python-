from aiogram.filters import Command
from aiogram.types.bot_command import BotCommand

FILMS_COMMAND = Command('films')
START_COMMAND = Command('start')
FILM_CREATE_COMMAND = Command("create_film")

BOT_COMMANDS = [
   BotCommand(command="films", description="Перегляд списку фільмів"),
   BotCommand(command="start", description="Почати розмову"),
   BotCommand(command="create_film", description="Додати новий фільм"),
   BotCommand(command="search_movie", description="Пошук фільма за назвою"),
   BotCommand(command="filter_movies", description="Пошук фільма за жанром або роком"),
   BotCommand(command="delete_movie", description="Видалення фільму за назвою"),
   BotCommand(command="edit_movie", description="Редагування опису фільму за назвою"),
   BotCommand(command="recommend_movie", description="Отримання рекомендованого фільму"),
   BotCommand(command="rate_movie", description="Оцінювання фільму"),
   BotCommand(command="filter_actor", description="Пошук фільма за актором"),

]