#!/usr/bin/env python3
"""
Accounting Error Detection System - Main Application
Interactive CLI for detecting posting errors and suggesting corrections
"""

import sys
import os
from datetime import datetime, date, timedelta
from decimal import Decimal
import logging

from accounting_models import (
    DatabaseManager, AccountManager, JournalEntryManager, ErrorDetectionManager,
    JournalEntry, JournalEntryLine, Account, AccountType, NormalBalance
)
from error_detector import ErrorDetectionEngine, CorrectionSuggestionEngine
from data_generator import SyntheticDataGenerator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('accounting_errors.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class AccountingErrorDetectorApp:
    """Main application class for the accounting error detection system"""
    
    def __init__(self, db_path: str = "accounting_errors.db"):
        """Initialize the application"""
        self.db = DatabaseManager(db_path)
        self.account_manager = AccountManager(self.db)
        self.journal_manager = JournalEntryManager(self.db)
        self.error_manager = ErrorDetectionManager(self.db)
        self.error_detector = ErrorDetectionEngine(self.db)
        self.suggestion_engine = CorrectionSuggestionEngine(self.db)
        self.data_generator = SyntheticDataGenerator(self.db)
        
        logger.info("Accounting Error Detection System initialized")
    
    def run(self):
        """Run the interactive CLI"""
        print("=" * 70)
        print("  ACCOUNTING ERROR DETECTION SYSTEM")
        print("=" * 70)
        print()
        
        try:
            while True:
                self._show_main_menu()
                choice = input("\nEnter your choice (1-9 or 'q' to quit): ").strip().lower()
                
                if choice in ['q', 'quit', 'exit']:
                    print("\nThank you for using the Accounting Error Detection System!")
                    break
                elif choice == '1':
                    self._data_management_menu()
                elif choice == '2':
                    self._entry_management_menu()
                elif choice == '3':
                    self._error_detection_menu()
                elif choice == '4':
                    self._error_analysis_menu()
                elif choice == '5':
                    self._correction_suggestions_menu()
                elif choice == '6':
                    self._reporting_menu()
                elif choice == '7':
                    self._testing_menu()
                elif choice == '8':
                    self._system_utilities_menu()
                elif choice == '9':
                    self._help_menu()
                else:
                    print("Invalid choice. Please try again.")
        
        except KeyboardInterrupt:
            print("\n\nApplication terminated by user.")
        except Exception as e:
            logger.error(f"Application error: {e}")
            print(f"\nError: {str(e)}")
        finally:
            self.db.close()
    
    def _show_main_menu(self):
        """Display the main menu"""
        print("\n" + "=" * 50)
        print("MAIN MENU")
        print("=" * 50)
        print("1. Data Management")
        print("2. Journal Entry Management")
        print("3. Error Detection")
        print("4. Error Analysis")
        print("5. Correction Suggestions")
        print("6. Reports & Statistics")
        print("7. Testing & Validation")
        print("8. System Utilities")
        print("9. Help")
        print("Q. Quit")
    
    def _data_management_menu(self):
        """Data management submenu"""
        while True:
            print("\n" + "-" * 40)
            print("DATA MANAGEMENT")
            print("-" * 40)
            print("1. Generate Synthetic Data")
            print("2. View Data Statistics")
            print("3. Clear All Data")
            print("4. Import Data")
            print("5. Export Data")
            print("6. Back to Main Menu")
            
            choice = input("\nEnter your choice: ").strip()
            
            if choice == '1':
                self._generate_synthetic_data()
            elif choice == '2':
                self._view_data_statistics()
            elif choice == '3':
                self._clear_all_data()
            elif choice == '4':
                self._import_data()
            elif choice == '5':
                self._export_data()
            elif choice == '6':
                break
            else:
                print("Invalid choice. Please try again.")
    
    def _entry_management_menu(self):
        """Journal entry management submenu"""
        while True:
            print("\n" + "-" * 40)
            print("JOURNAL ENTRY MANAGEMENT")
            print("-" * 40)
            print("1. Create New Entry")
            print("2. View Entry Details")
            print("3. List Recent Entries")
            print("4. Search Entries")
            print("5. Post Entries")
            print("6. Back to Main Menu")
            
            choice = input("\nEnter your choice: ").strip()
            
            if choice == '1':
                self._create_journal_entry()
            elif choice == '2':
                self._view_entry_details()
            elif choice == '3':
                self._list_recent_entries()
            elif choice == '4':
                self._search_entries()
            elif choice == '5':
                self._post_entries()
            elif choice == '6':
                break
            else:
                print("Invalid choice. Please try again.")
    
    def _error_detection_menu(self):
        """Error detection submenu"""
        while True:
            print("\n" + "-" * 40)
            print("ERROR DETECTION")
            print("-" * 40)
            print("1. Run Error Detection on Single Entry")
            print("2. Run Batch Error Detection")
            print("3. View Unresolved Errors")
            print("4. Error Detection Settings")
            print("5. Back to Main Menu")
            
            choice = input("\nEnter your choice: ").strip()
            
            if choice == '1':
                self._detect_single_entry_errors()
            elif choice == '2':
                self._run_batch_error_detection()
            elif choice == '3':
                self._view_unresolved_errors()
            elif choice == '4':
                self._error_detection_settings()
            elif choice == '5':
                break
            else:
                print("Invalid choice. Please try again.")
    
    def _error_analysis_menu(self):
        """Error analysis submenu"""
        while True:
            print("\n" + "-" * 40)
            print("ERROR ANALYSIS")
            print("-" * 40)
            print("1. Error Summary by Type")
            print("2. Error Trends Over Time")
            print("3. Most Common Errors")
            print("4. Error Resolution Statistics")
            print("5. Back to Main Menu")
            
            choice = input("\nEnter your choice: ").strip()
            
            if choice == '1':
                self._error_summary_by_type()
            elif choice == '2':
                self._error_trends_over_time()
            elif choice == '3':
                self._most_common_errors()
            elif choice == '4':
                self._error_resolution_statistics()
            elif choice == '5':
                break
            else:
                print("Invalid choice. Please try again.")
    
    def _correction_suggestions_menu(self):
        """Correction suggestions submenu"""
        while True:
            print("\n" + "-" * 40)
            print("CORRECTION SUGGESTIONS")
            print("-" * 40)
            print("1. Get Suggestions for Entry")
            print("2. Auto-Apply Safe Corrections")
            print("3. Review Pending Corrections")
            print("4. Mark Errors as Resolved")
            print("5. Back to Main Menu")
            
            choice = input("\nEnter your choice: ").strip()
            
            if choice == '1':
                self._get_correction_suggestions()
            elif choice == '2':
                self._auto_apply_corrections()
            elif choice == '3':
                self._review_pending_corrections()
            elif choice == '4':
                self._mark_errors_resolved()
            elif choice == '5':
                break
            else:
                print("Invalid choice. Please try again.")
    
    def _reporting_menu(self):
        """Reporting submenu"""
        while True:
            print("\n" + "-" * 40)
            print("REPORTS & STATISTICS")
            print("-" * 40)
            print("1. Error Detection Report")
            print("2. Data Quality Report")
            print("3. System Performance Report")
            print("4. Export Error Log")
            print("5. Back to Main Menu")
            
            choice = input("\nEnter your choice: ").strip()
            
            if choice == '1':
                self._error_detection_report()
            elif choice == '2':
                self._data_quality_report()
            elif choice == '3':
                self._system_performance_report()
            elif choice == '4':
                self._export_error_log()
            elif choice == '5':
                break
            else:
                print("Invalid choice. Please try again.")
    
    def _testing_menu(self):
        """Testing submenu"""
        while True:
            print("\n" + "-" * 40)
            print("TESTING & VALIDATION")
            print("-" * 40)
            print("1. Test Error Detection Accuracy")
            print("2. Validate Correction Suggestions")
            print("3. Performance Benchmark")
            print("4. Generate Test Cases")
            print("5. Back to Main Menu")
            
            choice = input("\nEnter your choice: ").strip()
            
            if choice == '1':
                self._test_detection_accuracy()
            elif choice == '2':
                self._validate_corrections()
            elif choice == '3':
                self._performance_benchmark()
            elif choice == '4':
                self._generate_test_cases()
            elif choice == '5':
                break
            else:
                print("Invalid choice. Please try again.")
    
    def _system_utilities_menu(self):
        """System utilities submenu"""
        while True:
            print("\n" + "-" * 40)
            print("SYSTEM UTILITIES")
            print("-" * 40)
            print("1. Database Maintenance")
            print("2. System Configuration")
            print("3. Backup & Restore")
            print("4. System Diagnostics")
            print("5. Back to Main Menu")
            
            choice = input("\nEnter your choice: ").strip()
            
            if choice == '1':
                self._database_maintenance()
            elif choice == '2':
                self._system_configuration()
            elif choice == '3':
                self._backup_restore()
            elif choice == '4':
                self._system_diagnostics()
            elif choice == '5':
                break
            else:
                print("Invalid choice. Please try again.")
    
    def _help_menu(self):
        """Help and documentation"""
        print("\n" + "-" * 60)
        print("HELP - ACCOUNTING ERROR DETECTION SYSTEM")
        print("-" * 60)
        print()
        print("This system helps detect and correct common accounting posting errors:")
        print()
        print("ERROR TYPES DETECTED:")
        print("• Unbalanced Entries - Debits ≠ Credits")
        print("• Account Type Mismatches - Wrong account categories")
        print("• Duplicate Entries - Potential duplicate transactions")
        print("• Unusual Amounts - Amounts outside normal ranges")
        print("• Invalid Accounts - Non-existent or inactive accounts")
        print("• Missing Descriptions - Inadequate transaction descriptions")
        print("• Invalid Dates - Future dates, old dates, weekend dates")
        print()
        print("CORRECTION SUGGESTIONS:")
        print("• Automatic balance correction suggestions")
        print("• Alternative account recommendations")
        print("• Amount validation checks")
        print("• Business rule compliance verification")
        print()
        print("GETTING STARTED:")
        print("1. Generate synthetic data (Data Management → Generate Synthetic Data)")
        print("2. Run error detection (Error Detection → Run Batch Error Detection)")
        print("3. Review errors (Error Detection → View Unresolved Errors)")
        print("4. Get corrections (Correction Suggestions → Get Suggestions)")
        print()
        print("For technical support, check the log files or documentation.")
        
        input("\nPress Enter to continue...")
    
    # Implementation methods for each menu option
    
    def _generate_synthetic_data(self):
        """Generate synthetic accounting data"""
        print("\n--- Generate Synthetic Data ---")
        print("This will create a chart of accounts and journal entries with intentional errors.")
        
        try:
            num_entries = input("Number of journal entries to generate (default 500): ").strip()
            num_entries = int(num_entries) if num_entries.isdigit() else 500
            
            print(f"\nGenerating {num_entries} entries with realistic errors...")
            print("This may take a few minutes...")
            
            stats = self.data_generator.generate_complete_dataset(num_entries)
            
            print(f"\n✓ Data generation completed successfully!")
            print(f"  • Accounts created: {stats['accounts_created']}")
            print(f"  • Journal entries created: {stats['journal_entries_created']}")
            print(f"  • Baseline entries created: {stats['baseline_entries_created']}")
            print(f"  • Total entries: {stats['total_entries']}")
            
        except ValueError:
            print("Invalid number entered.")
        except Exception as e:
            print(f"Error generating data: {str(e)}")
            logger.error(f"Data generation error: {e}")
    
    def _view_data_statistics(self):
        """View current data statistics"""
        print("\n--- Data Statistics ---")
        
        try:
            # Get basic counts
            accounts_query = "SELECT COUNT(*) as count FROM chart_of_accounts WHERE is_active = TRUE"
            accounts_count = self.db.execute_query(accounts_query)[0]['count']
            
            entries_query = "SELECT COUNT(*) as count FROM journal_entries"
            entries_count = self.db.execute_query(entries_query)[0]['count']
            
            errors_query = "SELECT COUNT(*) as count FROM error_detection_log WHERE is_resolved = FALSE"
            errors_count = self.db.execute_query(errors_query)[0]['count']
            
            print(f"\nDATABASE STATISTICS:")
            print(f"  • Active accounts: {accounts_count}")
            print(f"  • Journal entries: {entries_count}")
            print(f"  • Unresolved errors: {errors_count}")
            
            # Get error breakdown
            if errors_count > 0:
                error_breakdown_query = """
                SELECT error_type, error_severity, COUNT(*) as count
                FROM error_detection_log 
                WHERE is_resolved = FALSE
                GROUP BY error_type, error_severity
                ORDER BY count DESC
                """
                error_breakdown = self.db.execute_query(error_breakdown_query)
                
                print(f"\nERROR BREAKDOWN:")
                for error in error_breakdown:
                    print(f"  • {error['error_type']} ({error['error_severity']}): {error['count']}")
            
            # Get recent activity
            recent_entries_query = """
            SELECT COUNT(*) as count
            FROM journal_entries
            WHERE created_date >= date('now', '-7 days')
            """
            recent_count = self.db.execute_query(recent_entries_query)[0]['count']
            print(f"\nRECENT ACTIVITY:")
            print(f"  • Entries created (last 7 days): {recent_count}")
            
        except Exception as e:
            print(f"Error retrieving statistics: {str(e)}")
    
    def _clear_all_data(self):
        """Clear all data from the database"""
        print("\n--- Clear All Data ---")
        print("⚠️  WARNING: This will permanently delete ALL data!")
        
        confirm1 = input("Are you sure you want to delete all data? (type 'DELETE' to confirm): ").strip()
        if confirm1 != 'DELETE':
            print("Operation cancelled.")
            return
        
        confirm2 = input("This action cannot be undone. Type 'YES DELETE ALL' to proceed: ").strip()
        if confirm2 != 'YES DELETE ALL':
            print("Operation cancelled.")
            return
        
        try:
            # Delete in proper order to respect foreign key constraints
            tables_to_clear = [
                'error_detection_log',
                'audit_trail',
                'account_balances',
                'template_lines',
                'entry_templates',
                'posting_rules',
                'journal_entry_lines',
                'journal_entries',
                'chart_of_accounts'
            ]
            
            total_deleted = 0
            for table in tables_to_clear:
                try:
                    rows_deleted = self.db.execute_update(f"DELETE FROM {table}")
                    total_deleted += rows_deleted
                    print(f"  ✓ Cleared {table}: {rows_deleted} records")
                except Exception as e:
                    print(f"  ⚠️  Warning clearing {table}: {e}")
            
            print(f"\n✓ Data clearing completed. Total records deleted: {total_deleted}")
            
        except Exception as e:
            print(f"Error clearing data: {str(e)}")
    
    def _import_data(self):
        """Import data from external sources"""
        print("\n--- Import Data ---")
        print("This feature allows importing from CSV files or other accounting systems.")
        print("Currently under development - coming soon!")
        input("Press Enter to continue...")
    
    def _export_data(self):
        """Export data to external formats"""
        print("\n--- Export Data ---")
        print("This feature allows exporting to CSV, Excel, or other formats.")
        print("Currently under development - coming soon!")
        input("Press Enter to continue...")
    
    def _create_journal_entry(self):
        """Create a new journal entry interactively"""
        print("\n--- Create New Journal Entry ---")
        
        try:
            # Get entry header information
            entry_number = input("Entry number (or press Enter for auto-generation): ").strip()
            if not entry_number:
                # Auto-generate entry number
                last_entry_query = "SELECT entry_number FROM journal_entries ORDER BY entry_id DESC LIMIT 1"
                result = self.db.execute_query(last_entry_query)
                if result and result[0]['entry_number']:
                    last_num = result[0]['entry_number']
                    if 'JE-' in last_num:
                        try:
                            num_part = int(last_num.split('-')[-1])
                            entry_number = f"JE-{datetime.now().year}-{num_part + 1:04d}"
                        except:
                            entry_number = f"JE-{datetime.now().year}-0001"
                    else:
                        entry_number = f"JE-{datetime.now().year}-0001"
                else:
                    entry_number = f"JE-{datetime.now().year}-0001"
            
            description = input("Entry description: ").strip()
            if not description:
                print("Description is required.")
                return
            
            reference = input("Reference (invoice #, check #, etc., optional): ").strip()
            
            # Get entry date
            date_str = input("Entry date (YYYY-MM-DD, or press Enter for today): ").strip()
            if date_str:
                try:
                    entry_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                except ValueError:
                    print("Invalid date format. Using today's date.")
                    entry_date = date.today()
            else:
                entry_date = date.today()
            
            # Create the journal entry object
            entry = JournalEntry(
                entry_number=entry_number,
                entry_date=entry_date,
                description=description,
                reference=reference,
                created_by="manual_entry"
            )
            
            # Get entry lines
            print(f"\nAdding lines to entry {entry_number}")
            print("Enter account details for each line (minimum 2 lines required)")
            
            line_number = 1
            while True:
                print(f"\n--- Line {line_number} ---")
                
                # Show available accounts
                print("Available accounts (showing first 10):")
                accounts = self.account_manager.get_all_accounts()[:10]
                for i, acc in enumerate(accounts, 1):
                    print(f"  {i}. {acc.account_code} - {acc.account_name}")
                
                account_input = input("Enter account number or code: ").strip()
                if not account_input:
                    if line_number >= 3:  # Allow exit after minimum 2 lines
                        break
                    else:
                        print("At least 2 lines are required.")
                        continue
                
                # Find the account
                account = None
                if account_input.isdigit():
                    account_num = int(account_input)
                    if 1 <= account_num <= len(accounts):
                        account = accounts[account_num - 1]
                else:
                    # Search by account code
                    account = self.account_manager.get_account_by_code(account_input)
                
                if not account:
                    print("Account not found.")
                    continue
                
                line_description = input(f"Line description (optional): ").strip()
                
                # Get debit or credit amount
                while True:
                    debit_credit = input("Enter 'D' for debit or 'C' for credit: ").strip().upper()
                    if debit_credit in ['D', 'C']:
                        break
                    print("Please enter 'D' or 'C'")
                
                amount_str = input("Enter amount: ").strip()
                try:
                    amount = Decimal(amount_str)
                    if amount <= 0:
                        print("Amount must be positive.")
                        continue
                except (ValueError, Exception):
                    print("Invalid amount.")
                    continue
                
                # Create the line
                line = JournalEntryLine(
                    line_number=line_number,
                    account_id=account.account_id,
                    account_code=account.account_code,
                    account_name=account.account_name,
                    description=line_description or description,
                    debit_amount=amount if debit_credit == 'D' else Decimal('0'),
                    credit_amount=amount if debit_credit == 'C' else Decimal('0')
                )
                
                entry.add_line(line)
                print(f"✓ Line {line_number} added: {account.account_code} - ${amount} {debit_credit}")
                
                line_number += 1
                
                if line_number > 2:
                    continue_input = input("\nAdd another line? (y/n): ").strip().lower()
                    if continue_input != 'y':
                        break
            
            if len(entry.lines) < 2:
                print("Entry must have at least 2 lines.")
                return
            
            # Show entry summary
            print(f"\n--- Entry Summary ---")
            print(f"Entry Number: {entry.entry_number}")
            print(f"Date: {entry.entry_date}")
            print(f"Description: {entry.description}")
            print(f"Reference: {entry.reference}")
            print(f"Total Debits: ${entry.total_debits}")
            print(f"Total Credits: ${entry.total_credits}")
            print(f"Balanced: {'Yes' if entry.is_balanced else 'No'}")
            
            if not entry.is_balanced:
                print(f"⚠️  Out of balance by: ${entry.out_of_balance_amount}")
            
            # Confirm creation
            confirm = input("\nCreate this entry? (y/n): ").strip().lower()
            if confirm == 'y':
                entry_id = self.journal_manager.create_entry(entry)
                print(f"✓ Entry created successfully with ID {entry_id}")
                
                # Run error detection
                detect_errors = input("Run error detection on this entry? (y/n): ").strip().lower()
                if detect_errors == 'y':
                    errors = self.error_detector.detect_all_errors(entry)
                    if errors:
                        print(f"⚠️  {len(errors)} errors detected:")
                        for error in errors:
                            print(f"  • {error.error_type.value}: {error.error_description}")
                    else:
                        print("✓ No errors detected")
            else:
                print("Entry creation cancelled.")
        
        except Exception as e:
            print(f"Error creating entry: {str(e)}")
            logger.error(f"Entry creation error: {e}")
    
    def _view_entry_details(self):
        """View detailed information about a journal entry"""
        print("\n--- View Entry Details ---")
        
        entry_id_str = input("Enter entry ID or entry number: ").strip()
        
        try:
            # Try to find by ID first, then by entry number
            entry = None
            if entry_id_str.isdigit():
                entry = self.journal_manager.get_entry(int(entry_id_str))
            
            if not entry:
                # Search by entry number
                query = "SELECT entry_id FROM journal_entries WHERE entry_number = ?"
                result = self.db.execute_query(query, (entry_id_str,))
                if result:
                    entry = self.journal_manager.get_entry(result[0]['entry_id'])
            
            if not entry:
                print("Entry not found.")
                return
            
            # Display entry details
            print(f"\n--- Entry Details ---")
            print(f"Entry ID: {entry.entry_id}")
            print(f"Entry Number: {entry.entry_number}")
            print(f"Date: {entry.entry_date}")
            print(f"Description: {entry.description}")
            print(f"Reference: {entry.reference}")
            print(f"Created By: {entry.created_by}")
            print(f"Created Date: {entry.created_date}")
            print(f"Posted: {'Yes' if entry.is_posted else 'No'}")
            print(f"Total Debits: ${entry.total_debits}")
            print(f"Total Credits: ${entry.total_credits}")
            print(f"Balanced: {'Yes' if entry.is_balanced else 'No'}")
            
            # Display lines
            print(f"\n--- Entry Lines ---")
            print(f"{'Line':<4} {'Account':<15} {'Description':<25} {'Debit':<12} {'Credit':<12}")
            print("-" * 75)
            
            for line in entry.lines:
                debit_str = f"${line.debit_amount:,.2f}" if line.debit_amount > 0 else ""
                credit_str = f"${line.credit_amount:,.2f}" if line.credit_amount > 0 else ""
                account_str = f"{line.account_code}"
                desc_str = line.description[:23] + "..." if len(line.description) > 25 else line.description
                
                print(f"{line.line_number:<4} {account_str:<15} {desc_str:<25} {debit_str:<12} {credit_str:<12}")
            
            # Check for errors
            errors = self.error_manager.get_errors_for_entry(entry.entry_id)
            if errors:
                print(f"\n--- Detected Errors ({len(errors)}) ---")
                for error in errors:
                    severity_icon = "🔴" if error.error_severity.value == "HIGH" else "🟡" if error.error_severity.value == "MEDIUM" else "🟢"
                    print(f"{severity_icon} {error.error_type.value}: {error.error_description}")
                    if error.suggested_correction:
                        print(f"   Suggestion: {error.suggested_correction}")
                    print()
            else:
                print(f"\n✓ No errors detected for this entry")
        
        except Exception as e:
            print(f"Error viewing entry: {str(e)}")
    
    def _list_recent_entries(self):
        """List recent journal entries"""
        print("\n--- Recent Journal Entries ---")
        
        try:
            limit_str = input("Number of entries to show (default 20): ").strip()
            limit = int(limit_str) if limit_str.isdigit() else 20
            
            query = """
            SELECT entry_id, entry_number, entry_date, description, 
                   total_debits, total_credits, is_posted
            FROM journal_entries 
            ORDER BY created_date DESC 
            LIMIT ?
            """
            
            entries = self.db.execute_query(query, (limit,))
            
            if not entries:
                print("No entries found.")
                return
            
            print(f"\n{'ID':<6} {'Number':<15} {'Date':<12} {'Description':<30} {'Debits':<12} {'Credits':<12} {'Posted'}")
            print("-" * 95)
            
            for entry in entries:
                posted_str = "Yes" if entry['is_posted'] else "No"
                desc_str = entry['description'][:28] + "..." if len(entry['description']) > 30 else entry['description']
                
                print(f"{entry['entry_id']:<6} {entry['entry_number']:<15} {entry['entry_date']:<12} {desc_str:<30} "
                      f"${entry['total_debits']:<11.2f} ${entry['total_credits']:<11.2f} {posted_str}")
        
        except Exception as e:
            print(f"Error listing entries: {str(e)}")
    
    def _search_entries(self):
        """Search journal entries"""
        print("\n--- Search Journal Entries ---")
        print("Search by description, reference, or account code")
        
        search_term = input("Enter search term: ").strip()
        if not search_term:
            print("Search term is required.")
            return
        
        try:
            query = """
            SELECT DISTINCT je.entry_id, je.entry_number, je.entry_date, 
                   je.description, je.total_debits, je.total_credits
            FROM journal_entries je
            LEFT JOIN journal_entry_lines jel ON je.entry_id = jel.entry_id
            LEFT JOIN chart_of_accounts coa ON jel.account_id = coa.account_id
            WHERE je.description LIKE ?
               OR je.reference LIKE ?
               OR coa.account_code LIKE ?
               OR coa.account_name LIKE ?
            ORDER BY je.entry_date DESC
            LIMIT 50
            """
            
            search_pattern = f"%{search_term}%"
            results = self.db.execute_query(query, (search_pattern, search_pattern, search_pattern, search_pattern))
            
            if not results:
                print("No entries found matching the search criteria.")
                return
            
            print(f"\nFound {len(results)} entries:")
            print(f"\n{'ID':<6} {'Number':<15} {'Date':<12} {'Description':<40}")
            print("-" * 80)
            
            for result in results:
                desc_str = result['description'][:38] + "..." if len(result['description']) > 40 else result['description']
                print(f"{result['entry_id']:<6} {result['entry_number']:<15} {result['entry_date']:<12} {desc_str:<40}")
        
        except Exception as e:
            print(f"Error searching entries: {str(e)}")
    
    def _post_entries(self):
        """Post unposted journal entries"""
        print("\n--- Post Journal Entries ---")
        
        try:
            # Get unposted entries
            query = """
            SELECT entry_id, entry_number, entry_date, description, 
                   total_debits, total_credits
            FROM journal_entries 
            WHERE is_posted = FALSE
            ORDER BY entry_date, entry_number
            """
            
            unposted = self.db.execute_query(query)
            
            if not unposted:
                print("No unposted entries found.")
                return
            
            print(f"Found {len(unposted)} unposted entries:")
            print(f"\n{'ID':<6} {'Number':<15} {'Date':<12} {'Description':<30} {'Balanced'}")
            print("-" * 75)
            
            for entry in unposted:
                balanced = "Yes" if abs(entry['total_debits'] - entry['total_credits']) < 0.01 else "No"
                desc_str = entry['description'][:28] + "..." if len(entry['description']) > 30 else entry['description']
                print(f"{entry['entry_id']:<6} {entry['entry_number']:<15} {entry['entry_date']:<12} {desc_str:<30} {balanced}")
            
            print("\nPost options:")
            print("1. Post all balanced entries")
            print("2. Post specific entry by ID")
            print("3. Cancel")
            
            choice = input("Enter choice: ").strip()
            
            if choice == '1':
                posted_count = 0
                for entry in unposted:
                    if abs(entry['total_debits'] - entry['total_credits']) < 0.01:
                        if self.journal_manager.post_entry(entry['entry_id']):
                            posted_count += 1
                            print(f"✓ Posted entry {entry['entry_number']}")
                        else:
                            print(f"✗ Failed to post entry {entry['entry_number']}")
                
                print(f"\nPosted {posted_count} entries successfully.")
                
            elif choice == '2':
                entry_id_str = input("Enter entry ID to post: ").strip()
                if entry_id_str.isdigit():
                    entry_id = int(entry_id_str)
                    if self.journal_manager.post_entry(entry_id):
                        print(f"✓ Entry {entry_id} posted successfully.")
                    else:
                        print(f"✗ Failed to post entry {entry_id}.")
                else:
                    print("Invalid entry ID.")
            
        except Exception as e:
            print(f"Error posting entries: {str(e)}")
    
    def _detect_single_entry_errors(self):
        """Run error detection on a single entry"""
        print("\n--- Detect Errors in Single Entry ---")
        
        entry_id_str = input("Enter entry ID or entry number: ").strip()
        
        try:
            entry = None
            if entry_id_str.isdigit():
                entry = self.journal_manager.get_entry(int(entry_id_str))
            
            if not entry:
                # Search by entry number
                query = "SELECT entry_id FROM journal_entries WHERE entry_number = ?"
                result = self.db.execute_query(query, (entry_id_str,))
                if result:
                    entry = self.journal_manager.get_entry(result[0]['entry_id'])
            
            if not entry:
                print("Entry not found.")
                return
            
            print(f"Running error detection on entry {entry.entry_number}...")
            
            # Clear existing errors for this entry (re-run detection)
            self.db.execute_update("DELETE FROM error_detection_log WHERE entry_id = ?", (entry.entry_id,))
            
            errors = self.error_detector.detect_all_errors(entry)
            
            if not errors:
                print("✓ No errors detected in this entry.")
                return
            
            print(f"\n⚠️  Found {len(errors)} errors:")
            
            for i, error in enumerate(errors, 1):
                severity_icon = "🔴" if error.error_severity.value == "HIGH" else "🟡" if error.error_severity.value == "MEDIUM" else "🟢"
                print(f"\n{i}. {severity_icon} {error.error_type.value} ({error.error_severity.value})")
                print(f"   {error.error_description}")
                if error.suggested_correction:
                    print(f"   💡 Suggestion: {error.suggested_correction}")
            
            # Offer correction suggestions
            get_suggestions = input(f"\nGet detailed correction suggestions? (y/n): ").strip().lower()
            if get_suggestions == 'y':
                suggestions = self.suggestion_engine.suggest_corrections(entry, errors)
                
                print(f"\n--- Correction Suggestions ---")
                for error_type, suggestion_list in suggestions.items():
                    print(f"\n{error_type.replace('_', ' ').title()}:")
                    for i, suggestion in enumerate(suggestion_list, 1):
                        print(f"  {i}. {suggestion}")
        
        except Exception as e:
            print(f"Error detecting errors: {str(e)}")
    
    def _run_batch_error_detection(self):
        """Run error detection on multiple entries"""
        print("\n--- Batch Error Detection ---")
        
        try:
            # Get scope options
            print("Select scope for error detection:")
            print("1. All unposted entries")
            print("2. Entries from specific date range")
            print("3. All entries (may take a while)")
            
            choice = input("Enter choice (1-3): ").strip()
            
            entries_to_check = []
            
            if choice == '1':
                query = "SELECT entry_id FROM journal_entries WHERE is_posted = FALSE ORDER BY entry_id"
                results = self.db.execute_query(query)
                entries_to_check = [r['entry_id'] for r in results]
                print(f"Will check {len(entries_to_check)} unposted entries.")
                
            elif choice == '2':
                start_date = input("Start date (YYYY-MM-DD): ").strip()
                end_date = input("End date (YYYY-MM-DD): ").strip()
                
                try:
                    start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
                    end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
                except ValueError:
                    print("Invalid date format.")
                    return
                
                query = """
                SELECT entry_id FROM journal_entries 
                WHERE entry_date BETWEEN ? AND ?
                ORDER BY entry_id
                """
                results = self.db.execute_query(query, (start_date_obj, end_date_obj))
                entries_to_check = [r['entry_id'] for r in results]
                print(f"Will check {len(entries_to_check)} entries in date range.")
                
            elif choice == '3':
                query = "SELECT entry_id FROM journal_entries ORDER BY entry_id"
                results = self.db.execute_query(query)
                entries_to_check = [r['entry_id'] for r in results]
                print(f"Will check ALL {len(entries_to_check)} entries.")
                
                confirm = input("This may take a while. Continue? (y/n): ").strip().lower()
                if confirm != 'y':
                    print("Operation cancelled.")
                    return
            else:
                print("Invalid choice.")
                return
            
            if not entries_to_check:
                print("No entries found to check.")
                return
            
            # Run batch detection
            print(f"\nRunning error detection on {len(entries_to_check)} entries...")
            
            total_errors = 0
            processed = 0
            
            for entry_id in entries_to_check:
                try:
                    entry = self.journal_manager.get_entry(entry_id)
                    if entry:
                        # Clear existing errors for re-run
                        self.db.execute_update("DELETE FROM error_detection_log WHERE entry_id = ?", (entry_id,))
                        
                        errors = self.error_detector.detect_all_errors(entry)
                        total_errors += len(errors)
                        processed += 1
                        
                        if processed % 50 == 0:  # Progress indicator
                            print(f"  Processed {processed}/{len(entries_to_check)} entries...")
                
                except Exception as e:
                    logger.error(f"Error processing entry {entry_id}: {e}")
            
            print(f"\n✓ Batch error detection completed!")
            print(f"  • Entries processed: {processed}")
            print(f"  • Total errors detected: {total_errors}")
            print(f"  • Average errors per entry: {total_errors/processed:.2f}" if processed > 0 else "")
            
            # Show summary by error type
            if total_errors > 0:
                summary_query = """
                SELECT error_type, error_severity, COUNT(*) as count
                FROM error_detection_log 
                WHERE is_resolved = FALSE
                GROUP BY error_type, error_severity
                ORDER BY count DESC
                """
                summary = self.db.execute_query(summary_query)
                
                print(f"\nError Summary:")
                for error in summary:
                    print(f"  • {error['error_type']} ({error['error_severity']}): {error['count']}")
        
        except Exception as e:
            print(f"Error in batch detection: {str(e)}")
    
    def _view_unresolved_errors(self):
        """View all unresolved errors"""
        print("\n--- Unresolved Errors ---")
        
        try:
            errors = self.error_manager.get_all_unresolved_errors()
            
            if not errors:
                print("✓ No unresolved errors found!")
                return
            
            print(f"Found {len(errors)} unresolved errors:")
            
            # Group by entry
            errors_by_entry = {}
            for error in errors:
                if error.entry_id not in errors_by_entry:
                    errors_by_entry[error.entry_id] = []
                errors_by_entry[error.entry_id].append(error)
            
            for entry_id, entry_errors in errors_by_entry.items():
                # Get entry details
                entry = self.journal_manager.get_entry(entry_id)
                if not entry:
                    continue
                
                print(f"\n--- Entry {entry.entry_number} ({entry.entry_date}) ---")
                print(f"Description: {entry.description}")
                
                for error in entry_errors:
                    severity_icon = "🔴" if error.error_severity.value == "HIGH" else "🟡" if error.error_severity.value == "MEDIUM" else "🟢"
                    print(f"  {severity_icon} {error.error_type.value}: {error.error_description}")
                    if error.suggested_correction:
                        print(f"     💡 {error.suggested_correction}")
            
            # Offer bulk actions
            print(f"\nBulk Actions:")
            print("1. Mark all low-severity errors as resolved")
            print("2. Export error list to file")
            print("3. Get correction suggestions for all errors")
            print("4. Return to menu")
            
            action = input("Select action (1-4): ").strip()
            
            if action == '1':
                low_errors = [e for e in errors if e.error_severity.value == "LOW"]
                if low_errors:
                    confirm = input(f"Mark {len(low_errors)} low-severity errors as resolved? (y/n): ").strip().lower()
                    if confirm == 'y':
                        resolved_count = 0
                        for error in low_errors:
                            if self.error_manager.resolve_error(error.error_id, "bulk_resolution", "Low severity bulk resolution"):
                                resolved_count += 1
                        print(f"✓ Resolved {resolved_count} errors.")
                else:
                    print("No low-severity errors found.")
            
            elif action == '3':
                print("Getting correction suggestions for all errors...")
                # This would be implemented to show suggestions for all errors
                print("Feature under development.")
        
        except Exception as e:
            print(f"Error viewing unresolved errors: {str(e)}")
    
    def _error_detection_settings(self):
        """Configure error detection settings"""
        print("\n--- Error Detection Settings ---")
        print("Current settings:")
        print(f"  • Amount threshold multiplier: {self.error_detector.amount_threshold_multiplier}")
        print(f"  • Duplicate tolerance days: {self.error_detector.duplicate_tolerance_days}")
        print()
        print("Settings modification is currently under development.")
        input("Press Enter to continue...")
    
    # Additional method implementations would continue here...
    # For brevity, I'll include a few key ones and note that others follow similar patterns
    
    def _error_summary_by_type(self):
        """Show error summary grouped by type"""
        print("\n--- Error Summary by Type ---")
        
        try:
            query = """
            SELECT 
                error_type,
                error_severity,
                COUNT(*) as count,
                COUNT(*) * 100.0 / (SELECT COUNT(*) FROM error_detection_log WHERE is_resolved = FALSE) as percentage
            FROM error_detection_log 
            WHERE is_resolved = FALSE
            GROUP BY error_type, error_severity
            ORDER BY count DESC
            """
            
            results = self.db.execute_query(query)
            
            if not results:
                print("No errors found.")
                return
            
            print(f"\n{'Error Type':<25} {'Severity':<10} {'Count':<8} {'%':<8}")
            print("-" * 55)
            
            for row in results:
                print(f"{row['error_type']:<25} {row['error_severity']:<10} {row['count']:<8} {row['percentage']:<8.1f}")
        
        except Exception as e:
            print(f"Error generating summary: {str(e)}")
    
    def _get_correction_suggestions(self):
        """Get correction suggestions for a specific entry"""
        print("\n--- Get Correction Suggestions ---")
        
        entry_id_str = input("Enter entry ID or entry number: ").strip()
        
        try:
            entry = None
            if entry_id_str.isdigit():
                entry = self.journal_manager.get_entry(int(entry_id_str))
            
            if not entry:
                query = "SELECT entry_id FROM journal_entries WHERE entry_number = ?"
                result = self.db.execute_query(query, (entry_id_str,))
                if result:
                    entry = self.journal_manager.get_entry(result[0]['entry_id'])
            
            if not entry:
                print("Entry not found.")
                return
            
            # Get errors for this entry
            errors = self.error_manager.get_errors_for_entry(entry.entry_id)
            
            if not errors:
                print("No unresolved errors found for this entry.")
                return
            
            print(f"\nGenerating correction suggestions for entry {entry.entry_number}...")
            
            suggestions = self.suggestion_engine.suggest_corrections(entry, errors)
            
            print(f"\n--- Correction Suggestions ---")
            for error_type, suggestion_list in suggestions.items():
                print(f"\n{error_type.replace('_', ' ').title()}:")
                for i, suggestion in enumerate(suggestion_list, 1):
                    print(f"  {i}. {suggestion}")
            
            print(f"\nThese are suggestions only. Please review and apply corrections manually.")
        
        except Exception as e:
            print(f"Error getting suggestions: {str(e)}")
    
    def _mark_errors_resolved(self):
        """Mark errors as resolved"""
        print("\n--- Mark Errors as Resolved ---")
        
        try:
            # Show unresolved errors
            errors = self.error_manager.get_all_unresolved_errors()
            
            if not errors:
                print("No unresolved errors found.")
                return
            
            print(f"Found {len(errors)} unresolved errors:")
            
            for i, error in enumerate(errors[:10], 1):  # Show first 10
                severity_icon = "🔴" if error.error_severity.value == "HIGH" else "🟡" if error.error_severity.value == "MEDIUM" else "🟢"
                print(f"{i}. {severity_icon} ID {error.error_id}: {error.error_type.value}")
                print(f"   {error.error_description}")
            
            if len(errors) > 10:
                print(f"... and {len(errors) - 10} more errors")
            
            print(f"\nResolve options:")
            print("1. Resolve specific error by ID")
            print("2. Resolve all errors for an entry")
            print("3. Bulk resolve by error type")
            print("4. Cancel")
            
            choice = input("Enter choice (1-4): ").strip()
            
            if choice == '1':
                error_id_str = input("Enter error ID to resolve: ").strip()
                if error_id_str.isdigit():
                    error_id = int(error_id_str)
                    resolution_notes = input("Resolution notes: ").strip()
                    
                    if self.error_manager.resolve_error(error_id, "manual_resolution", resolution_notes):
                        print(f"✓ Error {error_id} marked as resolved.")
                    else:
                        print(f"✗ Failed to resolve error {error_id}.")
                else:
                    print("Invalid error ID.")
            
            elif choice == '2':
                entry_id_str = input("Enter entry ID: ").strip()
                if entry_id_str.isdigit():
                    entry_id = int(entry_id_str)
                    entry_errors = [e for e in errors if e.entry_id == entry_id]
                    
                    if entry_errors:
                        resolution_notes = input("Resolution notes for all entry errors: ").strip()
                        resolved_count = 0
                        
                        for error in entry_errors:
                            if self.error_manager.resolve_error(error.error_id, "manual_resolution", resolution_notes):
                                resolved_count += 1
                        
                        print(f"✓ Resolved {resolved_count}/{len(entry_errors)} errors for entry {entry_id}.")
                    else:
                        print(f"No errors found for entry {entry_id}.")
                else:
                    print("Invalid entry ID.")
        
        except Exception as e:
            print(f"Error resolving errors: {str(e)}")


def main():
    """Main application entry point"""
    print("Initializing Accounting Error Detection System...")
    
    try:
        # Create application instance
        app = AccountingErrorDetectorApp()
        
        # Run the interactive CLI
        app.run()
        
    except KeyboardInterrupt:
        print("\n\nApplication terminated by user.")
    except Exception as e:
        logger.error(f"Fatal application error: {e}")
        print(f"\nFatal error: {str(e)}")
        print("Check the log file 'accounting_errors.log' for details.")
    
    print("\nGoodbye!")


if __name__ == "__main__":
    main()