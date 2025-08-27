#!/usr/bin/env python3
"""
Accounting Error Detection System - Error Detection Engine
Advanced algorithms for detecting posting errors and suggesting corrections
"""

import re
import statistics
from datetime import datetime, date, timedelta
from decimal import Decimal
from typing import List, Dict, Set, Optional, Tuple
from collections import defaultdict
import logging

from accounting_models import (
    JournalEntry, JournalEntryLine, Account, ErrorDetectionResult,
    ErrorType, ErrorSeverity, AccountType, NormalBalance,
    DatabaseManager, JournalEntryManager, AccountManager, ErrorDetectionManager
)

logger = logging.getLogger(__name__)


class ErrorDetectionEngine:
    """Advanced error detection engine for accounting entries"""
    
    def __init__(self, db: DatabaseManager):
        self.db = db
        self.journal_manager = JournalEntryManager(db)
        self.account_manager = AccountManager(db)
        self.error_manager = ErrorDetectionManager(db)
        
        # Statistical thresholds for unusual amounts
        self.amount_threshold_multiplier = 3.0  # Standard deviations
        self.duplicate_tolerance_days = 30  # Days to check for duplicates
        
    def detect_all_errors(self, entry: JournalEntry) -> List[ErrorDetectionResult]:
        """Run all error detection algorithms on a journal entry"""
        errors = []
        
        # Basic validation errors
        errors.extend(self._check_balance_errors(entry))
        errors.extend(self._check_zero_amounts(entry))
        errors.extend(self._check_negative_amounts(entry))
        errors.extend(self._check_missing_descriptions(entry))
        errors.extend(self._check_invalid_accounts(entry))
        errors.extend(self._check_invalid_dates(entry))
        
        # Advanced detection
        errors.extend(self._check_account_type_consistency(entry))
        errors.extend(self._check_duplicate_entries(entry))
        errors.extend(self._check_unusual_amounts(entry))
        errors.extend(self._check_posting_patterns(entry))
        errors.extend(self._check_business_rules(entry))
        
        # Log all detected errors
        for error in errors:
            self.error_manager.log_error(error)
            
        return errors
    
    def _check_balance_errors(self, entry: JournalEntry) -> List[ErrorDetectionResult]:
        """Check if debits equal credits"""
        errors = []
        
        if not entry.is_balanced:
            out_of_balance = entry.out_of_balance_amount
            
            # Determine severity based on amount
            if abs(out_of_balance) > Decimal('1000'):
                severity = ErrorSeverity.HIGH
            elif abs(out_of_balance) > Decimal('100'):
                severity = ErrorSeverity.MEDIUM
            else:
                severity = ErrorSeverity.LOW
            
            # Generate correction suggestion
            if out_of_balance > 0:
                suggestion = f"Add credit of ${abs(out_of_balance)} or reduce debits by ${abs(out_of_balance)}"
            else:
                suggestion = f"Add debit of ${abs(out_of_balance)} or reduce credits by ${abs(out_of_balance)}"
            
            error = ErrorDetectionResult(
                entry_id=entry.entry_id,
                error_type=ErrorType.UNBALANCED_ENTRY,
                error_severity=severity,
                error_description=f"Entry is out of balance by ${out_of_balance}. Debits: ${entry.total_debits}, Credits: ${entry.total_credits}",
                suggested_correction=suggestion
            )
            errors.append(error)
            
        return errors
    
    def _check_zero_amounts(self, entry: JournalEntry) -> List[ErrorDetectionResult]:
        """Check for lines with zero amounts"""
        errors = []
        
        for line in entry.lines:
            if line.debit_amount == 0 and line.credit_amount == 0:
                error = ErrorDetectionResult(
                    entry_id=entry.entry_id,
                    line_id=line.line_id,
                    error_type=ErrorType.ZERO_AMOUNT,
                    error_severity=ErrorSeverity.MEDIUM,
                    error_description=f"Line {line.line_number} for account {line.account_code} has zero amount",
                    suggested_correction="Enter the correct debit or credit amount, or remove this line"
                )
                errors.append(error)
                
        return errors
    
    def _check_negative_amounts(self, entry: JournalEntry) -> List[ErrorDetectionResult]:
        """Check for negative amounts (should use opposite side instead)"""
        errors = []
        
        for line in entry.lines:
            if line.debit_amount < 0 or line.credit_amount < 0:
                error = ErrorDetectionResult(
                    entry_id=entry.entry_id,
                    line_id=line.line_id,
                    error_type=ErrorType.NEGATIVE_AMOUNT,
                    error_severity=ErrorSeverity.HIGH,
                    error_description=f"Line {line.line_number} has negative amount",
                    suggested_correction="Use positive amount on the opposite side (debit vs credit)"
                )
                errors.append(error)
                
        return errors
    
    def _check_missing_descriptions(self, entry: JournalEntry) -> List[ErrorDetectionResult]:
        """Check for missing or inadequate descriptions"""
        errors = []
        
        # Check entry description
        if not entry.description or len(entry.description.strip()) < 5:
            error = ErrorDetectionResult(
                entry_id=entry.entry_id,
                error_type=ErrorType.MISSING_DESCRIPTION,
                error_severity=ErrorSeverity.LOW,
                error_description="Entry description is missing or too short",
                suggested_correction="Add a meaningful description explaining the transaction"
            )
            errors.append(error)
        
        # Check line descriptions for complex entries
        if len(entry.lines) > 2:
            for line in entry.lines:
                if not line.description or len(line.description.strip()) < 3:
                    error = ErrorDetectionResult(
                        entry_id=entry.entry_id,
                        line_id=line.line_id,
                        error_type=ErrorType.MISSING_DESCRIPTION,
                        error_severity=ErrorSeverity.LOW,
                        error_description=f"Line {line.line_number} is missing description",
                        suggested_correction="Add description to clarify this line item"
                    )
                    errors.append(error)
                    
        return errors
    
    def _check_invalid_accounts(self, entry: JournalEntry) -> List[ErrorDetectionResult]:
        """Check for invalid or inactive accounts"""
        errors = []
        
        for line in entry.lines:
            account = self.account_manager.get_account(line.account_id)
            
            if not account:
                error = ErrorDetectionResult(
                    entry_id=entry.entry_id,
                    line_id=line.line_id,
                    error_type=ErrorType.INVALID_ACCOUNT,
                    error_severity=ErrorSeverity.HIGH,
                    error_description=f"Account ID {line.account_id} does not exist",
                    suggested_correction="Select a valid account from the chart of accounts"
                )
                errors.append(error)
            elif not account.is_active:
                error = ErrorDetectionResult(
                    entry_id=entry.entry_id,
                    line_id=line.line_id,
                    error_type=ErrorType.INVALID_ACCOUNT,
                    error_severity=ErrorSeverity.MEDIUM,
                    error_description=f"Account {account.account_code} - {account.account_name} is inactive",
                    suggested_correction="Use an active account or reactivate this account if appropriate"
                )
                errors.append(error)
                
        return errors
    
    def _check_invalid_dates(self, entry: JournalEntry) -> List[ErrorDetectionResult]:
        """Check for invalid or suspicious dates"""
        errors = []
        
        today = date.today()
        
        # Check for future dates (more than 1 day ahead)
        if entry.entry_date > today + timedelta(days=1):
            error = ErrorDetectionResult(
                entry_id=entry.entry_id,
                error_type=ErrorType.INVALID_DATE,
                error_severity=ErrorSeverity.MEDIUM,
                error_description=f"Entry date {entry.entry_date} is in the future",
                suggested_correction="Verify the entry date is correct"
            )
            errors.append(error)
        
        # Check for very old dates (more than 2 years ago)
        if entry.entry_date < today - timedelta(days=730):
            error = ErrorDetectionResult(
                entry_id=entry.entry_id,
                error_type=ErrorType.INVALID_DATE,
                error_severity=ErrorSeverity.LOW,
                error_description=f"Entry date {entry.entry_date} is more than 2 years old",
                suggested_correction="Verify this is not a data entry error"
            )
            errors.append(error)
        
        # Check for weekend posting (depending on business rules)
        if entry.entry_date.weekday() >= 5:  # Saturday = 5, Sunday = 6
            error = ErrorDetectionResult(
                entry_id=entry.entry_id,
                error_type=ErrorType.INVALID_DATE,
                error_severity=ErrorSeverity.LOW,
                error_description=f"Entry dated on weekend: {entry.entry_date}",
                suggested_correction="Consider using the next business day"
            )
            errors.append(error)
            
        return errors
    
    def _check_account_type_consistency(self, entry: JournalEntry) -> List[ErrorDetectionResult]:
        """Check for unusual account type combinations"""
        errors = []
        
        account_types = []
        for line in entry.lines:
            account = self.account_manager.get_account(line.account_id)
            if account:
                account_types.append(account.account_type)
        
        # Check for unusual combinations
        unusual_combinations = self._detect_unusual_account_combinations(account_types, entry.description)
        
        for combination_error in unusual_combinations:
            error = ErrorDetectionResult(
                entry_id=entry.entry_id,
                error_type=ErrorType.ACCOUNT_TYPE_MISMATCH,
                error_severity=ErrorSeverity.MEDIUM,
                error_description=combination_error,
                suggested_correction="Review account selection to ensure proper categorization"
            )
            errors.append(error)
            
        return errors
    
    def _detect_unusual_account_combinations(self, account_types: List[AccountType], description: str) -> List[str]:
        """Detect unusual account type combinations"""
        errors = []
        type_set = set(account_types)
        
        # All expense accounts (might be missing asset/liability)
        if len(type_set) == 1 and AccountType.EXPENSE in type_set:
            if not any(word in description.lower() for word in ['depreciation', 'amortization', 'write-off']):
                errors.append("Entry contains only expense accounts - may be missing asset/liability accounts")
        
        # Revenue with expenses (unusual unless closing entries)
        if AccountType.REVENUE in type_set and AccountType.EXPENSE in type_set:
            if not any(word in description.lower() for word in ['closing', 'year-end', 'adjustment']):
                errors.append("Entry mixes revenue and expense accounts - verify this is intentional")
        
        # Multiple asset types without clear business purpose
        asset_count = sum(1 for t in account_types if t == AccountType.ASSET)
        if asset_count > 2 and not any(word in description.lower() for word in ['transfer', 'reclassification', 'acquisition']):
            errors.append("Entry affects multiple asset accounts - ensure this reflects actual transaction")
        
        return errors
    
    def _check_duplicate_entries(self, entry: JournalEntry) -> List[ErrorDetectionResult]:
        """Check for potential duplicate entries"""
        errors = []
        
        # Look for entries with same amount and similar dates
        start_date = entry.entry_date - timedelta(days=self.duplicate_tolerance_days)
        end_date = entry.entry_date + timedelta(days=self.duplicate_tolerance_days)
        
        similar_entries = self.journal_manager.get_entries_by_date_range(start_date, end_date)
        
        for similar_entry in similar_entries:
            if (similar_entry.entry_id != entry.entry_id and
                similar_entry.total_debits == entry.total_debits and
                similar_entry.total_credits == entry.total_credits):
                
                # Check if account usage is similar
                entry_accounts = set(line.account_id for line in entry.lines)
                similar_accounts = set(line.account_id for line in similar_entry.lines)
                
                if len(entry_accounts.intersection(similar_accounts)) >= len(entry_accounts) * 0.5:
                    error = ErrorDetectionResult(
                        entry_id=entry.entry_id,
                        error_type=ErrorType.DUPLICATE_ENTRY,
                        error_severity=ErrorSeverity.HIGH,
                        error_description=f"Potential duplicate of entry {similar_entry.entry_number} dated {similar_entry.entry_date}",
                        suggested_correction="Verify this is not a duplicate transaction"
                    )
                    errors.append(error)
                    break  # Only report one potential duplicate
                    
        return errors
    
    def _check_unusual_amounts(self, entry: JournalEntry) -> List[ErrorDetectionResult]:
        """Check for unusually large or small amounts"""
        errors = []
        
        # Get historical amounts for comparison
        historical_stats = self._get_historical_amount_statistics(entry.entry_date)
        
        if not historical_stats:
            return errors  # No historical data to compare
        
        mean_amount = historical_stats['mean']
        std_amount = historical_stats['std']
        
        if std_amount == 0:
            return errors  # No variation in historical data
        
        threshold = mean_amount + (self.amount_threshold_multiplier * std_amount)
        
        for line in entry.lines:
            line_amount = max(line.debit_amount, line.credit_amount)
            
            if line_amount > threshold:
                error = ErrorDetectionResult(
                    entry_id=entry.entry_id,
                    line_id=line.line_id,
                    error_type=ErrorType.UNUSUAL_AMOUNT,
                    error_severity=ErrorSeverity.MEDIUM,
                    error_description=f"Line {line.line_number} amount ${line_amount} is unusually large (threshold: ${threshold:.2f})",
                    suggested_correction="Verify amount is correct - may need additional approval for large amounts"
                )
                errors.append(error)
            
            # Check for amounts that might be missing decimal places
            if line_amount >= 1000 and line_amount % 100 == 0:
                if self._might_be_missing_decimals(line_amount, historical_stats):
                    error = ErrorDetectionResult(
                        entry_id=entry.entry_id,
                        line_id=line.line_id,
                        error_type=ErrorType.UNUSUAL_AMOUNT,
                        error_severity=ErrorSeverity.LOW,
                        error_description=f"Amount ${line_amount} might be missing decimal places",
                        suggested_correction=f"Verify if amount should be ${line_amount/100:.2f}"
                    )
                    errors.append(error)
                    
        return errors
    
    def _get_historical_amount_statistics(self, entry_date: date) -> Optional[Dict]:
        """Get statistical data about historical transaction amounts"""
        try:
            # Look at last 90 days before entry date
            start_date = entry_date - timedelta(days=90)
            
            query = """
            SELECT debit_amount, credit_amount
            FROM journal_entry_lines jel
            JOIN journal_entries je ON jel.entry_id = je.entry_id
            WHERE je.entry_date BETWEEN ? AND ?
            AND je.is_posted = TRUE
            """
            
            rows = self.db.execute_query(query, (start_date, entry_date))
            
            if len(rows) < 10:  # Need minimum data points
                return None
            
            amounts = []
            for row in rows:
                amounts.extend([float(row['debit_amount']), float(row['credit_amount'])])
            
            # Remove zero amounts
            amounts = [amt for amt in amounts if amt > 0]
            
            if not amounts:
                return None
            
            return {
                'mean': statistics.mean(amounts),
                'std': statistics.stdev(amounts) if len(amounts) > 1 else 0,
                'median': statistics.median(amounts),
                'count': len(amounts)
            }
            
        except Exception as e:
            logger.error(f"Error calculating historical statistics: {e}")
            return None
    
    def _might_be_missing_decimals(self, amount: Decimal, historical_stats: Dict) -> bool:
        """Check if an amount might be missing decimal places"""
        if not historical_stats:
            return False
        
        # If dividing by 100 brings it closer to the historical mean
        adjusted_amount = float(amount) / 100
        original_deviation = abs(float(amount) - historical_stats['mean'])
        adjusted_deviation = abs(adjusted_amount - historical_stats['mean'])
        
        return adjusted_deviation < original_deviation * 0.5
    
    def _check_posting_patterns(self, entry: JournalEntry) -> List[ErrorDetectionResult]:
        """Check for unusual posting patterns"""
        errors = []
        
        # Check for round numbers that might indicate estimates
        for line in entry.lines:
            line_amount = max(line.debit_amount, line.credit_amount)
            
            if (line_amount >= 1000 and 
                line_amount % 1000 == 0 and 
                line_amount > 0):
                
                error = ErrorDetectionResult(
                    entry_id=entry.entry_id,
                    line_id=line.line_id,
                    error_type=ErrorType.UNUSUAL_AMOUNT,
                    error_severity=ErrorSeverity.LOW,
                    error_description=f"Round amount ${line_amount} might be an estimate",
                    suggested_correction="Verify exact amount if this is not an estimate"
                )
                errors.append(error)
        
        # Check for excessive number of lines
        if len(entry.lines) > 10:
            error = ErrorDetectionResult(
                entry_id=entry.entry_id,
                error_type=ErrorType.UNUSUAL_AMOUNT,
                error_severity=ErrorSeverity.LOW,
                error_description=f"Entry has {len(entry.lines)} lines - unusually complex",
                suggested_correction="Consider breaking into multiple entries or verify all lines are necessary"
            )
            errors.append(error)
        
        return errors
    
    def _check_business_rules(self, entry: JournalEntry) -> List[ErrorDetectionResult]:
        """Check against business-specific rules"""
        errors = []
        
        # Check for common business rule violations
        errors.extend(self._check_cash_account_rules(entry))
        errors.extend(self._check_revenue_recognition_rules(entry))
        errors.extend(self._check_expense_matching_rules(entry))
        
        return errors
    
    def _check_cash_account_rules(self, entry: JournalEntry) -> List[ErrorDetectionResult]:
        """Check rules specific to cash accounts"""
        errors = []
        
        cash_accounts = []
        for line in entry.lines:
            account = self.account_manager.get_account(line.account_id)
            if account and 'cash' in account.account_name.lower():
                cash_accounts.append((line, account))
        
        # Multiple cash accounts in one entry (unusual)
        if len(cash_accounts) > 1:
            error = ErrorDetectionResult(
                entry_id=entry.entry_id,
                error_type=ErrorType.ACCOUNT_TYPE_MISMATCH,
                error_severity=ErrorSeverity.MEDIUM,
                error_description="Entry affects multiple cash accounts",
                suggested_correction="Verify this represents an actual cash transfer"
            )
            errors.append(error)
        
        # Large cash transactions without reference
        for line, account in cash_accounts:
            line_amount = max(line.debit_amount, line.credit_amount)
            if line_amount > 10000 and not entry.reference:
                error = ErrorDetectionResult(
                    entry_id=entry.entry_id,
                    line_id=line.line_id,
                    error_type=ErrorType.MISSING_DESCRIPTION,
                    error_severity=ErrorSeverity.MEDIUM,
                    error_description=f"Large cash transaction ${line_amount} without reference",
                    suggested_correction="Add check number, wire transfer ID, or other reference"
                )
                errors.append(error)
        
        return errors
    
    def _check_revenue_recognition_rules(self, entry: JournalEntry) -> List[ErrorDetectionResult]:
        """Check revenue recognition rules"""
        errors = []
        
        revenue_lines = []
        for line in entry.lines:
            account = self.account_manager.get_account(line.account_id)
            if account and account.account_type == AccountType.REVENUE:
                revenue_lines.append((line, account))
        
        # Revenue without corresponding debit to asset or reduction of liability
        if revenue_lines:
            non_revenue_types = set()
            for line in entry.lines:
                account = self.account_manager.get_account(line.account_id)
                if account and account.account_type != AccountType.REVENUE:
                    non_revenue_types.add(account.account_type)
            
            if not any(acc_type in [AccountType.ASSET, AccountType.LIABILITY] for acc_type in non_revenue_types):
                error = ErrorDetectionResult(
                    entry_id=entry.entry_id,
                    error_type=ErrorType.ACCOUNT_TYPE_MISMATCH,
                    error_severity=ErrorSeverity.MEDIUM,
                    error_description="Revenue recognition without corresponding asset increase or liability decrease",
                    suggested_correction="Ensure proper asset (cash/receivable) or liability reduction"
                )
                errors.append(error)
        
        return errors
    
    def _check_expense_matching_rules(self, entry: JournalEntry) -> List[ErrorDetectionResult]:
        """Check expense matching principle"""
        errors = []
        
        expense_lines = []
        for line in entry.lines:
            account = self.account_manager.get_account(line.account_id)
            if account and account.account_type == AccountType.EXPENSE:
                expense_lines.append((line, account))
        
        # Large expenses that might need to be capitalized
        for line, account in expense_lines:
            line_amount = max(line.debit_amount, line.credit_amount)
            
            # Check for potential capitalization candidates
            if (line_amount > 5000 and 
                any(word in account.account_name.lower() for word in ['equipment', 'software', 'improvement', 'installation'])):
                
                error = ErrorDetectionResult(
                    entry_id=entry.entry_id,
                    line_id=line.line_id,
                    error_type=ErrorType.ACCOUNT_TYPE_MISMATCH,
                    error_severity=ErrorSeverity.MEDIUM,
                    error_description=f"Large expense ${line_amount} for {account.account_name} might need capitalization",
                    suggested_correction="Consider if this should be recorded as an asset and depreciated"
                )
                errors.append(error)
        
        return errors


class CorrectionSuggestionEngine:
    """Provides intelligent correction suggestions for detected errors"""
    
    def __init__(self, db: DatabaseManager):
        self.db = db
        self.account_manager = AccountManager(db)
        
    def suggest_corrections(self, entry: JournalEntry, errors: List[ErrorDetectionResult]) -> Dict[str, List[str]]:
        """Generate detailed correction suggestions for all errors"""
        suggestions = defaultdict(list)
        
        for error in errors:
            error_suggestions = self._generate_specific_suggestions(entry, error)
            suggestions[error.error_type.value].extend(error_suggestions)
        
        return dict(suggestions)
    
    def _generate_specific_suggestions(self, entry: JournalEntry, error: ErrorDetectionResult) -> List[str]:
        """Generate specific suggestions based on error type"""
        suggestions = []
        
        if error.error_type == ErrorType.UNBALANCED_ENTRY:
            suggestions.extend(self._suggest_balance_corrections(entry, error))
        elif error.error_type == ErrorType.ACCOUNT_TYPE_MISMATCH:
            suggestions.extend(self._suggest_account_corrections(entry, error))
        elif error.error_type == ErrorType.DUPLICATE_ENTRY:
            suggestions.extend(self._suggest_duplicate_corrections(entry, error))
        elif error.error_type == ErrorType.UNUSUAL_AMOUNT:
            suggestions.extend(self._suggest_amount_corrections(entry, error))
        else:
            suggestions.append(error.suggested_correction)
        
        return suggestions
    
    def _suggest_balance_corrections(self, entry: JournalEntry, error: ErrorDetectionResult) -> List[str]:
        """Suggest specific balance corrections"""
        suggestions = []
        out_of_balance = entry.out_of_balance_amount
        
        # Suggest common balancing accounts
        if out_of_balance > 0:
            # Need more credits
            suggestions.extend([
                f"Add credit to Cash account: ${abs(out_of_balance)}",
                f"Add credit to Accounts Payable: ${abs(out_of_balance)}",
                f"Add credit to Revenue account: ${abs(out_of_balance)}",
                f"Reduce existing debit by: ${abs(out_of_balance)}"
            ])
        else:
            # Need more debits
            suggestions.extend([
                f"Add debit to Cash account: ${abs(out_of_balance)}",
                f"Add debit to Accounts Receivable: ${abs(out_of_balance)}",
                f"Add debit to Expense account: ${abs(out_of_balance)}",
                f"Reduce existing credit by: ${abs(out_of_balance)}"
            ])
        
        return suggestions
    
    def _suggest_account_corrections(self, entry: JournalEntry, error: ErrorDetectionResult) -> List[str]:
        """Suggest account corrections"""
        suggestions = []
        
        # Get similar accounts for each account in the entry
        for line in entry.lines:
            current_account = self.account_manager.get_account(line.account_id)
            if current_account:
                similar_accounts = self._find_similar_accounts(current_account)
                for similar in similar_accounts[:3]:  # Top 3 suggestions
                    suggestions.append(
                        f"Consider using {similar.account_code} - {similar.account_name} instead of {current_account.account_code}"
                    )
        
        return suggestions
    
    def _suggest_duplicate_corrections(self, entry: JournalEntry, error: ErrorDetectionResult) -> List[str]:
        """Suggest duplicate entry corrections"""
        return [
            "Review both entries to confirm they represent different transactions",
            "If duplicate, void one of the entries",
            "Add distinguishing information to descriptions",
            "Check source documents to verify separate transactions"
        ]
    
    def _suggest_amount_corrections(self, entry: JournalEntry, error: ErrorDetectionResult) -> List[str]:
        """Suggest amount corrections"""
        suggestions = []
        
        # Find the problematic line
        if error.line_id:
            line = next((l for l in entry.lines if l.line_id == error.line_id), None)
            if line:
                line_amount = max(line.debit_amount, line.credit_amount)
                
                suggestions.extend([
                    f"Verify source document for ${line_amount} amount",
                    f"Check if amount should be ${line_amount/100:.2f} (missing decimals)",
                    f"Consider if amount should be ${line_amount/10:.2f} (extra zero)",
                    "Obtain additional approval for large amounts",
                    "Break large amount into multiple, smaller entries if appropriate"
                ])
        
        return suggestions
    
    def _find_similar_accounts(self, account: Account) -> List[Account]:
        """Find accounts similar to the given account"""
        all_accounts = self.account_manager.get_all_accounts()
        similar = []
        
        for acc in all_accounts:
            if acc.account_id == account.account_id:
                continue
            
            # Same account type
            if acc.account_type == account.account_type:
                similarity_score = self._calculate_account_similarity(account, acc)
                if similarity_score > 0.3:  # 30% similarity threshold
                    similar.append(acc)
        
        # Sort by similarity (implement simple scoring)
        similar.sort(key=lambda x: self._calculate_account_similarity(account, x), reverse=True)
        
        return similar
    
    def _calculate_account_similarity(self, acc1: Account, acc2: Account) -> float:
        """Calculate similarity score between two accounts"""
        score = 0.0
        
        # Same account type
        if acc1.account_type == acc2.account_type:
            score += 0.5
        
        # Similar names (simple word overlap)
        name1_words = set(acc1.account_name.lower().split())
        name2_words = set(acc2.account_name.lower().split())
        
        if name1_words and name2_words:
            overlap = len(name1_words.intersection(name2_words))
            union = len(name1_words.union(name2_words))
            score += 0.3 * (overlap / union)
        
        # Same normal balance
        if acc1.normal_balance == acc2.normal_balance:
            score += 0.2
        
        return score