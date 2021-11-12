#!/usr/bin/env python3
#todo list
'''
1. test out having multiple headers of the smae name (low priority)
2. add data sorting and analysis (high priority)
3. add time (medium priority)
'''

import asyncio
import getpass
import os
import string

import datetime
import discord
from discord.ext import commands
#import gspread
import nest_asyncio
from nextcloud import NextCloud
import pandas
import secret
import spreadsh_mgr

"""
    The actual python bot to manage the creation of spreadsheets and optional
    management of message metadata.
"""
class dataBot:
  def __init__(self, spreadsheet_obj):
    @bot.event
    async def on_ready():
      print(f'We have logged in as {bot.user}')
    
    @bot.event
    async def on_disconnect():
      print("The bot has disconnected successfully.")
    
    self.spreadsheet = spreadsheet_obj
    #self.spreadsheet.get_book(serverName)

  def author_id_worksheet_not_found(self, serverName, authorID):
    sheetList = spreadsheet.get_book(spreadsh_mgr.local_file_prefix+serverName+".ods").keys()
    result = str(authorID) not in sheetList
    return result

  # Note to my future self:
  # this primitive algorithm is actually running through each 
  # COLUMN and checking whether it match the given search QUERY,
  # which is oddly named "headers" ...
  # it's a pretty ugly implementation. Surely I can write a better one, no?
  # -VC
  def findColumn(self, guild_name, sheet_name, headers):
    rowValues = self.spreadsheet.get_row(guild_name, sheet_name, 0)
    count = 0
    self.test = False

    for i in rowValues:
      if i == headers:
        self.test = True
        
        self.matching_header_index = count
      count += 1

  def commands(self):
    @bot.command()
    async def ping(message):
      await message.channel.send('Pong!')

    @bot.command()
    async def register(message):
#      try:
      self.spreadsheet.new_worksheet(message.channel.guild.name, f'{message.author.id}')
      await message.channel.send(f'worksheet made!')
      
#      except gspread.exceptions.APIError:
#        await message.channel.send(f'Spreadsheet by the name of <@{message.author.id}> already exists')

    @bot.command()
    async def newHeader(message, *args):
      if self.author_id_worksheet_not_found(message.channel.guild.name, message.author.id):
        await message.channel.send('you need to register a spreadsheet with ;register first')
      else:
        # gets all cell values of top row
        rowValues = self.spreadsheet.get_row(message.channel.guild.name, f'{message.author.id}', 0)
        print(rowValues)
        count = 0
        headers = ''
        
        # compiling arguments in message contents
        headers = " ".join(str(next_header) for next_header in args)
        
        # find every second column so that I can fit datetime values for each cell (B, D, F, etc are all data columns while the other odds contain dates)
        for i in rowValues:
          count += 1
        
        # check for odd numbers and convert to even (why? -VC)
        if (count % 2 == 1):
          count += 1
          
        # same title column values cause issues I dont want to build around
        if headers in rowValues:
          await message.channel.send(f'You can\'t make two headers of the same name. \n(if ur trying to find bugs id like you to know ur an asshole)')
          
        else:
          self.spreadsheet.write_cell(message.channel.guild.name, f'{message.author.id}', f'{string.ascii_uppercase[count]}1', headers)
          await message.channel.send(f'Making header:`"{headers}"` on `{string.ascii_uppercase[count]}1` in file <@{message.author.id}>')


    @bot.command()
    async def displayHeaders(message): 
      if self.author_id_worksheet_not_found(message.channel.guild.name, message.author.id):
        await message.channel.send('you need to register a spreadsheet with ;register first')
      else:
        colValues = self.spreadsheet.get_row(message.channel.guild.name, f'{message.author.id}', 0)
        cleaned = []
        reformat = '['
        
        for i in colValues:
          if i != '':
            cleaned.append(i)
        
        # save last value in list to prevent it ending in a comma
        for i in range(0, len(cleaned)-1):
          reformat += f'`{cleaned[i]}`, '
          
        reformat += f'`{cleaned[-1]}`]' if len(cleaned) > 0 else '``]'
        bindEmbed = discord.Embed(color=0xFF99E5)
        bindEmbed.add_field(name='List of headers:', value=f'{reformat}', inline=True)
        
        await message.channel.send(embed=bindEmbed)
        
    @bot.command()
    async def postData(message, *args):
      if self.author_id_worksheet_not_found(message.channel.guild.name, message.author.id):
        await message.channel.send('you need to register a spreadsheet with ;register first')
      else:
        #holy fucking shit this may work but its slow as fuck fix it when u got time
        headers = ''
        for i in range(0, len(args)-2):
          headers += args[i] + ' '
        headers += args[-2]

        self.findColumn(message.channel.guild.name, f'{message.author.id}', headers)
        if self.test != True:
          await message.channel.send(f'There is no header called `{headers}`. Try ;displayHeaders to see what headers you have')
        else:
          count = 1
          while True:
            cell = string.ascii_uppercase[self.matching_header_index] + str(count)
            datecell = string.ascii_uppercase[self.matching_header_index-1] + str(count)

            cellValue = self.spreadsheet.get_cell(message.channel.guild.name, f'{message.author.id}', cell)
            if cellValue == '':
              now = datetime.datetime.now()
              formatted = now.strftime("%d/%m/%Y %H:%M:%S")
              
              self.spreadsheet.write_cell(message.channel.guild.name, f'{message.author.id}', datecell, formatted)
              self.spreadsheet.write_cell(message.channel.guild.name, f'{message.author.id}', cell, args[-1])
              bindEmbed = discord.Embed(color=0xFF99E5)
              bindEmbed.set_author(name=f'Header: `{headers}`')
              bindEmbed.add_field(name=f'Cell Value: `{cell}`', value=f'Data: `{args[-1]}`', inline=True)
              await message.channel.send(embed=bindEmbed)
              break

            count += 1

    @bot.command()
    async def rawData(message, *args):
      if self.author_id_worksheet_not_found(message.channel.guild.name, message.author.id):
        await message.channel.send('you need to register a spreadsheet with ;register first')
      else:
        headers = ''
        for i in args:
          if i != args[-1]:
            headers += i + ' '
        headers += args[-1]

        self.findColumn(message.channel.guild.name, f'{message.author.id}', headers)
        if self.test != True:
            await message.channel.send(f'There is no header called `{headers}`. Try ;displayHeaders to see what headers you have')
        else:
          columnValue = self.spreadsheet.get_column(self.matching_header_index+1)
          totalString = ''
          cell = string.ascii_uppercase[self.matching_header_index] + '2'
          for i in range(len(columnValue)):
            if i != 0 or len(columnValue)-1:
              
              totalString += f'(`{cell}`): ' + columnValue[i] + '\n'
              cell = string.ascii_uppercase[self.matching_header_index] + f'{i+2}'
          totalString += f'(`{cell}`): ' + columnValue[-1]

          bindEmbed = discord.Embed(color=0xFF99E5)
          bindEmbed.set_author(name=f'Getting values of {headers}')
          bindEmbed.add_field(name=f'Column: {headers}', value=f'{totalString}', inline=True)
          bindEmbed.set_footer(text=f'Note that cells begin at {string.ascii_uppercase[self.matching_header_index]}2, because the first cell is occupied by the header (title)')
          await message.channel.send(embed=bindEmbed)

    
    @bot.command()
    async def rawSheet(message):
      if self.author_id_worksheet_not_found(message.channel.guild.name, message.author.id):
        await message.channel.send('you need to register a spreadsheet with ;register first')
      else:
        rows = self.spreadsheet.get_row(message.channel.guild.name, f'{message.author.id}', 0)
        
        bindEmbed = discord.Embed(color=0xFF99E5)
        bindEmbed.set_author(name=f'Getting values of <@{message.author.id}>')
        
        for header in rows:
          if header != '':
            column = self.spreadsheet.get_column(header)
            print(column)
        '''
        for header in rows:
          column = self.spreadsheet.get_column(count)
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
      if self.author_id_worksheet_not_found(message.channel.guild.name, message.author.id):
        await message.channel.send('you need to register a spreadsheet with ;register first')
      else:
        temp = ''
        for i in range(len(args)):
          if i != 0:
            temp += args[i]
            
        try:
          if args[0][1] != '1':
            self.spreadsheet.write_cell(message.channel.guild.name, f'{message.author.id}', args[0], temp)
            await message.channel.send(f'replaced `{args[0]}` with `{temp}`')
          else:
            await message.channel.send('you cant replace headers')
        except:
          await message.channel.send('something went wrong?')
          

    @bot.command()
    async def basicAnalysis(message):
      if self.author_id_worksheet_not_found(message.channel.guild.name, message.author.id):
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
      When the bot is first run, obtain credentials for the nextcloud server.
  """
  try:
    NEXTCLOUD_URL = "https://{}".format(os.environ.get('NEXTCLOUD_HOSTNAME', 'localhost'))
  except KeyError:
    print("ERR -- no Nextcloud hostname was found!")
    NEXTCLOUD_URL = input("Enter one now: ")
  
  # DO NOT HARD_CODE PASSWORDS IN PLAINTEXT! -- VC
  user_username = input("Enter your username: ")
  user_password = getpass.getpass("Enter your password: ")
  
  nxc_obj = NextCloud(NEXTCLOUD_URL, user_username, user_password, json_output=True)
  bot = commands.Bot(command_prefix=';')
  
  spreadsheet = spreadsh_mgr.SpreadSheet(nxc_obj)
  dataBot = dataBot(spreadsheet)
  dataBot.run()

