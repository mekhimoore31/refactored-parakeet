#python library to deal with date and time
from datetime import datetime


#NEXT BIG STEP
#MAKE IT SPECIFIC TO USER INCOME, state what percent of income is needed to save 
#Find categories that may be flagged for over spending from total income percentage


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

Goal_options = {
    "1": "Vacation",
    "2": "College-Fund",
    "3": "General Saving",
    "4": "Retirement",
    "5": "Other"
}


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

class User_Responses:
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
    #something like
    #def calc_salary(self)
        #info = User_Info()
        #user income = expected salary in time period
        #divided by pay rate input
        #should return value of pay

    #need some retroactive function where
    #You saved *this much* from last weeks pay check, you need to save *this much*
    #to stay on pace



    def calc_save_time(self, target_amount, target_date_s):
        today = datetime.today()
        #Turns string into actual date time object to do calcs
        target_date = datetime.strptime(target_date_s, '%Y-%m-%d')
        
        #calc num of days left
        #.days extracts number of days from time difference
        days_left = (target_date - today).days
        weeks_left = round(days_left / 7)

        #to calculate amount needed to save per week
        save_per_week = target_amount/weeks_left

        print(f'You have {weeks_left} weeks left until your goal')


        return round(save_per_week,2)
   

       
    

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
                print('What are you saving for?\n')
                print("1. Vacation")
                print("2. College-Fund")
                print("3. General Saving")
                print("4. Retirement")
                print("5. Other")

                
                

                save_reason = input('Please enter a number: ')

                if save_reason in Goal_options:
                    goal_name = Goal_options[save_reason]
                
                if user_input.isdigit() and 1 <= int(save_reason) <= 4:
                    print(f"Great! Let's start saving for your {goal_name}")
                
                elif user_input.isdigit() and int(save_reason) == 5:
                    other_type = input('Please type out your reason: ')

                else:
                    print('Please select a number from 1-5')
                
                
                #Ask user for goal amount
                print('How much are you hoping to save?')
                save_amount = float(input('Please enter a numeric value: '))

                #Ask for goal time
                print('When you want to reach your goal?')
                save_time = input('Please enter the desired date to reach your goal (in YYYY-mm-d): ')

                #Then we will print something like
                goal_msg = (f'You need to save ${self.calc_save_time(save_amount, save_time)} per week to reach your goal')
                
                print(goal_msg)

                #Next step, store save amount and save time, need to subtract amount saved from total save amount
                #

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
                print('Invalid choice. Choose a number from 1 to 5.')




if __name__ == '__main__':
    budget = Budget_stuff()
    budget.start()