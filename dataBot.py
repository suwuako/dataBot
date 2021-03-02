from gspreadtest import spreadSheet
from discord.ext import commands
import asyncio
import gspread
import discord
import string

spreadSheet = spreadSheet()

class dataBot:
  def __init__(self):
    @bot.event
    async def on_ready():
      print(f'We have logged in as {bot.user}')
    spreadSheet.get_sheet()

  def authorID_worksheet(self, authorID):
    try:
      self.worksheet = spreadSheet.get_worksheet(str(authorID))
      return False
    except gspread.WorksheetNotFound:
      return True

  def findColumn(self, headers):
    rowValues = spreadSheet.get_row(1)
    count = 0
    self.test = False

    for i in rowValues:
      if i == headers:
        self.test = True
        self.count = count
      count += 1

  def commands(self):
    @bot.command()
    async def ping(message):
      await message.channel.send('Pong!')

    @bot.command()
    async def newTitle(message):
      try:
        spreadSheet.new_worksheet(f'{message.author.id}')
        await message.channel.send(f'worksheet made!')
      except gspread.exceptions.APIError:
        await message.channel.send(f'Spreadsheet by the name of <@{message.author.id}> already exists')

    @bot.command()
    async def newHeader(message, *args):
      if self.authorID_worksheet(message.author.id) == True:
        await message.channel.send('you need to register a spreadsheet with ;newTitle first')
      else:
        rowValues = spreadSheet.get_row(1)
        count = 0
        headers = ''

        for i in args:
          if i != args[-1]:
            headers += str(i) + ' '


        for i in rowValues:
          count += 1
        spreadSheet.write_cell(f'{string.ascii_uppercase[count]}1', headers + args[-1])
        
        await message.channel.send(f'Making header:`"{headers + args[-1]}"` on `{string.ascii_uppercase[count]}1` in file <@{message.author.id}>')

    @bot.command()
    async def displayHeaders(message): 
      if self.authorID_worksheet(message.author.id) == True:
        await message.channel.send('you need to register a spreadsheet with ;newTitle first')
      else:
        rowValues = spreadSheet.get_row(1)
        joinList = ''
        for i in rowValues:
          if i != rowValues[-1]:
            joinList += '`'+ i + '`, '
        send = f'[Headers: {joinList}`{rowValues[-1]}`]'
        await message.channel.send(send)
        
    @bot.command()
    async def postData(message, *args):
      if self.authorID_worksheet(message.author.id) == True:
        await message.channel.send('you need to register a spreadsheet with ;newTitle first')
      else:
        
        headers = ''
        filters = [args[-1], args[-2]]

        for i in args:
          if i not in filters:
            headers += i + ' '
        headers += args[-2]

        self.findColumn(headers)
        if self.test != True:
          await message.channel.send(f'There is no header called `{headers}`. Try ;displayHeaders to see what headers you have')
        else:
          count = 2
          while True:
            cell = string.ascii_uppercase[self.count] + str(count)

            cellValue = spreadSheet.get_cell(cell)
            if cellValue == '':
              spreadSheet.write_cell(cell, args[-1])
              bindEmbed = discord.Embed(color=0xFF99E5)
              bindEmbed.set_author(name=f'Header: `{headers}`')
              bindEmbed.add_field(name=f'Cell Value: `{cell}`', value=f'Data: `{args[-1]}`', inline=True)
              await message.channel.send(embed=bindEmbed)
              break

            count += 1

    @bot.command()
    async def rawData(message, *args):
      if self.authorID_worksheet(message.author.id) == True:
        await message.channel.send('you need to register a spreadsheet with ;newTitle first')
      else:
        headers = ''
        for i in args:
          if i != args[-1]:
            headers += i + ' '
        headers += args[-1]

        self.findColumn(headers)
        if self.test != True:
            await message.channel.send(f'There is no header called `{headers}`. Try ;displayHeaders to see what headers you have')
        else:
          columnValue = spreadSheet.get_column(self.count+1)
          totalString = ''
          valid = [0, len(columnValue)-1]
          cell = string.ascii_uppercase[self.count] + '2'
          for i in range(len(columnValue)):
            if i not in valid:
              
              totalString += f'(`{cell}`): ' + columnValue[i] + '\n'
              cell = string.ascii_uppercase[self.count] + f'{i+2}'
          totalString += f'(`{cell}`): ' + columnValue[-1]

          bindEmbed = discord.Embed(color=0xFF99E5)
          bindEmbed.set_author(name=f'Getting values of {headers}')
          bindEmbed.add_field(name=f'Column: {headers}', value=f'{totalString}', inline=True)
          bindEmbed.set_footer(text=f'Note that cells begin at {string.ascii_uppercase[self.count]}2, because the first cell is occupied by the header (title)')
          await message.channel.send(embed=bindEmbed)
  
  def run(self):
    self.commands()
    bot.run('Nzk4MTE5MzYwMDkwNjAzNTMw.X_wYkw.44XeXtmIe5JQ8Ex_xH7S7B7gIok')


if __name__ == '__main__':
  bot = commands.Bot(command_prefix=';')
  dataBot = dataBot()
  dataBot.run()                       