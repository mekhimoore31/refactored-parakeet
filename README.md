# refactored-parakeet

My CS32 final project - Mekhi Moore

## THE GOAL
I will be attempting to create a budgeting aid that will help an individual
save up money for a specific goal (i.e college-fund, a vacation, Christmas shopping, etc.). The aid will be user-specific, and depending on a user's income and spending habits, it will give a specific amount that should be saved on a week-by-week basis to hit a goal by a certain time.

## INSTRUCTIONS
The program is made to be run directly in your terminal. Upon running the program called "user_side.py", the user will pick a number that corresponds to the action they wish to take. Following that choice the program will ask a series of queries that the user will submit inputs for. Data will be saved directly in the program and can be accesed at anytime by the user selecting the appropriate choice from the main menu, which will then allow it to be displayed in the terminal.

## CONTRIBUTIONS
Generative AI was used to develop the appropriate code to save and view user inputs and for instructions for using sqlite3. The only full functions that written using generative AI were the create_tables function (found on line 49 of friendly_calcs.py) and the save goal function (found on line 90 of friendly_calcs.py). The lines that follow that function were written by myself, but with consultation with AI on how to use things like cursor, deleting saved entries from our data file, and how to view them. Also in creating the 2 functions other_expense_breakdown and nonessential_recs in the friendly_calcs.py file (lines 262 and 278 respectively), I was able to figure out the implementation of them mostly by myself, but used AI to check over it.

In learning how to properly implement the datetime python module, I consulted both the python library documentation and W3 schools 
as an online resource.

Python datetime documentation: https://docs.python.org/3/library/datetime.html

Python sqlite documentation: https://docs.python.org/3/library/sqlite3.html

The appropriate link to W3 schools datetime info and instructions can be found here: https://www.w3schools.com/python/python_datetime.asp




