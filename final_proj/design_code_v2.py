import sqlite3
from datetime import datetime, timedelta

#Create a list to access later
EXPENSE_CATS = [
    'Rent/Mortgage',
    'Food',
    'Transportation',
    'Utilities/Bills',
    'Other',
]

GOAL_OPTIONS = {
    "1": "Vacation",
    "2": "College-Fund",
    "3": "General Saving",
    "4": "Retirement",
    "5": "Other"
}


class TargetGoal:
    def __init__(self, name, goal_amount, target_date):
        self.name = name
        self.goal_amount = goal_amount
        self.target_date = target_date


class Expense:
    def __init__(self, category, total_cost, date):
        self.category = category
        self.total_cost = total_cost
        self.date = date


#Opens/creates sqlite file
def connect_db(db_name="friendly_finance.db"):
    return sqlite3.connect(db_name)

#Makes tables for expenses and goals if they don't already exist, then saves them to database
def create_tables(conn):
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS goals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            goal_amount REAL NOT NULL,
            target_date TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL,
            total_cost REAL NOT NULL,
            date TEXT NOT NULL
        )
    """)

    conn.commit()


def welcome_msg():
    print("Welcome to Friendly Finance")
    print("We hope to help you on your budgeting journey!")


#To calculate amount of time needed to save
def calc_save_time(target_amount, target_date_s):
    today = datetime.today()
    target_date = datetime.strptime(target_date_s, '%Y-%m-%d')

    days_left = (target_date - today).days
    weeks_left = max(1, round(days_left / 7))

    save_per_week = target_amount / weeks_left
    return round(save_per_week, 2), weeks_left


def save_goal(conn, goal):
    #Cursor sends sql command to database file
    cursor = conn.cursor()
    #Execute does the action
    cursor.execute("""
        INSERT INTO goals (name, goal_amount, target_date)
        VALUES (?, ?, ?)
    """, (goal.name, goal.goal_amount, goal.target_date))
    conn.commit()


def get_current_goal(conn):
    cursor = conn.cursor()
    cursor.execute("""
        SELECT name, goal_amount, target_date
        FROM goals
        ORDER BY id DESC
        LIMIT 1
    """)
    return cursor.fetchone()


def show_all_goals(conn):
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, name, goal_amount, target_date
        FROM goals
        ORDER BY id ASC
    """)
    rows = cursor.fetchall()

    if not rows:
        print("No goals found.")
        return

    print("\nAll Goals:\n")
    for row in rows:
        goal_id, name, amount, target_date = row
        print(f"ID: {goal_id} | {name} | ${amount:.2f} | Target Date: {target_date}")


def add_expense(conn, expense):
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO expenses (category, total_cost, date)
        VALUES (?, ?, ?)
    """, (expense.category, expense.total_cost, expense.date))
    conn.commit()


def show_all_expenses(conn):
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, category, total_cost, date
        FROM expenses
        ORDER BY date ASC
    """)
    rows = cursor.fetchall()

    if not rows:
        print("No expenses found.")
        return

    print("\nAll Expenses:\n")
    for row in rows:
        expense_id, category, cost, expense_date = row
        print(f"ID: {expense_id} | {category} | ${cost:.2f} | {expense_date}")


def show_expenses_by_category(conn, category):
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, category, total_cost, date
        FROM expenses
        WHERE category = ?
        ORDER BY date ASC
    """, (category,))
    rows = cursor.fetchall()

    if not rows:
        print(f"No expenses found for category: {category}")
        return

    print(f"\nExpenses for {category}:\n")
    for row in rows:
        expense_id, category, cost, expense_date = row
        print(f"ID: {expense_id} | {category} | ${cost:.2f} | {expense_date}")


def get_weekly_expenses(conn):
    today = datetime.today()
    start_of_week = today - timedelta(days=today.weekday())
    end_of_week = start_of_week + timedelta(days=6)

    #Sets format as year-month-day
    start_str = start_of_week.strftime('%Y-%m-%d')
    end_str = end_of_week.strftime('%Y-%m-%d')

    cursor = conn.cursor()
    cursor.execute("""
        SELECT COALESCE(SUM(total_cost), 0)
        FROM expenses
        WHERE date BETWEEN ? AND ?
    """, (start_str, end_str))

    total = cursor.fetchone()[0]
    return total, start_str, end_str


def monthly_summary(conn):
    today = datetime.today()
    #Takes the current day and changes it to the 1st day of the month
    month_start = today.replace(day=1)

    if today.month == 12:
        next_month = today.replace(year=today.year + 1, month=1, day=1)
    else:
        next_month = today.replace(month=today.month + 1, day=1)

    start_str = month_start.strftime('%Y-%m-%d')
    end_str = (next_month - timedelta(days=1)).strftime('%Y-%m-%d')

    cursor = conn.cursor()

    cursor.execute("""
        SELECT COALESCE(SUM(total_cost), 0)
        FROM expenses
        WHERE date BETWEEN ? AND ?
    """, (start_str, end_str))
    total_monthly = cursor.fetchone()[0]

    cursor.execute("""
        SELECT category, COALESCE(SUM(total_cost), 0)
        FROM expenses
        WHERE date BETWEEN ? AND ?
        GROUP BY category
        ORDER BY SUM(total_cost) DESC
    """, (start_str, end_str))
    #Grabs all rows of a query result
    category_rows = cursor.fetchall()

    print(f"\nMonthly Summary for {today.strftime('%B %Y')}")
    print(f"Date Range: {start_str} to {end_str}")
    print(f"Total Spent: ${total_monthly:.2f}")

    if not category_rows:
        print("No expenses recorded for this month.")
        return

    print("\nSpending by Category:")

    #Prints each expense category and its total amount, formatted like money
    for category, total in category_rows:
        print(f"{category}: ${total:.2f}")

def delete_expense(conn, expense_id):
    #Will delete a chosen expense by user by id number
    cursor = conn.cursor()
    my_query = "delete from expenses where id = ?"
    cursor.execute(my_query, (expense_id,))

    conn.commit()

    if cursor.rowcount == 0:
        print("No expense with that ID.")
    else:
        print("Expense deleted.")

def delete_goal(conn, goal_id):
    cursor = conn.cursor()
    my_query = "delete from goals where id = ?"
    cursor.execute(my_query, (goal_id,))

    conn.commit()

    if cursor.rowcount == 0:
        print("No goal with that ID")
    else:
        print("Goal deleted")

def delete_all_expenses(conn):
    cursor = conn.cursor()
    cursor.execute("delete from expenses")
    #Clears out all expenses and their ids
    cursor.execute("delete from sqlite_sequence where name = 'expenses'")
    #Saves that action of deleting
    conn.commit()
    print("All expenses have been deleted")

def delete_all_goals(conn):
    cursor = conn.cursor()
    cursor.execute("delete from goals")
    cursor.execute("delete from sqlite_sequence where name = 'goals'")
    conn.commit()
    print("All goals have been deleted")

def start_msg():
        print('\nWhat would you like to do?\n')
        print('1. Set a goal                    2. View most recent goal')
        # print('2. Check Current Goal')
        print('3. Enter an expense              4. View expenses by week')
        # print('4. Expenses by week')
        print('5. View all expenses             6. View all goals')
        # print('6. Show all goals')
        print('7. View expenses by category     8. Monthly expense summary')
        # print('8. Monthly summary')
        print('9. Delete 1 expense              10. Delete 1 goal')
        # print('10. Delete 1 goal')
        print('11. Delete all expenses          12. Delete all goals')
        # print('12. Delete all goals')
        print('13. Exit')



def start_program():
    conn = connect_db()
    create_tables(conn)
    welcome_msg()

    while True:
        start_msg()

        user_input = input('Please choose an option: ').strip()

        if user_input == '1':
            print('What are you saving for?\n')
            for key, value in GOAL_OPTIONS.items():
                print(f"{key}. {value}")

            save_reason = input('Please enter a number: ').strip()

            if save_reason not in GOAL_OPTIONS:
                print('Please select a number from 1-5')
                continue

            goal_name = GOAL_OPTIONS[save_reason]
            if save_reason == "5":
                goal_name = input('Please type out your reason: ').strip()

            try:
                save_amount = float(input('How much are you hoping to save? '))
            except ValueError:
                print('Please enter a valid numeric value.')
                continue

            save_time = input('Enter target date (YYYY-MM-DD): ').strip()

            try:
                save_per_week, weeks_left = calc_save_time(save_amount, save_time)
            except ValueError:
                print('Invalid date format.')
                continue

            goal = TargetGoal(goal_name, save_amount, save_time)
            save_goal(conn, goal)

            print(f'You have {weeks_left} weeks left.')
            print(f'You need to save ${save_per_week:.2f} per week.')

        elif user_input == '2':

            #Go fetch the current goal from the database and store it in goal
            goal = get_current_goal(conn)
            if goal is None:
                print('No goal has been set yet.')
            else:
                name, amount, target_date = goal
                print(f'Current goal: {name}')
                print(f'Goal amount: ${amount:.2f}')
                print(f'Target date: {target_date}')

        elif user_input == '3':
            print('What type of expense would you like to log?\n')
            for i, category in enumerate(EXPENSE_CATS, start=1):
                print(f'{i}. {category}')

            cat_choice = input('Choose a category number: ').strip()
            if not cat_choice.isdigit() or not (1 <= int(cat_choice) <= len(EXPENSE_CATS)):
                print('Invalid category choice.')
                continue

            category = EXPENSE_CATS[int(cat_choice) - 1]

            try:
                total_cost = float(input('How much was the expense? '))
            except ValueError:
                print('Please enter a valid number.')
                continue

            expense_date = input('What is the date of the expense? (YYYY-MM-DD): ').strip()

            try:
                datetime.strptime(expense_date, '%Y-%m-%d')
            except ValueError:
                print('Invalid date format.')
                continue

            expense = Expense(category, total_cost, expense_date)
            add_expense(conn, expense)
            print('Expense saved successfully.')

        elif user_input == '4':
            total, start_date, end_date = get_weekly_expenses(conn)
            print(f'You spent ${total:.2f} from {start_date} to {end_date}')

        elif user_input == '5':
            show_all_expenses(conn)

        elif user_input == '6':
            show_all_goals(conn)

        elif user_input == '7':
            print('\nChoose a category:\n')
            for i, category in enumerate(EXPENSE_CATS, start=1):
                print(f'{i}. {category}')


            cat_choice = input('Choose a category number: ').strip()
            #If it’s not a valid number or not within the list range, reject it and ask again
            if not cat_choice.isdigit() or not (1 <= int(cat_choice) <= len(EXPENSE_CATS)):
                print('Invalid category choice.')
                continue

            category = EXPENSE_CATS[int(cat_choice) - 1]
            show_expenses_by_category(conn, category)

        elif user_input == '8':
            monthly_summary(conn)


        elif user_input == '9':
            show_all_expenses(conn)

            try:
                expense_id = int(input("Please enter the ID of the expense you wish to delete: ").strip())
                delete_expense(conn, expense_id)
            except ValueError:
                print("Please enter a valid ID number.")

        elif user_input == '10':
            show_all_goals(conn)
            
            try:
                goal_id = int(input("Please enter the ID of the goal you wish to delete: ").strip())
                delete_goal(conn, goal_id)
            except ValueError:
                print("Please enter a valid ID number.")
        elif user_input == '11':
            print("Please respond to the following with y or n")
            check = input("Are you sure you want to delete ALL expenses?  ")

            if check == "y":
                delete_all_expenses(conn)
            else:
                print("Action Canceled")

        elif user_input == '12':
            print("Please respond to the following with y or n")
            check = input("Are you sure you want to delete ALL goals?  ")

            if check == "y":
                delete_all_goals(conn)
            else:
                print("Action Canceled")

        elif user_input == '13':
            print('Thank you for using Friendly Finance')
            print('Have a nice day!')
            conn.close()
            break

        else:
            print('Invalid choice. Choose a number from 1 to 13.')


if __name__ == '__main__':
    start_program()