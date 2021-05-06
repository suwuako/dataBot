#!/usr/bin/env python3
"""
    A consolidated class to unify the gspreadtest class and the
    minimal_upload_example.
    It serves as a replacement for Google Drive by periodically syncing with
    Nextcloud instead.
"""

# python libraries
import os
import re # to parse cell names
import string

# third-party dependencies
import collections   # for OrderedDict
import getpass       # for getting the nextcloud user's password securely
import pyexcel_ods   # for using an open spreadsheet format
#import pyexcel_odsr # for pagination: https://github.com/pyexcel/pyexcel-odsr

from nextcloud import NextCloud

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
    print("[DEBUG]    Constructor is being run")
    if (nextcld != None):
      print("[     ]        nextcloud sync is set ON")
      self.enable_sync = True
      self.nc_obj = nextcld
      #self.nc_host = kwargs["nc_url"]
      #self.nc_user = kwargs["nc_user"]
      #self.nc_pass = kwargs["nc_pass"]
    else:
      print("[     ]        nextcloud sync is set OFF")
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
    new_worksheet("default")
    if (assigned_name == None or assigned_name == ""):
      pyexcel_ods.save_data("dataSheet.ods", self.book)
    else:
      pyexcel_ods.save_data(assigned_name, self.book)

  # renamed from get_sheet to get_book, in the interest of clarity
  def get_book(self, filename):
    try:
      self.book = pyexcel_ods.get_data(filename)
    except FileNotFoundError:
      self.new_book(filename)

  # This call creates a new 2d array (for a new sheet inside the spreadsheet
  # book), also allowing the user to specify a custom size of the array.
  def new_worksheet(self, name, row_ct=2000, col_ct=20):
    self.worksheet_name = name
    sheet_as_arr = [[]]
    for i in range(0, row_ct):
      sheet_as_arr.append([])
      for h in range(0, col_ct):
        sheet_as_arr[i].append('')
    
    sheet_as_dict = { name: sheet_as_arr }
    
    self.book.update(sheet_as_dict)
    return self.book[name]

  def get_worksheet(self, name, force):
    self.worksheet_name = name
    try:
      return self.book[name]
    except KeyError:
      if (force):
        # the `self.` here is necessary...? TODO find out why.
        return self.new_worksheet(name)
      else:
        return None

  def get_row(self, row, wsheet=None):
    if (wsheet == None):
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
    index = len(letter_seq) - 1
    while (index >= 0):
      factor = 1
      count = 0
      upper_limit = len(letter_seq) - index - 1
      
      # get the proper power of 26 to apply.
      # Yes, I know I could use math.pow(), but I am afraid of doubles.
      # Mock me if you want, but integers can grow as large as they need to in
      # python, so there's no risk of imprecision or overflow.
      while (count < upper_limit):
        factor *= 26
        count += 1
      sigma += (string.ascii_uppercase.find(letter_seq[index].upper()) + 1)*factor
      index -= 1
    return sigma

  def get_cell(self, cell_label):
    match_obj = re.match("^(\\w+)(\\d+)$", cell)
    assert(match_obj != None),"Invalid cell name. It must be a sequence of letters followed by a number."
    row_num = int(match_obj.group(2))
    column_num = self.convert_alphabetic_to_column(match_obj.group(1))
    return self.book[worksheetname][row_num][column_num]

  def write_cell(self, cell, message):
    assert (len(cell) >= 2),"Invalid cell size. It must be at least two characters in length."
    
    # RECALL: Valid cell names could be really long like "ACE6561"
    match_obj = re.match("^([a-zA-Z]+)(\\d+)$", cell)
    assert(match_obj != None),"Invalid cell name. It must be a sequence of letters followed by a number."
    
    row = int(match_obj.group(2)) - 1 # indices start at zero
    col = self.convert_alphabetic_to_column(match_obj.group(1)) # index conversion built-in to the member function
    
    print("[DEBUG]    Now OVERWRITING value at row %d, col %d" % (row, col))
    self.book[self.worksheet_name][row][col] = message
    pyexcel_ods.save_data("ok.ods", self.book)

    if (self.enable_sync):
      print("connection to Nextcloud is a WIP")

  def testGetMethods(self):
    self.get_book("dataBook.ods")
    self.get_worksheet('SEIS_DE_MAYO', True)
    self.write_cell('A1', 'bruh zone')
    self.write_cell('C11', 'another test message')

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
  
  r1 = spreadSheet.convert_alphabetic_to_column("C")
  r2 = spreadSheet.convert_alphabetic_to_column("AC")
  r3 = spreadSheet.convert_alphabetic_to_column("CA")
  r4 = spreadSheet.convert_alphabetic_to_column("YA")
  
  print("%d, %d, %d, %d" % (r1, r2, r3, r4))
  
  # test
  spreadSheet.testGetMethods()


