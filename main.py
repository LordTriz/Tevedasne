import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from db import BotDB

import random

# anketa its a form which presents a person 
# i didn't use a lot of my mind naming variables, you see

bot = Bot(token="5994778197:AAHsrsujK3IF4K_IndtA5x2BmBs2gHNskkU")
dp = Dispatcher(bot, storage=MemoryStorage())
logging.basicConfig(level=logging.INFO)

BotDB = BotDB('database.db')

# Blanks

menu_main_text = '1. មើលកម្រងព័ត៌មាន\n2. ប្រវត្តិរូបរបស់ខ្ញុំ\n3. លុបប្រវត្តិរូប'
my_anketa_text = '1. បំពេញកម្រងសំណួរម្តងទៀត\n2. ផ្លាស់ប្តូរអត្ថបទនៃកម្រងសំណួរ\n3. កែរូបថត\n4. នឹងត្រលប់មកវិញ'

def show_anketa(name, age, city, text):
    return f'{name}\n{age}\n{city}\n{text}'

def get_random_anketa(list_of_anketi):
    anketa = list_of_anketi[random.randint(0, len(list_of_anketi) - 1)]
    a = anketa
    return [show_anketa(a[2], a[3], a[4], a[5]), BotDB.get_photo_id(a[1])]
        
# States for dialog navigation

class Wait(StatesGroup):
    choosing_gender = State()
    choosing_interest = State()
    name = State()
    age = State()
    city = State()
    text = State()
    photo = State()
    menu_answer = State()
    my_anketa_answer = State()
    change_text = State()
    change_photo = State()
    delete_confirm = State()
    anketa_reaction = State()

@dp.message_handler(commands="start", state = "*")
async def anketa_start(message: types.Message):
    if(not BotDB.user_exists(message.from_user.id)):
        BotDB.add_user(message.from_user.id)

    # If anketa exists - show menu
    # If not - create new

    if(BotDB.anketa_exists(message.from_user.id)):

        anketa = BotDB.get_anketa(message.from_user.id)
        a = anketa[0]
        caption = show_anketa(a[2], a[3], a[4], a[5])
        await bot.send_photo(photo = open(f"photos/{message.from_user.id}.jpg", "rb"), chat_id = message.from_user.id, caption = caption)

        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        buttons = ["1", "2", "3"]
        keyboard.add(*buttons)

        await message.answer(menu_main_text, reply_markup = keyboard)
        await Wait.menu_answer.set()

    else:

        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        buttons = ["ប្រុស", "ស្រី"]
        keyboard.add(*buttons)

        await message.answer("សូមបំពេញព័ត៌មាន!\ដំបូង សូមជ្រេីសរេីសភេទ",
         reply_markup=keyboard)
        await Wait.choosing_gender.set()

@dp.message_handler(state = Wait.choosing_gender)
async def choose_gender(message: types.Message, state: FSMContext):
    if message.text not in ["ប្រុស", "ស្រី"]:
        await message.answer("សូមជ្រេីសរេីស Button ខាងក្រោម")
        return
    await state.update_data(gender = message.text.lower())

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ["ប្រុស", "ស្រី"]
    keyboard.add(*buttons)
    await message.answer("តេីអ្នកចងបានដៃគូរមានលក្ខណះបែបណា?", reply_markup = keyboard)
    await Wait.choosing_interest.set()

@dp.message_handler(state = Wait.choosing_interest)
async def choose_interest(message: types.Message, state: FSMContext):
    if message.text == "ប្រុស" or message.text == "ស្រី":
        await state.update_data(interest = message.text.lower())
        await message.answer("សូមដាក់ឈ្មោះរបស់អ្នក", reply_markup=types.ReplyKeyboardRemove())
        await Wait.name.set()
    else:
        await message.answer("សូមជ្រេីសរេីស Button ខាងក្រោម")
        return

@dp.message_handler(state = Wait.name)
async def name(message: types.Message, state: FSMContext):
    if len(message.text) > 30:
        await message.answer("ឈ្មោះវែងពេកហេីយ")
        return
    await state.update_data(name = message.text)                    
    await message.answer("តេីអ្នកអាយុប៉ុន្មាន?")
    await Wait.age.set()

@dp.message_handler(state = Wait.age)
async def age(message: types.Message, state: FSMContext):
    try:
        if 10 > int(message.text) or int(message.text) > 100:
            await message.answer("អាយុច្រេីនម្លេះ")
            return
    except(TypeError, ValueError):
        await message.answer("ដាក់អាយុខុសហេីយ")
        return
    await state.update_data(age = message.text)
    await message.answer("តេីអ្នករស់នៅស្រុកអ្វី?")
    await Wait.city.set()

@dp.message_handler(state = Wait.city)
async def city(message: types.Message, state: FSMContext):
    if len(message.text) > 30:
        await message.answer("ឈ្មោះវែងពេកហេីយ")
        return

    await state.update_data(city = message.text)

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add("សុំមិសសរសេរ")

    await message.answer("សរសេរពីខ្លួនអ្នក (មិនសរសេរក៏បាន)", reply_markup = keyboard)
    await Wait.text.set()

@dp.message_handler(state = Wait.text)
async def text(message: types.Message, state: FSMContext):
    if message.text == "សុំមិសសរសេរ":
        await state.update_data(text = '')
    else:
        if len(message.text) > 200:
            await message.answer("អ្នកអាចសរសេរបានត្រឹមតែ 200 អក្សរនោះទេ")
            return
        await state.update_data(text = message.text)
    
    await message.answer("សូម uplaod រូបថតរបស់អ្នក", reply_markup=types.ReplyKeyboardRemove())
    await Wait.photo.set()

@dp.message_handler(state = Wait.photo, content_types = ["photo"])
async def download_photo(message: types.Message, state: FSMContext):
    await message.photo[-1].download(destination_file=f"photos/{message.from_user.id}.jpg")

    # convert data(dictionary) values to list "d"
    data = await state.get_data()
    d = list(data.values())
    print(d)

    BotDB.add_anketa(message.from_user.id, d[0], d[1], d[2], d[3], d[4], d[5])

    caption = show_anketa(d[2], d[3], d[4], d[5])
    await message.answer("Profile របស់អ្នក: ")
    await bot.send_photo(photo = open(f"photos/{message.from_user.id}.jpg", "rb"), caption = caption, chat_id = message.from_user.id)

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ["1", "2", "3"]
    keyboard.add(*buttons)

    await message.answer(menu_main_text, reply_markup = keyboard)
    await Wait.menu_answer.set()

@dp.message_handler(state = Wait.menu_answer)
async def menu_answer(message: types.Message, state: FSMContext):
    if message.text == "1":
        anketa = BotDB.get_anketa(message.from_user.id)
        a = anketa[0]
        caption = show_anketa(a[2], a[3], a[4], a[5])       

        list_of_anketi = BotDB.find_anketi(message.from_user.id, a[7], a[4], a[3])

        try:
            get_random_anketa(list_of_anketi)
        except ValueError:
            await message.answer("ខ្ញុំមិនអាចស្វែងរកនណាម្នាក់សម្រាប់អ្នកបានទេ /nប្រហែលនៅតំបន់អ្នករស់នៅមិនសូវមានអ្នកប្រេីប្រាស់ខ្ញុំ ឬ មិនមានអ្នកអាយុប្រហែលអ្នក")

            await bot.send_photo(photo = open(f"photos/{message.from_user.id}.jpg", "rb"), caption = caption, chat_id = message.from_user.id)
            
            keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
            buttons = ["1", "2", "3", "4"]
            keyboard.add(*buttons)

            await message.answer(my_anketa_text, reply_markup = keyboard)
            await Wait.my_anketa_answer.set()

        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        buttons = ["ចូលចិត្ត", "រំលង", "អគុណច្រេីន"]
        keyboard.add(*buttons)

        anketa = get_random_anketa(list_of_anketi)

        caption = anketa[0]
        photo_id = anketa[1]

        await state.update_data(liked_id = photo_id)

        await bot.send_photo(photo = open(f"photos/{photo_id}.jpg", "rb"), caption = caption, chat_id = message.from_user.id, reply_markup = keyboard)

        await Wait.anketa_reaction.set()
        
    elif message.text == "2":

        """ Show form (anketa) in 4 strings """

        anketa = BotDB.get_anketa(message.from_user.id)
        a = anketa[0]
        caption = show_anketa(a[2], a[3], a[4], a[5])

        await bot.send_photo(photo = open(f"photos/{message.from_user.id}.jpg", "rb"), caption = caption, chat_id = message.from_user.id)
        
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        buttons = ["1", "2", "3", "4"]
        keyboard.add(*buttons)

        await message.answer(my_anketa_text, reply_markup = keyboard)
        await Wait.my_anketa_answer.set()

    elif message.text == "3":
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        buttons = ["យល់ព្រម", "ទេ"]
        keyboard.add(*buttons)
        await message.answer("អ្នកពិតជាចងលុប Profile របស់អ្នកមែនទេ?", reply_markup = keyboard)
        await Wait.delete_confirm.set("សូមជ្រេីសរេីសជំរេីសខាងក្រោម")

    else:
        await message.answer()
        return

@dp.message_handler(state = Wait.anketa_reaction)
async def anketa_reaction(message: types.Message, state: FSMContext):
    if message.text == "ចូលចិត្ត":
        
        data = await state.get_data() ##############
        d = list(data.values())

        anketa = BotDB.get_anketa(message.from_user.id)
        a = anketa[0]
        caption = show_anketa(a[2], a[3], a[4], a[5])

        list_of_anketi = BotDB.find_anketi(message.from_user.id, data["interest"], data["city"], data["age"])

        liked_id = data["liked_id"]

        await bot.send_message(text = "ម្នាក់នេះបានចូលចិត្តអ្នក: ", chat_id = liked_id)
        await bot.send_photo(photo = open(f"photos/{message.from_user.id}.jpg", "rb"), chat_id = liked_id, caption = caption)
        await bot.send_message(text = f"ចាប់ផ្តេីមការជជែកប្រសិនជាអ្នកពេញចិត្ត - @{message.from_user.username}", chat_id = liked_id)

        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        buttons = ["ចូលចិត្ត", "រំលង", "អគុណច្រេីន"]
        keyboard.add(*buttons)

        anketa = get_random_anketa(list_of_anketi)
        caption = anketa[0]
        photo_id = anketa[1]
        
        await bot.send_photo(photo = open(f"photos/{photo_id}.jpg", "rb"), caption = caption, chat_id = message.from_user.id)
        await Wait.anketa_reaction.set()

    elif message.text == "រំលង":

        data = await state.get_data() ##############
        list_of_anketi = BotDB.find_anketi(message.from_user.id, data["interest"], data["city"], data["age"])

        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        buttons = ["ចូលចិត្ត", "រំលង", "អគុណច្រេីន"]
        keyboard.add(*buttons)

        caption = get_random_anketa(list_of_anketi)[0]
        photo_id = get_random_anketa(list_of_anketi)[1]
        await bot.send_photo(photo = open(f"photos/{photo_id}.jpg", "rb"), caption = caption, chat_id = message.from_user.id)

        await Wait.anketa_reaction.set()

    elif message.text == "អគុណច្រេីន":
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        buttons = ["1", "2", "3"]
        keyboard.add(*buttons)

        await message.answer(menu_main_text, reply_markup = keyboard)
        await Wait.menu_answer.set()
    else:
        await message.answer("ជ្រេីសជម្រេីសខាងក្រោម")
        return

@dp.message_handler(state = Wait.delete_confirm)
async def delete_confirm(message: types.Message, state: FSMContext):
    if message.text == "យល់ព្រម":
        BotDB.delete_anketa(message.from_user.id)
        BotDB.delete_user(message.from_user.id)
        await message.answer("អ្នកបាម Delete Profile បានជោគជ័យ!\nអ្នកអាចបង្កេីត Profile ថ្មីដោយប្រេី /start", reply_markup = types.ReplyKeyboardRemove())        
    elif message.text == "ទេ":
        anketa = BotDB.get_anketa(message.from_user.id)
        a = anketa[0]
        caption = show_anketa(a[2], a[3], a[4], a[5])

        await bot.send_photo(photo = open(f"photos/{message.from_user.id}.jpg", "rb"), caption = caption, chat_id = message.from_user.id)
        
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        buttons = ["1", "2", "3", "4"]
        keyboard.add(*buttons)

        await message.answer(my_anketa_text, reply_markup = keyboard)
        await Wait.my_anketa_answer.set()
    else:
        await message.answer("ជ្រេីសរេីសជម្រេីសខាងក្រោម")
        return

@dp.message_handler(state = Wait.my_anketa_answer)
async def my_anketa_answer(message: types.Message, state: FSMContext):
    # Re-do form
    if message.text == "1":
        BotDB.delete_anketa(message.from_user.id)

        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        buttons = ["ប្រុស", "ស្រី"]
        keyboard.add(*buttons)

        await message.answer("ជ្រេីសរេីសភេទ",
         reply_markup=keyboard)
        await Wait.choosing_gender.set()
    # Enter new text
    elif message.text == "2":
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add("មិនបំពេញ")
        await message.answer("បញ្ចូលអត្ថបទថ្មីនៃកម្រងសំណួរ", reply_markup=keyboard)
        await Wait.change_text.set()

    elif message.text == "3":
        await message.answer(" Upload រូបភាព Profile ថ្មី", reply_markup = types.ReplyKeyboardRemove())
        await Wait.change_photo.set()

    elif message.text == "4":
        anketa = BotDB.get_anketa(message.from_user.id)
        a = anketa[0]
        caption = show_anketa(a[2], a[3], a[4], a[5])

        await bot.send_photo(photo = open(f"photos/{message.from_user.id}.jpg", "rb"), caption = caption, chat_id = message.from_user.id)
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        buttons = ["1", "2", "3"]
        keyboard.add(*buttons)

        await message.answer(menu_main_text, reply_markup = keyboard)
        await Wait.menu_answer.set()
    else:
        await message.answer("ជ្រើសរើសជម្រើសខាងក្រោម")
        return

@dp.message_handler(state = Wait.change_text)
async def change_text(message: types.Message, state: FSMContext):
    if message.text == "ទុកឲ្យនៅទទេ":
            BotDB.update_text(message.from_user.id, '')

            anketa = BotDB.get_anketa(message.from_user.id)
            a = anketa[0]
            caption = show_anketa(a[2], a[3], a[4], a[5])   

            await bot.send_photo(photo = open(f"photos/{message.from_user.id}.jpg", "rb"), caption = caption, chat_id = message.from_user.id)
            
            keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
            buttons = ["1", "2", "3", "4"]
            keyboard.add(*buttons)

            await message.answer(my_anketa_text, reply_markup = keyboard)
            await Wait.my_anketa_answer.set()
    else:
        if len(message.text) > 200:
            await message.answer("ច្រេីនពេកហេីយ (1-200)")
            return
        BotDB.update_text(message.from_user.id, message.text)

        anketa = BotDB.get_anketa(message.from_user.id)
        a = anketa[0]
        caption = show_anketa(a[2], a[3], a[4], a[5])   

        await bot.send_photo(photo = open(f"photos/{message.from_user.id}.jpg", "rb"), caption = caption, chat_id = message.from_user.id)

        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        buttons = ["1", "2", "3"]
        keyboard.add(*buttons)

        await message.answer(menu_main_text, reply_markup = keyboard)
        await Wait.menu_answer.set()

@dp.message_handler(state = Wait.change_photo, content_types = ["photo"])
async def change_photo(message: types.Message, state: FSMContext):
    await message.photo[-1].download(destination_file=f"photos/{message.from_user.id}.jpg")

    anketa = BotDB.get_anketa(message.from_user.id)
    a = anketa[0]
    caption = show_anketa(a[2], a[3], a[4], a[5])   

    await message.answer("Вот ваша анкета: ")
    await bot.send_photo(photo = open(f"photos/{message.from_user.id}.jpg", "rb"), caption = caption, chat_id = message.from_user.id)

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ["1", "2", "3"]
    keyboard.add(*buttons)

    await message.answer(menu_main_text, reply_markup = keyboard)
    await Wait.menu_answer.set()

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
