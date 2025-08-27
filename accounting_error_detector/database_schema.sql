-- Accounting Error Detection System Database Schema
-- SQLite schema for comprehensive accounting system with error detection

-- Chart of Accounts
CREATE TABLE chart_of_accounts (
    account_id INTEGER PRIMARY KEY AUTOINCREMENT,
    account_code VARCHAR(20) UNIQUE NOT NULL,
    account_name VARCHAR(100) NOT NULL,
    account_type VARCHAR(20) NOT NULL, -- ASSET, LIABILITY, EQUITY, REVENUE, EXPENSE
    account_subtype VARCHAR(30), -- CURRENT_ASSET, FIXED_ASSET, etc.
    normal_balance VARCHAR(6) NOT NULL, -- DEBIT or CREDIT
    parent_account_id INTEGER,
    is_active BOOLEAN DEFAULT TRUE,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (parent_account_id) REFERENCES chart_of_accounts(account_id)
);

-- Journal Entries
CREATE TABLE journal_entries (
    entry_id INTEGER PRIMARY KEY AUTOINCREMENT,
    entry_number VARCHAR(20) UNIQUE NOT NULL,
    entry_date DATE NOT NULL,
    description TEXT NOT NULL,
    reference VARCHAR(50), -- Invoice number, check number, etc.
    created_by VARCHAR(50) NOT NULL,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    modified_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_posted BOOLEAN DEFAULT FALSE,
    is_reversed BOOLEAN DEFAULT FALSE,
    reversal_entry_id INTEGER,
    total_debits DECIMAL(15,2) DEFAULT 0,
    total_credits DECIMAL(15,2) DEFAULT 0,
    FOREIGN KEY (reversal_entry_id) REFERENCES journal_entries(entry_id)
);

-- Journal Entry Line Items
CREATE TABLE journal_entry_lines (
    line_id INTEGER PRIMARY KEY AUTOINCREMENT,
    entry_id INTEGER NOT NULL,
    line_number INTEGER NOT NULL,
    account_id INTEGER NOT NULL,
    description TEXT,
    debit_amount DECIMAL(15,2) DEFAULT 0,
    credit_amount DECIMAL(15,2) DEFAULT 0,
    FOREIGN KEY (entry_id) REFERENCES journal_entries(entry_id) ON DELETE CASCADE,
    FOREIGN KEY (account_id) REFERENCES chart_of_accounts(account_id),
    CHECK (debit_amount >= 0 AND credit_amount >= 0),
    CHECK (NOT (debit_amount > 0 AND credit_amount > 0)) -- Can't have both debit and credit
);

-- Error Detection Log
CREATE TABLE error_detection_log (
    error_id INTEGER PRIMARY KEY AUTOINCREMENT,
    entry_id INTEGER,
    line_id INTEGER,
    error_type VARCHAR(50) NOT NULL,
    error_severity VARCHAR(10) NOT NULL, -- HIGH, MEDIUM, LOW
    error_description TEXT NOT NULL,
    suggested_correction TEXT,
    detected_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_resolved BOOLEAN DEFAULT FALSE,
    resolved_date TIMESTAMP,
    resolved_by VARCHAR(50),
    resolution_notes TEXT,
    FOREIGN KEY (entry_id) REFERENCES journal_entries(entry_id),
    FOREIGN KEY (line_id) REFERENCES journal_entry_lines(line_id)
);

-- Account Balance History (for trend analysis)
CREATE TABLE account_balances (
    balance_id INTEGER PRIMARY KEY AUTOINCREMENT,
    account_id INTEGER NOT NULL,
    balance_date DATE NOT NULL,
    debit_balance DECIMAL(15,2) DEFAULT 0,
    credit_balance DECIMAL(15,2) DEFAULT 0,
    net_balance DECIMAL(15,2) DEFAULT 0,
    FOREIGN KEY (account_id) REFERENCES chart_of_accounts(account_id),
    UNIQUE(account_id, balance_date)
);

-- Posting Rules (for validation)
CREATE TABLE posting_rules (
    rule_id INTEGER PRIMARY KEY AUTOINCREMENT,
    rule_name VARCHAR(100) NOT NULL,
    rule_type VARCHAR(30) NOT NULL, -- BALANCE_CHECK, ACCOUNT_TYPE, AMOUNT_LIMIT, etc.
    rule_description TEXT,
    rule_condition TEXT, -- JSON or SQL condition
    error_message VARCHAR(200),
    is_active BOOLEAN DEFAULT TRUE,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Standard Journal Entry Templates
CREATE TABLE entry_templates (
    template_id INTEGER PRIMARY KEY AUTOINCREMENT,
    template_name VARCHAR(100) NOT NULL,
    template_description TEXT,
    template_type VARCHAR(30), -- RECURRING, ADJUSTING, CLOSING, etc.
    is_active BOOLEAN DEFAULT TRUE
);

CREATE TABLE template_lines (
    template_line_id INTEGER PRIMARY KEY AUTOINCREMENT,
    template_id INTEGER NOT NULL,
    line_number INTEGER NOT NULL,
    account_id INTEGER NOT NULL,
    description VARCHAR(200),
    debit_amount DECIMAL(15,2) DEFAULT 0,
    credit_amount DECIMAL(15,2) DEFAULT 0,
    is_variable_amount BOOLEAN DEFAULT FALSE, -- If amount needs to be entered
    FOREIGN KEY (template_id) REFERENCES entry_templates(template_id) ON DELETE CASCADE,
    FOREIGN KEY (account_id) REFERENCES chart_of_accounts(account_id)
);

-- Audit Trail
CREATE TABLE audit_trail (
    audit_id INTEGER PRIMARY KEY AUTOINCREMENT,
    table_name VARCHAR(50) NOT NULL,
    record_id INTEGER NOT NULL,
    action VARCHAR(10) NOT NULL, -- INSERT, UPDATE, DELETE
    old_values TEXT, -- JSON of old values
    new_values TEXT, -- JSON of new values
    changed_by VARCHAR(50) NOT NULL,
    change_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX idx_journal_entries_date ON journal_entries(entry_date);
CREATE INDEX idx_journal_entries_posted ON journal_entries(is_posted);
CREATE INDEX idx_journal_entry_lines_entry ON journal_entry_lines(entry_id);
CREATE INDEX idx_journal_entry_lines_account ON journal_entry_lines(account_id);
CREATE INDEX idx_error_detection_entry ON error_detection_log(entry_id);
CREATE INDEX idx_error_detection_resolved ON error_detection_log(is_resolved);
CREATE INDEX idx_account_balances_date ON account_balances(balance_date);
CREATE INDEX idx_chart_of_accounts_type ON chart_of_accounts(account_type);
CREATE INDEX idx_audit_trail_date ON audit_trail(change_date);

-- Create views for common queries
CREATE VIEW trial_balance AS
SELECT 
    coa.account_code,
    coa.account_name,
    coa.account_type,
    coa.normal_balance,
    COALESCE(SUM(jel.debit_amount), 0) as total_debits,
    COALESCE(SUM(jel.credit_amount), 0) as total_credits,
    CASE 
        WHEN coa.normal_balance = 'DEBIT' THEN 
            COALESCE(SUM(jel.debit_amount), 0) - COALESCE(SUM(jel.credit_amount), 0)
        ELSE 
            COALESCE(SUM(jel.credit_amount), 0) - COALESCE(SUM(jel.debit_amount), 0)
    END as balance
FROM chart_of_accounts coa
LEFT JOIN journal_entry_lines jel ON coa.account_id = jel.account_id
LEFT JOIN journal_entries je ON jel.entry_id = je.entry_id AND je.is_posted = TRUE
WHERE coa.is_active = TRUE
GROUP BY coa.account_id, coa.account_code, coa.account_name, coa.account_type, coa.normal_balance;

CREATE VIEW unresolved_errors AS
SELECT 
    edl.error_id,
    je.entry_number,
    je.entry_date,
    edl.error_type,
    edl.error_severity,
    edl.error_description,
    edl.suggested_correction,
    edl.detected_date
FROM error_detection_log edl
JOIN journal_entries je ON edl.entry_id = je.entry_id
WHERE edl.is_resolved = FALSE
ORDER BY edl.error_severity DESC, edl.detected_date DESC;

CREATE VIEW posting_summary AS
SELECT 
    DATE(je.entry_date) as posting_date,
    COUNT(*) as total_entries,
    SUM(je.total_debits) as total_debits,
    SUM(je.total_credits) as total_credits,
    COUNT(CASE WHEN je.is_posted = FALSE THEN 1 END) as unposted_entries,
    COUNT(DISTINCT edl.error_id) as total_errors
FROM journal_entries je
LEFT JOIN error_detection_log edl ON je.entry_id = edl.entry_id AND edl.is_resolved = FALSE
GROUP BY DATE(je.entry_date)
ORDER BY posting_date DESC;