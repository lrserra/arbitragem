import telegram
from util import Util

class Telegram:

    def enviarMensagem(mensagem):
        credenciais = Util.obterCredenciais() 
        token = credenciais['Telegram']['Token']
        bot = telegram.Bot(token=token)
        bot.sendMessage(chat_id=credenciais['Telegram']['ChatId'], text=mensagem)