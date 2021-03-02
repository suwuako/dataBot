# -*- coding: utf-8 -*-
"""
Created on Sun Jan 17 01:15:39 2021

@author: User
"""


from gspreadtest import spreadSheet
import pandas
spreadSheet = spreadSheet()

spreadSheet.get_sheet()
ss = spreadSheet.get_worksheet('431491115775164418')
ws = spreadSheet.worksheet

strdata = ws.get_all_values()
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


print(strdf)
print(intdf.describe())
