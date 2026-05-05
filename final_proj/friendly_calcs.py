import sqlite3
from datetime import datetime, timedelta

#Create a list to access later

EXPENSE_CATS = [
    "Rent/Mortgage",
    "Groceries",
    "Transportation",
    "Utilities/Bills",
    "Other",
]

ESSENTIAL_CATS = [
    "Rent/Mortgage",
    "Groceries",
    "Transportation",
    "Utilities/Bills",
]

GOAL_OPTIONS = {
    "1": "Vacation",
    "2": "College-Fund",
    "3": "General Saving",
    "4": "Retirement",
    "5": "Other",
}


class TargetGoal:
    def __init__(self, name, goal_amount, target_date):
        self.name = name
        self.goal_amount = goal_amount
        self.target_date = target_date


class Expense:
    def __init__(self, category, total_cost, date, description = None):
        self.category = category
        self.total_cost = total_cost
        self.date = date
        self.description = description

#Opens/creates sqlite file
def connect_db(db_name="friendly_finance.db"):
    return sqlite3.connect(db_name)

#Makes tables for expenses and goals if they don't already exist
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
            date TEXT NOT NULL,
            description TEXT
        )
    """)

    conn.commit()

#To calculate amount of time needed to save
def calc_save_time(target_amount, target_date_s):
    today = datetime.today()
    target_date = datetime.strptime(target_date_s, "%Y-%m-%d")

    days_left = (target_date - today).days
    weeks_left = max(1, round(days_left / 7))

    save_per_week = target_amount / weeks_left
    return round(save_per_week, 2), weeks_left


def validate_date(date_string):
    datetime.strptime(date_string, "%Y-%m-%d")
    return True


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


def get_all_goals(conn):
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, name, goal_amount, target_date
        FROM goals
        ORDER BY id ASC
    """)
    return cursor.fetchall()


def add_expense(conn, expense):
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO expenses (category, total_cost, date, description)
        VALUES (?, ?, ?, ?)
    """, (expense.category, expense.total_cost, expense.date, expense.description))
    conn.commit()


def get_all_expenses(conn):
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, category, total_cost, date, description
        FROM expenses
        ORDER BY date ASC
    """)
    return cursor.fetchall()


def get_expenses_by_category(conn, category):
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, category, total_cost, date, description
        FROM expenses
        WHERE category = ?
        ORDER BY date ASC
    """, (category,))
    return cursor.fetchall()


def get_weekly_expenses(conn):
    today = datetime.today()
    start_of_week = today - timedelta(days=today.weekday())
    end_of_week = start_of_week + timedelta(days=6)

    #Sets format as year-month-day
    start_str = start_of_week.strftime("%Y-%m-%d")
    end_str = end_of_week.strftime("%Y-%m-%d")

    cursor = conn.cursor()
    cursor.execute("""
        SELECT COALESCE(SUM(total_cost), 0)
        FROM expenses
        WHERE date BETWEEN ? AND ?
    """, (start_str, end_str))

    total = cursor.fetchone()[0]
    return total, start_str, end_str


def get_monthly_expenses(conn, start_date, end_date):
    cursor = conn.cursor()
    cursor.execute("""
                   SELECT id, category, total_cost, date, description
                   FROM expenses
                   WHERE date BETWEEN ? and ?
                   ORDER BY date ASC
                   """, (start_date, end_date))
    
    return cursor.fetchall()


def get_monthly_summary(conn):
    today = datetime.today()
    #Takes the current day and changes it to the 1st day of the month
    month_start = today.replace(day=1)

    if today.month == 12:
        next_month = today.replace(year=today.year + 1, month=1, day=1)
    else:
        next_month = today.replace(month=today.month + 1, day=1)

    start_str = month_start.strftime("%Y-%m-%d")
    end_str = (next_month - timedelta(days=1)).strftime("%Y-%m-%d")

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

    return {
        "month_label": today.strftime("%B %Y"),
        "start_date": start_str,
        "end_date": end_str,
        "total_spent": total_monthly,
        "categories": category_rows,
    }


def delete_expense(conn, expense_id):
    #Will delete a chosen expense by id number
    cursor = conn.cursor()
    cursor.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
    conn.commit()
    return cursor.rowcount > 0


def delete_goal(conn, goal_id):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM goals WHERE id = ?", (goal_id,))
    conn.commit()
    return cursor.rowcount > 0


def delete_all_expenses(conn):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM expenses")
    #Clears out all expenses and their ids
    cursor.execute("DELETE FROM sqlite_sequence WHERE name = 'expenses'")
    #Saves that action of deleting
    conn.commit()


def delete_all_goals(conn):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM goals")
    cursor.execute("DELETE FROM sqlite_sequence WHERE name = 'goals'")
    conn.commit()


def categorize_expense(category):
    #determines wheter a category is considered essential or not
    if category in ESSENTIAL_CATS:
        return "Essential"
    return "Non-essential"

def other_expense_breakdown(conn, start_date, end_date):
    cursor = conn.cursor()
    cursor.execute("""
                   SELECT description, SUM(total_cost)
                   FROM expenses
                   WHERE category = 'Other'
                   AND date BETWEEN ? and ?
                   GROUP by description
                   ORDER by SUM(total_cost) DESC
                   """,
                   (start_date, end_date))
    
    return cursor.fetchall()


#THE FINAL BIT - LET'S MAKE SOME RECS
def nonessential_recs(conn, start_date, end_date):
    cursor = conn.cursor()
    cursor.execute("""
        SELECT description, SUM(total_cost)
        FROM expenses
        WHERE category = 'Other'
        AND date BETWEEN ? and ?
        GROUP BY description
        ORDER BY SUM(total_cost) DESC
        """,
        (start_date, end_date))
    

    rows = cursor.fetchall()

    #Make an empty list to store all of the reccomendations
    recs = []
    for description, total_cost in rows:
        recs.append((description, total_cost))

    return recs
                    
    