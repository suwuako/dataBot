#todo list
'''
1. test out having multiple headers of the smae name (low priority)
2. add data sorting and analysis (high priority)
3. add time (medium priority)
'''

from gspreadtest import spreadSheet
from discord.ext import commands
import datetime
import asyncio
import nest_asyncio
import gspread
import discord
import string
import pandas

spreadSheet = spreadSheet()

class dataBot:
  def __init__(self):
    @bot.event
    async def on_ready():
      print(f'We have logged in as {bot.user}')
    spreadSheet.get_sheet()

  def authorID_worksheet(self, authorID):
    try:
      spreadSheet.get_worksheet(str(authorID))
      self.worksheet = spreadSheet.worksheet
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
    async def register(message):
      #try:
        spreadSheet.new_worksheet(f'{message.author.id}')
        count = 2
        dateValue = 'A'
        today = datetime.date.today()
        for i in range(2500):
          cell = dateValue + str(count)
          futureDay = datetime.timedelta(days=i+1)
          value = today+futureDay
          spreadSheet.write_cell(cell, value.strftime('%Y-%m-%d'))
          count += 1
        await message.channel.send(f'worksheet made!')
          
      #except gspread.exceptions.APIError:
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
        headers += args[-1]

        for i in rowValues:
          count += 1
          
        if headers in rowValues:
          await message.channel.send(f'You can\'t make two headers of the same name. \n(if ur trying to find bugs id like you to know ur an asshole)')
          
        else:
          spreadSheet.write_cell(f'{string.ascii_uppercase[count]}1', headers)
          
          await message.channel.send(f'Making header:`"{headers}"` on `{string.ascii_uppercase[count]}1` in file <@{message.author.id}>')

    @bot.command()
    async def displayHeaders(message): 
      if self.authorID_worksheet(message.author.id) == True:
        await message.channel.send('you need to register a spreadsheet with ;newTitle first')
      else:
        rowValues = spreadSheet.get_row(1)
        joinList = ''
        for i in range(len(rowValues)):
          if i != len(rowValues):
            joinList += '`'+ rowValues[i] + '`, '
        send = f'[{joinList}`{rowValues[-1]}`]'
        
        bindEmbed = discord.Embed(color=0xFF99E5)
        bindEmbed.add_field(name='Total headers:', value=f'{send}', inline=True)
        await message.channel.send(embed=bindEmbed)
        
    @bot.command()
    async def postData(message, *args):
      if self.authorID_worksheet(message.author.id) == True:
        await message.channel.send('you need to register a spreadsheet with ;newTitle first')
      else:
        
        headers = ''
        invalid = [len(args)-1, len(args)-2]
        for i in range(len(args)):
          if i not in invalid:
            headers += args[i] + ' '
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
          cell = string.ascii_uppercase[self.count] + '2'
          for i in range(len(columnValue)):
            if i != 0 or len(columnValue)-1:
              
              totalString += f'(`{cell}`): ' + columnValue[i] + '\n'
              cell = string.ascii_uppercase[self.count] + f'{i+2}'
          totalString += f'(`{cell}`): ' + columnValue[-1]

          bindEmbed = discord.Embed(color=0xFF99E5)
          bindEmbed.set_author(name=f'Getting values of {headers}')
          bindEmbed.add_field(name=f'Column: {headers}', value=f'{totalString}', inline=True)
          bindEmbed.set_footer(text=f'Note that cells begin at {string.ascii_uppercase[self.count]}2, because the first cell is occupied by the header (title)')
          await message.channel.send(embed=bindEmbed)

    
    @bot.command()
    async def rawSheet(message):
      if self.authorID_worksheet(message.author.id) == True:
        await message.channel.send('you need to register a spreadsheet with ;newTitle first')
      else:
        rows = spreadSheet.get_row(1)
        count = 1
        cellCount = 1
        output = ''
        
        bindEmbed = discord.Embed(color=0xFF99E5)
        bindEmbed.set_author(name=f'Getting values of <@{message.author.id}>')
        
        for header in rows:
          column = spreadSheet.get_column(count)
          for value in column:
            cell = string.ascii_uppercase[count-1] + str(cellCount)
            output += f'`{cell}`: {value}\n'
            cellCount += 1
          cellCount = 1
          count += 1
          bindEmbed.add_field(name=f'Column: {header}', value=f'{output}', inline=True)
          output = ''
        
        await message.channel.send(embed=bindEmbed)
        
    @bot.command()
    async def replace(message, *args):
      if self.authorID_worksheet(message.author.id) == True:
        await message.channel.send('you need to register a spreadsheet with ;newTitle first')
      else:
        temp = ''
        for i in range(len(args)):
          if i != 0:
            temp += args[i]
            
        try:
          if args[0][1] != '1':
            spreadSheet.write_cell(args[0], temp)
            await message.channel.send(f'replaced `{args[0]}` with `{temp}`')
          else:
            await message.channel.send('you cant replace headers')
        except:
          await message.channel.send('something went wrong?')
          

    @bot.command()
    async def analysis(message):
      if self.authorID_worksheet(message.author.id) == True:
        await message.channel.send('you need to register a spreadsheet with ;newTitle first')
      else:
        strdata = self.worksheet.get_all_values()
        headers = strdata.pop(0)

        intdata = []
        for value in strdata:
          tempList = []
          for i in value:
            try:
              i = int(i)
              tempList.append(i)
            except:
              pass
          intdata.append(tempList)
        
        intdf = pandas.DataFrame(intdata, columns=headers)
        strdf = pandas.DataFrame(strdata, columns=headers)
        
        '''
        await message.channel.send(strdf)
        await message.channel.send(intdf.describe())
        await message.channel.send(intdf.info)
        '''
    
    
  def run(self):
    self.commands()
    bot.run('')


if __name__ == '__main__':
  bot = commands.Bot(command_prefix=';')
  nest_asyncio.apply()
  dataBot = dataBot()
  dataBot.run()                       
