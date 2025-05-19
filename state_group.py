from aiogram.fsm.state import State, StatesGroup

class FilmForm(StatesGroup):
   name = State()
   description = State()
   rating = State()
   genre = State()
   actors = State()
   poster = State()

class MovieStates(StatesGroup):
    search_query = State()
    filter_criteria = State()
    filter_actor = State()
    delete_query = State()
    edit_query = State()
    edit_description = State()
    review_movie = ()
    review_text = ()

class MovieRatingStates(StatesGroup):
    rate_query = State()
    set_rating = State() 