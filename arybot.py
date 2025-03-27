import logging
import json
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler, CallbackQueryHandler
from keep_alive import keep_alive   

# Configuration du logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Fichier JSON pour stocker les données utilisateur
USER_DATA_FILE = "user_data.json"
# Canal requis
REQUIRED_CHANNEL = "@elprofesoraryprono"

# États pour les conversations
WAITING_FIRST_SCREENSHOT, WAITING_SECOND_SCREENSHOT, WAITING_THIRD_SCREENSHOT = range(3)

# Fonction pour charger les données utilisateur
def load_user_data():
    try:
        # Vérifier si le fichier existe, sinon le créer avec un dict vide
        if not os.path.exists(USER_DATA_FILE):
            with open(USER_DATA_FILE, "w") as file:
                json.dump({}, file)
            return {}
        
        with open(USER_DATA_FILE, "r") as file:
            # Vérifier si le fichier est vide
            file_content = file.read()
            if not file_content.strip():
                return {}
            return json.loads(file_content)
    except Exception as e:
        logger.error(f"Erreur lors du chargement des données utilisateur: {e}")
        return {}

# Fonction pour sauvegarder les données utilisateur
def save_user_data(user_data):
    try:
        with open(USER_DATA_FILE, "w") as file:
            json.dump(user_data, file, indent=4)
    except Exception as e:
        logger.error(f"Erreur lors de la sauvegarde des données utilisateur: {e}")

# Fonction pour générer un lien de parrainage
def generate_referral_link(user_id):
    return f"https://t.me/ariprono_bot?start={user_id}"

# Fonction pour vérifier l'abonnement au canal
async def check_channel_subscription(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    try:
        member = await context.bot.get_chat_member(chat_id=REQUIRED_CHANNEL, user_id=user_id)
        return member.status in ["member", "administrator", "creator"]
    except Exception as e:
        logger.error(f"Erreur lors de la vérification du canal: {e}")
        return False

# Commande /start avec bouton Démarrer 🚀
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_message = (
        "Que peut faire ce bot ?\n\n"
        "Je suis le robot 🤖 qui vas vous permettre d'avoir les grosses cotes bien analysé et fiable dont les cotes allant de (5 et +99).\n\n"
        "Je peux te permettre aussi de rejoindre le canal de mon boss ARY PRONO 💪 ou il poste des pronostics fiables gratuitement et bien d'autres astuces gratuites\n\n"
        "https://t.me/elprofesoraryprono\n"
        "https://t.me/elprofesoraryprono\n\n"
        "👆🏼👆🏼Faites votre demande en cliquant ici haut ⬆️\n\n"
        "👇🏼N'oubliez pas de cliquer sur démarrer pour tenter de gagner une recharge de 100$ 👇🏼👇🏼👇🏼"
    )
    
    keyboard = [
        [InlineKeyboardButton("Démarrer 🚀", callback_data="start_bot")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(welcome_message, reply_markup=reply_markup)

# Callback pour le bouton Démarrer 🚀
async def start_bot_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user = query.from_user
    user_id = str(user.id)
    user_data = load_user_data()

    # Gestion du parrainage
    if context.args and user_id not in user_data:
        referrer_id = context.args[0]
        if referrer_id in user_data:
            user_data[referrer_id]["solde"] += 3000
            save_user_data(user_data)
            logger.info(f"Utilisateur {referrer_id} a reçu 3000 FCFA pour le parrainage de {user_id}")

    # Initialisation de l'utilisateur
    if user_id not in user_data:
        user_data[user_id] = {
            "prenom": user.first_name,
            "solde": 0,
            "affilies": 0,
            "inscrit": False
        }
        save_user_data(user_data)
        logger.info(f"Nouvel utilisateur initialisé: {user_data[user_id]}")

    # Envoi du message de bienvenue avec l'image
    welcome_message = (
        f"🤝 Bienvenue {user.first_name} parmi nous.\n\n"
        "..Comme dis plus haut, je suis le robot qui va te permettre d'avoir des Coupons grosses cotes (de 5 à 99), et en plus de permettre de Gagner de l'argent passif si tu le veux.\n\n"
        f"👉🏼 Mr. {user.first_name},\n"
        "..Rejoignez directement le canal officiel de mon BOSS, tout juste là ⬇️👇🏼\n\n"
        "https://t.me/elprofesoraryprono\n"
        "https://t.me/elprofesoraryprono\n"
        "https://t.me/elprofesoraryprono\n\n"
        "👆🏻👆🏻👆🏻👆🏻👆🏻👆🏻👆🏻👆🏻👆🏻👆🏻👆🏻👆🏻\n\n"
        "👇🏼 clic sur le menu 🎛️ pour commencer👇🏼"
    )

    # Bouton inline pour rejoindre le canal
    keyboard = [
        [InlineKeyboardButton("Rejoindre ✅", url="https://t.me/elprofesoraryprono")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    try:
        with open("debut.png", "rb") as photo:
            await query.message.reply_photo(
                photo=photo,
                caption=welcome_message,
                reply_markup=reply_markup
            )
    except Exception as e:
        logger.error(f"Erreur lors de l'envoi de l'image: {e}")
        await query.message.reply_text(welcome_message, reply_markup=reply_markup)

    # Affichage du menu principal
    await show_main_menu(query, context)

# Fonction pour afficher le menu principal
async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [KeyboardButton("🔥 Compte Authentique")],
        [KeyboardButton("🏆 Jeux Concours 🏆"), KeyboardButton("👊🏼 Super Safe 👊🏼")],
        [KeyboardButton("Grosse cote 🥳"), KeyboardButton("Confiance du jour ✅")],
        [KeyboardButton("Gagner de l'argent 💰")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    if isinstance(update, Update) and update.message:
        await update.message.reply_text("🔝 Main Menu", reply_markup=reply_markup)
    else:  # Si c'est un CallbackQuery
        await update.message.reply_text("🔝 Main Menu", reply_markup=reply_markup)

# Gestion du bouton "🔥 Compte Authentique"
async def handle_authentic_account(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = (
        "Utiliser le code promo ELBET777 sur n'importe quel bookmakers, pour avoir un Compte Authentique 🔥 avec plusieurs avantages et Bonus qui suivent 💰🎁\n\n"
        "DÉPÔT MINIMUM APRÈS INSCRIPTION 👉 2.000F\n\n"
        "JOUR DE BONUS 🎁\n\n"
        "Code promo 👉 ELBET777\n\n"
        "S'inscrire 1xbet : https://refpa7921972.top/L?tag=d_2461113m_1573c_&site=2461113&ad=1573\n\n"
        "S'inscrire Betwinner : https://bwredir.com/1XCq?p=%2Fregistration%2F\n\n"
        "S'inscrire 888starz : https://bonusweb.org/L?tag=d_2979115m_37513c_&site=2979115&ad=37513\n\n"
        "S'inscrire WinWin : https://refpa196654.top/L?tag=d_4049028m_68383c_&site=4049028&ad=68383"
    )
    
    try:
        with open("affiche.png", "rb") as photo:
            await update.message.reply_photo(
                photo=photo,
                caption=message
            )
    except Exception as e:
        logger.error(f"Erreur lors de l'envoi de l'image: {e}")
        await update.message.reply_text(message)

# Gestion du bouton "🏆 Jeux Concours 🏆"
async def handle_contest(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = (
        "🎉 DÉPÔT EFFECTUÉ À NOS 3 GAGNANT DU Jeux concours! ✅✅✅\n\n"
        "🍃 PARTICIPER 🍃\n\n"
        "Totalement gratuit pour tous mes abonnés, car c'est juste pour montrer ma gratitude!!\n\n"
        "➡️ partagez ou taguez deux de ses amis. Ne gagnez pas seul.\n\n"
        "⚪️Partagez le lien du canal pour soutenir: ➡️\n"
        "https://t.me/elprofesoraryprono\n\n"
        "➡️ je pense c'est tout, gratuit pour tous 🫂\n\n"
        "..restez branchée pour le prochain jeux concours 🫂✊🏻"
    )
    
    try:
        with open("jeux.png", "rb") as photo:
            await update.message.reply_photo(
                photo=photo,
                caption=message
            )
    except Exception as e:
        logger.error(f"Erreur lors de l'envoi de l'image: {e}")
        await update.message.reply_text(message)

# Gestion du bouton "👊🏼 Super Safe 👊🏼"
async def handle_super_safe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = (
        "🔴- COMMENT AVOIR UN COMPTE AUTHENTIQUE ( + Bonus ) ❓🎁\n\n"
        "📣 suivez très attentivement chaque étape pour mettre au maximum toutes les chances de votre côté ✍️\n\n"
        "C'est le même principe sur tous les bookmakers ‼️ - 🚀⚡🚀🟢🚀🚀 -\n\n"
        "⛔️ - Après l'inscription remplissez « vos paramètres de sécurité et votre profil personnel » 👨‍💻\n\n"
        "..bonne chance à tous merci d'exploser les cœurs ❤️"
    )
    
    try:
        with open("inscription.mp4", "rb") as video:
            await update.message.reply_video(
                video=video,
                caption=message
            )
    except Exception as e:
        logger.error(f"Erreur lors de l'envoi de la vidéo: {e}")
        await update.message.reply_text(message)
    
    # Afficher le sous-menu Super Safe
    keyboard = [
        [KeyboardButton("Super safe_du jour 😊")],
        [KeyboardButton("🔙 Back")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("Menu Super Safe", reply_markup=reply_markup)

# Gestion du bouton "Super safe_du jour 😊"
async def handle_safe_of_day(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = (
        "🍃SAFE DU JOUR VALIDÉ ✅✅\n"
        "✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅\n\n"
        "Les bons comptes font les bons amis 🍾🍾\n\n"
        "…crée dès maintenant votre compte authentique Melbet ou 1xBet activer avec le code promo ELBET777 ⬅️ et bénéficiez de tous nos super _safes et d'un incroyable bonus échangeable de 200% ( ~ 130.000 fcfa ).\n\n"
        "Demain c'est un autre jour, tenez vous prêt à tout casser.\n\n"
        "..merci d'exploser les coeurs ♥️"
    )
    
    try:
        with open("coupon.png", "rb") as photo:
            await update.message.reply_photo(
                photo=photo,
                caption=message
            )
    except Exception as e:
        logger.error(f"Erreur lors de l'envoi de l'image: {e}")
        await update.message.reply_text(message)

# Gestion du bouton "Grosse cote 🥳"
async def handle_big_odds(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = (
        "✍️ Cette option est disponible uniquement pour ceux qui utilisent un compte 1xbet authentique créé avec le code promo ELBET777 👈🏼\n\n"
        "➡️Donc veillez créer un nouveau compte en utilisant le code promo ELBET777\n\n"
        "➡️Ensuite faire une capture d'écran et envoyer ici👇🏼\n\n"
        "🔴NB: tout personne qui va envoyer de faut capture d'écran seront renvoyer du bot crème 😈"
    )
    
    keyboard = [[KeyboardButton("🚫 Annuler")]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(message, reply_markup=reply_markup)
    return WAITING_FIRST_SCREENSHOT

# Gestion de la première capture d'écran
async def handle_first_screenshot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.photo:
        user = update.message.from_user
        message = (
            f"Mr {user.first_name}, envoie la capture d'écran pris quand tu es connecté dans ton compte inscris avec le code promo ELBET777 et qui montre ton identifiant (ou tout simplement envoie la capture de ton identifiant)\n\n"
            "👇🏼👇🏼👇🏼👇🏼👇🏼👇🏼👇🏼"
        )
        
        keyboard = [[KeyboardButton("🚫 Annuler")]]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text(message, reply_markup=reply_markup)
        return WAITING_SECOND_SCREENSHOT
    else:
        await update.message.reply_text("Veuillez envoyer une image valide.")
        return WAITING_FIRST_SCREENSHOT

# Gestion de la deuxième capture d'écran
async def handle_second_screenshot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.photo:
        message = "Veuillez effectuer un dépôt d'au minimum 1000 FCFA et envoyer la capture ✅"
        
        keyboard = [[KeyboardButton("🚫 Annuler")]]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text(message, reply_markup=reply_markup)
        return WAITING_THIRD_SCREENSHOT
    else:
        await update.message.reply_text("Veuillez envoyer une image valide.")
        return WAITING_SECOND_SCREENSHOT

# Gestion de la troisième capture d'écran
async def handle_third_screenshot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.photo:
        await update.message.reply_text("Merci, vos documents sont en cours de vérification 🤝")
        return await show_main_menu(update, context)
    else:
        await update.message.reply_text("Veuillez envoyer une image valide.")
        return WAITING_THIRD_SCREENSHOT

# Gestion du bouton "Confiance du jour ✅"
async def handle_trust_of_day(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = (
        "⚪️Cliquez sur le lien pour rejoindre mon boss ARY PRONO et gagné de l'argent avec lui 🤝❤️\n\n"
        "Cliquez sur le lien 👇🏼\n"
        "https://t.me/elprofesoraryprono"
    )
    
    try:
        with open("canal.png", "rb") as photo:
            await update.message.reply_photo(
                photo=photo,
                caption=message
            )
    except Exception as e:
        logger.error(f"Erreur lors de l'envoi de l'image: {e}")
        await update.message.reply_text(message)

# Gestion du bouton "Gagner de l'argent 💰"
async def handle_earn_money(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Vérifier l'abonnement au canal
    if not await check_channel_subscription(update, context):
        message = (
            "🚨 Veuillez rejoindre le canal pour avoir accès à cette fonctionnalité.\n"
            "Cliquez sur le lien et rejoignez-nous pour qu'on gagne ensemble 🔥\n"
            "https://t.me/elprofesoraryprono"
        )
        await update.message.reply_text(message)
        return
    
    # Si abonné, afficher le sous-menu
    message = "Vous aurez la possibilité de gagner énormément d'argent rien qu'en invitant vos amis\n\nSuivez les instructions pour commencer 👇🏼"
    
    keyboard = [
        [KeyboardButton("Solde 💰"), KeyboardButton("Retrait 💰")],
        [KeyboardButton("Lien de parrainage 🫂")],
        [KeyboardButton("🔙 Back")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(message, reply_markup=reply_markup)

# Gestion du bouton "Solde 💰"
async def handle_balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    user_data = load_user_data()
    
    if user_id not in user_data:
        await update.message.reply_text("❌ Vous n'êtes pas encore enregistré. Utilisez /start pour commencer.")
        return
    
    balance = user_data[user_id]["solde"]
    message = (
        f"{user_data[user_id]['prenom']} votre solde actuel est de {balance} FCFA\n\n"
        "Retrait minimum 60k FCFA\n\n"
        "Vous gagnez 3000 FCFA pour chaque personne invité ✅"
    )
    await update.message.reply_text(message)

# Gestion du bouton "Lien de parrainage 🫂"
async def handle_referral_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    user_data = load_user_data()
    
    if user_id not in user_data:
        await update.message.reply_text("❌ Vous n'êtes pas encore enregistré. Utilisez /start pour commencer.")
        return
    
    referral_link = generate_referral_link(user_id)
    message = (
        "Dès maintenant invite 30 personnes et obtient direct un dépôt de 10.000 frcs valable uniquement pour les 500 premiers\n"
        "(vous n'atteignez pas encore 100 vas y)\n\n"
        "⬇️ Voici ton lien de parrainage ⬇️\n\n"
        f"👉🏼 {referral_link} 👈🏼\n\n"
        "( ☝🏼 maintiens pour copier et partage ou tu veux et gagne de l'argent ensuite )"
    )
    await update.message.reply_text(message)

# Gestion du bouton "Retrait 💰"
async def handle_withdrawal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    user_data = load_user_data()
    
    if user_id not in user_data:
        await update.message.reply_text("❌ Vous n'êtes pas encore enregistré. Utilisez /start pour commencer.")
        return
    
    balance = user_data[user_id]["solde"]
    if balance < 60000:
        message = (
            "❌ Accès refusé\n\n"
            "Vous devez atteindre le minimum de retrait avant de lancer votre retrait\n\n"
            f"Le retrait minimum est de 60000 FCFA et votre solde actuel est de {balance} FCFA\n\n"
            "continuer d'inviter vos amis"
        )
        await update.message.reply_text(message)
    else:
        await update.message.reply_text("🚨 La fonction de retrait est temporairement indisponible, veuillez réessayer plus tard.")

# Gestion du bouton "🔙 Back"
async def handle_back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await show_main_menu(update, context)
    return ConversationHandler.END

# Gestion du bouton "🚫 Annuler"
async def handle_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await show_main_menu(update, context)
    return ConversationHandler.END

# Fonction principale
def main():
    # Vérifier/créer le fichier JSON au démarrage
    if not os.path.exists(USER_DATA_FILE):
        with open(USER_DATA_FILE, "w") as file:
            json.dump({}, file)
    
    application = ApplicationBuilder().token("7678683447:AAFwQS5dG5xWa9aEI7NbbMMaDRhOXdEv6T4").build()

    # Handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(start_bot_callback, pattern="^start_bot$"))
    application.add_handler(MessageHandler(filters.Text("🔥 Compte Authentique"), handle_authentic_account))
    application.add_handler(MessageHandler(filters.Text("🏆 Jeux Concours 🏆"), handle_contest))
    application.add_handler(MessageHandler(filters.Text("👊🏼 Super Safe 👊🏼"), handle_super_safe))
    application.add_handler(MessageHandler(filters.Text("Super safe_du jour 😊"), handle_safe_of_day))
    
    # ConversationHandler pour le processus d'envoi de captures d'écran
    screenshot_conv_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Text("Grosse cote 🥳"), handle_big_odds)],
        states={
            WAITING_FIRST_SCREENSHOT: [
                MessageHandler(filters.PHOTO, handle_first_screenshot),
                MessageHandler(filters.Text("🚫 Annuler"), handle_cancel)
            ],
            WAITING_SECOND_SCREENSHOT: [
                MessageHandler(filters.PHOTO, handle_second_screenshot),
                MessageHandler(filters.Text("🚫 Annuler"), handle_cancel)
            ],
            WAITING_THIRD_SCREENSHOT: [
                MessageHandler(filters.PHOTO, handle_third_screenshot),
                MessageHandler(filters.Text("🚫 Annuler"), handle_cancel)
            ]
        },
        fallbacks=[MessageHandler(filters.Text("🚫 Annuler"), handle_cancel)]
    )
    application.add_handler(screenshot_conv_handler)
    
    application.add_handler(MessageHandler(filters.Text("Confiance du jour ✅"), handle_trust_of_day))
    application.add_handler(MessageHandler(filters.Text("Gagner de l'argent 💰"), handle_earn_money))
    application.add_handler(MessageHandler(filters.Text("Solde 💰"), handle_balance))
    application.add_handler(MessageHandler(filters.Text("Lien de parrainage 🫂"), handle_referral_link))
    application.add_handler(MessageHandler(filters.Text("Retrait 💰"), handle_withdrawal))
    application.add_handler(MessageHandler(filters.Text("🔙 Back"), handle_back))

    # Lancement du bot
    application.run_polling()

keep_alive()

if __name__ == '__main__':
    main()
