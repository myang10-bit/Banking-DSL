##############################################
# Authors: Thomas Sauro, Moua Yang
# CSC 330 – Team Assignment - DSL Banking Program
# Term: Fall 2025
#
# Honesty Pledge:
# We pledge that all the code I submit for this assignment is our own work.
#
# This file contains:
#   • class BankAccount (domain model)
#   • Helpers: initialize_accounts, print_accounts_table, find_account
#   • DSL components: Token/TokenType, Lexer, AST nodes, Parser
#   • class Interpreter ( DSL + banking ops + user menu)
#   • main() entry point
#
##############################################

import re
from enum import Enum
import random
from datetime import datetime

##############################################
#####          BANK ACCOUNT CLASS        #####
##############################################

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
        print(f"[{self._now()}] Deposit successful: +${amount:,} | New Balance: ${self.__balance:,}")
        return self.__balance

    def withdraw(self, amount):
        amount = int(amount)
        if amount <= 0:
            raise ValueError("Withdrawal amount must be positive")
        if amount > self.__balance:
            raise RuntimeError("Insufficient funds")
        self.__balance -= amount
        self._log("WITHDRAW", amount)
        print(f"[{self._now()}] Withdrawal successful: -${amount:,} | New Balance: ${self.__balance:,}")
        return self.__balance

    def transfer_to(self, other_account, amount):
        # moves money from this account to another
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

##############################################
#####         TABLE / INIT HELPERS        ####
##############################################

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

##############################################
#####           LEXER / TOKENS          ######
##############################################

class TokenType(Enum):
    CREATE   = "CREATE"
    DEPOSIT  = "DEPOSIT"
    WITHDRAW = "WITHDRAW"
    BALANCE  = "BALANCE"
    EXIT     = "EXIT"
    NAME     = "NAME"       # first / last name
    ACC_NUM  = "ACC_NUM"    # AA###### format
    NUMBER   = "NUMBER"     # integer
    EOF      = "EOF"
    UNKNOWN  = "UNKNOWN"

KEYWORDS = {
    "create":   TokenType.CREATE,
    "deposit":  TokenType.DEPOSIT,
    "withdraw": TokenType.WITHDRAW,
    "balance":  TokenType.BALANCE,
    "exit":     TokenType.EXIT,
}

ACC_NUM_RE = re.compile(r"[A-Za-z]{2}\d{6}\b")
NUMBER_RE  = re.compile(r"\d+")
NAME_RE    = re.compile(r"[A-Za-z][A-Za-z'\-]*")  # letter then letters or ' or -

class Token:
    def __init__(self, ttype: TokenType, value: str = ""):
        self.type = ttype
        self.value = value

    def __repr__(self):
        return f"Token({self.type.value}, {repr(self.value)})"

class Lexer:
    def __init__(self, text: str):
        self.text = text or ""
        self.pos = 0
        self.n = len(self.text)

    def _at_end(self):
        return self.pos >= self.n

    def _peek_char(self):
        return "" if self._at_end() else self.text[self.pos]

    def _advance(self, k=1):
        self.pos += k

    def _skip_ws(self):
        while not self._at_end() and self.text[self.pos].isspace():
            self._advance()

    def _match_regex_from_pos(self, regex: re.Pattern):
        m = regex.match(self.text, self.pos)
        if m:
            lexeme = m.group(0)
            self._advance(len(lexeme))
            return lexeme
        return None

    def _try_acc_num(self):
        # Exact AA###### and word boundary
        return self._match_regex_from_pos(ACC_NUM_RE)

    def _try_number(self):
        return self._match_regex_from_pos(NUMBER_RE)

    def _try_name_or_keyword(self):
        # Read a name like Jimmy or O'Neil or Jean-Luc (names without all letters)
        m = NAME_RE.match(self.text, self.pos)
        if not m:
            return None, None
        lexeme = m.group(0)
        self._advance(len(lexeme))
        lower = lexeme.lower()
        if lower in KEYWORDS:
            return KEYWORDS[lower], lexeme
        return TokenType.NAME, lexeme

    def get_next_token(self) -> Token:
        self._skip_ws()
        if self._at_end():
            return Token(TokenType.EOF, "")

        # 1) account number format: AA###### 
        acc = self._try_acc_num()
        if acc:
            return Token(TokenType.ACC_NUM, acc)

        ch = self._peek_char()

        # 2) number
        if ch.isdigit():
            num = self._try_number()
            return Token(TokenType.NUMBER, num)

        # 3) name or keyword
        if ch.isalpha():
            ttype, val = self._try_name_or_keyword()
            if ttype:
                return Token(ttype, val)

        # 4) unknown single character token to avoid stalling
        val = ch
        self._advance()
        return Token(TokenType.UNKNOWN, val)

    def peek_next_token(self) -> Token:
        saved = self.pos
        tok = self.get_next_token()
        self.pos = saved
        return tok

##############################################
#####           LEX DEBUG HELPERS        #####
##############################################

# Helper for demo and debugging
def lex_debug(line: str):
    lx = Lexer(line)
    out = []
    tok = lx.get_next_token()
    while tok.type != TokenType.EOF:
        out.append(repr(tok))
        tok = lx.get_next_token()
    out.append("Token(EOF, '')")
    print("Tokens:", " -> ".join(out))

##############################################
#####             AST / PARSER          ######
##############################################

class ParseError(Exception):
    pass


class ASTNode:
    pass


class CreateNode(ASTNode):
    def __init__(self, first_name: str, last_name: str, initial_balance: int):
        self.first_name = first_name
        self.last_name = last_name
        self.initial_balance = int(initial_balance)

    def __repr__(self):
        return f"CreateNode({self.first_name}, {self.last_name}, {self.initial_balance})"


class DepositNode(ASTNode):
    def __init__(self, account_number: str, amount: int):
        self.account_number = account_number
        self.amount = int(amount)

    def __repr__(self):
        return f"DepositNode({self.account_number}, {self.amount})"


class WithdrawNode(ASTNode):
    def __init__(self, account_number: str, amount: int):
        self.account_number = account_number
        self.amount = int(amount)

    def __repr__(self):
        return f"WithdrawNode({self.account_number}, {self.amount})"


class BalanceNode(ASTNode):
    def __init__(self, account_number: str):
        self.account_number = account_number

    def __repr__(self):
        return f"BalanceNode({self.account_number})"


class ExitNode(ASTNode):
    def __repr__(self):
        return "ExitNode()"


class ProgramNode(ASTNode):
    def __init__(self, commands):
        self.commands = commands or []

    def __repr__(self):
        return f"ProgramNode({self.commands})"


class Parser:
    def __init__(self, lexer: 'Lexer'):
        self.lexer = lexer
        self.current = self.lexer.get_next_token()

    # helpers 
    def _eat(self, ttype):
        if self.current.type == ttype:
            self.current = self.lexer.get_next_token()
        else:
            raise ParseError(f"Expected {ttype.value} but got {self.current.type.value} ({self.current.value})")

    def _eat_with_value(self, ttype):
        if self.current.type == ttype:
            val = self.current.value
            self.current = self.lexer.get_next_token()
            return val
        raise ParseError(f"Expected {ttype.value} but got {self.current.type.value} ({self.current.value})")

    # entry points 
    def parse_program(self) -> ProgramNode:
        cmds = []
        while self.current.type != TokenType.EOF:
            cmds.append(self.parse_command())
        return ProgramNode(cmds)

    def parse_command(self) -> ASTNode:
        t = self.current.type

        if t == TokenType.CREATE:
            return self._parse_create()
        elif t == TokenType.DEPOSIT:
            return self._parse_deposit()
        elif t == TokenType.WITHDRAW:
            return self._parse_withdraw()
        elif t == TokenType.BALANCE:
            return self._parse_balance()
        elif t == TokenType.EXIT:
            self._eat(TokenType.EXIT)
            return ExitNode()
        else:
            raise ParseError(f"Unexpected token at start of command: {t.value} ({self.current.value})")

    # productions 
    def _parse_create(self) -> CreateNode:
        self._eat(TokenType.CREATE)
        first = self._eat_with_value(TokenType.NAME)
        last  = self._eat_with_value(TokenType.NAME)
        amt   = self._eat_with_value(TokenType.NUMBER)
        return CreateNode(first, last, amt)

    def _parse_deposit(self) -> DepositNode:
        self._eat(TokenType.DEPOSIT)
        acct = self._eat_with_value(TokenType.ACC_NUM)
        amt  = self._eat_with_value(TokenType.NUMBER)
        return DepositNode(acct, amt)

    def _parse_withdraw(self) -> WithdrawNode:
        self._eat(TokenType.WITHDRAW)
        acct = self._eat_with_value(TokenType.ACC_NUM)
        amt  = self._eat_with_value(TokenType.NUMBER)
        return WithdrawNode(acct, amt)

    def _parse_balance(self) -> BalanceNode:
        self._eat(TokenType.BALANCE)
        acct = self._eat_with_value(TokenType.ACC_NUM)
        return BalanceNode(acct)

# Parser debugging

def parse_line(line: str) -> ASTNode:
    parser = Parser(Lexer(line))
    node = parser.parse_command()
    if parser.current.type != TokenType.EOF:
        raise ParseError(f"Unexpected extra input after command: {parser.current}")
    return node

def parse_script(text: str) -> ProgramNode:
    commands = []
    for raw in (text or "").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        commands.append(parse_line(line))
    return ProgramNode(commands)

def parse_debug(line: str):
    """Prints the AST in a nice single line format."""
    try:
        node = parse_line(line)
        print("AST:", node)
    except ParseError as e:
        print("ParseError:", e)


class Interpreter:
    def __init__(self):
        self.accounts = initialize_accounts()
        self.current_account = None

    # Small input helper
    def _ask_yes_no(self, prompt: str) -> bool:
        ans = input(prompt).strip().lower()
        while ans not in ("yes", "no"):
            print("Please enter 'yes' or 'no'.")
            ans = input(prompt).strip().lower()
        return ans == "yes"

    # Banking utilities
    def list_accounts(self):
        print_accounts_table(self.accounts)

    def find_account(self, account_number):
        try:
            self.current_account = find_account(self.accounts, account_number)
            print(f"Accessed account {self.current_account.get_account_number()}")
        except ValueError:
            print("Account not found.")
            self.current_account = None

    def create_account(self, first_name, last_name, initial_deposit):
        try:
            new_account = BankAccount(first_name, last_name, initial_deposit)
            self.accounts.append(new_account)
            print("Account created successfully:")
            print_accounts_table([new_account])
        except ValueError as e:
            print("Error creating account:", e)

    def deposit(self, amount):
        if self.current_account:
            try:
                new_bal = self.current_account.deposit(amount)
                print(f"Deposited. New balance: ${new_bal:,}")
            except ValueError as e:
                print("Error:", e)
        else:
            print("No account selected. Access an account first.")

    def withdraw(self, amount):
        if self.current_account:
            try:
                new_bal = self.current_account.withdraw(amount)
                print(f"Withdrawn. New balance: ${new_bal:,}")
            except (ValueError, RuntimeError) as e:
                print("Error:", e)
        else:
            print("No account selected. Access an account first.")

    def check_balance(self):
        if self.current_account:
            print(f"Current balance: ${self.current_account.get_balance():,}")
        else:
            print("No account selected. Access an account first.")

    def logout(self):
        self.current_account = None
        print("Logged out of account.")

    # DSL wiring
    def _get_account_by_no(self, acct_no: str):
        try:
            return find_account(self.accounts, acct_no)
        except ValueError:
            return None

    def interpret_node(self, node):
        status = "ERR"

        if isinstance(node, CreateNode):
            self.create_account(node.first_name, node.last_name, node.initial_balance)
            status = "OK"

        elif isinstance(node, DepositNode):
            acc = self._get_account_by_no(node.account_number)
            if acc:
                try:
                    new_bal = acc.deposit(node.amount)
                    print(f"Deposited ${node.amount:,} to {acc.get_account_number()}. New balance ${new_bal:,}")
                    status = "OK"
                except ValueError as e:
                    print("Error:", e)
            else:
                print(f"Account not found: {node.account_number}")

        elif isinstance(node, WithdrawNode):
            acc = self._get_account_by_no(node.account_number)
            if acc:
                try:
                    new_bal = acc.withdraw(node.amount)
                    print(f"Withdrew ${node.amount:,} from {acc.get_account_number()}. New balance ${new_bal:,}")
                    status = "OK"
                except (ValueError, RuntimeError) as e:
                    print("Error:", e)
            else:
                print(f"Account not found: {node.account_number}")

        elif isinstance(node, BalanceNode):
            acc = self._get_account_by_no(node.account_number)
            if acc:
                print(f"Balance for {acc.get_account_number()} is ${acc.get_balance():,}")
                status = "OK"
            else:
                print(f"Account not found: {node.account_number}")

        elif isinstance(node, ExitNode):
            status = "EXIT"

        else:
            print("Unknown command node:", node)

        return status

    def run_dsl_line(self, line: str, show_tokens=False, show_ast=False):
        line = (line or "").strip()
        status = "OK"

        if line:
            if show_tokens:
                lex_debug(line)
            try:
                node = parse_line(line)
                if show_ast:
                    print("AST:", node)
                status = self.interpret_node(node)
            except ParseError as e:
                print("ParseError:", e)
                status = "ERR"

        return status

    def run_dsl_repl(self, show_tokens=False, show_ast=False):
        print("\nEntering DSL mode. (For reference) Type commands in this format:")
        print("  create Jimmy Smith 1200")
        print("  deposit JS905471 200")
        print("  withdraw JS905471 50")
        print("  balance JS905471")
        print("  exit   (to leave DSL mode)")
        running_dsl = True
        while running_dsl:
            line = input("dsl> ")
            status = self.run_dsl_line(line, show_tokens=show_tokens, show_ast=show_ast)
            if status == "EXIT":
                running_dsl = False
        print("Leaving DSL mode.")

    # Main interactive Loop UI
    def run(self):
        print("Welcome to the Sauro&Yang banking program.")
        print("\n--- Initialized Accounts ---")
        self.list_accounts()

        running = True
        while running:
            print("\nMain Menu:")
            print("1. Access existing account")
            print("2. Create new account")
            print("3. Exit program")
            print("4. Run DSL Banking Commands")
            choice = input("Choose an option (1-4): ").strip()

            if choice == "1":
                acct_id = input("Enter account number: ").strip()
                try:
                    account = find_account(self.accounts, acct_id)
                    self.current_account = account
                    logged_in = True
                except ValueError:
                    print("Account not found.")
                    self.current_account = None
                    logged_in = False

                # Account session loop
                while logged_in:
                    print(f"\nAccount: {account.get_account_number()} | Balance: ${account.get_balance():,}")
                    print("a. Deposit")
                    print("b. Withdraw")
                    print("c. Check balance")
                    print("d. Log out")
                    sub = input("Choose an option (a-d): ").strip().lower()

                    if sub == "a":
                        amt = input("Enter deposit amount: ").strip()
                        try:
                            new_bal = account.deposit(amt)
                            print(f"Deposited. New balance: ${new_bal:,}")
                        except ValueError as e:
                            print("Error:", e)

                    elif sub == "b":
                        amt = input("Enter withdrawal amount: ").strip()
                        try:
                            new_bal = account.withdraw(amt)
                            print(f"Withdrawn. New balance: ${new_bal:,}")
                        except (ValueError, RuntimeError) as e:
                            print("Error:", e)

                    elif sub == "c":
                        print(f"Current balance: ${account.get_balance():,}")

                    elif sub == "d":
                        logged_in = False
                        self.logout()

                    else:
                        print("Invalid option.")

                # updated prompt wording & safe input
                continue_program = self._ask_yes_no("Would you like to continue using the banking program? (yes/no): ")
                if not continue_program:
                    print("Thank you for banking with us. Goodbye!")
                running = False

            elif choice == "2":
                first = input("First name: ").strip()
                last = input("Last name: ").strip()
                bal = input("Initial deposit: ").strip()
                try:
                    new_account = BankAccount(first, last, bal)
                    self.accounts.append(new_account)
                    print("Account created successfully:")
                    print_accounts_table([new_account])
                except ValueError as e:
                    print("Error creating account:", e)

            elif choice == "3":
                running = False
                print("Thank you for banking with us. Goodbye!")

            elif choice == "4":
                show_tokens = True
                show_ast = True
                self.run_dsl_repl(show_tokens=show_tokens, show_ast=show_ast)

            else:
                print("Invalid option. Please choose 1, 2, 3, or 4.")


def main():
    interpreter = Interpreter()
    interpreter.run()

if __name__ == "__main__":
    main()
