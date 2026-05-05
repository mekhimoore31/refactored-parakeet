from friendly_calcs import (EXPENSE_CATS, GOAL_OPTIONS, TargetGoal, Expense,
    connect_db, create_tables, calc_save_time, validate_date, save_goal, get_current_goal,
    get_all_goals, add_expense, get_all_expenses, get_expenses_by_category, get_weekly_expenses,
    get_monthly_summary, delete_expense, delete_goal, delete_all_expenses, delete_all_goals, categorize_expense, other_expense_breakdown,
    get_monthly_expenses, nonessential_recs)


def welcome_msg():
    print("Welcome to Friendly Finance")
    print("We hope to help you on your budgeting journey!")


def start_msg():
    print("\nWhat would you like to do?\n")
    print("1. Set a goal                    2. View most recent goal")
    print("3. Enter an expense              4. View expenses this week")
    print("5. View all expenses             6. View all goals")
    print("7. View expenses by category     8. Monthly expense summary")
    print("9. Delete 1 expense              10. Delete 1 goal")
    print("11. Delete all expenses          12. Delete all goals")
    print("13. Budgeting Reccomendations    14. Exit")


def print_goals(rows):
    if not rows:
        print("No goals found.")
        return

    print("\nAll Goals:\n")
    for goal_id, name, amount, target_date in rows:
        print(f"ID: {goal_id} | {name} | ${amount:.2f} | Target Date: {target_date}")


def print_expenses(rows):
    if not rows:
        print("No expenses found.")
        return

    print("\nAll Expenses:\n")
    for expense_id, category, cost, expense_date, description in rows:
        status = categorize_expense(category)

        if category == "Other" and description:
            display_name = description

        else:
            display_name = category

        print(f"ID: {expense_id} | {display_name} | {status} | ${cost:.2f} | {expense_date}")


def choose_expense_category():
    print("What type of expense would you like to log?\n")
    for i, category in enumerate(EXPENSE_CATS, start=1):
        print(f"{i}. {category}")

    cat_choice = input("Choose a category number: ").strip()
    if not cat_choice.isdigit() or not (1 <= int(cat_choice) <= len(EXPENSE_CATS)):
        print("Invalid category choice.")
        return None

    return EXPENSE_CATS[int(cat_choice) - 1]


def choose_category_for_view():
    print("\nChoose a category:\n")
    for i, category in enumerate(EXPENSE_CATS, start=1):
        print(f"{i}. {category}")

    cat_choice = input("Choose a category number: ").strip()
    if not cat_choice.isdigit() or not (1 <= int(cat_choice) <= len(EXPENSE_CATS)):
        print("Invalid category choice.")
        return None

    return EXPENSE_CATS[int(cat_choice) - 1]


def handle_set_goal(conn):
    print("What are you saving for?\n")
    for key, value in GOAL_OPTIONS.items():
        print(f"{key}. {value}")

    save_reason = input("Please enter a number: ").strip()

    if save_reason not in GOAL_OPTIONS:
        print("Please select a number from 1-5")
        return

    goal_name = GOAL_OPTIONS[save_reason]
    if save_reason == "5":
        goal_name = input("Please type out your reason: ").strip()

    try:
        save_amount = float(input("How much are you hoping to save? "))
    except ValueError:
        print("Please enter a valid numeric value.")
        return

    save_time = input("Enter target date (YYYY-MM-DD): ").strip()

    try:
        save_per_week, weeks_left = calc_save_time(save_amount, save_time)
    except ValueError:
        print("Invalid date format.")
        return

    goal = TargetGoal(goal_name, save_amount, save_time)
    save_goal(conn, goal)

    print(f"You have {weeks_left} weeks left.")
    print(f"You need to save ${save_per_week:.2f} per week.")


def handle_view_current_goal(conn):
    goal = get_current_goal(conn)

    #Go fetch the current goal from the database and store it in goal
    if goal is None:
        print("No goal has been set yet.")
        return

    name, amount, target_date = goal
    print(f"Current goal: {name}")
    print(f"Goal amount: ${amount:.2f}")
    print(f"Target date: {target_date}")


def handle_add_expense(conn):
    #prompts user to choose category
    category = choose_expense_category()

    description = None
    #allows user to add a custom description for expense
    if category == "Other":
        description = input("What would you like to call this expense? ").strip()

    if category is None:
        return

    try:
        total_cost = float(input("How much was the expense? "))
    except ValueError:
        print("Please enter a valid number.")
        return

    expense_date = input("What is the date of the expense? (YYYY-MM-DD): ").strip()

    try:
        validate_date(expense_date)
    except ValueError:
        print("Invalid date format.")
        return

    #creates expense object and saves it to db file
    expense = Expense(category, total_cost, expense_date, description)
    add_expense(conn, expense)
    print("Expense saved successfully.")


def handle_view_weekly_expenses(conn):
    total, start_date, end_date = get_weekly_expenses(conn)
    print(f"You spent ${total:.2f} from {start_date} to {end_date}")


def handle_view_all_expenses(conn):
    rows = get_all_expenses(conn)
    print_expenses(rows)


def handle_view_all_goals(conn):
    rows = get_all_goals(conn)
    print_goals(rows)


def handle_view_expenses_by_category(conn):
    category = choose_category_for_view()
    if category is None:
        return

    rows = get_expenses_by_category(conn, category)
    if not rows:
        print(f"No expenses found for category: {category}")
        return

    print(f"\nExpenses for {category}:\n")
    for expense_id, category_name, cost, expense_date, description in rows:

        if category_name == "Other" and description:
            display_name = description

        else:
            display_name = category_name

        print(f"ID: {expense_id} | {display_name} | ${cost:.2f} | {expense_date}")


def handle_monthly_summary(conn):
    #get totals by month and date range from database
    summary = get_monthly_summary(conn)

    print(f"\nMonthly Summary for {summary['month_label']}")
    print(f"Date Range: {summary['start_date']} to {summary['end_date']}")
    print(f"Total Spent: ${summary['total_spent']:.2f}")

    if not summary["categories"]:
        print("No expenses recorded for this month.")
        return

    #For category totals
    print("\nSpending this month by Category:")
    for category, total in summary["categories"]:
        status = categorize_expense(category)
        print(f"{category} ({status}): ${total:.2f}")


    #provides breakdown of "other" entries with custom descriptions
    other_breakdown = other_expense_breakdown(conn, summary['start_date'], summary['end_date'])

    if other_breakdown:
        print("\nBreakdown of 'Other': ")
        for description, total in other_breakdown:
            if description:
                name = description
            else:
                name = 'Unlabeled'
            
            print(f"{name}: ${total:.2f}")

    monthly_expenses = get_monthly_expenses(conn, summary['start_date'], summary['end_date'])

    #displays all individual expenses this month
    print('\nAll Expenses This Month: ')
    for expense_id, category, total_cost, expense_date, description in monthly_expenses:
        status = categorize_expense(category)

        if category == "Other" and description:
            display_name = description

        else:
            display_name = category

        print(f"{expense_id} | {display_name} | {status} | ${total_cost:.2f} | {expense_date}")


def handle_delete_expense(conn):
    rows = get_all_expenses(conn)
    print_expenses(rows)

    if not rows:
        return

    try:
        expense_id = int(input("Please enter the ID of the expense you wish to delete: ").strip())
    except ValueError:
        print("Please enter a valid ID number.")
        return

    deleted = delete_expense(conn, expense_id)
    if deleted:
        print("Expense deleted.")
    else:
        print("No expense with that ID.")


def handle_delete_goal(conn):
    rows = get_all_goals(conn)
    print_goals(rows)

    if not rows:
        return

    try:
        goal_id = int(input("Please enter the ID of the goal you wish to delete: ").strip())
    except ValueError:
        print("Please enter a valid ID number.")
        return

    deleted = delete_goal(conn, goal_id)
    if deleted:
        print("Goal deleted.")
    else:
        print("No goal with that ID.")


def handle_delete_all_expenses(conn):
    print("Please respond to the following with y or n")
    check = input("Are you sure you want to delete ALL expenses? ").strip().lower()

    if check == "y":
        delete_all_expenses(conn)
        print("All expenses have been deleted")
    else:
        print("Action canceled")


def handle_delete_all_goals(conn):
    print("Please respond to the following with y or n")
    check = input("Are you sure you want to delete ALL goals? ").strip().lower()

    if check == "y":
        delete_all_goals(conn)
        print("All goals have been deleted")
    else:
        print("Action canceled")


def budget_recs(conn):
    summary = get_monthly_summary(conn)

    #gets  non-essential expenses (stuff in the other category)
    recs = nonessential_recs(conn, summary['start_date'], summary['end_date'])

    if not recs:
        print('There are no non-essential expenses this month.\nGreat job!')
        return
    

    print("\nConsider reducing costs for: ")

    for description, total_cost in recs:
        if description:
            name = description
        else:
            name = 'Unlabeled'
    
        print(f"{name}: ${total_cost:.2f}")

    #unpacks the desired tuple entry first, then gets the appropriate index from that tuple
    #essentially just gets the largest non-essential expense
    if recs[0][0] == None:
        top_name = 'Unlabeled'
        
    else:
        top_name = recs[0][0]

    top_total = recs[0][1]

    print(f"\nBiggest opportunity for savings: {top_name} - {top_total}")

def start_program():
    conn = connect_db()
    create_tables(conn)
    welcome_msg()

    while True:
        start_msg()
        user_input = input("Please choose an option: ").strip()

        if user_input == "1":
            handle_set_goal(conn)
        elif user_input == "2":
            handle_view_current_goal(conn)
        elif user_input == "3":
            handle_add_expense(conn)
        elif user_input == "4":
            handle_view_weekly_expenses(conn)
        elif user_input == "5":
            handle_view_all_expenses(conn)
        elif user_input == "6":
            handle_view_all_goals(conn)
        elif user_input == "7":
            handle_view_expenses_by_category(conn)
        elif user_input == "8":
            handle_monthly_summary(conn)
        elif user_input == "9":
            handle_delete_expense(conn)
        elif user_input == "10":
            handle_delete_goal(conn)
        elif user_input == "11":
            handle_delete_all_expenses(conn)
        elif user_input == "12":
            handle_delete_all_goals(conn)
        elif user_input == "13":
            budget_recs(conn)
        elif user_input == "14":
            print("Thank you for using Friendly Finance")
            print("Have a nice day!")
            conn.close()
            break
        else:
            print("Invalid choice. Choose a number from 1 to 14.")


if __name__ == "__main__":
    start_program()