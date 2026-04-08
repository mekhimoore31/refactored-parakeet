#python library to deal with date and time
from datetime import datetime

#Need to store the data somewhere to keep
#record of the users budget info


#Categories for a user to indicate expense from
Expense_cats = [
    'Rent/Mortgage',
    'Food',
    'Transportation',
    'Utilites/Bills',
    'Other',

]


#dictionary of options for a user to indicate how often they are paid by week
Pay_rate = {
    'weekly': 1 ,
    'biweekly': 2 , 
    'monthly': 52/12 ,
    'salary': 52 ,
}

Goal_options = [
    'Vacation',
    'College-Fund',
    'General Saving',
    'Retirement',
    'Other'
]


#To figure out user goal
class Target_Goal:
    def __init__(self, name, goal_amount, num_weeks):
        self.name = name
        self.goal_amount = goal_amount
        self.num_weeks = num_weeks

#To get user info
class User_Info:
     def __init__(self, name, weekly_inc, goal):
        self.name = name
        self.weekly_inc = weekly_inc
        self.goal = goal

#For figuring out expenses
class Expense:
    def __init__(self, category, total_cost, date):
        self.category = category
        self.total_cost = total_cost
        self.date = date

#Actual budgeting part of the program
class Budget_stuff:


    #Our welcome message for the user
    def welcome_msg(self):
        print('Welcome to Friendly Finance')
        print('We hope to help you on your budgeting journey!')


    #function to calculate weekly salary if not already
    # reported as weekly
    
    # function to 

    #
    

    def start(self):
        self.welcome_msg()
        
        while True:
            print('\nWhat would you like to do?\n')
            print('1. Set a goal')
            print('2. Check Current Goal')
            print('3. Enter an expense')
            print("4. Expenses by week")
            print('5. Exit' )

            user_input = input('Please choose an option: ').strip()

            #The following are just test outputs that show what we would expect

            if user_input == '1':
                print('What are you saving for?')
                print('User: vacation')
                #Will come from a list of options like vacation, college-fund, etc,
                #Let's say user chose vaction
                print("Great! Let's start saving for vacation")
                #Ask user for goal amount
                print('How much are you hoping to save?')
                print('User: $2100')
                print('How long until you want to reach your goal?')
                print('User: Septermber 23, 2026')
                #Then we will print something like
                print('\nYou will need to save $175 a week for 12 weeks to reach your goal')

            elif user_input == '2':
                #Want to tell user how much time they have left and how much money left
                print('You have 9 weeks left to reach your goal')
                print('You are $1,927 away from your goal, keep up the good work!')

            elif user_input == '3':
                #Ask user for category of expense
                print('What type of expense would you like to log?\n')
                #Will have the aforementioned list of expenses
                print('How much was the expense? ')
                #Ask date when
                print('What is the date of the expense? ')

            elif user_input == '4':
                #Have a way of tracking how many expenses within a given period
                #EXAMPLE - just hardcoding things for now
                
                #Ask user for time period (Sunday-Saturday week schedule)
                print('You spent $843 from April 5 - April 11')
            
            #If user wants to exit, send a goodbye message
            elif user_input == '5':
                print('Thank you for using Friendly Finance')
                print('Have a nice day!')
                break
            #Make sure the user puts in a number option for simplicity sake
            else:
                print('Invalid choice. Choose a number from 1 to 6.')




if __name__ == '__main__':
    budget = Budget_stuff()
    budget.start()