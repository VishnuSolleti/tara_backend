from django.db import models
from django.core.exceptions import ValidationError
from djongo.models import ArrayField, EmbeddedField, JSONField


def validate_pincode(value):
    if len(str(value)) != 6:  # Assuming 6-digit pin codes
        raise ValidationError(f"{value} is not a valid pin code.")


class PayrollOrg(models.Model):
    business_id = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)  # Use auto_now_add for creation timestamp
    org_name = models.CharField(max_length=150)  # Use snake_case for consistency
    logo = models.CharField(max_length=200, null=True, blank=True)
    industry = models.CharField(max_length=60, null=True, blank=True)
    contact_email = models.EmailField(max_length=120, null=True, blank=True)
    sender_email = models.EmailField(max_length=120, null=True, blank=True)
    org_address_line1 = models.CharField(max_length=150, null=True, blank=True)
    org_address_line2 = models.CharField(max_length=150, null=True, blank=True)
    org_address_state = models.CharField(max_length=150, null=True, blank=True)
    org_address_city = models.CharField(max_length=150, null=True, blank=True)
    org_address_pincode = models.PositiveIntegerField(null=True, validators=[validate_pincode])  # No max_length
    filling_address_line1 = models.CharField(max_length=150, null=True, blank=True)
    filling_address_line2 = models.CharField(max_length=150, null=True, blank=True)
    filling_address_state = models.CharField(max_length=150, null=True, blank=True)
    filling_address_city = models.CharField(max_length=150, null=True, blank=True)
    filling_address_pincode = models.PositiveIntegerField(null=True, validators=[validate_pincode]) # No max_length

    def __str__(self):
        return self.org_name


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
    description = models.CharField(max_length=220, null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['payroll', 'designation_name'], name='unique_designation_per_payroll'),
        ]

    def __str__(self):
        return self.designation_name


class EPF(models.Model):
    payroll = models.OneToOneField('PayrollOrg', on_delete=models.CASCADE, related_name='epf_details')
    epf_number = models.CharField(max_length=100)  # Adjust max_length as needed
    employee_actual_pf_wage = models.DecimalField(max_digits=10, decimal_places=2)  # Wage amount
    employee_actual_restricted_wage = models.DecimalField(max_digits=10, decimal_places=2)  # Restricted wage
    employer_actual_pf_wage = models.DecimalField(max_digits=10, decimal_places=2)  # Wage amount
    employer_actual_restricted_wage = models.DecimalField(max_digits=10, decimal_places=2)  # Restricted wage
    employer_edli_contribution_in_ctc = models.BooleanField()  # EDLI contribution included
    # in CTC Employees' Deposit Linked Insurance
    admin_charge_in_ctc = models.BooleanField()  # Admin charge included in CTC
    allow_employee_level_override = models.BooleanField()  # Can employee override PF?
    prorate_restricted_pf_wage = models.BooleanField()  # Prorate restricted PF wage?

    def __str__(self):
        return f"EPF Details for Payroll: {self.payroll.orgName} (EPF No: {self.epf_number})"


class ESI(models.Model):
    payroll = models.OneToOneField('PayrollOrg', on_delete=models.CASCADE, related_name='esi_details')
    esi_number = models.CharField(max_length=100)  # Adjust max_length as needed
    employee_contribution = models.DecimalField(max_digits=5, decimal_places=2)  # e.g., 0.75
    employer_contribution = models.DecimalField(max_digits=5, decimal_places=2)  # e.g., 3.25
    include_employer_contribution_in_ctc = models.BooleanField()  # Include employer contribution in CTC?

    def __str__(self):
        return f"ESI Details for Payroll: {self.payroll.orgName} (ESI No: {self.esi_number})"


class PF(models.Model):
    payroll = models.OneToOneField('PayrollOrg', on_delete=models.CASCADE, related_name='pf_details')
    location = models.CharField(max_length=150)  # Added max_length to restrict the size of the location
    state = models.CharField(max_length=100)
    pt_number = models.CharField(max_length=100)  # Adjusted name and added max_length for clarity
    slab = JSONField(default=list, blank=True)  # JSONField for flexible storage of slab data

    def __str__(self):
        return f"PF Details for Payroll: {self.payroll.orgName} (Location: {self.location})"


class Earnings(models.Model):
    payroll = models.ForeignKey('PayrollOrg', on_delete=models.CASCADE, related_name='earnings')
    earning_name = models.CharField(max_length=150)  # Name of the earning
    earning_type = models.CharField(max_length=60)  # Type of earning
    payslip_name = models.CharField(max_length=60, unique=True)  # Display name in the payslip
    is_flat_amount = models.BooleanField(default=False)  # Indicates if the earning is a flat amount
    is_basic_percentage = models.BooleanField(default=False)  # Indicates if it's based on a percentage of the basic salary
    amount_value = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # Value of the amount
    is_active = models.BooleanField(default=True)  # Whether the earning is active
    is_part_of_employee_salary_structure = models.BooleanField(default=False)  # Part of salary structure
    is_taxable = models.BooleanField(default=True)  # Taxable earning
    is_pro_rate_basis = models.BooleanField(default=False)  # Pro-rata basis
    is_flexible_benefit_plan = models.BooleanField(default=False)  # Flexible benefit plan
    includes_epf_contribution = models.BooleanField(default=False)  # EPF contribution
    includes_esi_contribution = models.BooleanField(default=False)  # ESI contribution
    is_included_in_payslip = models.BooleanField(default=True)  # Included in payslip

    def clean(self):
        # Enforce mutually exclusive fields
        if self.is_flat_amount and self.is_basic_percentage:
            raise ValidationError(
                "Both 'is_flat_amount' and 'is_basic_percentage' cannot be True at the same time."
            )
        if not self.is_flat_amount and not self.is_basic_percentage:
            raise ValidationError(
                "Either 'is_flat_amount' or 'is_basic_percentage' must be True."
            )

    def save(self, *args, **kwargs):
        # Call the clean method to validate the model
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Earning: {self.earning_name} ({self.payslip_name})"


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
















