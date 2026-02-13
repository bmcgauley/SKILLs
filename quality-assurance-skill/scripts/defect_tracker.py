#!/usr/bin/env python3
"""
Defect Tracker
Comprehensive defect lifecycle management system
"""

import json
import sqlite3
from datetime import datetime
import argparse
from typing import List, Dict, Optional
from enum import Enum

class DefectSeverity(Enum):
    """Defect severity levels"""
    CRITICAL = 1  # System crash, data loss, security breach
    MAJOR = 2     # Major functionality broken, workaround difficult
    MODERATE = 3  # Functionality impaired, workaround exists
    MINOR = 4     # Cosmetic, UI, minor inconvenience
    TRIVIAL = 5   # Suggestion, enhancement

class DefectStatus(Enum):
    """Defect lifecycle states"""
    NEW = "New"
    OPEN = "Open"
    ASSIGNED = "Assigned"
    IN_PROGRESS = "In Progress"
    FIXED = "Fixed"
    VERIFIED = "Verified"
    CLOSED = "Closed"
    REOPENED = "Reopened"
    DEFERRED = "Deferred"
    REJECTED = "Rejected"

class DefectPriority(Enum):
    """Defect priority levels"""
    IMMEDIATE = 1  # Fix immediately
    HIGH = 2       # Fix in current iteration
    MEDIUM = 3     # Fix in next iteration
    LOW = 4        # Fix when time permits

class DefectTracker:
    """Manage defect lifecycle and tracking"""
    
    def __init__(self, db_path: str = "defects.db"):
        """Initialize defect tracker with database"""
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self._create_tables()
    
    def _create_tables(self):
        """Create database tables if they don't exist"""
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS defects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                severity INTEGER NOT NULL,
                priority INTEGER NOT NULL,
                status TEXT NOT NULL,
                module TEXT,
                found_by TEXT NOT NULL,
                assigned_to TEXT,
                found_date TEXT NOT NULL,
                fixed_date TEXT,
                verified_date TEXT,
                closed_date TEXT,
                environment TEXT,
                steps_to_reproduce TEXT,
                expected_result TEXT,
                actual_result TEXT,
                root_cause TEXT,
                resolution TEXT,
                test_case_id TEXT,
                build_version TEXT,
                attachments TEXT
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS defect_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                defect_id INTEGER NOT NULL,
                changed_by TEXT NOT NULL,
                change_date TEXT NOT NULL,
                field_changed TEXT,
                old_value TEXT,
                new_value TEXT,
                comment TEXT,
                FOREIGN KEY(defect_id) REFERENCES defects(id)
            )
        ''')
        
        self.conn.commit()
    
    def create_defect(self, title: str, description: str, 
                     severity: DefectSeverity, priority: DefectPriority,
                     found_by: str, module: str = None, **kwargs) -> int:
        """
        Create a new defect
        
        Args:
            title: Brief defect description
            description: Detailed description
            severity: Defect severity level
            priority: Fix priority
            found_by: Person who found the defect
            module: Component/module affected
            **kwargs: Additional defect fields
        
        Returns:
            Defect ID
        """
        found_date = datetime.now().isoformat()
        
        self.cursor.execute('''
            INSERT INTO defects (
                title, description, severity, priority, status,
                module, found_by, found_date, environment,
                steps_to_reproduce, expected_result, actual_result,
                test_case_id, build_version
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            title, description, severity.value, priority.value,
            DefectStatus.NEW.value, module, found_by, found_date,
            kwargs.get('environment'), kwargs.get('steps_to_reproduce'),
            kwargs.get('expected_result'), kwargs.get('actual_result'),
            kwargs.get('test_case_id'), kwargs.get('build_version')
        ))
        
        self.conn.commit()
        defect_id = self.cursor.lastrowid
        
        # Log creation in history
        self._log_change(defect_id, found_by, None, None, 
                        DefectStatus.NEW.value, "Defect created")
        
        return defect_id
    
    def update_status(self, defect_id: int, new_status: DefectStatus, 
                     changed_by: str, comment: str = None) -> bool:
        """Update defect status"""
        # Get current status
        self.cursor.execute('SELECT status FROM defects WHERE id = ?', (defect_id,))
        result = self.cursor.fetchone()
        
        if not result:
            return False
        
        old_status = result[0]
        
        # Update status and relevant dates
        update_query = 'UPDATE defects SET status = ?'
        params = [new_status.value]
        
        if new_status == DefectStatus.FIXED:
            update_query += ', fixed_date = ?'
            params.append(datetime.now().isoformat())
        elif new_status == DefectStatus.VERIFIED:
            update_query += ', verified_date = ?'
            params.append(datetime.now().isoformat())
        elif new_status == DefectStatus.CLOSED:
            update_query += ', closed_date = ?'
            params.append(datetime.now().isoformat())
        
        update_query += ' WHERE id = ?'
        params.append(defect_id)
        
        self.cursor.execute(update_query, params)
        self.conn.commit()
        
        # Log change
        self._log_change(defect_id, changed_by, 'status', 
                        old_status, new_status.value, comment)
        
        return True
    
    def assign_defect(self, defect_id: int, assignee: str, 
                     assigned_by: str, comment: str = None) -> bool:
        """Assign defect to someone"""
        self.cursor.execute('SELECT assigned_to, status FROM defects WHERE id = ?', 
                           (defect_id,))
        result = self.cursor.fetchone()
        
        if not result:
            return False
        
        old_assignee = result[0]
        
        # Update assignment and status if needed
        if result[1] == DefectStatus.NEW.value:
            new_status = DefectStatus.ASSIGNED.value
            self.cursor.execute('''
                UPDATE defects SET assigned_to = ?, status = ? WHERE id = ?
            ''', (assignee, new_status, defect_id))
        else:
            self.cursor.execute('UPDATE defects SET assigned_to = ? WHERE id = ?',
                              (assignee, defect_id))
        
        self.conn.commit()
        
        # Log change
        self._log_change(defect_id, assigned_by, 'assigned_to',
                        old_assignee, assignee, comment)
        
        return True
    
    def add_resolution(self, defect_id: int, resolution: str, 
                      root_cause: str = None, resolved_by: str = None) -> bool:
        """Add resolution details to defect"""
        self.cursor.execute('''
            UPDATE defects SET resolution = ?, root_cause = ? WHERE id = ?
        ''', (resolution, root_cause, defect_id))
        
        self.conn.commit()
        
        if resolved_by:
            self._log_change(defect_id, resolved_by, 'resolution',
                           None, resolution, f"Root cause: {root_cause}")
        
        return True
    
    def _log_change(self, defect_id: int, changed_by: str, 
                   field_changed: str = None, old_value: str = None,
                   new_value: str = None, comment: str = None):
        """Log defect change history"""
        self.cursor.execute('''
            INSERT INTO defect_history (
                defect_id, changed_by, change_date, field_changed,
                old_value, new_value, comment
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            defect_id, changed_by, datetime.now().isoformat(),
            field_changed, old_value, new_value, comment
        ))
        self.conn.commit()
    
    def search_defects(self, **criteria) -> List[Dict]:
        """
        Search defects by various criteria
        
        Args:
            **criteria: Search parameters (status, severity, priority, assigned_to, etc.)
        
        Returns:
            List of matching defects
        """
        query = 'SELECT * FROM defects WHERE 1=1'
        params = []
        
        if 'status' in criteria:
            query += ' AND status = ?'
            params.append(criteria['status'])
        
        if 'severity' in criteria:
            query += ' AND severity = ?'
            params.append(criteria['severity'])
        
        if 'priority' in criteria:
            query += ' AND priority = ?'
            params.append(criteria['priority'])
        
        if 'assigned_to' in criteria:
            query += ' AND assigned_to = ?'
            params.append(criteria['assigned_to'])
        
        if 'module' in criteria:
            query += ' AND module = ?'
            params.append(criteria['module'])
        
        self.cursor.execute(query, params)
        columns = [desc[0] for desc in self.cursor.description]
        
        results = []
        for row in self.cursor.fetchall():
            results.append(dict(zip(columns, row)))
        
        return results
    
    def get_metrics(self) -> Dict:
        """Calculate defect metrics"""
        metrics = {}
        
        # Total defects by status
        self.cursor.execute('''
            SELECT status, COUNT(*) FROM defects GROUP BY status
        ''')
        metrics['by_status'] = dict(self.cursor.fetchall())
        
        # Total defects by severity
        self.cursor.execute('''
            SELECT severity, COUNT(*) FROM defects GROUP BY severity
        ''')
        severity_counts = {}
        for sev, count in self.cursor.fetchall():
            severity_name = DefectSeverity(sev).name
            severity_counts[severity_name] = count
        metrics['by_severity'] = severity_counts
        
        # Total defects by priority
        self.cursor.execute('''
            SELECT priority, COUNT(*) FROM defects GROUP BY priority
        ''')
        priority_counts = {}
        for pri, count in self.cursor.fetchall():
            priority_name = DefectPriority(pri).name
            priority_counts[priority_name] = count
        metrics['by_priority'] = priority_counts
        
        # Average resolution time (for closed defects)
        self.cursor.execute('''
            SELECT AVG(
                julianday(closed_date) - julianday(found_date)
            ) FROM defects WHERE status = 'Closed' AND closed_date IS NOT NULL
        ''')
        result = self.cursor.fetchone()
        metrics['avg_resolution_days'] = round(result[0], 1) if result[0] else None
        
        # Defect density by module
        self.cursor.execute('''
            SELECT module, COUNT(*) FROM defects 
            WHERE module IS NOT NULL GROUP BY module
        ''')
        metrics['by_module'] = dict(self.cursor.fetchall())
        
        # Reopened defects
        self.cursor.execute('''
            SELECT COUNT(*) FROM defects WHERE status = 'Reopened'
        ''')
        metrics['reopened_count'] = self.cursor.fetchone()[0]
        
        return metrics
    
    def export_defects(self, format_type: str = 'json', 
                      status_filter: str = None) -> str:
        """Export defects in various formats"""
        # Get defects
        if status_filter:
            defects = self.search_defects(status=status_filter)
        else:
            defects = self.search_defects()
        
        if format_type == 'json':
            return json.dumps(defects, indent=2, default=str)
        
        elif format_type == 'csv':
            if not defects:
                return "No defects found"
            
            # CSV header
            output = ','.join(defects[0].keys()) + '\n'
            
            # CSV rows
            for defect in defects:
                values = [str(v) if v else '' for v in defect.values()]
                output += ','.join(f'"{v}"' for v in values) + '\n'
            
            return output
        
        elif format_type == 'markdown':
            output = "# Defect Report\n\n"
            output += f"**Total Defects:** {len(defects)}\n\n"
            
            if defects:
                output += "| ID | Title | Severity | Priority | Status | Assigned To |\n"
                output += "|-----|-------|----------|----------|--------|-------------|\n"
                
                for d in defects:
                    severity = DefectSeverity(d['severity']).name if d['severity'] else ''
                    priority = DefectPriority(d['priority']).name if d['priority'] else ''
                    output += f"| {d['id']} | {d['title']} | {severity} | "
                    output += f"{priority} | {d['status']} | {d.get('assigned_to', '')} |\n"
            
            return output
        
        else:  # text format
            output = "DEFECT LIST\n" + "=" * 50 + "\n\n"
            for d in defects:
                output += f"ID: {d['id']}\n"
                output += f"Title: {d['title']}\n"
                output += f"Severity: {DefectSeverity(d['severity']).name}\n"
                output += f"Status: {d['status']}\n"
                output += "-" * 30 + "\n"
            
            return output
    
    def close(self):
        """Close database connection"""
        self.conn.close()

def main():
    parser = argparse.ArgumentParser(description='Track and manage defects')
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Create defect
    create_parser = subparsers.add_parser('create', help='Create new defect')
    create_parser.add_argument('title', help='Defect title')
    create_parser.add_argument('-d', '--description', help='Detailed description')
    create_parser.add_argument('-s', '--severity', type=int, choices=[1,2,3,4,5],
                             default=3, help='Severity (1=Critical, 5=Trivial)')
    create_parser.add_argument('-p', '--priority', type=int, choices=[1,2,3,4],
                             default=3, help='Priority (1=Immediate, 4=Low)')
    create_parser.add_argument('-m', '--module', help='Affected module')
    create_parser.add_argument('-f', '--found-by', required=True, help='Reporter name')
    
    # Update status
    status_parser = subparsers.add_parser('status', help='Update defect status')
    status_parser.add_argument('defect_id', type=int, help='Defect ID')
    status_parser.add_argument('new_status', choices=['Open', 'Fixed', 'Verified', 'Closed'],
                              help='New status')
    status_parser.add_argument('-u', '--user', required=True, help='User making change')
    
    # Search defects
    search_parser = subparsers.add_parser('search', help='Search defects')
    search_parser.add_argument('-s', '--status', help='Filter by status')
    search_parser.add_argument('--severity', type=int, help='Filter by severity')
    search_parser.add_argument('-a', '--assigned-to', help='Filter by assignee')
    
    # Get metrics
    metrics_parser = subparsers.add_parser('metrics', help='Get defect metrics')
    
    # Export defects
    export_parser = subparsers.add_parser('export', help='Export defects')
    export_parser.add_argument('-f', '--format', choices=['json', 'csv', 'markdown', 'text'],
                              default='markdown', help='Export format')
    export_parser.add_argument('-s', '--status', help='Filter by status')
    
    args = parser.parse_args()
    
    tracker = DefectTracker()
    
    if args.command == 'create':
        defect_id = tracker.create_defect(
            args.title,
            args.description or args.title,
            DefectSeverity(args.severity),
            DefectPriority(args.priority),
            args.found_by,
            args.module
        )
        print(f"Created defect ID: {defect_id}")
    
    elif args.command == 'status':
        status = DefectStatus[args.new_status.upper()]
        if tracker.update_status(args.defect_id, status, args.user):
            print(f"Updated defect {args.defect_id} to {args.new_status}")
        else:
            print(f"Failed to update defect {args.defect_id}")
    
    elif args.command == 'search':
        criteria = {}
        if args.status:
            criteria['status'] = args.status
        if args.severity:
            criteria['severity'] = args.severity
        if args.assigned_to:
            criteria['assigned_to'] = args.assigned_to
        
        defects = tracker.search_defects(**criteria)
        print(f"Found {len(defects)} defects")
        for d in defects:
            print(f"  ID {d['id']}: {d['title']} ({d['status']})")
    
    elif args.command == 'metrics':
        metrics = tracker.get_metrics()
        print(json.dumps(metrics, indent=2))
    
    elif args.command == 'export':
        output = tracker.export_defects(args.format, args.status)
        print(output)
    
    else:
        parser.print_help()
    
    tracker.close()

if __name__ == "__main__":
    main()
