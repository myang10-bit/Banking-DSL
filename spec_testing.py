# I Thomas Sauro certify that this code is my own work. 10/12/25.
# CSC 330 Banking Project Specification Tests.
import unittest
from banking import BankAccount, initialize_accounts

# Test case class for banking DSL functionality.
class TestBankingDSL(unittest.TestCase):

    def setUp(self):
        self.accounts = initialize_accounts()
        self.acc1 = self.accounts[0]  # Jimmy Smith.
        self.acc2 = self.accounts[1]  # Timmy Jones.

    def test_account_creation(self):
        # Verify name and account number format.
        expected_first = "Jimmy"
        expected_last = "Smith"
        acct_num = self.acc1.get_account_number()
        self.assertEqual(self.acc1.get_first_name(), expected_first,
                         f"FAIL: Expected first name '{expected_first}', got '{self.acc1.get_first_name()}'")
        self.assertEqual(self.acc1.get_last_name(), expected_last,
                         f"FAIL: Expected last name '{expected_last}', got '{self.acc1.get_last_name()}'")
        self.assertTrue(acct_num.startswith("JS") and len(acct_num) == 8,
                        f"FAIL: Account number '{acct_num}' should start with 'JS' and be 8 characters long.")
        print("PASS: Account creation test passed with correct name and account number format.")

    def test_deposit(self):
        # Check deposit updates balance correctly.
        initial_balance = self.acc1.get_balance()
        deposit_amount = 500
        new_balance = self.acc1.deposit(deposit_amount)
        self.assertEqual(new_balance, initial_balance + deposit_amount,
                         f"FAIL: Deposited ${deposit_amount}. Expected balance ${initial_balance + deposit_amount}, got ${new_balance}")
        print(f"PASS: Deposit test passed. Balance updated from ${initial_balance} to ${new_balance}.")

    def test_withdraw(self):
        # Check withdrawal deducts correct amount.
        initial_balance = self.acc1.get_balance()
        withdraw_amount = 300
        new_balance = self.acc1.withdraw(withdraw_amount)
        self.assertEqual(new_balance, initial_balance - withdraw_amount,
                         f"FAIL: Withdrew ${withdraw_amount}. Expected balance ${initial_balance - withdraw_amount}, got ${new_balance}")
        print(f"PASS: Withdrawal test passed. Balance updated from ${initial_balance} to ${new_balance}.")

    def test_transfer(self):
        # Ensure transfer updates both account balances.
        initial_balance_1 = self.acc1.get_balance()
        initial_balance_2 = self.acc2.get_balance()
        transfer_amount = 200
        self.acc1.transfer_to(self.acc2, transfer_amount)
        self.assertEqual(self.acc1.get_balance(), initial_balance_1 - transfer_amount,
                         f"FAIL: Transferred ${transfer_amount}. Expected sender balance ${initial_balance_1 - transfer_amount}, got ${self.acc1.get_balance()}")
        self.assertEqual(self.acc2.get_balance(), initial_balance_2 + transfer_amount,
                         f"FAIL: Transferred ${transfer_amount}. Expected receiver balance ${initial_balance_2 + transfer_amount}, got ${self.acc2.get_balance()}")
        print(f"PASS: Transfer test passed. ${transfer_amount} moved from account 1 to account 2 as expected.")

# Execute all test cases.
def run_all_tests():
    print("\nRunning all tests...\n")
    unittest.TextTestRunner(verbosity=2).run(unittest.TestLoader().loadTestsFromTestCase(TestBankingDSL))

# Run a specific test by name.
def run_single_test(test_name):
    print(f"\nRunning test: {test_name}\n")
    suite = unittest.TestSuite()
    suite.addTest(TestBankingDSL(test_name))
    unittest.TextTestRunner(verbosity=2).run(suite)

# Menu for running tests.
def main():
    running = True
    while running:
        print("\n--- Sauro&Yang Banking Spec Testing Menu ---")
        print("1. Run all tests")
        print("2. Run test: Account Creation")
        print("3. Run test: Deposit")
        print("4. Run test: Withdraw")
        print("5. Run test: Transfer")
        print("6. Exit")

        choice = input("Enter selection (1-6): ").strip()

        if choice == "1":
            run_all_tests()
        elif choice == "2":
            run_single_test("test_account_creation")
        elif choice == "3":
            run_single_test("test_deposit")
        elif choice == "4":
            run_single_test("test_withdraw")
        elif choice == "5":
            run_single_test("test_transfer")
        elif choice == "6":
            print("Exiting spec testing program.")
            running = False
        else:
            print("Invalid selection. Please enter a number between 1 and 6.")

if __name__ == "__main__":
    main()
