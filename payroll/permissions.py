"""
Payroll Permission Management System

This module defines the permission structure and access control for the payroll system.
It provides level-based permissions and manual permission override capabilities.
"""


class PayrollPermissionManager:
    """Manages payroll permissions and feature access"""

    # Define all payroll features
    PAYROLL_FEATURES = [
        # PayrollOrg Management
        ('payrollorg', 'create', 'Can Create Payroll Organization'),
        ('payrollorg', 'read', 'Can View Payroll Organization'),
        ('payrollorg', 'update', 'Can Update Payroll Organization'),
        ('payrollorg', 'delete', 'Can Delete Payroll Organization'),

        # Work Locations
        ('worklocations', 'create', 'Can Create Work Locations'),
        ('worklocations', 'read', 'Can View Work Locations'),
        ('worklocations', 'update', 'Can Update Work Locations'),
        ('worklocations', 'delete', 'Can Delete Work Locations'),

        # Departments
        ('departments', 'create', 'Can Create Departments'),
        ('departments', 'read', 'Can View Departments'),
        ('departments', 'update', 'Can Update Departments'),
        ('departments', 'delete', 'Can Delete Departments'),

        # Designations
        ('designation', 'create', 'Can Create Designations'),
        ('designation', 'read', 'Can View Designations'),
        ('designation', 'update', 'Can Update Designations'),
        ('designation', 'delete', 'Can Delete Designations'),

        # Statutory Components
        ('epf', 'create', 'Can Create EPF Details'),
        ('epf', 'read', 'Can View EPF Details'),
        ('epf', 'update', 'Can Update EPF Details'),
        ('epf', 'delete', 'Can Delete EPF Details'),
        ('esi', 'create', 'Can Create ESI Details'),
        ('esi', 'read', 'Can View ESI Details'),
        ('esi', 'update', 'Can Update ESI Details'),
        ('esi', 'delete', 'Can Delete ESI Details'),
        ('pt', 'create', 'Can Create Professional Tax'),
        ('pt', 'read', 'Can View Professional Tax'),
        ('pt', 'update', 'Can Update Professional Tax'),
        ('pt', 'delete', 'Can Delete Professional Tax'),

        # Salary Components
        ('earnings', 'create', 'Can Create Earnings'),
        ('earnings', 'read', 'Can View Earnings'),
        ('earnings', 'update', 'Can Update Earnings'),
        ('earnings', 'delete', 'Can Delete Earnings'),
        ('benefits', 'create', 'Can Create Benefits'),
        ('benefits', 'read', 'Can View Benefits'),
        ('benefits', 'update', 'Can Update Benefits'),
        ('benefits', 'delete', 'Can Delete Benefits'),
        ('deduction', 'create', 'Can Create Deductions'),
        ('deduction', 'read', 'Can View Deductions'),
        ('deduction', 'update', 'Can Update Deductions'),
        ('deduction', 'delete', 'Can Delete Deductions'),
        ('reimbursement', 'create', 'Can Create Reimbursements'),
        ('reimbursement', 'read', 'Can View Reimbursements'),
        ('reimbursement', 'update', 'Can Update Reimbursements'),
        ('reimbursement', 'delete', 'Can Delete Reimbursements'),

        # Salary Templates
        ('salarytemplate', 'create', 'Can Create Salary Templates'),
        ('salarytemplate', 'read', 'Can View Salary Templates'),
        ('salarytemplate', 'update', 'Can Update Salary Templates'),
        ('salarytemplate', 'delete', 'Can Delete Salary Templates'),

        # Leave & Holiday Management
        ('leavemanagement', 'create', 'Can Create Leave Policies'),
        ('leavemanagement', 'read', 'Can View Leave Policies'),
        ('leavemanagement', 'update', 'Can Update Leave Policies'),
        ('leavemanagement', 'delete', 'Can Delete Leave Policies'),
        ('holidaymanagement', 'create', 'Can Create Holidays'),
        ('holidaymanagement', 'read', 'Can View Holidays'),
        ('holidaymanagement', 'update', 'Can Update Holidays'),
        ('holidaymanagement', 'delete', 'Can Delete Holidays'),

        # Employee Management
        ('employeemanagement', 'create', 'Can Create Employees'),
        ('employeemanagement', 'read', 'Can View Employees'),
        ('employeemanagement', 'update', 'Can Update Employees'),
        ('employeemanagement', 'delete', 'Can Delete Employees'),
        ('employeereportingmanager', 'create', 'Can Create Reporting Managers'),
        ('employeereportingmanager', 'read', 'Can View Reporting Managers'),
        ('employeereportingmanager', 'update', 'Can Update Reporting Managers'),
        ('employeereportingmanager', 'delete', 'Can Delete Reporting Managers'),

        # Employee Data
        ('employeeleavebalance', 'create', 'Can Create Leave Balances'),
        ('employeeleavebalance', 'read', 'Can View Leave Balances'),
        ('employeeleavebalance', 'update', 'Can Update Leave Balances'),
        ('employeeleavebalance', 'delete', 'Can Delete Leave Balances'),
        ('employeesalarydetails', 'create', 'Can Create Salary Details'),
        ('employeesalarydetails', 'read', 'Can View Salary Details'),
        ('employeesalarydetails', 'update', 'Can Update Salary Details'),
        ('employeesalarydetails', 'delete', 'Can Delete Salary Details'),
        ('employeesalaryrevisionhistory', 'create', 'Can Create Salary Revisions'),
        ('employeesalaryrevisionhistory', 'read', 'Can View Salary Revisions'),
        ('employeesalaryrevisionhistory', 'update', 'Can Update Salary Revisions'),
        ('employeesalaryrevisionhistory', 'delete', 'Can Delete Salary Revisions'),
        ('employeepersonaldetails', 'create', 'Can Create Personal Details'),
        ('employeepersonaldetails', 'read', 'Can View Personal Details'),
        ('employeepersonaldetails', 'update', 'Can Update Personal Details'),
        ('employeepersonaldetails', 'delete', 'Can Delete Personal Details'),
        ('employeebankdetails', 'create', 'Can Create Bank Details'),
        ('employeebankdetails', 'read', 'Can View Bank Details'),
        ('employeebankdetails', 'update', 'Can Update Bank Details'),
        ('employeebankdetails', 'delete', 'Can Delete Bank Details'),
        ('employeeeducationdetails', 'create', 'Can Create Education Details'),
        ('employeeeducationdetails', 'read', 'Can View Education Details'),
        ('employeeeducationdetails', 'update', 'Can Update Education Details'),
        ('employeeeducationdetails', 'delete', 'Can Delete Education Details'),

        # Employee Exit
        ('employeeexit', 'create', 'Can Create Employee Exit'),
        ('employeeexit', 'read', 'Can View Employee Exit'),
        ('employeeexit', 'update', 'Can Update Employee Exit'),
        ('employeeexit', 'delete', 'Can Delete Employee Exit'),

        # Loans & Advances
        ('advanceloan', 'create', 'Can Create Advance Loans'),
        ('advanceloan', 'read', 'Can View Advance Loans'),
        ('advanceloan', 'update', 'Can Update Advance Loans'),
        ('advanceloan', 'delete', 'Can Delete Advance Loans'),

        # Bonuses & Incentives
        ('bonusincentive', 'create', 'Can Create Bonuses'),
        ('bonusincentive', 'read', 'Can View Bonuses'),
        ('bonusincentive', 'update', 'Can Update Bonuses'),
        ('bonusincentive', 'delete', 'Can Delete Bonuses'),

        # Attendance
        ('employeeattendance', 'create', 'Can Create Attendance'),
        ('employeeattendance', 'read', 'Can View Attendance'),
        ('employeeattendance', 'update', 'Can Update Attendance'),
        ('employeeattendance', 'delete', 'Can Delete Attendance'),
        ('attendancelog', 'create', 'Can Create Attendance Logs'),
        ('attendancelog', 'read', 'Can View Attendance Logs'),
        ('attendancelog', 'update', 'Can Update Attendance Logs'),
        ('attendancelog', 'delete', 'Can Delete Attendance Logs'),
        ('attendancegeotag', 'create', 'Can Create Geo Tags'),
        ('attendancegeotag', 'read', 'Can View Geo Tags'),
        ('attendancegeotag', 'update', 'Can Update Geo Tags'),
        ('attendancegeotag', 'delete', 'Can Delete Geo Tags'),
        ('employeefacerecognition', 'create', 'Can Create Face Recognition'),
        ('employeefacerecognition', 'read', 'Can View Face Recognition'),
        ('employeefacerecognition', 'update', 'Can Update Face Recognition'),
        ('employeefacerecognition', 'delete', 'Can Delete Face Recognition'),

        # Salary History & Processing
        ('employeesalaryhistory', 'create', 'Can Create Salary History'),
        ('employeesalaryhistory', 'read', 'Can View Salary History'),
        ('employeesalaryhistory', 'update', 'Can Update Salary History'),
        ('employeesalaryhistory', 'delete', 'Can Delete Salary History'),

        # Payroll Workflow
        ('payrollworkflow', 'create', 'Can Create Payroll Workflow'),
        ('payrollworkflow', 'read', 'Can View Payroll Workflow'),
        ('payrollworkflow', 'update', 'Can Update Payroll Workflow'),
        ('payrollworkflow', 'delete', 'Can Delete Payroll Workflow'),

        # Leave Applications
        ('leaveapplication', 'create', 'Can Create Leave Applications'),
        ('leaveapplication', 'read', 'Can View Leave Applications'),
        ('leaveapplication', 'update', 'Can Update Leave Applications'),
        ('leaveapplication', 'delete', 'Can Delete Leave Applications'),
        ('leavenotification', 'create', 'Can Create Leave Notifications'),
        ('leavenotification', 'read', 'Can View Leave Notifications'),
        ('leavenotification', 'update', 'Can Update Leave Notifications'),
        ('leavenotification', 'delete', 'Can Delete Leave Notifications'),

        # Events
        ('eventmanagement', 'create', 'Can Create Events'),
        ('eventmanagement', 'read', 'Can View Events'),
        ('eventmanagement', 'update', 'Can Update Events'),
        ('eventmanagement', 'delete', 'Can Delete Events'),

        # Employee Credentials
        ('employeecredentials', 'create', 'Can Create Employee Credentials'),
        ('employeecredentials', 'read', 'Can View Employee Credentials'),
        ('employeecredentials', 'update', 'Can Update Employee Credentials'),
        ('employeecredentials', 'delete', 'Can Delete Employee Credentials'),

        # Special Actions
        ('payroll', 'process', 'Can Process Payroll'),
        ('payroll', 'finalize', 'Can Finalize Payroll'),
        ('payroll', 'lock', 'Can Lock Payroll'),
        ('payroll', 'unlock', 'Can Unlock Payroll'),
        ('salary', 'calculate', 'Can Calculate Salary'),
        ('payslip', 'generate', 'Can Generate Payslips'),
        ('payslip', 'send', 'Can Send Payslips'),
        ('reports', 'generate', 'Can Generate Reports'),
        ('reports', 'export', 'Can Export Reports'),
        ('analytics', 'view', 'Can View Analytics'),
        ('bulk', 'upload_employees', 'Can Bulk Upload Employees'),
        ('bulk', 'upload_salary', 'Can Bulk Upload Salary'),
        ('bulk', 'upload_attendance', 'Can Bulk Upload Attendance'),
        ('bulk', 'update_employees', 'Can Bulk Update Employees'),
        ('bulk', 'delete_employees', 'Can Bulk Delete Employees'),
        ('system', 'manage_permissions', 'Can Manage Permissions'),
        ('system', 'manage_roles', 'Can Manage Roles'),
        ('system', 'settings', 'Can Manage System Settings'),
        ('system', 'backup', 'Can Backup Data'),

        # Self-service actions
        ('own_profile', 'read', 'Can View Own Profile'),
        ('own_profile', 'update', 'Can Update Own Profile'),
        ('own_attendance', 'read', 'Can View Own Attendance'),
        ('own_leave', 'read', 'Can View Own Leave'),
        ('own_leave', 'create', 'Can Apply for Leave'),
        ('own_salary', 'read', 'Can View Own Salary'),
        ('own_payslip', 'read', 'Can View Own Payslip'),
        ('own_payslip', 'export', 'Can Download Own Payslip'),
        ('password', 'change', 'Can Change Own Password'),
        ('password', 'reset', 'Can Reset Password'),
    ]

    # Feature access by employee level
    FEATURE_ACCESS_BY_LEVEL = {
        '0': [  # CEO/Director/Executive - All features
            'payrollorg.create', 'payrollorg.read', 'payrollorg.update', 'payrollorg.delete',
            'worklocations.create', 'worklocations.read', 'worklocations.update', 'worklocations.delete',
            'departments.create', 'departments.read', 'departments.update', 'departments.delete',
            'designation.create', 'designation.read', 'designation.update', 'designation.delete',
            'epf.create', 'epf.read', 'epf.update', 'epf.delete',
            'esi.create', 'esi.read', 'esi.update', 'esi.delete',
            'pt.create', 'pt.read', 'pt.update', 'pt.delete',
            'earnings.create', 'earnings.read', 'earnings.update', 'earnings.delete',
            'benefits.create', 'benefits.read', 'benefits.update', 'benefits.delete',
            'deduction.create', 'deduction.read', 'deduction.update', 'deduction.delete',
            'reimbursement.create', 'reimbursement.read', 'reimbursement.update', 'reimbursement.delete',
            'salarytemplate.create', 'salarytemplate.read', 'salarytemplate.update', 'salarytemplate.delete',
            'leavemanagement.create', 'leavemanagement.read', 'leavemanagement.update', 'leavemanagement.delete',
            'holidaymanagement.create', 'holidaymanagement.read', 'holidaymanagement.update',
            'holidaymanagement.delete',
            'employeemanagement.create', 'employeemanagement.read', 'employeemanagement.update',
            'employeemanagement.delete',
            'employeereportingmanager.create', 'employeereportingmanager.read', 'employeereportingmanager.update',
            'employeereportingmanager.delete',
            'employeeleavebalance.create', 'employeeleavebalance.read', 'employeeleavebalance.update',
            'employeeleavebalance.delete',
            'employeesalarydetails.create', 'employeesalarydetails.read', 'employeesalarydetails.update',
            'employeesalarydetails.delete',
            'employeesalaryrevisionhistory.create', 'employeesalaryrevisionhistory.read',
            'employeesalaryrevisionhistory.update', 'employeesalaryrevisionhistory.delete',
            'employeepersonaldetails.create', 'employeepersonaldetails.read', 'employeepersonaldetails.update',
            'employeepersonaldetails.delete',
            'employeebankdetails.create', 'employeebankdetails.read', 'employeebankdetails.update',
            'employeebankdetails.delete',
            'employeeeducationdetails.create', 'employeeeducationdetails.read', 'employeeeducationdetails.update',
            'employeeeducationdetails.delete',
            'employeeexit.create', 'employeeexit.read', 'employeeexit.update', 'employeeexit.delete',
            'advanceloan.create', 'advanceloan.read', 'advanceloan.update', 'advanceloan.delete',
            'bonusincentive.create', 'bonusincentive.read', 'bonusincentive.update', 'bonusincentive.delete',
            'employeeattendance.create', 'employeeattendance.read', 'employeeattendance.update',
            'employeeattendance.delete',
            'attendancelog.create', 'attendancelog.read', 'attendancelog.update', 'attendancelog.delete',
            'attendancegeotag.create', 'attendancegeotag.read', 'attendancegeotag.update', 'attendancegeotag.delete',
            'employeefacerecognition.create', 'employeefacerecognition.read', 'employeefacerecognition.update',
            'employeefacerecognition.delete',
            'employeesalaryhistory.create', 'employeesalaryhistory.read', 'employeesalaryhistory.update',
            'employeesalaryhistory.delete',
            'payrollworkflow.create', 'payrollworkflow.read', 'payrollworkflow.update', 'payrollworkflow.delete',
            'leaveapplication.create', 'leaveapplication.read', 'leaveapplication.update', 'leaveapplication.delete',
            'leavenotification.create', 'leavenotification.read', 'leavenotification.update',
            'leavenotification.delete',
            'eventmanagement.create', 'eventmanagement.read', 'eventmanagement.update', 'eventmanagement.delete',
            'employeecredentials.create', 'employeecredentials.read', 'employeecredentials.update',
            'employeecredentials.delete',
            'payroll.process', 'payroll.finalize', 'payroll.lock', 'payroll.unlock',
            'salary.calculate', 'payslip.generate', 'payslip.send',
            'reports.generate', 'reports.export', 'analytics.view',
            'bulk.upload_employees', 'bulk.upload_salary', 'bulk.upload_attendance',
            'bulk.update_employees', 'bulk.delete_employees',
            'system.manage_permissions', 'system.manage_roles', 'system.settings', 'system.backup',
            'own_profile.read', 'own_profile.update', 'own_attendance.read', 'own_leave.read', 'own_leave.create',
            'own_salary.read', 'own_payslip.read', 'own_payslip.export', 'password.change', 'password.reset'
        ],
        '1': [  # VP/General Manager - High access
            'payrollorg.read', 'payrollorg.update',
            'worklocations.create', 'worklocations.read', 'worklocations.update', 'worklocations.delete',
            'departments.create', 'departments.read', 'departments.update', 'departments.delete',
            'designation.create', 'designation.read', 'designation.update', 'designation.delete',
            'epf.read', 'epf.update', 'esi.read', 'esi.update', 'pt.read', 'pt.update',
            'earnings.create', 'earnings.read', 'earnings.update', 'earnings.delete',
            'benefits.create', 'benefits.read', 'benefits.update', 'benefits.delete',
            'deduction.create', 'deduction.read', 'deduction.update', 'deduction.delete',
            'reimbursement.create', 'reimbursement.read', 'reimbursement.update', 'reimbursement.delete',
            'salarytemplate.create', 'salarytemplate.read', 'salarytemplate.update', 'salarytemplate.delete',
            'leavemanagement.create', 'leavemanagement.read', 'leavemanagement.update', 'leavemanagement.delete',
            'holidaymanagement.create', 'holidaymanagement.read', 'holidaymanagement.update',
            'holidaymanagement.delete',
            'employeemanagement.create', 'employeemanagement.read', 'employeemanagement.update',
            'employeereportingmanager.create', 'employeereportingmanager.read', 'employeereportingmanager.update',
            'employeeleavebalance.read', 'employeeleavebalance.update',
            'employeesalarydetails.read', 'employeesalarydetails.update',
            'employeesalaryrevisionhistory.create', 'employeesalaryrevisionhistory.read',
            'employeesalaryrevisionhistory.update',
            'employeepersonaldetails.read', 'employeepersonaldetails.update',
            'employeebankdetails.read', 'employeebankdetails.update',
            'employeeeducationdetails.read', 'employeeeducationdetails.update',
            'employeeexit.create', 'employeeexit.read', 'employeeexit.update',
            'advanceloan.create', 'advanceloan.read', 'advanceloan.update',
            'bonusincentive.create', 'bonusincentive.read', 'bonusincentive.update',
            'employeeattendance.read', 'employeeattendance.update',
            'attendancelog.read', 'attendancelog.update',
            'attendancegeotag.read', 'attendancegeotag.update',
            'employeesalaryhistory.read', 'employeesalaryhistory.update',
            'payrollworkflow.read', 'payrollworkflow.update',
            'leaveapplication.read', 'leaveapplication.update',
            'leavenotification.read', 'leavenotification.update',
            'eventmanagement.create', 'eventmanagement.read', 'eventmanagement.update',
            'reports.generate', 'reports.export', 'analytics.view',
            'payroll.process', 'salary.calculate', 'payslip.generate',
            'bulk.upload_employees', 'bulk.upload_salary', 'bulk.upload_attendance',
            'own_profile.read', 'own_profile.update', 'own_attendance.read', 'own_leave.read', 'own_leave.create',
            'own_salary.read', 'own_payslip.read', 'own_payslip.export', 'password.change', 'password.reset'
        ],
        '2': [  # HR Manager - HR focused access
            'payrollorg.read',
            'worklocations.create', 'worklocations.read', 'worklocations.update',
            'departments.create', 'departments.read', 'departments.update',
            'designation.create', 'designation.read', 'designation.update',
            'epf.read', 'epf.update', 'esi.read', 'esi.update', 'pt.read', 'pt.update',
            'earnings.create', 'earnings.read', 'earnings.update',
            'benefits.create', 'benefits.read', 'benefits.update',
            'deduction.create', 'deduction.read', 'deduction.update',
            'reimbursement.create', 'reimbursement.read', 'reimbursement.update',
            'salarytemplate.create', 'salarytemplate.read', 'salarytemplate.update',
            'leavemanagement.create', 'leavemanagement.read', 'leavemanagement.update', 'leavemanagement.delete',
            'holidaymanagement.create', 'holidaymanagement.read', 'holidaymanagement.update',
            'holidaymanagement.delete',
            'employeemanagement.create', 'employeemanagement.read', 'employeemanagement.update',
            'employeemanagement.delete',
            'employeereportingmanager.create', 'employeereportingmanager.read', 'employeereportingmanager.update',
            'employeeleavebalance.create', 'employeeleavebalance.read', 'employeeleavebalance.update',
            'employeesalarydetails.create', 'employeesalarydetails.read', 'employeesalarydetails.update',
            'employeesalaryrevisionhistory.create', 'employeesalaryrevisionhistory.read',
            'employeesalaryrevisionhistory.update',
            'employeepersonaldetails.create', 'employeepersonaldetails.read', 'employeepersonaldetails.update',
            'employeebankdetails.create', 'employeebankdetails.read', 'employeebankdetails.update',
            'employeeeducationdetails.create', 'employeeeducationdetails.read', 'employeeeducationdetails.update',
            'employeeexit.create', 'employeeexit.read', 'employeeexit.update',
            'leaveapplication.create', 'leaveapplication.read', 'leaveapplication.update', 'leaveapplication.delete',
            'leavenotification.create', 'leavenotification.read', 'leavenotification.update',
            'employeeattendance.read', 'employeeattendance.update',
            'attendancelog.read', 'attendancelog.update',
            'reports.generate', 'reports.export',
            'bulk.upload_employees', 'bulk.upload_salary',
            'own_profile.read', 'own_profile.update', 'own_attendance.read', 'own_leave.read', 'own_leave.create',
            'own_salary.read', 'own_payslip.read', 'own_payslip.export', 'password.change', 'password.reset'
        ],
        '3': [  # Department Manager - Department focused
            'payrollorg.read', 'worklocations.read', 'departments.read', 'designation.read',
            'employeemanagement.read', 'employeemanagement.update',
            'employeereportingmanager.read', 'employeereportingmanager.update',
            'employeeleavebalance.read', 'employeeleavebalance.update',
            'employeesalarydetails.read', 'employeesalarydetails.update',
            'employeepersonaldetails.read', 'employeepersonaldetails.update',
            'employeebankdetails.read', 'employeebankdetails.update',
            'employeeeducationdetails.read', 'employeeeducationdetails.update',
            'leavemanagement.read', 'holidaymanagement.read',
            'leaveapplication.read', 'leaveapplication.update',
            'leavenotification.read', 'leavenotification.update',
            'employeeattendance.read', 'employeeattendance.update',
            'attendancelog.read', 'attendancelog.update',
            'employeesalaryhistory.read', 'reports.generate',
            'earnings.read', 'benefits.read', 'deduction.read', 'reimbursement.read',
            'salarytemplate.read', 'epf.read', 'esi.read', 'pt.read',
            'own_profile.read', 'own_profile.update', 'own_attendance.read', 'own_leave.read', 'own_leave.create',
            'own_salary.read', 'own_payslip.read', 'own_payslip.export', 'password.change', 'password.reset'
        ],
        '4': [  # Team Lead - Limited management
            'employeemanagement.read', 'worklocations.read', 'departments.read', 'designation.read',
            'employeeleavebalance.read', 'employeeleavebalance.update',
            'employeepersonaldetails.read', 'employeepersonaldetails.update',
            'leavemanagement.read', 'holidaymanagement.read',
            'leaveapplication.read', 'leaveapplication.update',
            'leavenotification.read', 'leavenotification.update',
            'employeeattendance.read', 'employeeattendance.update',
            'attendancelog.read', 'attendancelog.update',
            'earnings.read', 'benefits.read', 'deduction.read', 'reimbursement.read',
            'salarytemplate.read', 'epf.read', 'esi.read', 'pt.read',
            'employeesalarydetails.read', 'employeesalaryhistory.read',
            'own_profile.read', 'own_profile.update', 'own_attendance.read', 'own_leave.read', 'own_leave.create',
            'own_salary.read', 'own_payslip.read', 'own_payslip.export', 'password.change', 'password.reset'
        ],
        '5': [  # Employee/Trainee - Self-service only
            'own_profile.read', 'own_profile.update',
            'own_attendance.read', 'own_leave.read', 'own_leave.create',
            'own_salary.read', 'own_payslip.read', 'own_payslip.export',
            'password.change', 'password.reset'
        ]
    }

    @classmethod
    def get_permissions_for_level(cls, level):
        """Get permissions for a specific employee level"""
        return cls.FEATURE_ACCESS_BY_LEVEL.get(str(level), cls.FEATURE_ACCESS_BY_LEVEL['5'])

    @classmethod
    def get_all_features(cls):
        """Get all available payroll features"""
        return cls.PAYROLL_FEATURES

    @classmethod
    def get_levels(cls):
        """Get all available employee levels"""
        return list(cls.FEATURE_ACCESS_BY_LEVEL.keys())

    @classmethod
    def validate_permissions(cls, permissions):
        """Validate if the given permissions are valid"""
        valid_permissions = set()
        for service, action, _ in cls.PAYROLL_FEATURES:
            valid_permissions.add(f"{service}.{action}")

        invalid_permissions = set(permissions) - valid_permissions
        if invalid_permissions:
            raise ValueError(f"Invalid permissions: {invalid_permissions}")

        return True

    @classmethod
    def get_permission_description(cls, permission):
        """Get description for a specific permission"""
        service, action = permission.split('.', 1)
        for s, a, desc in cls.PAYROLL_FEATURES:
            if s == service and a == action:
                return desc
        return f"Unknown permission: {permission}"
