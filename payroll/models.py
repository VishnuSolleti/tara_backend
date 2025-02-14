from django.db import models
from django.core.exceptions import ValidationError
from djongo.models import ArrayField, EmbeddedField, JSONField
from user_management.models import *


def validate_pincode(value):
    if len(str(value)) != 6:  # Assuming 6-digit pin codes
        raise ValidationError(f"{value} is not a valid pin code.")


class PayrollOrg(models.Model):
    business = models.OneToOneField(Business, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)  # Use auto_now_add for creation timestamp
    logo = models.CharField(max_length=200, null=True, blank=True)
    contact_email = models.EmailField(max_length=120, null=True, blank=True)
    sender_email = models.EmailField(max_length=120, null=True, blank=True)
    filling_address_line1 = models.CharField(max_length=150, null=True, blank=True)
    filling_address_line2 = models.CharField(max_length=150, null=True, blank=True)
    filling_address_state = models.CharField(max_length=150, null=True, blank=True)
    filling_address_city = models.CharField(max_length=150, null=True, blank=True)
    filling_address_pincode = models.PositiveIntegerField(null=True, validators=[validate_pincode]) # No max_length
    work_location = models.BooleanField(default=False)
    department = models.BooleanField(default=False)
    designation = models.BooleanField(default=False)
    # JSONFields should have a default empty dictionary
    statutory_component = models.BooleanField(default=False)
    salary_component = models.BooleanField(default=False)
    industry = models.CharField(max_length=150, null=False, blank=False)

    def __str__(self):
        return f"PayrollOrg {self.business.id}"


class WorkLocations(models.Model):
    payroll = models.ForeignKey('PayrollOrg', on_delete=models.CASCADE, related_name='work_locations')
    created_at = models.DateTimeField(auto_now_add=True)
    location_name = models.CharField(max_length=120)
    address_line1 = models.CharField(max_length=150, null=True, blank=True)
    address_line2 = models.CharField(max_length=150, null=True, blank=True)
    address_state = models.CharField(max_length=150, null=True, blank=True)
    address_city = models.CharField(max_length=150, null=True, blank=True)
    address_pincode = models.PositiveIntegerField(null=True, validators=[validate_pincode])

    class Meta:
        unique_together = ('payroll', 'location_name')

    def __str__(self):
        return self.location_name


class Departments(models.Model):
    payroll = models.ForeignKey('PayrollOrg', on_delete=models.CASCADE, related_name='departments')
    dept_code = models.CharField(max_length=150)
    dept_name = models.CharField(max_length=150)
    description = models.CharField(max_length=220, null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['payroll', 'dept_code'], name='unique_dept_code_per_payroll'),
            models.UniqueConstraint(fields=['payroll', 'dept_name'], name='unique_dept_name_per_payroll'),
        ]

    def __str__(self):
        return f"{self.dept_name} ({self.dept_code})"


class Designation(models.Model):
    payroll = models.ForeignKey('PayrollOrg', on_delete=models.CASCADE, related_name='designations')
    designation_name = models.CharField(max_length=150)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['payroll', 'designation_name'], name='unique_designation_per_payroll'),
        ]

    def __str__(self):
        return self.designation_name


class EPF(models.Model):
    payroll = models.OneToOneField('PayrollOrg', on_delete=models.CASCADE, related_name='epf_details')
    epf_number = models.CharField(max_length=100)  # Adjust max_length as needed
    employee_contribution_rate = models.CharField(max_length=240, null=False, blank=False)
    employer_contribution_rate = models.CharField(max_length=240, null=False, blank=False)
    employer_edil_contribution_in_ctc = models.BooleanField()  # EDLI contribution included
    # in CTC Employees' Deposit Linked Insurance
    include_employer_contribution_in_ctc = models.BooleanField()
    admin_charge_in_ctc = models.BooleanField()  # Admin charge included in CTC
    allow_employee_level_override = models.BooleanField()  # Can employee override PF?
    prorate_restricted_pf_wage = models.BooleanField()  # Prorate restricted PF wage?

    def __str__(self):
        return f"EPF Details for Payroll: {self.payroll.business.nameOfBusiness} (EPF No: {self.epf_number})"


class ESI(models.Model):
    payroll = models.OneToOneField('PayrollOrg', on_delete=models.CASCADE, related_name='esi_details')
    esi_number = models.CharField(max_length=100)  # Adjust max_length as needed
    employee_contribution = models.DecimalField(max_digits=5, decimal_places=2)  # e.g., 0.75
    employer_contribution = models.DecimalField(max_digits=5, decimal_places=2)  # e.g., 3.25
    include_employer_contribution_in_ctc = models.BooleanField()  # Include employer contribution in CTC?

    def __str__(self):
        return f"ESI Details for Payroll: {self.payroll.business.nameOfBusiness} (ESI No: {self.esi_number})"


class PT(models.Model):
    payroll = models.ForeignKey('PayrollOrg', on_delete=models.CASCADE, related_name='pt_details')
    work_location = models.ForeignKey('WorkLocations', on_delete=models.CASCADE, related_name='pt_records')
    pt_number = models.CharField(max_length=100, unique=True)  # Added unique constraint
    slab = JSONField(default=list, blank=True)  # Flexible JSON storage for slab data

    class Meta:
        unique_together = ('payroll', 'work_location')  # Ensures one PT per payroll-location pair

    def __str__(self):
        return (f"PT Details - Payroll: {self.payroll.business.nameOfBusiness}, "
                f"Location: {self.work_location.location_name}")


class Earnings(models.Model):
    payroll = models.ForeignKey('PayrollOrg', on_delete=models.CASCADE, related_name='earnings')
    component_name = models.CharField(max_length=150)  # Name of the earning
    component_type = models.CharField(max_length=60)  # Type of earning
    calculation_type = JSONField(default=dict)  # Stores calculation details
    is_active = models.BooleanField(default=True)  # Whether the earning is active
    is_part_of_employee_salary_structure = models.BooleanField(default=False)  # Part of salary structure
    is_taxable = models.BooleanField(default=True)  # Taxable earning
    is_pro_rate_basis = models.BooleanField(default=False)  # Pro-rata basis
    is_flexible_benefit_plan = models.BooleanField(default=False)  # Flexible benefit plan
    includes_epf_contribution = models.BooleanField(default=False)  # EPF contribution
    includes_esi_contribution = models.BooleanField(default=False)  # ESI contribution
    is_included_in_payslip = models.BooleanField(default=True)  # Included in payslip
    tax_deduction_preference = models.CharField(max_length=120, null=True, blank=True)
    is_scheduled_earning = models.BooleanField(default=True)

    def clean(self):
        # Ensure tax_deduction_preference is required if component_name is "Bonus"
        if self.component_name.lower() == "bonus" and not self.tax_deduction_preference:
            raise ValidationError(
                {"tax_deduction_preference": "This field is required when component name is 'Bonus'."}
            )

    def save(self, *args, **kwargs):
        # Call the clean method to validate the model before saving
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Earning: {self.component_name} ({self.component_type})"


class Benefits(models.Model):
    payroll = models.ForeignKey('PayrollOrg', on_delete=models.CASCADE, related_name='benefits')
    benefit_type = models.CharField(max_length=150)  # Type of benefit (e.g., health insurance, transport)
    associated_with = models.CharField(max_length=60)  # What the benefit is linked to
    payslip_name = models.CharField(max_length=60, unique=True) # Display name in the payslip
    is_active = models.BooleanField(default=True)  # Whether the benefit is active
    is_pro_rated = models.BooleanField(default=False)  # Indicates if the benefit is pro-rated
    includes_employer_contribution = models.BooleanField(default=False)  # Whether employer contributes
    frequency = models.CharField(max_length=120)  # Frequency of benefit (e.g., monthly, yearly)

    def __str__(self):
        return f"{self.benefit_type} ({self.payslip_name})"

class Deduction(models.Model):
    payroll = models.ForeignKey('PayrollOrg', on_delete=models.CASCADE, related_name='deductions')
    deduction_type = models.CharField(max_length=150)  # Type of deduction (e.g., tax, insurance)
    payslip_name = models.CharField(max_length=60, unique=True)  # Display name in the payslip (unique)
    is_active = models.BooleanField(default=True)  # Whether the deduction is active
    frequency = models.CharField(max_length=120)  # Frequency of deduction (e.g., monthly, yearly)

    def __str__(self):
        return f"{self.deduction_type} ({self.payslip_name})"

class Reimbursement(models.Model):
    payroll = models.ForeignKey('PayrollOrg', on_delete=models.CASCADE, related_name='reimbursements')
    reimbursement_type = models.CharField(max_length=150)  # Type of reimbursement (e.g., medical, travel)
    payslip_name = models.CharField(max_length=60, unique=True)  # Display name in the payslip (unique)
    include_in_flexible_benefit_plan = models.BooleanField()  # Whether it should be included in flexible benefit plan
    unclaimed_reimbursement = models.BooleanField()  # Whether the reimbursement is unclaimed
    amount_value = models.IntegerField()  # The reimbursement amount value
    is_active = models.BooleanField(default=True)  # Whether the reimbursement is active

    def __str__(self):
        return f"{self.reimbursement_type} ({self.payslip_name})"


class SalaryTemplate(models.Model):
    payroll = models.ForeignKey('PayrollOrg', on_delete=models.CASCADE, related_name='salary_templates')
    template_name = models.CharField(max_length=150, null=False, blank=False)
    description = models.CharField(max_length=250, null=True, blank=True)
    annual_ctc = models.IntegerField()

    # Fields for earnings, benefits, deductions that should contain specific structures
    earnings = JSONField(default=list, blank=True)
    gross_salary = JSONField(default=dict, blank=True)
    benefits = JSONField(default=list, blank=True)
    total_ctc = JSONField(default=dict, blank=True)
    deductions = JSONField(default=list, blank=True)
    net_salary = JSONField(default=dict, blank=True)

    def clean(self):
        # Ensure earnings, benefits, and deductions contain required fields when present
        for section in [self.earnings, self.benefits, self.deductions]:
            for item in section:
                if not isinstance(item, dict):
                    raise ValidationError(f"Each item in {section} must be a dictionary.")
                if ('salary_component' not in item or 'calculation_type' not in item or 'monthly'
                        not in item or 'annually' not in item):
                    raise ValidationError(f"Each item in {section} "
                                          f"must contain 'salary_component', 'calculation_type', "
                                          f"'monthly', and 'annually'.")

        # Validate structure for gross_salary, total_ctc, and net_salary
        for field_name in ['gross_salary', 'total_ctc', 'net_salary']:
            field_data = getattr(self, field_name)
            if not isinstance(field_data, dict):
                raise ValidationError(f"{field_name} must be a dictionary containing 'monthly' and 'annually'.")
            if 'monthly' not in field_data or 'annually' not in field_data:
                raise ValidationError(f"{field_name} must contain 'monthly' and 'annually' fields.")

    def save(self, *args, **kwargs):
        # Call clean method to validate the model before saving
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Salary Template: {self.template_name}"


















