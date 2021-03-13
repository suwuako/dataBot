import secret
import nest_asyncio
from discord.ext import tasks, commands


class bot_main:
    def __init__(self):
        @bot.event
        async def on_ready():
            print(f'Bot started as {bot.user}')
            
            channelRecipient = bot.get_channel(secret.update_channel_ID)
            await channelRecipient.send(f'Bot started as <@{bot.user.id}> by {secret.host_username}')
    '''
    def bot_admin_commands(self):
        if userID in secret.bot_admins:
            d
        else:
            pass
    '''
    def commands(self):
        @bot.command()
        async def ping(message):
            await message.send('pong!')
            
        
            
    
    def run(self):
        self.commands()
        #self.bot_admin_commands()
        bot.run(secret.bot_token)
        
if __name__ == '__main__':
    bot = commands.Bot(command_prefix=';')
    nest_asyncio.apply()
    
    bot_main = bot_main()   
    bot_main.run()
    
            