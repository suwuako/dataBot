#!/usr/bin/env python3
"""
    A consolidated class to unify the gspreadtest class with the
    minimal_upload_example.
    It serves as a replacement for Google Drive by periodically syncing with
    Nextcloud instead.
"""

# python libraries
import os
import re # to parse cell names and check filenames
import string

# third-party dependencies
import collections   # for OrderedDict
import getpass       # for getting the nextcloud user's password securely
import pyexcel_ods   # for using an open spreadsheet format
#import pyexcel_odsr # for pagination: https://github.com/pyexcel/pyexcel-odsr

from nextcloud import NextCloud

local_file_prefix = "local-data/"

"""
    A class to wrap any and all modifications to the spreadsheet files...
    Based on the original implementation that used gspread, this new version
    is intended to be free of Google services and instead process ODS files
    "locally," wherever the bot script is running.

    Let `book` be a wrapper of many `sheets`, and `sheets` be the typical
    definition of a single table of data with a given name.
"""
class SpreadSheet:
  def __init__(self, nextcld, **kwargs):
    self.alphabet_base_powers = [1, 26, 26*26, 26*26*26, 26*26*26*26, 26*26*26*26*26]
    # FIXME: keeping the book name and worksheet name might sooner or later
    # introduce multithreaded problems!!!
    # What if multiple different users try similar commands at the same time???
    # One user might be setting the worksheet name, whereas another user might
    # be trying to get data (headers etc.) from a different worksheet!
    # Then, if the instructions are interlaced, then the variable
    # self.worksheet_name might be reassigned just in the nick of time, by the
    # time the data is retrieved for the second user!
    # Similar problems might potentially exist within the "self.book" variables,
    # if the same bot instance is managing multiple different servers (which
    # might, I believe, be possible).
    #
    # Therefore, I believe we need to restructure the design of this class (add
    # parameters for book name and sheet name to each method!), or at a minimum,
    # add mutexes. :(
    self.worksheet_name = "default"
    if (nextcld != None):
      print("[ constructor ]        nextcloud sync is set ON")
      self.enable_sync = True
      self.nc_obj = nextcld
      #self.nc_host = kwargs["nc_url"]
      #self.nc_user = kwargs["nc_user"]
      #self.nc_pass = kwargs["nc_pass"]
    else:
      print("[ constructor ]        nextcloud sync is set OFF")
      self.nc_obj = None
      self.enable_sync = False

  """
      If enabled, this object can SYNC DATA with a remote nextcloud server
  """
  def sync():
    """
        TODO we also want to download the file to manage changes... right?
        FIXME there'd be race conditions if multiple users try to edit and
        download the same ODS file at the same time... how should we deal with
        this? Add mutexes, or split it up into multiple ODS files, one per user,
        and perhaps add a system of user permissions to each file?
    """
    assert (self.enable_sync),"Sync not enabled for this spreadsheet manager!"
    upload_file(self.book_filename)
  
  # low-level nextcloud-specific functions
  def upload_file(file_name, file_content=None, timestamp=None):
    file_local_path = os.path.join(os.getcwd(), file_name)
    
    # In order to upload the file, create it right here and now!
    # TODO replace with a `tempfile` invocation,
    # in order to prevent overwriting a local file.
    if (file_content is None):
      f = open(file_name, "r")
    else:
      f = open(file_name, "w")
      f.write(str(file_content))
    
    file_local_path = os.path.abspath(file_name)
    print("About to try to upload \"%s\" to %s" % (file_content, file_name))
    try:
      self.nc_obj.upload_file(user_username, file_local_path, file_name, timestamp)
    except Error:
      print("Upload encountered a failure!!")
    print("Just tried to upload...")
    
    # check status code -- TODO port this functionality somehow?
    #assert res.is_ok
    #assert res.raw.status_code == self.CREATED_CODE
    
    # test uploaded file can be found with list_folders
    file_nextcloud_href = os.path.join(WebDAV.API_URL, user_username, file_name)
    folder_info = self.nc_obj.list_folders(user_username, path=file_name)
    assert folder_info.is_ok
    assert len(folder_info.data) == 1
    assert isinstance(folder_info.data[0], dict)
    
    # check href
    assert folder_info.data[0]['href'] == file_nextcloud_href
    
    # remove file on local machine
    os.remove(file_local_path)
    self.nc_obj.download_file(user_username, file_name)
    
    # test file is downloaded to current dir
    assert file_name in os.listdir(".")
    f = open(file_local_path)
    downloaded_file_content = f.read()
    assert downloaded_file_content == file_content

  # renamed from new_sheet to new_book, in the interest of clarity
  def new_book(self, assigned_name):
    self.book_filename = assigned_name
    self.book = collections.OrderedDict()
    self.new_worksheet("default")
    if (assigned_name == None or assigned_name == ""):
      pyexcel_ods.save_data(local_file_prefix + "dataSheet.ods", self.book)
    else:
      pyexcel_ods.save_data(assigned_name, self.book)
  
  def finish_filename(self, book_name):
    prefixed_filename = book_name if re.match("^"+local_file_prefix, book_name) != None else local_file_prefix+"/"+book_name
    return prefixed_filename if re.match(".*\.ods$", prefixed_filename) != None else prefixed_filename+".ods"

  # Precondition: filename is a valid filename in the given file system
  # Postcondition: will retrieve (and create) the proper OrderedDict
  # for the server with the given filename
  def get_book(self, filename, force=True):
    finished_filename = self.finish_filename(filename)
    try:
      self.book = pyexcel_ods.get_data(finished_filename)
      return self.book
    except FileNotFoundError:
      if (force):
        self.new_book(finished_filename)
        return self.book
      else:
        return None

  # This call creates a new 2d array (for a new sheet inside the spreadsheet
  # book), also allowing the user to specify a custom size of the array.
  def new_worksheet(self, book_name, sheet_name, row_ct=2000, col_ct=26):
    finished_filename = self.finish_filename(book_name)
    book_obj = self.get_book(finished_filename, False)
    assert (book_obj != None),"Spreadsheet book has not been set!!"
    self.book = book_name
    self.worksheet_name = sheet_name
    print("setting the sheet name to \"%s\"" % self.worksheet_name)
    sheet_as_arr = [[]]
    for i in range(0, row_ct):
      sheet_as_arr.append([])
      for h in range(0, col_ct):
        sheet_as_arr[i].append('')
    
    sheet_as_dict = { sheet_name: sheet_as_arr }
    
    book_obj.update(sheet_as_dict)
    pyexcel_ods.save_data(finished_filename, book_obj)
    return book_obj[sheet_name]

  def get_worksheet(self, name, force):
    self.worksheet_name = name
    try:
      return self.book[name]
    except KeyError:
      if (force):
        return self.new_worksheet(name)
      else:
        return None

  def get_row(self, book_name, wsheet="default", row=0):
    if (wsheet == None):
      print("argument to get_row is None, so we will use the sheet name \"%s\"" % self.worksheet_name)
      return self.book[self.worksheet_name][row]
    else:
      return self.book[wsheet][row]

  # FIXME add logic to avoid OutOfBounds exceptions!
  def get_column(self, column):
    matrix = self.book[self.worksheet_name]
    return [matrix[row][column] for row in self.book]
  
  """
      GSpread actually offers a `Cell` object that wraps its value, row, and
      column, in addition to its (letter,number) location (aka "cell label")...

      I'm hoping we don't need to define out own cell object, but it is worth
      noting...

      We could of course parse out the label using RegEx, but then there's the
      matter of actually converting the letter sequence to its index.

      here, I make space for an algorithm to do this.
  """
  def convert_alphabetic_to_column(self, letter_seq):
    sigma = 0
    while (len(self.alphabet_base_powers) < len(letter_seq)):
      self.alphabet_base_powers.append(self.alphabet_base_powers[-1] * 26)
    for index in range(0, len(letter_seq)):
      #letter = (string.ascii_uppercase.find(letter_seq[index].upper()) + 1)
      #place_value = self.alphabet_base_powers[len(letter_seq) - index - 1]
      #summand = letter*place_value
      #print("Now adding %d*%d = %d" % (letter, place_value, summand))
      sigma += (string.ascii_uppercase.find(letter_seq[index].upper()) + 1)*self.alphabet_base_powers[len(letter_seq) - index - 1]
    return sigma

  def get_cell(self, book_name, sheet_name, cell_label):
    cleansed_filename = self.finish_filename(book_name)
    book = pyexcel_ods.get_data(cleansed_filename)
    assert (book != None),"Spreadsheet book has not been set!!"
    match_obj = re.match("^([a-zA-Z]+)(\\d+)$", cell_label)
    assert(match_obj != None),"Invalid cell name. It must be a sequence of letters followed by a number."
    row_num = int(match_obj.group(2)) - 1
    column_num = self.convert_alphabetic_to_column(match_obj.group(1)) - 1
    while (row_num >= len(book[sheet_name])):
      book[sheet_name].append(['']*column_num)
    while (column_num+1 >= len(book[sheet_name][row_num])):
      # fill the sheet with more COLUMNS in order to be able to access the given index
      book[sheet_name][row_num].append('')
    return book[sheet_name][row_num][column_num]

  def write_cell(self, book_name, sheet_name, cell, message):
    cleansed_filename = self.finish_filename(book_name)
    book = pyexcel_ods.get_data(cleansed_filename)
    assert (book != None),"Spreadsheet book has not been set!!"
    assert (len(cell) >= 2),"Invalid cell size. It must be at least two characters in length."
    
    # RECALL: Valid cell names could be really long like "ACE6561"
    match_obj = re.match("^([a-zA-Z]+)(\\d+)$", cell)
    assert(match_obj != None),"Invalid cell name. It must be a sequence of letters followed by a number."
    
    row = int(match_obj.group(2)) - 1 # don't forget, indices start at zero!
    col = self.convert_alphabetic_to_column(match_obj.group(1)) - 1
    
    print("[DEBUG]    Now trying to write %s at %s[%d][%d]" % (message, sheet_name, row, col))
    selected_sheet = book[sheet_name]
    while (row >= len(selected_sheet)):
      # fill the sheet with more ROWS in order to access the given index
      selected_sheet.append([])
    
    while (col >= len(selected_sheet[row])):
      # fill the sheet with more COLUMNS in order to be able to access the given index
      for i in range(0, (col+1)):
        selected_sheet[row].append('')
    
    book[sheet_name][row][col] = message
    pyexcel_ods.save_data(cleansed_filename, book)
    
    if (self.enable_sync):
      print("connection to Nextcloud is a WIP")

  def test_get_methods(self):
    self.get_book(local_file_prefix+"ok.ods")
    self.get_worksheet('SEIS_DE_NOVIEMBRE', True)
    self.write_cell('ok', 'SEIS_DE_NOVIEMBRE', 'A1', 'bruh zone')
    self.write_cell('ok', 'SEIS_DE_NOVIEMBRE', 'A1', 'am I a valuable person?')
    self.write_cell('ok', 'SEIS_DE_NOVIEMBRE', 'BA1', 'what is the meaning of life?')
    self.write_cell('ok', 'SEIS_DE_NOVIEMBRE', 'AC11', 'isolation is killing chocorho :(')

# TODO put simpler unit tests in a new file
if __name__ == '__main__':
  # nextcloud-related variables
  #try:
  #  NEXTCLOUD_URL = "http://{}:80".format(os.environ.get('NEXTCLOUD_HOSTNAME', 'localhost'))
  #except KeyError:
  
  NEXTCLOUD_URL = input("enter the full nextcloud server url:")
  # DO NOT HARD_CODE PASSWORDS IN PLAINTEXT!
  user_username = input("Enter your username: ")
  user_password = getpass.getpass("Enter your password: ")
  
  nxc_obj = NextCloud(NEXTCLOUD_URL, user_username, user_password, json_output=True)
  
  spreadSheet = SpreadSheet(nxc_obj)
  
  r1  = spreadSheet.convert_alphabetic_to_column("C")
  r2  = spreadSheet.convert_alphabetic_to_column("AC")
  r3  = spreadSheet.convert_alphabetic_to_column("CA")
  r4  = spreadSheet.convert_alphabetic_to_column("YA")
  r5  = spreadSheet.convert_alphabetic_to_column("AA")
  r6  = spreadSheet.convert_alphabetic_to_column("AAA")
  r7  = spreadSheet.convert_alphabetic_to_column("AAAA") # 26 + 26*26 + 26*26*26
  r8  = spreadSheet.convert_alphabetic_to_column("AAAAA")
  r9  = spreadSheet.convert_alphabetic_to_column("AAAAAA")
  r10 = spreadSheet.convert_alphabetic_to_column("AAAAAAA")
  r11 = spreadSheet.convert_alphabetic_to_column("AAAAAAAA")
  
  print("%d, %d, %d, %d" % (r1, r2, r3, r4))
  print("%d, %d, %d, %d, %d, %d, %d" % (r5, r6, r7, r8, r9, r10, r11))
  
  # test
  spreadSheet.test_get_methods()


