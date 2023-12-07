# PythonFinal.py
# Name: Taylor Nii
# Class: CIT-95
# Date: 12-06-2023

from datetime import date, timedelta
import matplotlib.pyplot as plt
import numpy as np

fileipath_excelsheet = "/Users/taylornii/PycharmProjects/CIT95Programs/CIT95Final/budgetx_copy.csv"
fileopath_outputFile = ""


def parse_date(date_str):
    """takes string date yy/mm/dd and return datetime date"""
    date_split = date_str.split("/")
    date_dict = {"year": date_split[0], "month": date_split[1], "day": date_split[2]}
    for key in date_dict:
        if len(date_dict[key]) == 2 and key == "year":  # if year is 2 digits
            date_dict[key] = int("20" + date_dict[key])  # assuming no entries dated before year 2000 or after year 2099
        elif len(date_dict[key]) != 4 and key == "year":
            print("date is not right length")
            date_dict[key] = 2000
        elif len(date_dict[key]) != 2 and key != "year":
            date_dict[key] = 1
        else:
            date_dict[key] = int(date_dict[key])
    return date(date_dict["year"], date_dict["month"], date_dict["day"])


def last_day_of_month(any_day):
    # The day 28 exists in every month. 4 days later, it's always next month
    next_month = any_day.replace(day=28) + timedelta(days=4)
    # subtracting the number of the current day brings us back one month
    return next_month - timedelta(days=next_month.day)


def first_day_of_month(any_day):
    return any_day.replace(day=1)


def days_betw_dates(beg, end):
    """takes 2 datetime dates, returns int number of days between two (inclusive)"""
    return (end-beg).days + 1

def insert_item_in_list(a_list, an_item, position):
    if position < 0 or position > len(a_list):
        print("Invalid position. Item not inserted.")
        return a_list

    return a_list[:position] + [an_item] + a_list[position:]


class LineItem:
    def __init__(self, date="00-00-00", description="", amount=0.0, income_or_expense="",
                 fixed_or_variable="", frequency=""):
        self.date = date
        self.description = description
        self.amount = amount
        self.type = income_or_expense
        self.fixed_or_var = fixed_or_variable
        self.frequency = frequency
        self.running_balance = 0
        self.timeline_xval = 0

    def __str__(self):
        return (f"{self.date}, {self.description}, ${self.amount}, {self.type}, "
                f"{self.fixed_or_var}, {self.frequency}, {self.running_balance}, {self.timeline_xval}")

    def get_balance_before_transaction(self):
        before_bal = 0
        if self.type == 'income':
            before_bal=round(self.running_balance - self.amount, 3)
        elif self.type == 'expense':
            before_bal = round(self.running_balance + self.amount, 3)
        return before_bal


class Expense(LineItem):
    def __init__(self, date="00-00-00", description="", amount=0.0, fixed_or_variable="", frequency=""):
        super().__init__(date, description, amount, "expense", fixed_or_variable, frequency)


class Income(LineItem):
    def __init__(self, date="00-00-00", description="", amount=0.0, fixed_or_variable="", frequency=""):
        super().__init__(date, description, amount, "income", fixed_or_variable, frequency)


class CashBudget:
    def __init__(self, ledger=[], revenue=0.0, expenses=0.0):
        self.ledger = ledger
        self.revenue = revenue
        self.expenses = expenses
        self.discretionary = revenue-expenses
        self.cash_goal = 0

    def __str__(self):
        ledge_str = "\n"
        for entry in self.ledger:
            ledge_str += (str(entry)+"\n")
        return ledge_str

    def populate_ledger(self, transaction_list):
        self.ledger = transaction_list

    def sort_ledger(self):
        """bubble sort ledger chronologically by date of transaction"""  # fine for small dataset mostly presorted;
        for i in range(len(self.ledger)):  # each iteration ensures next item is in the right order/ how many passes
            swaps = 0
            for j in range(len(self.ledger) - i - 1):
                if int(((self.ledger[j]).date - (self.ledger[j+1]).date).days) > 0:
                    self.ledger[j], self.ledger[j+1] = self.ledger[j+1], self.ledger[j]
                    swaps += 1
                else:
                    pass
            if swaps == 0:
                return self.ledger

    def get_balances(self):
        """returns list of balances after transaction of sorted ledger"""
        balances = []
        index = 0
        for entry in self.ledger:
            if entry.type == 'income':
                if index == 0:
                    balances.append(round(entry.amount, 3))
                else:
                    new_balance = round(balances[index-1]+entry.amount, 3)
                    balances.append(new_balance)
            elif entry.type == 'expense':
                if index == 0:
                    balances.append(round(-entry.amount, 3))
                else:
                    new_balance = round(balances[index-1]-entry.amount, 3)
                    balances.append(new_balance)
            index += 1
        return balances


    def set_balances(self, balances):
        """assigns ending balances to each expense & income line item"""
        index = 0
        for entry in self.ledger:
            entry.running_balance = balances[index]
            index += 1
        print("balances assigned")

    def set_xval(self, beg_date, end_date):
        """sets line items' timeline_xval in relation to beg_date @ x=0 and end_date"""
        beg = beg_date
        end = end_date
        for entry in self.ledger:
            entry_date = entry.date
            if int((entry_date-beg).days)+1 > 0 and int((end-entry_date).days)+1 > 0:
                entry.timeline_xval = int((entry_date - beg).days) + 1
            else:
                entry.timeline_xval = -1  # these are not within graph endpoints, tells which instances to exclude

    def set_cash_goal(self, amount):
        """takes float"""
        self.cash_goal = np.round(amount,3)

    def display_stats(self, beg_date, end_date):
        self.set_xval(beg_date, end_date)
        print(self)
        x = []
        y = []
        index = -1
        for entry in self.ledger:
            # creates a list of balances within given beg & end date
            if entry.timeline_xval != -1:
                x.append(entry.timeline_xval)
                y.append(entry.running_balance)
                index += 1
                if index == 0:
                    first_entry = entry

        beg_bal1 = first_entry.get_balance_before_transaction()
        position_index = 0
        for i in range(days_betw_dates(beg_date, end_date)):
            day_inserted = False
            if len(x) < days_betw_dates(beg_date, end_date) and x.count(position_index+1) == 0:
                x = insert_item_in_list(x, position_index+1, position_index)
                day_inserted = True
                if position_index == 0:
                    y = insert_item_in_list(y, beg_bal1, position_index)
                else:
                    y = insert_item_in_list(y, y[position_index-1], position_index)

            position_index += 1

        x = insert_item_in_list(x, 0, 0)
        y = insert_item_in_list(y, beg_bal1, 0)


        print(f"Month Statistics ({beg_date} to {end_date})")
        beg_bal = beg_bal1
        end_bal = y[len(y)-1]
        net_bal = np.round(end_bal - beg_bal1, 3)
        print("BEG BAL:", beg_bal)
        print("END BAL:", end_bal)
        if net_bal > 0:
            print(f"Nice! This month your funds grew.\nNET: {net_bal}")
        else:
            print(f"NET BAL: {net_bal}\n")
        print("graphing...")
        print(x, y)
        # Plotting balances on y, against days in specified period on x
        plt.plot(x, y, marker=".")
        # TODO: plot self.cash_goal as a line
        plt.xlabel('days')
        plt.ylabel('balance($)')
        return plt.show()

    def generate_month_report_for(self, date_inp):
        """note: must populate_ledger(a_list) on instance before running this"""
        date_for_report = parse_date(date_inp)
        self.sort_ledger()
        self.set_balances(self.get_balances())
        print("SORTED LEDGER:", self)
        self.display_stats(first_day_of_month(date_for_report), last_day_of_month(date_for_report))


try:
    with (open(fileipath_excelsheet, 'r') as excelsheet):
        a_lines = excelsheet.readlines()  # reading in unsorted ledger
        a_list = []
        for line in a_lines:
            line = line.strip()
            line = line.split(",")
            if line != ['', '', '', '', '', ''] and line != ['date', 'description', 'amount', 'income/expense',
                                                             'fixed/variable', 'frequency']:
                #  if entry is not empty or header
                if line[3] == 'income':
                    incomex = Income(parse_date(line[0]), line[1], float(line[2]), line[4], line[5])
                    a_list.append(incomex)
                elif line[3] == 'expense':
                    expensex = Expense(parse_date(line[0]), line[1], float(line[2]), line[4], line[5])
                    a_list.append(expensex)
                else:
                    print("not an income or expense")
                    a_list.append('?')
        new_budget = CashBudget()
        new_budget.populate_ledger(a_list)
        new_budget.generate_month_report_for("2021/04/15")

except Exception as e:
    print(f"An error occurred: {str(e)}")
