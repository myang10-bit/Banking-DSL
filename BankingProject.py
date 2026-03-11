# Thomas Sauro, Moua Yang
# CSC 330 Assignment 7 Banking Project
# Banking DSL

import random
from datetime import datetime

class BankAccount:
    def __init__(self, first_name, last_name, balance):
        self.__first_name = first_name
        self.__last_name = last_name

        # make sure balance is a non negative int
        bal = int(balance)
        self.__balance = bal if bal >= 0 else 0
        self.__account_number = self.__generate_account_number()

        # keep a simple list of transaction using dictionaries
        self._transactions = []
        self._log("OPEN", 0, note="Account created")

    def __generate_account_number(self):
        prefix = self.__first_name[0].upper() + self.__last_name[0].upper()
        suffix = ''.join(str(random.randint(0, 9)) for _ in range(6))
        return prefix + suffix

    def _now(self):
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def _log(self, kind, amount, note="", counterparty=None):
        # kind examples: OPEN, DEPOSIT, WITHDRAW, TRANSFER_OUT, TRANSFER_IN
        self._transactions.append({
            "time": self._now(),
            "type": kind,
            "amount": int(amount),
            "balance_after": self.__balance,
            "note": note,
            "counterparty": counterparty
        })

    # simple getters
    def get_first_name(self):
        return self.__first_name

    def get_last_name(self):
        return self.__last_name

    def get_account_number(self):
        return self.__account_number

    def get_balance(self):
        return self.__balance

    def get_transactions(self, last_n=None):
        # return all or only the last N items
        if last_n is None:
            return list(self._transactions)
        return self._transactions[-int(last_n):]

    # basic actions
    def deposit(self, amount):
        amount = int(amount)
        if amount <= 0:
            raise ValueError("Deposit amount must be positive")
        self.__balance += amount
        self._log("DEPOSIT", amount)
        return self.__balance

    def withdraw(self, amount):
        amount = int(amount)
        if amount <= 0:
            raise ValueError("Withdrawal amount must be positive")
        if amount > self.__balance:
            raise RuntimeError("Insufficient funds")
        self.__balance -= amount
        self._log("WITHDRAW", amount)
        return self.__balance

    def transfer_to(self, other_account, amount):
        # move money from this account to another
        if not isinstance(other_account, BankAccount):
            raise ValueError("Target must be a BankAccount")
        if other_account.get_account_number() == self.get_account_number():
            raise ValueError("Cannot transfer to the same account")

        amount = int(amount)
        if amount <= 0:
            raise ValueError("Transfer amount must be positive")

        # withdraw then deposit
        self.withdraw(amount)
        other_account.deposit(amount)

        # extra logs to show that it was a transfer
        self._log("TRANSFER_OUT", amount, counterparty=other_account.get_account_number())
        other_account._log("TRANSFER_IN", amount, counterparty=self.get_account_number())
        return self.__balance

def print_accounts_table(accounts):
    # seperate column widths so everything lines up
    names = [f"{a.get_first_name()} {a.get_last_name()}" for a in accounts]
    accts = [a.get_account_number() for a in accounts]
    bals  = [f"${a.get_balance():,}" for a in accounts]

    name_w = max(len(a) for a in names)
    acct_w = max(len(x) for x in accts)
    bal_w  = max(len(b) for b in bals)

    # print each row: Name | Account | $Balance
    for n, x, b in zip(names, accts, bals):
        print(f"{n:<{name_w}} | {x:<{acct_w}} | {b:>{bal_w}}")


def initialize_accounts():
    sample_data = [
        ("Jimmy", "Smith", 1200),
        ("Timmy", "Jones", 950),
        ("Billy", "White", 3000),
        ("Philly", "Brown", 500),
        ("Eric", "Green", 2200),
        ("Frank", "Black", 1800),
        ("Matt", "Stone", 750),
        ("Hank", "Wood", 4000),
        ("Ashley", "Hill", 600),
        ("Nate", "Lake", 1000)
    ]
    accounts = []
    for first, last, balance in sample_data:
        accounts.append(BankAccount(first, last, balance))
    return accounts


# helper to find an account by number
def find_account(accounts, account_number):
    for acc in accounts:
        if acc.get_account_number() == account_number:
            return acc
    raise ValueError("Account not found")

# helper to do a transfer by account numbers
def transfer_funds(accounts, from_acct_no, to_acct_no, amount):
    src = find_account(accounts, from_acct_no)
    dst = find_account(accounts, to_acct_no)
    return src.transfer_to(dst, amount)


def main():
    print("Welcome to the Banking DSL project.")
    accounts = initialize_accounts()
    print_accounts_table(accounts)

    # simple demo
    a1 = accounts[0]
    a2 = accounts[1]
    print("\nTransfer 200 from first to second account")
    try:
        transfer_funds(accounts, a1.get_account_number(), a2.get_account_number(), 200)
        print(f"{a1.get_account_number()} - New balance ${a1.get_balance()}")
        print(f"{a2.get_account_number()} - New balance ${a2.get_balance()}")
    except (ValueError, RuntimeError) as e:
        print("Transfer failed:", e)

    print("\nRecent transactions for first account:")
    for t in a1.get_transactions(last_n=5):
        cp = f" counterparty {t['counterparty']}" if t["counterparty"] else ""
        print(f"{t['time']} {t['type']} amount {t['amount']} "
              f"balance {t['balance_after']}{cp} note {t['note']}")

if __name__ == "__main__":
    main()
