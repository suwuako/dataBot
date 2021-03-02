import gspread
gc = gspread.service_account(filename='credentials.json')

class spreadSheet:
  def __init__(self):
    print('init ran')

  def new_sheet(self):    
    self.dataSheet = gc.create('dataSheet')
    self.get_sheet()

  def get_sheet(self):
    try:
      self.spreadsheet = gc.open('dataSheet')
    except gspread.SpreadsheetNotFound:
      self.new_sheet()

  def new_worksheet(self, name):
    self.worksheet = self.spreadsheet.add_worksheet(title=name, rows="2500", cols="50")
    self.get_worksheet(name)

  def get_worksheet(self, name):
    self.worksheet = self.spreadsheet.worksheet(name)

  def get_row(self, row):
    return self.worksheet.row_values(row)

  def get_column(self, column):
    return self.worksheet.col_values(column)
  
  def get_cell(self, cell):
    return self.worksheet.acell(cell).value

  def write_cell(self, cell, message):
    self.worksheet.update(cell, message)
  
  def run(self):
    self.get_sheet()
    self.get_worksheet('m')
    self.write_cell('A1', 'bruh')


if __name__ == '__main__':
  spreadSheet = spreadSheet()
  spreadSheet.run()
