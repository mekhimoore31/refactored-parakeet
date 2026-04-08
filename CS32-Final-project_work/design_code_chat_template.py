import json
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Dict

DATA_FILE = Path("budget_data.json")

DEFAULT_CATEGORIES = [
    "food",
    "transportation",
    "bills",
    "entertainment",
    "housing",
    "health",
    "shopping",
    "education",
    "savings",
    "other",
]

PAY_FREQUENCIES = {
    "weekly": 1,
    "biweekly": 2,
    "monthly": 52 / 12,
    "salary": 52,
}


@dataclass
class Goal:
    name: str
    target_amount: float
    target_weeks: int


@dataclass
class Expense:
    date: str
    amount: float
    category: str
    note: str


@dataclass
class UserProfile:
    name: str
    weekly_income: float
    goal: Goal


class BudgetAssistant:
    def __init__(self) -> None:
        self.data = self.load_data()

    def load_data(self) -> Dict:
        if DATA_FILE.exists():
            try:
                with open(DATA_FILE, "r", encoding="utf-8") as file:
                    return json.load(file)
            except json.JSONDecodeError:
                print("Warning: data file was corrupted. Starting with a fresh profile.")
        return {"profile": None, "expenses": []}

    def save_data(self) -> None:
        with open(DATA_FILE, "w", encoding="utf-8") as file:
            json.dump(self.data, file, indent=4)

    def run(self) -> None:
        self.show_welcome()

        while True:
            print("\nMain Menu")
            print("1. Set up or update profile")
            print("2. Log an expense")
            print("3. Enter a full past week of expenses")
            print("4. View weekly summary")
            print("5. View goal progress")
            print("6. Exit")

            choice = input("Choose an option: ").strip()

            if choice == "1":
                self.setup_profile()
            elif choice == "2":
                self.log_single_expense()
            elif choice == "3":
                self.log_past_week_expenses()
            elif choice == "4":
                self.show_weekly_summary()
            elif choice == "5":
                self.show_goal_progress()
            elif choice == "6":
                self.save_data()
                print("\nGoodbye. Keep building better financial habits one week at a time.")
                break
            else:
                print("Invalid option. Please choose a number from 1 to 6.")

    def show_welcome(self) -> None:
        print("=" * 60)
        print("Welcome to the Budgeting Assistant")
        print("This program helps a user track spending and reach savings goals.")
        print("=" * 60)

    def setup_profile(self) -> None:
        print("\n--- Profile Setup ---")
        name = input("Enter the user's name: ").strip() or "User"

        weekly_income = self.get_weekly_income()

        print("\nSet a savings goal.")
        goal_name = input("What is the goal? (trip, retirement, college fund, etc.): ").strip()
        target_amount = self.get_positive_float("How much would the user like to save in total? $")
        target_weeks = self.get_positive_int("In how many weeks does the user want to reach this goal? ")

        profile = UserProfile(
            name=name,
            weekly_income=weekly_income,
            goal=Goal(
                name=goal_name,
                target_amount=target_amount,
                target_weeks=target_weeks,
            ),
        )

        self.data["profile"] = asdict(profile)
        self.save_data()
        print(f"\nProfile saved for {name}.")
        print(f"Weekly income: ${weekly_income:.2f}")
        print(
            f"To save ${target_amount:.2f} for {goal_name} in {target_weeks} weeks, "
            f"the user should save about ${self.required_weekly_savings():.2f} per week."
        )

    def get_weekly_income(self) -> float:
        print("\nIncome Setup")
        print("Choose how the user is paid:")
        print("1. Weekly")
        print("2. Biweekly")
        print("3. Monthly")
        print("4. Salary (annual)")

        while True:
            choice = input("Enter 1, 2, 3, or 4: ").strip()

            if choice == "1":
                amount = self.get_positive_float("Enter amount earned each week: $")
                return amount
            if choice == "2":
                amount = self.get_positive_float("Enter amount earned every 2 weeks: $")
                return amount / PAY_FREQUENCIES["biweekly"]
            if choice == "3":
                amount = self.get_positive_float("Enter amount earned each month: $")
                return amount / PAY_FREQUENCIES["monthly"]
            if choice == "4":
                amount = self.get_positive_float("Enter annual salary: $")
                return amount / PAY_FREQUENCIES["salary"]

            print("Invalid choice. Please enter 1, 2, 3, or 4.")

    def log_single_expense(self) -> None:
        if not self.profile_exists():
            return

        print("\n--- Log Daily Expense ---")
        expense = self.collect_expense()
        self.data["expenses"].append(asdict(expense))
        self.save_data()
        print("Expense saved.")

    def log_past_week_expenses(self) -> None:
        if not self.profile_exists():
            return

        print("\n--- Enter Previous Week's Expenses ---")
        print("Enter each expense from the last week. Type 'done' when finished.")

        while True:
            done = input("Add an expense? (yes/done): ").strip().lower()
            if done == "done":
                break
            if done != "yes":
                print("Please type 'yes' to continue or 'done' to stop.")
                continue

            expense = self.collect_expense()
            self.data["expenses"].append(asdict(expense))

        self.save_data()
        print("Past week expenses saved.")

    def collect_expense(self) -> Expense:
        amount = self.get_positive_float("Expense amount: $")
        category = self.choose_category()
        note = input("Short note for this expense: ").strip() or "No note"
        date_input = input("Date (YYYY-MM-DD) or press Enter for today: ").strip()

        if not date_input:
            date_input = datetime.today().strftime("%Y-%m-%d")
        else:
            while not self.valid_date(date_input):
                print("Please enter the date in YYYY-MM-DD format.")
                date_input = input("Date (YYYY-MM-DD): ").strip()

        return Expense(date=date_input, amount=amount, category=category, note=note)

    def choose_category(self) -> str:
        print("\nExpense Categories")
        for index, category in enumerate(DEFAULT_CATEGORIES, start=1):
            print(f"{index}. {category.title()}")
        print(f"{len(DEFAULT_CATEGORIES) + 1}. Custom category")

        while True:
            choice = input("Choose a category number: ").strip()
            if choice.isdigit():
                numeric = int(choice)
                if 1 <= numeric <= len(DEFAULT_CATEGORIES):
                    return DEFAULT_CATEGORIES[numeric - 1]
                if numeric == len(DEFAULT_CATEGORIES) + 1:
                    custom = input("Enter custom category name: ").strip().lower()
                    if custom:
                        return custom
            print("Invalid category choice.")

    def show_weekly_summary(self) -> None:
        if not self.profile_exists():
            return

        expenses = [Expense(**expense) for expense in self.data["expenses"]]
        if not expenses:
            print("\nNo expenses have been logged yet.")
            return

        total_spent = sum(expense.amount for expense in expenses)
        by_category: Dict[str, float] = {}
        for expense in expenses:
            by_category[expense.category] = by_category.get(expense.category, 0) + expense.amount

        weekly_income = self.data["profile"]["weekly_income"]
        target_savings = self.required_weekly_savings()
        suggested_spending_limit = weekly_income - target_savings
        remaining_after_expenses = weekly_income - total_spent

        print("\n--- Weekly Summary ---")
        print(f"Weekly income: ${weekly_income:.2f}")
        print(f"Total logged expenses: ${total_spent:.2f}")
        print(f"Recommended weekly savings: ${target_savings:.2f}")
        print(f"Suggested spending limit: ${suggested_spending_limit:.2f}")
        print(f"Amount left after expenses: ${remaining_after_expenses:.2f}")

        print("\nSpending by category:")
        for category, amount in sorted(by_category.items(), key=lambda item: item[1], reverse=True):
            print(f"- {category.title()}: ${amount:.2f}")

        if remaining_after_expenses >= target_savings:
            print("\nGreat job. Based on this week, the goal is on track.")
        else:
            shortfall = target_savings - max(remaining_after_expenses, 0)
            print(
                f"\nThe current spending pattern is short by ${shortfall:.2f} for this week's savings target."
            )
            print("Cutting spending in high-cost categories could help.")

    def show_goal_progress(self) -> None:
        if not self.profile_exists():
            return

        weekly_income = self.data["profile"]["weekly_income"]
        goal_data = self.data["profile"]["goal"]
        expenses = [Expense(**expense) for expense in self.data["expenses"]]
        total_spent = sum(expense.amount for expense in expenses)
        available_to_save = max(weekly_income - total_spent, 0)
        required = self.required_weekly_savings()

        print("\n--- Goal Progress ---")
        print(f"Goal: {goal_data['name']}")
        print(f"Target amount: ${goal_data['target_amount']:.2f}")
        print(f"Time frame: {goal_data['target_weeks']} weeks")
        print(f"Required savings per week: ${required:.2f}")
        print(f"Available to save from logged week: ${available_to_save:.2f}")

        if available_to_save >= required:
            extra = available_to_save - required
            print(f"The user is on pace to hit the goal, with ${extra:.2f} extra this week.")
        else:
            missing = required - available_to_save
            print(f"The user is behind pace by ${missing:.2f} this week.")
            print("Suggestion: reduce non-essential spending or increase weekly income.")

    def required_weekly_savings(self) -> float:
        goal = self.data["profile"]["goal"]
        return goal["target_amount"] / goal["target_weeks"]

    def profile_exists(self) -> bool:
        if self.data.get("profile") is None:
            print("\nPlease set up a profile first.")
            return False
        return True

    @staticmethod
    def get_positive_float(prompt: str) -> float:
        while True:
            try:
                value = float(input(prompt))
                if value > 0:
                    return value
                print("Please enter a value greater than 0.")
            except ValueError:
                print("Please enter a valid number.")

    @staticmethod
    def get_positive_int(prompt: str) -> int:
        while True:
            try:
                value = int(input(prompt))
                if value > 0:
                    return value
                print("Please enter a whole number greater than 0.")
            except ValueError:
                print("Please enter a valid whole number.")

    @staticmethod
    def valid_date(value: str) -> bool:
        try:
            datetime.strptime(value, "%Y-%m-%d")
            return True
        except ValueError:
            return False


if __name__ == "__main__":
    app = BudgetAssistant()
    app.run()
