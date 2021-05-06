#todo list
'''
1. test out having multiple headers of the smae name (low priority)
2. add data sorting and analysis (high priority)
3. add time (medium priority)
'''

import getpass
import os
import string

import spreadsh_mgr
from discord.ext import commands
import datetime
import asyncio
import nest_asyncio
import gspread
import discord
import pandas
import secret

spreadsheet = spreadsh_mgr.SpreadSheet()

"""
    The actual python bot to manage the creation of spreadsheets and optional
    management of message metadata.
"""
class dataBot:
  def __init__(self):
    @bot.event
    async def on_ready():
      print(f'We have logged in as {bot.user}')
    spreadsheet.get_book()

  def author_id_worksheet_not_found(self, authorID):
    sheetList = spreadsheet.book.keys()
    return (str(authorID) in sheetList)
#    try:
#      spreadsheet.get_worksheet(str(authorID))
#      self.worksheet = spreadsheet.worksheet
#      return False
#    except gspread.WorksheetNotFound:
#      return True

  def findColumn(self, headers):
    rowValues = spreadsheet.get_row(1)
    count = 0
    self.test = False

    for i in rowValues:
      if i == headers:
        self.test = True
        
        # TODO find a better (non-overloaded) name for this instance variable!!
        self.count = count
      count += 1

  def commands(self):
    @bot.command()
    async def ping(message):
      await message.channel.send('Pong!')

    @bot.command()
    async def register(message):
      try:
        spreadsheet.new_worksheet(f'{message.author.id}')
        await message.channel.send(f'worksheet made!')
          
      except gspread.exceptions.APIError:
        await message.channel.send(f'Spreadsheet by the name of <@{message.author.id}> already exists')

    @bot.command()
    async def newHeader(message, *args):
      if self.author_id_worksheet_not_found(message.author.id):
        await message.channel.send('you need to register a spreadsheet with ;register first')
      else:
        #gets all cell values of top row
        rowValues = spreadsheet.get_row(1)
        count = 0
        headers = ''
        
        #compiling arguments in message contents
        headers = " ".join(str(next_header) for next_header in args)
        
        #find every second column so that I can fit datetine values for each cell (B, D, F, etc are all data columns while the other odds contain dates)
        for i in rowValues:
          count += 1
        
        #catching for odd numbers and gets converted to even (i think)
        if type(count/2) == float:
          count += 1
          
        #same title column values cause issues I dont want to build around
        if headers in rowValues:
          await message.channel.send(f'You can\'t make two headers of the same name. \n(if ur trying to find bugs id like you to know ur an asshole)')
          
        else:
          spreadsheet.write_cell(f'{string.ascii_uppercase[count]}1', headers)
        
          await message.channel.send(f'Making header:`"{headers}"` on `{string.ascii_uppercase[count]}1` in file <@{message.author.id}>')


    @bot.command()
    async def displayHeaders(message): 
      if self.author_id_worksheet_not_found(message.author.id):
        await message.channel.send('you need to register a spreadsheet with ;register first')
      else:
        rowValues = spreadsheet.get_row(1)
        cleaned = []
        reformat = '['
        
        for i in rowValues:
          if i != '':
            cleaned.append(i)
        
        for i in cleaned:
          #saving last value in list to prevent it ending in a comma
          if cleaned[-1] != i:
            reformat += f'`{i}`, '
          
        reformat += f'`{i}`]'
        bindEmbed = discord.Embed(color=0xFF99E5)
        bindEmbed.add_field(name='List of headers:', value=f'{reformat}', inline=True)
        
        await message.channel.send(embed=bindEmbed)
        
    @bot.command()
    async def postData(message, *args):
      if self.author_id_worksheet_not_found(message.author.id):
        await message.channel.send('you need to register a spreadsheet with ;register first')
      else:
        #holy fucking shit this may work but its slow as fuck fix it when u got time
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
            datecell = string.ascii_uppercase[self.count-1] + str(count)

            cellValue = spreadsheet.get_cell(cell)
            if cellValue == '':
              now = datetime.datetime.now()
              formatted = now.strftime("%d/%m/%Y %H:%M:%S")
              
              spreadsheet.write_cell(datecell, formatted)
              spreadsheet.write_cell(cell, args[-1])
              bindEmbed = discord.Embed(color=0xFF99E5)
              bindEmbed.set_author(name=f'Header: `{headers}`')
              bindEmbed.add_field(name=f'Cell Value: `{cell}`', value=f'Data: `{args[-1]}`', inline=True)
              await message.channel.send(embed=bindEmbed)
              break

            count += 1

    @bot.command()
    async def rawData(message, *args):
      if self.author_id_worksheet_not_found(message.author.id):
        await message.channel.send('you need to register a spreadsheet with ;register first')
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
          columnValue = spreadsheet.get_column(self.count+1)
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
      if self.author_id_worksheet_not_found(message.author.id):
        await message.channel.send('you need to register a spreadsheet with ;register first')
      else:
        rows = spreadsheet.get_row(1)
        
        bindEmbed = discord.Embed(color=0xFF99E5)
        bindEmbed.set_author(name=f'Getting values of <@{message.author.id}>')
        
        for header in rows:
          if header != '':
            column = spreadsheet.get_column(header)
            print(column)
        '''
        for header in rows:
          column = spreadsheet.get_column(count)
          for value in column:
            cell = string.ascii_uppercase[count-1] + str(cellCount)
            output += f'`{cell}`: {value}\n'
            cellCount += 1
          cellCount = 1
          count += 1
          bindEmbed.add_field(name=f'Column: {header}', value=f'{output}', inline=True)
          output = ''
        '''
        
        await message.channel.send(embed=bindEmbed)
        
    @bot.command()
    async def replace(message, *args):
      if self.author_id_worksheet_not_found(message.author.id):
        await message.channel.send('you need to register a spreadsheet with ;register first')
      else:
        temp = ''
        for i in range(len(args)):
          if i != 0:
            temp += args[i]
            
        try:
          if args[0][1] != '1':
            spreadsheet.write_cell(args[0], temp)
            await message.channel.send(f'replaced `{args[0]}` with `{temp}`')
          else:
            await message.channel.send('you cant replace headers')
        except:
          await message.channel.send('something went wrong?')
          

    @bot.command()
    async def basicAnalysis(message):
      if self.author_id_worksheet_not_found(message.author.id):
        await message.channel.send('you need to register a spreadsheet with ;register first')
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
        
        
        await message.channel.send(strdf)
        await message.channel.send(intdf.describe())
        await message.channel.send(intdf.info)
        
    
    
  def run(self):
    self.commands()
    bot.run(secret.credentials.bottoken)


if __name__ == '__main__':
  """
      When the bot is first run, determine whether we need to obtain credentials
      for the nextcloud server.
  """
  bot = commands.Bot(command_prefix=';')
  nest_asyncio.apply()
  dataBot = dataBot()
  dataBot.run()

