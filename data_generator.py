#!/usr/bin/env python3
"""
Accounting Error Detection System - Synthetic Data Generator
Generates realistic accounting data with intentional errors for testing
"""

import random
import uuid
from datetime import datetime, date, timedelta
from decimal import Decimal, ROUND_HALF_UP
from typing import List, Dict, Tuple
import logging

from accounting_models import (
    Account, JournalEntry, JournalEntryLine, AccountType, NormalBalance,
    DatabaseManager, AccountManager, JournalEntryManager
)

logger = logging.getLogger(__name__)


class SyntheticDataGenerator:
    """Generates synthetic accounting data for testing the error detection system"""
    
    def __init__(self, db: DatabaseManager):
        self.db = db
        self.account_manager = AccountManager(db)
        self.journal_manager = JournalEntryManager(db)
        
        # Control error injection rates
        self.error_rates = {
            'unbalanced_entries': 0.15,      # 15% of entries will be unbalanced
            'wrong_accounts': 0.08,          # 8% will use inappropriate accounts
            'unusual_amounts': 0.12,         # 12% will have unusual amounts
            'missing_descriptions': 0.05,    # 5% will have poor descriptions
            'duplicate_entries': 0.03,       # 3% will be duplicates
            'invalid_dates': 0.07,           # 7% will have date issues
        }
        
        # Company simulation parameters
        self.company_name = "Demo Manufacturing Corp"
        self.start_date = date(2024, 1, 1)
        self.end_date = date(2024, 12, 31)
        
        # Amount ranges for different transaction types
        self.amount_ranges = {
            'sales': (500, 50000),
            'purchases': (100, 25000),
            'payroll': (1000, 15000),
            'utilities': (200, 2000),
            'rent': (3000, 8000),
            'insurance': (500, 3000),
            'depreciation': (1000, 5000),
            'loan_payment': (2000, 10000),
        }
    
    def generate_complete_dataset(self, num_entries: int = 500) -> Dict[str, int]:
        """Generate a complete dataset with chart of accounts and journal entries"""
        logger.info(f"Generating complete dataset with {num_entries} journal entries")
        
        # Initialize the database
        self._initialize_database()
        
        # Create chart of accounts
        accounts_created = self._create_chart_of_accounts()
        
        # Generate journal entries
        entries_created = self._generate_journal_entries(num_entries)
        
        # Generate some error-free entries for baseline
        baseline_entries = self._generate_baseline_entries(50)
        
        stats = {
            'accounts_created': accounts_created,
            'journal_entries_created': entries_created,
            'baseline_entries_created': baseline_entries,
            'total_entries': entries_created + baseline_entries
        }
        
        logger.info(f"Dataset generation complete: {stats}")
        return stats
    
    def _initialize_database(self):
        """Initialize the database with the schema"""
        try:
            with open('database_schema.sql', 'r') as f:
                schema_sql = f.read()
            
            # Execute schema creation
            statements = schema_sql.split(';')
            for statement in statements:
                statement = statement.strip()
                if statement and not statement.startswith('--'):
                    try:
                        self.db.execute_update(statement)
                    except Exception as e:
                        if "already exists" not in str(e).lower():
                            logger.warning(f"Schema statement failed: {e}")
            
            logger.info("Database schema initialized")
        except FileNotFoundError:
            logger.warning("Schema file not found, assuming database already initialized")
    
    def _create_chart_of_accounts(self) -> int:
        """Create a realistic chart of accounts"""
        accounts = [
            # Assets
            Account("1000", "Cash - Operating", AccountType.ASSET, "CURRENT_ASSET", NormalBalance.DEBIT),
            Account("1010", "Cash - Savings", AccountType.ASSET, "CURRENT_ASSET", NormalBalance.DEBIT),
            Account("1100", "Accounts Receivable", AccountType.ASSET, "CURRENT_ASSET", NormalBalance.DEBIT),
            Account("1110", "Allowance for Doubtful Accounts", AccountType.ASSET, "CURRENT_ASSET", NormalBalance.CREDIT),
            Account("1200", "Inventory - Raw Materials", AccountType.ASSET, "CURRENT_ASSET", NormalBalance.DEBIT),
            Account("1210", "Inventory - Work in Process", AccountType.ASSET, "CURRENT_ASSET", NormalBalance.DEBIT),
            Account("1220", "Inventory - Finished Goods", AccountType.ASSET, "CURRENT_ASSET", NormalBalance.DEBIT),
            Account("1300", "Prepaid Insurance", AccountType.ASSET, "CURRENT_ASSET", NormalBalance.DEBIT),
            Account("1310", "Prepaid Rent", AccountType.ASSET, "CURRENT_ASSET", NormalBalance.DEBIT),
            Account("1500", "Equipment", AccountType.ASSET, "FIXED_ASSET", NormalBalance.DEBIT),
            Account("1510", "Accumulated Depreciation - Equipment", AccountType.ASSET, "FIXED_ASSET", NormalBalance.CREDIT),
            Account("1600", "Building", AccountType.ASSET, "FIXED_ASSET", NormalBalance.DEBIT),
            Account("1610", "Accumulated Depreciation - Building", AccountType.ASSET, "FIXED_ASSET", NormalBalance.CREDIT),
            Account("1700", "Land", AccountType.ASSET, "FIXED_ASSET", NormalBalance.DEBIT),
            
            # Liabilities
            Account("2000", "Accounts Payable", AccountType.LIABILITY, "CURRENT_LIABILITY", NormalBalance.CREDIT),
            Account("2100", "Accrued Wages Payable", AccountType.LIABILITY, "CURRENT_LIABILITY", NormalBalance.CREDIT),
            Account("2110", "Payroll Tax Payable", AccountType.LIABILITY, "CURRENT_LIABILITY", NormalBalance.CREDIT),
            Account("2200", "Notes Payable - Short Term", AccountType.LIABILITY, "CURRENT_LIABILITY", NormalBalance.CREDIT),
            Account("2300", "Unearned Revenue", AccountType.LIABILITY, "CURRENT_LIABILITY", NormalBalance.CREDIT),
            Account("2400", "Current Portion of Long-term Debt", AccountType.LIABILITY, "CURRENT_LIABILITY", NormalBalance.CREDIT),
            Account("2500", "Long-term Debt", AccountType.LIABILITY, "LONG_TERM_LIABILITY", NormalBalance.CREDIT),
            Account("2600", "Mortgage Payable", AccountType.LIABILITY, "LONG_TERM_LIABILITY", NormalBalance.CREDIT),
            
            # Equity
            Account("3000", "Common Stock", AccountType.EQUITY, "CAPITAL", NormalBalance.CREDIT),
            Account("3100", "Retained Earnings", AccountType.EQUITY, "RETAINED_EARNINGS", NormalBalance.CREDIT),
            Account("3200", "Dividends", AccountType.EQUITY, "DIVIDENDS", NormalBalance.DEBIT),
            
            # Revenue
            Account("4000", "Sales Revenue", AccountType.REVENUE, "OPERATING_REVENUE", NormalBalance.CREDIT),
            Account("4100", "Service Revenue", AccountType.REVENUE, "OPERATING_REVENUE", NormalBalance.CREDIT),
            Account("4200", "Interest Income", AccountType.REVENUE, "NON_OPERATING_REVENUE", NormalBalance.CREDIT),
            Account("4300", "Gain on Sale of Assets", AccountType.REVENUE, "NON_OPERATING_REVENUE", NormalBalance.CREDIT),
            
            # Expenses
            Account("5000", "Cost of Goods Sold", AccountType.EXPENSE, "COST_OF_SALES", NormalBalance.DEBIT),
            Account("5100", "Wages Expense", AccountType.EXPENSE, "OPERATING_EXPENSE", NormalBalance.DEBIT),
            Account("5110", "Payroll Tax Expense", AccountType.EXPENSE, "OPERATING_EXPENSE", NormalBalance.DEBIT),
            Account("5200", "Rent Expense", AccountType.EXPENSE, "OPERATING_EXPENSE", NormalBalance.DEBIT),
            Account("5300", "Utilities Expense", AccountType.EXPENSE, "OPERATING_EXPENSE", NormalBalance.DEBIT),
            Account("5400", "Insurance Expense", AccountType.EXPENSE, "OPERATING_EXPENSE", NormalBalance.DEBIT),
            Account("5500", "Depreciation Expense", AccountType.EXPENSE, "OPERATING_EXPENSE", NormalBalance.DEBIT),
            Account("5600", "Office Supplies Expense", AccountType.EXPENSE, "OPERATING_EXPENSE", NormalBalance.DEBIT),
            Account("5700", "Advertising Expense", AccountType.EXPENSE, "OPERATING_EXPENSE", NormalBalance.DEBIT),
            Account("5800", "Travel Expense", AccountType.EXPENSE, "OPERATING_EXPENSE", NormalBalance.DEBIT),
            Account("5900", "Professional Fees", AccountType.EXPENSE, "OPERATING_EXPENSE", NormalBalance.DEBIT),
            Account("6000", "Interest Expense", AccountType.EXPENSE, "NON_OPERATING_EXPENSE", NormalBalance.DEBIT),
            Account("6100", "Bad Debt Expense", AccountType.EXPENSE, "OPERATING_EXPENSE", NormalBalance.DEBIT),
        ]
        
        count = 0
        for account in accounts:
            try:
                account.account_id = self.account_manager.create_account(account)
                count += 1
            except Exception as e:
                logger.warning(f"Failed to create account {account.account_code}: {e}")
        
        logger.info(f"Created {count} accounts")
        return count
    
    def _generate_journal_entries(self, num_entries: int) -> int:
        """Generate journal entries with various types of errors"""
        entries_created = 0
        current_date = self.start_date
        
        # Get all accounts for reference
        all_accounts = self.account_manager.get_all_accounts()
        account_map = {acc.account_code: acc for acc in all_accounts}
        
        transaction_types = [
            ('sales', 0.25),
            ('purchases', 0.20),
            ('payroll', 0.15),
            ('utilities', 0.10),
            ('rent', 0.08),
            ('depreciation', 0.07),
            ('loan_payment', 0.05),
            ('misc_expense', 0.10),
        ]
        
        for i in range(num_entries):
            # Select transaction type
            transaction_type = self._weighted_choice(transaction_types)
            
            # Advance date randomly (1-5 days)
            current_date += timedelta(days=random.randint(1, 5))
            if current_date > self.end_date:
                current_date = self.start_date + timedelta(days=random.randint(0, 30))
            
            try:
                entry = self._create_transaction_entry(
                    transaction_type, current_date, i + 1, account_map
                )
                
                # Inject errors based on rates
                entry = self._inject_errors(entry, account_map)
                
                # Create the entry
                entry.entry_id = self.journal_manager.create_entry(entry)
                entries_created += 1
                
            except Exception as e:
                logger.error(f"Failed to create entry {i + 1}: {e}")
        
        logger.info(f"Created {entries_created} journal entries with errors")
        return entries_created
    
    def _weighted_choice(self, choices: List[Tuple[str, float]]) -> str:
        """Make a weighted random choice"""
        total = sum(weight for _, weight in choices)
        r = random.uniform(0, total)
        
        upto = 0
        for choice, weight in choices:
            if upto + weight >= r:
                return choice
            upto += weight
        
        return choices[-1][0]  # Fallback
    
    def _create_transaction_entry(self, transaction_type: str, entry_date: date, 
                                entry_num: int, account_map: Dict[str, Account]) -> JournalEntry:
        """Create a specific type of transaction entry"""
        
        entry = JournalEntry(
            entry_number=f"JE-2024-{entry_num:04d}",
            entry_date=entry_date,
            created_by="system_generator"
        )
        
        if transaction_type == 'sales':
            amount = self._random_amount('sales')
            entry.description = f"Sales invoice #{random.randint(1000, 9999)}"
            entry.reference = f"INV-{random.randint(1000, 9999)}"
            
            # Debit: Accounts Receivable, Credit: Sales Revenue
            entry.add_line(JournalEntryLine(
                account_id=account_map['1100'].account_id,
                description="Customer payment due",
                debit_amount=amount
            ))
            entry.add_line(JournalEntryLine(
                account_id=account_map['4000'].account_id,
                description="Product sales",
                credit_amount=amount
            ))
            
        elif transaction_type == 'purchases':
            amount = self._random_amount('purchases')
            entry.description = f"Purchase of raw materials"
            entry.reference = f"PO-{random.randint(1000, 9999)}"
            
            # Debit: Inventory, Credit: Accounts Payable
            entry.add_line(JournalEntryLine(
                account_id=account_map['1200'].account_id,
                description="Raw materials purchased",
                debit_amount=amount
            ))
            entry.add_line(JournalEntryLine(
                account_id=account_map['2000'].account_id,
                description="Amount owed to supplier",
                credit_amount=amount
            ))
            
        elif transaction_type == 'payroll':
            gross_pay = self._random_amount('payroll')
            tax_amount = gross_pay * Decimal('0.25')  # 25% tax rate
            net_pay = gross_pay - tax_amount
            
            entry.description = f"Bi-weekly payroll"
            entry.reference = f"PR-{entry_date.strftime('%Y%m%d')}"
            
            # Debit: Wages Expense, Credit: Cash and Payroll Tax Payable
            entry.add_line(JournalEntryLine(
                account_id=account_map['5100'].account_id,
                description="Employee wages",
                debit_amount=gross_pay
            ))
            entry.add_line(JournalEntryLine(
                account_id=account_map['1000'].account_id,
                description="Net pay to employees",
                credit_amount=net_pay
            ))
            entry.add_line(JournalEntryLine(
                account_id=account_map['2110'].account_id,
                description="Payroll taxes withheld",
                credit_amount=tax_amount
            ))
            
        elif transaction_type == 'utilities':
            amount = self._random_amount('utilities')
            entry.description = f"Monthly utilities"
            entry.reference = f"UTIL-{entry_date.strftime('%Y%m')}"
            
            # Debit: Utilities Expense, Credit: Cash
            entry.add_line(JournalEntryLine(
                account_id=account_map['5300'].account_id,
                description="Electricity and water",
                debit_amount=amount
            ))
            entry.add_line(JournalEntryLine(
                account_id=account_map['1000'].account_id,
                description="Payment for utilities",
                credit_amount=amount
            ))
            
        elif transaction_type == 'rent':
            amount = self._random_amount('rent')
            entry.description = f"Monthly rent payment"
            entry.reference = f"RENT-{entry_date.strftime('%Y%m')}"
            
            # Debit: Rent Expense, Credit: Cash
            entry.add_line(JournalEntryLine(
                account_id=account_map['5200'].account_id,
                description="Office rent",
                debit_amount=amount
            ))
            entry.add_line(JournalEntryLine(
                account_id=account_map['1000'].account_id,
                description="Rent payment",
                credit_amount=amount
            ))
            
        elif transaction_type == 'depreciation':
            amount = self._random_amount('depreciation')
            entry.description = f"Monthly depreciation"
            entry.reference = f"DEPR-{entry_date.strftime('%Y%m')}"
            
            # Debit: Depreciation Expense, Credit: Accumulated Depreciation
            entry.add_line(JournalEntryLine(
                account_id=account_map['5500'].account_id,
                description="Equipment depreciation",
                debit_amount=amount
            ))
            entry.add_line(JournalEntryLine(
                account_id=account_map['1510'].account_id,
                description="Accumulated depreciation",
                credit_amount=amount
            ))
            
        elif transaction_type == 'loan_payment':
            total_payment = self._random_amount('loan_payment')
            interest_amount = total_payment * Decimal('0.3')  # 30% interest
            principal_amount = total_payment - interest_amount
            
            entry.description = f"Monthly loan payment"
            entry.reference = f"LOAN-{entry_date.strftime('%Y%m')}"
            
            # Debit: Interest Expense and Long-term Debt, Credit: Cash
            entry.add_line(JournalEntryLine(
                account_id=account_map['6000'].account_id,
                description="Interest on loan",
                debit_amount=interest_amount
            ))
            entry.add_line(JournalEntryLine(
                account_id=account_map['2500'].account_id,
                description="Principal payment",
                debit_amount=principal_amount
            ))
            entry.add_line(JournalEntryLine(
                account_id=account_map['1000'].account_id,
                description="Loan payment",
                credit_amount=total_payment
            ))
            
        else:  # misc_expense
            amount = self._random_amount('utilities')  # Use utilities range
            expense_accounts = ['5600', '5700', '5800', '5900']  # Office supplies, advertising, travel, professional fees
            selected_account = random.choice(expense_accounts)
            
            entry.description = f"Miscellaneous business expense"
            entry.reference = f"EXP-{random.randint(1000, 9999)}"
            
            entry.add_line(JournalEntryLine(
                account_id=account_map[selected_account].account_id,
                description="Business expense",
                debit_amount=amount
            ))
            entry.add_line(JournalEntryLine(
                account_id=account_map['1000'].account_id,
                description="Cash payment",
                credit_amount=amount
            ))
        
        return entry
    
    def _random_amount(self, transaction_type: str) -> Decimal:
        """Generate a random amount for a transaction type"""
        min_amt, max_amt = self.amount_ranges.get(transaction_type, (100, 5000))
        amount = random.uniform(min_amt, max_amt)
        
        # Round to nearest cent
        return Decimal(str(amount)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    
    def _inject_errors(self, entry: JournalEntry, account_map: Dict[str, Account]) -> JournalEntry:
        """Inject various types of errors into an entry based on error rates"""
        
        # Unbalanced entries
        if random.random() < self.error_rates['unbalanced_entries']:
            entry = self._create_unbalanced_entry(entry)
        
        # Wrong account usage
        if random.random() < self.error_rates['wrong_accounts']:
            entry = self._use_wrong_accounts(entry, account_map)
        
        # Unusual amounts
        if random.random() < self.error_rates['unusual_amounts']:
            entry = self._create_unusual_amounts(entry)
        
        # Missing descriptions
        if random.random() < self.error_rates['missing_descriptions']:
            entry = self._remove_descriptions(entry)
        
        # Invalid dates
        if random.random() < self.error_rates['invalid_dates']:
            entry = self._create_invalid_dates(entry)
        
        return entry
    
    def _create_unbalanced_entry(self, entry: JournalEntry) -> JournalEntry:
        """Make an entry unbalanced"""
        if entry.lines:
            # Randomly adjust one line's amount
            line_to_adjust = random.choice(entry.lines)
            error_amount = Decimal(str(random.uniform(1, 500))).quantize(Decimal('0.01'))
            
            if random.choice([True, False]):
                if line_to_adjust.debit_amount > 0:
                    line_to_adjust.debit_amount += error_amount
                else:
                    line_to_adjust.credit_amount += error_amount
            else:
                if line_to_adjust.debit_amount > 0:
                    line_to_adjust.debit_amount = max(Decimal('0.01'), line_to_adjust.debit_amount - error_amount)
                else:
                    line_to_adjust.credit_amount = max(Decimal('0.01'), line_to_adjust.credit_amount - error_amount)
        
        return entry
    
    def _use_wrong_accounts(self, entry: JournalEntry, account_map: Dict[str, Account]) -> JournalEntry:
        """Use inappropriate accounts"""
        if entry.lines:
            line_to_change = random.choice(entry.lines)
            
            # Get all accounts of different types
            all_accounts = list(account_map.values())
            current_account = next((acc for acc in all_accounts if acc.account_id == line_to_change.account_id), None)
            
            if current_account:
                # Find an account of a different type
                different_type_accounts = [acc for acc in all_accounts if acc.account_type != current_account.account_type]
                if different_type_accounts:
                    wrong_account = random.choice(different_type_accounts)
                    line_to_change.account_id = wrong_account.account_id
        
        return entry
    
    def _create_unusual_amounts(self, entry: JournalEntry) -> JournalEntry:
        """Create unusual amounts"""
        if entry.lines:
            line_to_modify = random.choice(entry.lines)
            
            # Create different types of unusual amounts
            error_type = random.choice(['too_large', 'missing_decimals', 'round_number'])
            
            current_amount = max(line_to_modify.debit_amount, line_to_modify.credit_amount)
            
            if error_type == 'too_large':
                # Make amount unusually large
                multiplier = random.uniform(10, 100)
                new_amount = current_amount * Decimal(str(multiplier))
            elif error_type == 'missing_decimals':
                # Multiply by 100 (missing decimal point)
                new_amount = current_amount * Decimal('100')
            else:  # round_number
                # Make it a suspiciously round number
                new_amount = Decimal(str(round(float(current_amount), -3)))  # Round to thousands
            
            new_amount = new_amount.quantize(Decimal('0.01'))
            
            if line_to_modify.debit_amount > 0:
                line_to_modify.debit_amount = new_amount
            else:
                line_to_modify.credit_amount = new_amount
            
            # Update the balancing line to maintain balance (sometimes)
            if len(entry.lines) == 2 and random.choice([True, False]):
                other_line = entry.lines[1] if entry.lines[0] == line_to_modify else entry.lines[0]
                if other_line.debit_amount > 0:
                    other_line.debit_amount = new_amount
                else:
                    other_line.credit_amount = new_amount
        
        return entry
    
    def _remove_descriptions(self, entry: JournalEntry) -> JournalEntry:
        """Remove or make descriptions inadequate"""
        error_type = random.choice(['empty_entry_desc', 'short_entry_desc', 'empty_line_desc'])
        
        if error_type == 'empty_entry_desc':
            entry.description = ""
        elif error_type == 'short_entry_desc':
            entry.description = random.choice(["", "Adj", "Entry", "Misc"])
        else:  # empty_line_desc
            if entry.lines:
                line_to_modify = random.choice(entry.lines)
                line_to_modify.description = ""
        
        return entry
    
    def _create_invalid_dates(self, entry: JournalEntry) -> JournalEntry:
        """Create entries with problematic dates"""
        error_type = random.choice(['future_date', 'old_date', 'weekend_date'])
        
        if error_type == 'future_date':
            # Date too far in the future
            future_days = random.randint(2, 30)
            entry.entry_date = date.today() + timedelta(days=future_days)
        elif error_type == 'old_date':
            # Very old date
            old_days = random.randint(800, 1500)  # 2+ years ago
            entry.entry_date = date.today() - timedelta(days=old_days)
        else:  # weekend_date
            # Ensure it's a weekend
            while entry.entry_date.weekday() < 5:  # 0-4 are weekdays
                entry.entry_date += timedelta(days=1)
        
        return entry
    
    def _generate_baseline_entries(self, num_entries: int) -> int:
        """Generate error-free entries for baseline comparison"""
        # Temporarily disable error injection
        original_rates = self.error_rates.copy()
        self.error_rates = {key: 0.0 for key in self.error_rates}
        
        try:
            baseline_created = self._generate_journal_entries(num_entries)
            logger.info(f"Created {baseline_created} baseline (error-free) entries")
            return baseline_created
        finally:
            # Restore original error rates
            self.error_rates = original_rates
    
    def generate_error_summary(self) -> Dict[str, any]:
        """Generate a summary of the types of errors in the dataset"""
        # Get all entries
        all_entries_query = """
        SELECT COUNT(*) as total_entries,
               SUM(CASE WHEN ABS(total_debits - total_credits) > 0.01 THEN 1 ELSE 0 END) as unbalanced_entries
        FROM journal_entries
        """
        
        entry_stats = self.db.execute_query(all_entries_query)[0]
        
        # Get error statistics
        error_stats_query = """
        SELECT 
            error_type,
            error_severity,
            COUNT(*) as count
        FROM error_detection_log
        WHERE is_resolved = FALSE
        GROUP BY error_type, error_severity
        ORDER BY error_type, error_severity
        """
        
        error_details = self.db.execute_query(error_stats_query)
        
        return {
            'total_entries': entry_stats['total_entries'],
            'unbalanced_entries': entry_stats['unbalanced_entries'],
            'error_injection_rates': self.error_rates,
            'error_details': [dict(row) for row in error_details]
        }