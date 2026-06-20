import telebot
from telebot import types

TOKEN = "8606161072:AAHA1H9wa5kNrWt2v8JiIasUbBkDmMSeBjw"
ADMIN_IDS = [6968818472, 2028517332]

bot = telebot.TeleBot(TOKEN)

MENU = {
    "🎂 Tortlar": [
        {"nom": "Shokoladli tort", "narx": 150000, "tavsif": "Qora shokolad va malina bilan"},
        {"nom": "Honey cake Medovik", "narx": 120000, "tavsif": "Asal va qaymoq qatlamlari"},
        {"nom": "Cheesecake Qulupnayli", "narx": 180000, "tavsif": "Yangi qulupnay bilan"},
        {"nom": "Cheesecake Moviy meva", "narx": 180000, "tavsif": "Blueberry sousida"},
        {"nom": "Tiramisu", "narx": 160000, "tavsif": "Italian klassik desert"},
    ],
    "🥐 Pishiriqlar": [
        {"nom": "Croissant", "narx": 25000, "tavsif": "Yangi pishirilgan"},
        {"nom": "Eclair", "narx": 20000, "tavsif": "Shokolad glazuri bilan"},
    ],
    "🍭 Shirinliklar": [
        {"nom": "Baklava", "narx": 30000, "tavsif": "Pista va asal bilan"},
        {"nom": "Cupcake", "narx": 20000, "tavsif": "Pushti va binafsha krem"},
        {"nom": "Donut", "narx": 15000, "tavsif": "Turli xil glazur"},
    ]
}

user_states = {}
user_orders = {}
user_data = {}

def main_menu():
    m = types.ReplyKeyboardMarkup(resize_keyboard=True)
    m.row("🛍 Buyurtma berish", "📋 Menyu")
    m.row("📞 Boglanish", "ℹ️ Haqimizda")
    m.row("🛒 Savatcha")
    return m

def category_menu():
    m = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for cat in MENU.keys():
        m.add(types.KeyboardButton(cat))
    m.row("🛒 Savatchani korish", "✅ Tasdiqlash")
    m.add("🏠 Bosh menu")
    return m

@bot.message_handler(commands=['start'])
def start(msg):
    name = msg.from_user.first_name
    user_orders[msg.chat.id] = []
    text = (
        "Salom, " + name + "!\n\n"
        "TOTO CAKE ga xush kelibsiz!\n\n"
        "Manzil: Qorong'i bozor, Hokimyat oldi\n"
        "Tel: +998-91-779-12-97\n"
        "Instagram: @Toto_cake\n\n"
        "Eng mazali tort va shirinliklarni buyurtma qiling!"
    )
    bot.send_message(msg.chat.id, text, reply_markup=main_menu())

@bot.message_handler(func=lambda m: m.text == "🏠 Bosh menu")
def go_home(msg):
    user_orders[msg.chat.id] = []
    user_states.pop(msg.chat.id, None)
    bot.send_message(msg.chat.id, "Bosh menyu", reply_markup=main_menu())

@bot.message_handler(func=lambda m: m.text == "📋 Menyu")
def show_menu(msg):
    text = "TOTO CAKE MENYU\n\n"
    for cat, items in MENU.items():
        text += cat + "\n"
        for item in items:
            text += "  " + item['nom'] + " - " + str(item['narx']) + " som\n"
            text += "  " + item['tavsif'] + "\n"
        text += "\n"
    bot.send_message(msg.chat.id, text)

@bot.message_handler(func=lambda m: m.text == "🛍 Buyurtma berish")
def order_start(msg):
    if msg.chat.id not in user_orders:
        user_orders[msg.chat.id] = []
    user_states[msg.chat.id] = "category"
    bot.send_message(msg.chat.id, "Kategoriya tanlang:", reply_markup=category_menu())

@bot.message_handler(func=lambda m: m.text in MENU.keys())
def select_category(msg):
    cat = msg.text
    items = MENU[cat]
    m = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for item in items:
        m.add(types.KeyboardButton(item['nom'] + " - " + str(item['narx']) + " som"))
    m.row("Kategoriyalar", "Savatchani korish")
    m.add("Tasdiqlash")
    user_states[msg.chat.id] = "item:" + cat
    bot.send_message(msg.chat.id, cat + " - taom tanlang:", reply_markup=m)

@bot.message_handler(func=lambda m: user_states.get(m.chat.id, "").startswith("item:"))
def select_item(msg):
    if msg.text == "Kategoriyalar":
        order_start(msg); return
    if msg.text == "Savatchani korish":
        show_cart(msg); return
    if msg.text == "Tasdiqlash":
        confirm_order(msg); return
    cat = user_states[msg.chat.id].split(":", 1)[1]
    for item in MENU[cat]:
        btn = item['nom'] + " - " + str(item['narx']) + " som"
        if msg.text == btn:
            user_states[msg.chat.id] = "qty:" + cat + ":" + item['nom'] + ":" + str(item['narx'])
            m = types.ReplyKeyboardMarkup(resize_keyboard=True)
            m.row("1", "2", "3")
            m.row("4", "5", "6")
            m.add("Orqaga")
            bot.send_message(msg.chat.id,
                item['nom'] + "\n" + str(item['narx']) + " som/dona\n\nNechta?",
                reply_markup=m)
            return

@bot.message_handler(func=lambda m: user_states.get(m.chat.id, "").startswith("qty:"))
def select_qty(msg):
    if msg.text == "Orqaga":
        order_start(msg); return
    try:
        qty = int(msg.text)
        parts = user_states[msg.chat.id].split(":")
        cat = parts[1]; nom = parts[2]; narx = int(parts[3])
        if msg.chat.id not in user_orders:
            user_orders[msg.chat.id] = []
        for o in user_orders[msg.chat.id]:
            if o["nom"] == nom:
                o["qty"] += qty; o["total"] = o["qty"] * narx; break
        else:
            user_orders[msg.chat.id].append({"nom": nom, "narx": narx, "qty": qty, "total": narx*qty})
        jami = sum(o["total"] for o in user_orders[msg.chat.id])
        text = nom + " x" + str(qty) + " qoshildi!\n\nSavatcha:\n"
        for o in user_orders[msg.chat.id]:
            text += "  - " + o['nom'] + " x" + str(o['qty']) + " = " + str(o['total']) + " som\n"
        text += "\nJami: " + str(jami) + " som"
        user_states[msg.chat.id] = "category"
        bot.send_message(msg.chat.id, text, reply_markup=category_menu())
    except:
        bot.send_message(msg.chat.id, "Raqam kiriting!")

@bot.message_handler(func=lambda m: m.text in ["🛒 Savatcha", "🛒 Savatchani korish", "Savatchani korish"])
def show_cart(msg):
    orders = user_orders.get(msg.chat.id, [])
    if not orders:
        bot.send_message(msg.chat.id, "Savatcha bosh!", reply_markup=main_menu()); return
    jami = sum(o["total"] for o in orders)
    text = "Savatingiz:\n\n"
    for o in orders:
        text += "  - " + o['nom'] + " x" + str(o['qty']) + " = " + str(o['total']) + " som\n"
    text += "\nJami: " + str(jami) + " som"
    m = types.ReplyKeyboardMarkup(resize_keyboard=True)
    m.add("Tasdiqlash")
    m.row("Yana qoshish", "Tozalash")
    m.add("🏠 Bosh menu")
    bot.send_message(msg.chat.id, text, reply_markup=m)

@bot.message_handler(func=lambda m: m.text == "Tozalash")
def clear_cart(msg):
    user_orders[msg.chat.id] = []
    bot.send_message(msg.chat.id, "Savatcha tozalandi!", reply_markup=main_menu())

@bot.message_handler(func=lambda m: m.text == "Yana qoshish")
def add_more(msg):
    order_start(msg)

@bot.message_handler(func=lambda m: m.text == "Tasdiqlash")
def confirm_order(msg):
    orders = user_orders.get(msg.chat.id, [])
    if not orders:
        bot.send_message(msg.chat.id, "Savatcha bosh!", reply_markup=main_menu()); return
    user_states[msg.chat.id] = "name"
    m = types.ReplyKeyboardMarkup(resize_keyboard=True)
    m.add("Bekor qilish")
    bot.send_message(msg.chat.id, "Ismingizni kiriting:", reply_markup=m)

@bot.message_handler(func=lambda m: user_states.get(m.chat.id) == "name")
def get_name(msg):
    if msg.text == "Bekor qilish":
        cancel(msg); return
    user_data[msg.chat.id] = {"name": msg.text}
    user_states[msg.chat.id] = "phone"
    m = types.ReplyKeyboardMarkup(resize_keyboard=True)
    m.add(types.KeyboardButton("Raqamni yuborish", request_contact=True))
    m.add("Bekor qilish")
    bot.send_message(msg.chat.id, "Telefon raqamingizni yuboring:", reply_markup=m)

@bot.message_handler(content_types=['contact'])
def get_contact(msg):
    if user_states.get(msg.chat.id) == "phone":
        user_data[msg.chat.id]["phone"] = msg.contact.phone_number
        user_states[msg.chat.id] = "address"
        m = types.ReplyKeyboardMarkup(resize_keyboard=True)
        m.add("Bekor qilish")
        bot.send_message(msg.chat.id, "Yetkazib berish manzilini kiriting:", reply_markup=m)

@bot.message_handler(func=lambda m: user_states.get(m.chat.id) == "phone")
def get_phone(msg):
    if msg.text == "Bekor qilish":
        cancel(msg); return
    user_data[msg.chat.id]["phone"] = msg.text
    user_states[msg.chat.id] = "address"
    m = types.ReplyKeyboardMarkup(resize_keyboard=True)
    m.add("Bekor qilish")
    bot.send_message(msg.chat.id, "Yetkazib berish manzilini kiriting:", reply_markup=m)

@bot.message_handler(func=lambda m: user_states.get(m.chat.id) == "address")
def get_address(msg):
    if msg.text == "Bekor qilish":
        cancel(msg); return
    orders = user_orders.get(msg.chat.id, [])
    jami = sum(o["total"] for o in orders)
    data = user_data.get(msg.chat.id, {})
    text = "YANGI BUYURTMA!\n\nBuyurtma:\n"
    for o in orders:
        text += "  - " + o['nom'] + " x" + str(o['qty']) + " = " + str(o['total']) + " som\n"
    text += (
        "\nJami: " + str(jami) + " som\n\n"
        "Ism: " + data.get('name', '-') + "\n"
        "Tel: " + data.get('phone', '-') + "\n"
        "Manzil: " + msg.text + "\n\n"
        "Tel: +998-91-779-12-97"
    )
    bot.send_message(msg.chat.id, "Buyurtmangiz qabul qilindi!\n\n" + text, reply_markup=main_menu())
    for aid in ADMIN_IDS:
        try:
            bot.send_message(aid, text)
        except:
            pass
    user_orders[msg.chat.id] = []
    user_states.pop(msg.chat.id, None)
    user_data.pop(msg.chat.id, None)

@bot.message_handler(func=lambda m: m.text == "Bekor qilish")
def cancel(msg):
    user_orders[msg.chat.id] = []
    user_states.pop(msg.chat.id, None)
    bot.send_message(msg.chat.id, "Bekor qilindi.", reply_markup=main_menu())

@bot.message_handler(func=lambda m: m.text == "📞 Boglanish")
def contact(msg):
    text = (
        "TOTO CAKE bilan boglanish:\n\n"
        "Tel: +998-91-779-12-97\n"
        "Manzil: Qorong'i bozor, Hokimyat oldi\n"
        "Instagram: @Toto_cake\n"
        "Ish vaqti: 09:00 - 21:00"
    )
    bot.send_message(msg.chat.id, text)

@bot.message_handler(func=lambda m: m.text == "ℹ️ Haqimizda")
def about(msg):
    text = (
        "TOTO CAKE haqida:\n\n"
        "Biz eng chiroyli va mazali tortlar tayyorlaymiz!\n\n"
        "Faqat tabiiy ingredientlar\n"
        "Individual dizayn tortlar\n"
        "Yetkazib berish xizmati\n"
        "Toy, tugilgan kun, tadbirlar uchun\n\n"
        "Manzil: Qorong'i bozor, Hokimyat oldi\n"
        "Tel: +998-91-779-12-97\n"
        "Instagram: @Toto_cake"
    )
    bot.send_message(msg.chat.id, text)

@bot.message_handler(commands=['admin'])
def admin_panel(msg):
    if msg.chat.id in ADMIN_IDS:
        bot.send_message(msg.chat.id, "Admin panel ishlamoqda!")

print("TTcake bot ishga tushdi!")
bot.polling(none_stop=True)
