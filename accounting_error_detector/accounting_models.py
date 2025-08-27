#!/usr/bin/env python3
"""
Accounting Error Detection System - Core Models
Contains data models and classes for accounting entries and error detection
"""

import sqlite3
import json
from datetime import datetime, date
from decimal import Decimal, ROUND_HALF_UP
from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AccountType(Enum):
    ASSET = "ASSET"
    LIABILITY = "LIABILITY"
    EQUITY = "EQUITY"
    REVENUE = "REVENUE"
    EXPENSE = "EXPENSE"


class NormalBalance(Enum):
    DEBIT = "DEBIT"
    CREDIT = "CREDIT"


class ErrorSeverity(Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class ErrorType(Enum):
    UNBALANCED_ENTRY = "UNBALANCED_ENTRY"
    ACCOUNT_TYPE_MISMATCH = "ACCOUNT_TYPE_MISMATCH"
    DUPLICATE_ENTRY = "DUPLICATE_ENTRY"
    UNUSUAL_AMOUNT = "UNUSUAL_AMOUNT"
    INVALID_ACCOUNT = "INVALID_ACCOUNT"
    NEGATIVE_AMOUNT = "NEGATIVE_AMOUNT"
    ZERO_AMOUNT = "ZERO_AMOUNT"
    MISSING_DESCRIPTION = "MISSING_DESCRIPTION"
    INVALID_DATE = "INVALID_DATE"
    CIRCULAR_REFERENCE = "CIRCULAR_REFERENCE"


@dataclass
class Account:
    """Represents a chart of accounts entry"""
    account_id: Optional[int] = None
    account_code: str = ""
    account_name: str = ""
    account_type: AccountType = AccountType.ASSET
    account_subtype: Optional[str] = None
    normal_balance: NormalBalance = NormalBalance.DEBIT
    parent_account_id: Optional[int] = None
    is_active: bool = True
    created_date: Optional[datetime] = None
    
    def __post_init__(self):
        if self.created_date is None:
            self.created_date = datetime.now()


@dataclass
class JournalEntryLine:
    """Represents a single line in a journal entry"""
    line_id: Optional[int] = None
    entry_id: Optional[int] = None
    line_number: int = 0
    account_id: int = 0
    account_code: str = ""
    account_name: str = ""
    description: str = ""
    debit_amount: Decimal = field(default_factory=lambda: Decimal('0.00'))
    credit_amount: Decimal = field(default_factory=lambda: Decimal('0.00'))
    
    def __post_init__(self):
        # Ensure amounts are Decimal with 2 decimal places
        self.debit_amount = Decimal(str(self.debit_amount)).quantize(
            Decimal('0.01'), rounding=ROUND_HALF_UP
        )
        self.credit_amount = Decimal(str(self.credit_amount)).quantize(
            Decimal('0.01'), rounding=ROUND_HALF_UP
        )
    
    @property
    def net_amount(self) -> Decimal:
        """Return the net amount (debit - credit)"""
        return self.debit_amount - self.credit_amount
    
    def is_valid(self) -> bool:
        """Check if the line is valid"""
        return (
            self.account_id > 0 and
            (self.debit_amount > 0 or self.credit_amount > 0) and
            not (self.debit_amount > 0 and self.credit_amount > 0)
        )


@dataclass
class JournalEntry:
    """Represents a complete journal entry"""
    entry_id: Optional[int] = None
    entry_number: str = ""
    entry_date: Optional[date] = None
    description: str = ""
    reference: str = ""
    created_by: str = ""
    created_date: Optional[datetime] = None
    modified_date: Optional[datetime] = None
    is_posted: bool = False
    is_reversed: bool = False
    reversal_entry_id: Optional[int] = None
    lines: List[JournalEntryLine] = field(default_factory=list)
    
    def __post_init__(self):
        if self.entry_date is None:
            self.entry_date = date.today()
        if self.created_date is None:
            self.created_date = datetime.now()
        if self.modified_date is None:
            self.modified_date = datetime.now()
    
    @property
    def total_debits(self) -> Decimal:
        """Calculate total debits for the entry"""
        return sum(line.debit_amount for line in self.lines)
    
    @property
    def total_credits(self) -> Decimal:
        """Calculate total credits for the entry"""
        return sum(line.credit_amount for line in self.lines)
    
    @property
    def is_balanced(self) -> bool:
        """Check if the entry is balanced (debits = credits)"""
        return self.total_debits == self.total_credits
    
    @property
    def out_of_balance_amount(self) -> Decimal:
        """Return the out of balance amount"""
        return self.total_debits - self.total_credits
    
    def add_line(self, line: JournalEntryLine):
        """Add a line to the journal entry"""
        line.entry_id = self.entry_id
        line.line_number = len(self.lines) + 1
        self.lines.append(line)
    
    def is_valid(self) -> bool:
        """Check if the journal entry is valid"""
        return (
            bool(self.entry_number) and
            bool(self.description) and
            len(self.lines) >= 2 and
            all(line.is_valid() for line in self.lines) and
            self.is_balanced
        )


@dataclass
class ErrorDetectionResult:
    """Represents the result of error detection"""
    error_id: Optional[int] = None
    entry_id: Optional[int] = None
    line_id: Optional[int] = None
    error_type: ErrorType = ErrorType.UNBALANCED_ENTRY
    error_severity: ErrorSeverity = ErrorSeverity.MEDIUM
    error_description: str = ""
    suggested_correction: str = ""
    detected_date: Optional[datetime] = None
    is_resolved: bool = False
    
    def __post_init__(self):
        if self.detected_date is None:
            self.detected_date = datetime.now()


class DatabaseManager:
    """Handles database operations for the accounting system"""
    
    def __init__(self, db_path: str = "accounting_errors.db"):
        self.db_path = db_path
        self.connection = None
        self.connect()
    
    def connect(self):
        """Establish database connection"""
        try:
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row
            self.connection.execute("PRAGMA foreign_keys = ON")
            logger.info(f"Connected to database: {self.db_path}")
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            raise
    
    def execute_query(self, query: str, params: tuple = ()) -> List[sqlite3.Row]:
        """Execute a SELECT query and return results"""
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params)
            return cursor.fetchall()
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            raise
    
    def execute_update(self, query: str, params: tuple = ()) -> int:
        """Execute an INSERT, UPDATE, or DELETE query"""
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params)
            self.connection.commit()
            return cursor.rowcount
        except Exception as e:
            logger.error(f"Update execution failed: {e}")
            self.connection.rollback()
            raise
    
    def execute_many(self, query: str, params_list: List[tuple]) -> int:
        """Execute multiple queries with different parameters"""
        try:
            cursor = self.connection.cursor()
            cursor.executemany(query, params_list)
            self.connection.commit()
            return cursor.rowcount
        except Exception as e:
            logger.error(f"Batch execution failed: {e}")
            self.connection.rollback()
            raise
    
    def get_last_insert_id(self) -> int:
        """Get the ID of the last inserted record"""
        return self.connection.lastrowid
    
    def begin_transaction(self):
        """Begin a database transaction"""
        self.connection.execute("BEGIN")
    
    def commit_transaction(self):
        """Commit the current transaction"""
        self.connection.commit()
    
    def rollback_transaction(self):
        """Rollback the current transaction"""
        self.connection.rollback()
    
    def close(self):
        """Close the database connection"""
        if self.connection:
            self.connection.close()
            logger.info("Database connection closed")


class AccountManager:
    """Manages chart of accounts operations"""
    
    def __init__(self, db: DatabaseManager):
        self.db = db
    
    def create_account(self, account: Account) -> int:
        """Create a new account"""
        query = """
        INSERT INTO chart_of_accounts 
        (account_code, account_name, account_type, account_subtype, 
         normal_balance, parent_account_id, is_active)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        params = (
            account.account_code, account.account_name, account.account_type.value,
            account.account_subtype, account.normal_balance.value,
            account.parent_account_id, account.is_active
        )
        self.db.execute_update(query, params)
        return self.db.get_last_insert_id()
    
    def get_account(self, account_id: int) -> Optional[Account]:
        """Get an account by ID"""
        query = "SELECT * FROM chart_of_accounts WHERE account_id = ?"
        rows = self.db.execute_query(query, (account_id,))
        
        if rows:
            row = rows[0]
            return Account(
                account_id=row['account_id'],
                account_code=row['account_code'],
                account_name=row['account_name'],
                account_type=AccountType(row['account_type']),
                account_subtype=row['account_subtype'],
                normal_balance=NormalBalance(row['normal_balance']),
                parent_account_id=row['parent_account_id'],
                is_active=bool(row['is_active']),
                created_date=datetime.fromisoformat(row['created_date']) if row['created_date'] else None
            )
        return None
    
    def get_account_by_code(self, account_code: str) -> Optional[Account]:
        """Get an account by code"""
        query = "SELECT * FROM chart_of_accounts WHERE account_code = ?"
        rows = self.db.execute_query(query, (account_code,))
        
        if rows:
            row = rows[0]
            return Account(
                account_id=row['account_id'],
                account_code=row['account_code'],
                account_name=row['account_name'],
                account_type=AccountType(row['account_type']),
                account_subtype=row['account_subtype'],
                normal_balance=NormalBalance(row['normal_balance']),
                parent_account_id=row['parent_account_id'],
                is_active=bool(row['is_active']),
                created_date=datetime.fromisoformat(row['created_date']) if row['created_date'] else None
            )
        return None
    
    def get_all_accounts(self) -> List[Account]:
        """Get all active accounts"""
        query = """
        SELECT * FROM chart_of_accounts 
        WHERE is_active = TRUE 
        ORDER BY account_code
        """
        rows = self.db.execute_query(query)
        
        accounts = []
        for row in rows:
            accounts.append(Account(
                account_id=row['account_id'],
                account_code=row['account_code'],
                account_name=row['account_name'],
                account_type=AccountType(row['account_type']),
                account_subtype=row['account_subtype'],
                normal_balance=NormalBalance(row['normal_balance']),
                parent_account_id=row['parent_account_id'],
                is_active=bool(row['is_active']),
                created_date=datetime.fromisoformat(row['created_date']) if row['created_date'] else None
            ))
        
        return accounts


class JournalEntryManager:
    """Manages journal entry operations"""
    
    def __init__(self, db: DatabaseManager):
        self.db = db
        self.account_manager = AccountManager(db)
    
    def create_entry(self, entry: JournalEntry) -> int:
        """Create a new journal entry with lines"""
        try:
            self.db.begin_transaction()
            
            # Insert journal entry header
            entry_query = """
            INSERT INTO journal_entries 
            (entry_number, entry_date, description, reference, created_by,
             total_debits, total_credits)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """
            entry_params = (
                entry.entry_number, entry.entry_date, entry.description,
                entry.reference, entry.created_by,
                float(entry.total_debits), float(entry.total_credits)
            )
            self.db.execute_update(entry_query, entry_params)
            entry_id = self.db.get_last_insert_id()
            
            # Insert journal entry lines
            line_query = """
            INSERT INTO journal_entry_lines
            (entry_id, line_number, account_id, description, debit_amount, credit_amount)
            VALUES (?, ?, ?, ?, ?, ?)
            """
            line_params = []
            for line in entry.lines:
                line.entry_id = entry_id
                line_params.append((
                    entry_id, line.line_number, line.account_id,
                    line.description, float(line.debit_amount), float(line.credit_amount)
                ))
            
            self.db.execute_many(line_query, line_params)
            self.db.commit_transaction()
            
            logger.info(f"Created journal entry {entry.entry_number} with ID {entry_id}")
            return entry_id
            
        except Exception as e:
            self.db.rollback_transaction()
            logger.error(f"Failed to create journal entry: {e}")
            raise
    
    def get_entry(self, entry_id: int) -> Optional[JournalEntry]:
        """Get a journal entry by ID"""
        # Get entry header
        entry_query = "SELECT * FROM journal_entries WHERE entry_id = ?"
        entry_rows = self.db.execute_query(entry_query, (entry_id,))
        
        if not entry_rows:
            return None
        
        entry_row = entry_rows[0]
        
        # Get entry lines with account information
        lines_query = """
        SELECT jel.*, coa.account_code, coa.account_name
        FROM journal_entry_lines jel
        JOIN chart_of_accounts coa ON jel.account_id = coa.account_id
        WHERE jel.entry_id = ?
        ORDER BY jel.line_number
        """
        line_rows = self.db.execute_query(lines_query, (entry_id,))
        
        # Create journal entry lines
        lines = []
        for line_row in line_rows:
            line = JournalEntryLine(
                line_id=line_row['line_id'],
                entry_id=line_row['entry_id'],
                line_number=line_row['line_number'],
                account_id=line_row['account_id'],
                account_code=line_row['account_code'],
                account_name=line_row['account_name'],
                description=line_row['description'],
                debit_amount=Decimal(str(line_row['debit_amount'])),
                credit_amount=Decimal(str(line_row['credit_amount']))
            )
            lines.append(line)
        
        # Create journal entry
        entry = JournalEntry(
            entry_id=entry_row['entry_id'],
            entry_number=entry_row['entry_number'],
            entry_date=date.fromisoformat(entry_row['entry_date']),
            description=entry_row['description'],
            reference=entry_row['reference'],
            created_by=entry_row['created_by'],
            created_date=datetime.fromisoformat(entry_row['created_date']) if entry_row['created_date'] else None,
            modified_date=datetime.fromisoformat(entry_row['modified_date']) if entry_row['modified_date'] else None,
            is_posted=bool(entry_row['is_posted']),
            is_reversed=bool(entry_row['is_reversed']),
            reversal_entry_id=entry_row['reversal_entry_id'],
            lines=lines
        )
        
        return entry
    
    def get_entries_by_date_range(self, start_date: date, end_date: date) -> List[JournalEntry]:
        """Get journal entries within a date range"""
        query = """
        SELECT entry_id FROM journal_entries 
        WHERE entry_date BETWEEN ? AND ?
        ORDER BY entry_date, entry_number
        """
        rows = self.db.execute_query(query, (start_date, end_date))
        
        entries = []
        for row in rows:
            entry = self.get_entry(row['entry_id'])
            if entry:
                entries.append(entry)
        
        return entries
    
    def post_entry(self, entry_id: int) -> bool:
        """Mark a journal entry as posted"""
        try:
            query = """
            UPDATE journal_entries 
            SET is_posted = TRUE, modified_date = CURRENT_TIMESTAMP
            WHERE entry_id = ?
            """
            rows_affected = self.db.execute_update(query, (entry_id,))
            return rows_affected > 0
        except Exception as e:
            logger.error(f"Failed to post entry {entry_id}: {e}")
            return False


class ErrorDetectionManager:
    """Manages error detection and logging"""
    
    def __init__(self, db: DatabaseManager):
        self.db = db
    
    def log_error(self, error: ErrorDetectionResult) -> int:
        """Log an error detection result"""
        query = """
        INSERT INTO error_detection_log
        (entry_id, line_id, error_type, error_severity, error_description,
         suggested_correction)
        VALUES (?, ?, ?, ?, ?, ?)
        """
        params = (
            error.entry_id, error.line_id, error.error_type.value,
            error.error_severity.value, error.error_description,
            error.suggested_correction
        )
        self.db.execute_update(query, params)
        return self.db.get_last_insert_id()
    
    def get_errors_for_entry(self, entry_id: int) -> List[ErrorDetectionResult]:
        """Get all errors for a specific journal entry"""
        query = """
        SELECT * FROM error_detection_log 
        WHERE entry_id = ? AND is_resolved = FALSE
        ORDER BY error_severity DESC, detected_date
        """
        rows = self.db.execute_query(query, (entry_id,))
        
        errors = []
        for row in rows:
            error = ErrorDetectionResult(
                error_id=row['error_id'],
                entry_id=row['entry_id'],
                line_id=row['line_id'],
                error_type=ErrorType(row['error_type']),
                error_severity=ErrorSeverity(row['error_severity']),
                error_description=row['error_description'],
                suggested_correction=row['suggested_correction'],
                detected_date=datetime.fromisoformat(row['detected_date']) if row['detected_date'] else None,
                is_resolved=bool(row['is_resolved'])
            )
            errors.append(error)
        
        return errors
    
    def get_all_unresolved_errors(self) -> List[ErrorDetectionResult]:
        """Get all unresolved errors"""
        query = """
        SELECT * FROM error_detection_log 
        WHERE is_resolved = FALSE
        ORDER BY error_severity DESC, detected_date DESC
        """
        rows = self.db.execute_query(query)
        
        errors = []
        for row in rows:
            error = ErrorDetectionResult(
                error_id=row['error_id'],
                entry_id=row['entry_id'],
                line_id=row['line_id'],
                error_type=ErrorType(row['error_type']),
                error_severity=ErrorSeverity(row['error_severity']),
                error_description=row['error_description'],
                suggested_correction=row['suggested_correction'],
                detected_date=datetime.fromisoformat(row['detected_date']) if row['detected_date'] else None,
                is_resolved=bool(row['is_resolved'])
            )
            errors.append(error)
        
        return errors
    
    def resolve_error(self, error_id: int, resolved_by: str, resolution_notes: str = "") -> bool:
        """Mark an error as resolved"""
        query = """
        UPDATE error_detection_log
        SET is_resolved = TRUE, resolved_date = CURRENT_TIMESTAMP,
            resolved_by = ?, resolution_notes = ?
        WHERE error_id = ?
        """
        try:
            rows_affected = self.db.execute_update(query, (resolved_by, resolution_notes, error_id))
            return rows_affected > 0
        except Exception as e:
            logger.error(f"Failed to resolve error {error_id}: {e}")
            return False