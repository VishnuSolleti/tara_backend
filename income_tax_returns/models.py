from django.db import models
from Tara.settings.default import *
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from djongo.models import ArrayField, EmbeddedField, JSONField
from .helpers import *
from usermanagement.models import ServiceRequest, Users
from servicetasks.models import ServiceTask
from django.db.models.signals import post_save
from django.dispatch import receiver


class PersonalInformation(models.Model):
    service_request = models.OneToOneField(ServiceRequest, on_delete=models.CASCADE,
                                           related_name='personal_information')
    service_type = models.CharField(
        max_length=20,
        default="Income Tax Returns",
        editable=False
    )
    service_task_id = models.IntegerField(null=True, blank=True)
    first_name = models.CharField(max_length=255, null=False, blank=False)
    middle_name = models.CharField(max_length=255, null=False, blank=False)
    last_name = models.CharField(max_length=255, null=False, blank=False)
    gender = models.CharField(max_length=255, null=False, blank=False)
    residentail_status = models.CharField(max_length=255, null=False, blank=False)
    pan = models.FileField(upload_to=personal_information_pan,
                                    null=True, blank=True)
    aadhar = models.FileField(upload_to=personal_information_aadhar,
                           null=True, blank=True)
    status = models.CharField(max_length=20, choices=[('in progress', 'In Progress'), ('completed', 'Completed'),
                                                      ('sent for approval', 'Sent for Approval'),
                                                      ('revoked', 'Revoked')], null=False, blank=False)
    assignee = models.ForeignKey(
        Users,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='personal_information_assigned'
    )

    reviewer = models.ForeignKey(
        Users,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='personal_information_reviewed'
    )
    non_resident_indian = models.CharField(max_length=255, null=True, blank=True)

    def save(self, *args, **kwargs):
        # Default to service_request values if not set
        if not self.assignee and self.service_task.assignee:
            self.assignee = self.service_task.assignee
        if not self.reviewer and self.service_task.reviewer:
            self.reviewer = self.service_task.reviewer
        super().save(*args, **kwargs)

    def __str__(self):
        return self.first_name


class TaxPaidDetails(models.Model):
    service_request = models.OneToOneField(ServiceRequest, on_delete=models.CASCADE,
                                           related_name='tax_paid_details')
    service_type = models.CharField(
        max_length=20,
        default="Income Tax Returns",
        editable=False
    )
    service_task_id = models.IntegerField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=[('in progress', 'In Progress'), ('completed', 'Completed'),
                                                      ('sent for approval', 'Sent for Approval'),
                                                      ('revoked', 'Revoked')], null=False, blank=False)
    assignee = models.ForeignKey(
        Users,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tax_paid_details_assigned'
    )

    reviewer = models.ForeignKey(
        Users,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tax_paid_details_reviewed'
    )

    def save(self, *args, **kwargs):
        # Default to service_request values if not set
        if not self.assignee and self.service_task.assignee:
            self.assignee = self.service_task.assignee
        if not self.reviewer and self.service_task.reviewer:
            self.reviewer = self.service_task.reviewer
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.service_request.id} - Tax Paid Details"


class TaxPaidDetailsFile(models.Model):
    DOCUMENT_TYPES = [
        ('26AS', 'Form 16'),
        ('AIS', 'AIS'),
        ('AdvanceTax', 'Bank Statement'),
    ]

    tax_paid = models.ForeignKey(TaxPaidDetails, on_delete=models.CASCADE, related_name='tax_paid_documents')
    document_type = models.CharField(max_length=30, choices=DOCUMENT_TYPES)
    file = models.FileField(upload_to=tax_paid_details_file,
                           null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.tax_paid.service_request.id} - {self.document_type}"


class SalaryIncome(models.Model):
    service_request = models.OneToOneField(ServiceRequest, on_delete=models.CASCADE,
                                           related_name='salary_income_details')
    service_type = models.CharField(
        max_length=20,
        default="Income Tax Returns",
        editable=False
    )
    service_task_id = models.IntegerField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=[('in progress', 'In Progress'), ('completed', 'Completed'),
                                                      ('sent for approval', 'Sent for Approval'),
                                                      ('revoked', 'Revoked')], null=False, blank=False)
    assignee = models.ForeignKey(
        Users,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tax_paid_details_assigned'
    )

    reviewer = models.ForeignKey(
        Users,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tax_paid_details_reviewed'
    )

    def save(self, *args, **kwargs):
        # Default to service_request values if not set
        if not self.assignee and self.service_task.assignee:
            self.assignee = self.service_task.assignee
        if not self.reviewer and self.service_task.reviewer:
            self.reviewer = self.service_task.reviewer
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.service_request.id} - Tax Paid Details"


class SalaryDocumentFile(models.Model):
    DOCUMENT_TYPES = [
        ('FORM_16', 'Form 16'),
        ('PAYSLIP', 'Payslip'),
        ('BANK_STATEMENT', 'Bank Statement'),
    ]

    income = models.ForeignKey(SalaryIncome, on_delete=models.CASCADE, related_name='documents')
    document_type = models.CharField(max_length=30, choices=DOCUMENT_TYPES)
    file = models.FileField(upload_to=salary_income_details_file,
                            null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.income.service_request.id} - {self.document_type}"


class OtherIncomeDetails(models.Model):
    service_request = models.ForeignKey(ServiceRequest, on_delete=models.CASCADE,
                                           related_name='other_income_details')
    service_type = models.CharField(
        max_length=20,
        default="Income Tax Returns",
        editable=False
    )
    service_task_id = models.IntegerField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=[('in progress', 'In Progress'), ('completed', 'Completed'),
                                                      ('sent for approval', 'Sent for Approval'),
                                                      ('revoked', 'Revoked')], null=False, blank=False)
    assignee = models.ForeignKey(
        Users,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='other_income_details_assigned'
    )

    reviewer = models.ForeignKey(
        Users,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='other_income_details_reviewed'
    )
    details = models.CharField(max_length=255, null=True, blank=True)
    amount = models.IntegerField(max_digits=10, decimal_places=2, null=True, blank=True)
    file = models.FileField(upload_to=salary_income_details_file,
                            null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Default to service_request values if not set
        if not self.assignee and self.service_task.assignee:
            self.assignee = self.service_task.assignee


class NRIEmployeeSalaryDetails(models.Model):
    service_request = models.OneToOneField(ServiceRequest, on_delete=models.CASCADE,
                                           related_name='foreign_income_details')
    service_type = models.CharField(
        max_length=20,
        default="Income Tax Returns",
        editable=False
    )
    service_task_id = models.IntegerField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=[('in progress', 'In Progress'), ('completed', 'Completed'),
                                                      ('sent for approval', 'Sent for Approval'),
                                                      ('revoked', 'Revoked')], null=False, blank=False)
    assignee = models.ForeignKey(
        Users,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='foreign_income_details_assigned'
    )

    reviewer = models.ForeignKey(
        Users,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='foreign_income_details_reviewed'
    )
    foreign_salary_and_employment = models.CharField(max_length=255, null=True, blank=True)
    employment_history = JSONField(null=True, blank=True, default=[])

    def save(self, *args, **kwargs):
        # Default to service_request values if not set
        if not self.assignee and self.service_task.assignee:
            self.assignee = self.service_task.assignee
        if not self.reviewer and self.service_task.reviewer:
            self.reviewer = self.service_task.reviewer
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.service_request.id} - Foreign Employee Salary Details"


class ForeignEmployeeSalaryDetailsFiles(models.Model):
    DOCUMENT_TYPES = [
        ('SALARY_SLIP', 'Salary Slip'),
        ('TAX_PAID_CERTIFICATE_BOARD', 'TAX PAID CERTIFICATE BOARD'),
        ('BANK_STATEMENT', 'Bank Statement'),
    ]

    nri = models.ForeignKey(NRIEmployeeSalaryDetails, on_delete=models.CASCADE, related_name='foreigner_documents')
    document_type = models.CharField(max_length=30, choices=DOCUMENT_TYPES)
    file = models.FileField(upload_to=salary_income_details_file,
                            null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.income.service_request.id} - {self.document_type}"


class HousePropertyIncomeDetails(models.Model):
    service_request = models.ForeignKey(ServiceRequest, on_delete=models.CASCADE,
                                           related_name='house_property_details')
    service_type = models.CharField(
        max_length=20,
        default="Income Tax Returns",
        editable=False
    )
    service_task_id = models.IntegerField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=[('in progress', 'In Progress'), ('completed', 'Completed'),
                                                      ('sent for approval', 'Sent for Approval'),
                                                      ('revoked', 'Revoked')], null=False, blank=False)
    assignee = models.ForeignKey(
        Users,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='house_property_details_assigned'
    )

    reviewer = models.ForeignKey(
        Users,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='house_property_details_reviewed'
    )
    type_of_property = models.CharField(max_length=255, null=True, blank=True)
    property_address = JSONField(null=True, blank=True, default={})
    owned_property = models.BooleanField(default=False)
    ownership_percentage = models.IntegerField(null=True, blank=True)
    country = models.CharField(max_length=255, null=True, blank=True)
    is_it_property_let_out = models.BooleanField(default=False)
    annual_rent_received = models.IntegerField(null=True, blank=True)
    rent_received = models.CharField(max_length=255, null=True, blank=True)
    pay_municipal_tax = models.BooleanField(default=False)
    municipal_tax_paid = models.IntegerField(null=True, blank=True)
    municipal_tax_recipt = models.FileField(upload_to=salary_income_details_file, null=True, blank=True)
    home_loan_on_property = models.BooleanField(default=False)
    interest_during_financial_year = models.IntegerField(null=True, blank=True)
    principal_during_financial_year = models.IntegerField(null=True, blank=True)
    loan_statement = models.FileField(upload_to=salary_income_details_file, null=True, blank=True)
    upload_loan_interest_certificate = models.FileField(upload_to=salary_income_details_file, null=True, blank=True)

    def save(self, *args, **kwargs):
        # Default to service_request values if not set
        if not self.assignee and self.service_task.assignee:
            self.assignee = self.service_task.assignee
        if not self.reviewer and self.service_task.reviewer:
            self.reviewer = self.service_task.reviewer
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.service_request.id} - House Property Details"


class InterestIncome(models.Model):
    service_request = models.ForeignKey(ServiceRequest, on_delete=models.CASCADE,
                                        related_name='other_income')
    service_type = models.CharField(
        max_length=20,
        default="Income Tax Returns",
        editable=False
    )
    service_task_id = models.IntegerField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=[('in progress', 'In Progress'), ('completed', 'Completed'),
                                                      ('sent for approval', 'Sent for Approval'),
                                                      ('revoked', 'Revoked')], null=False, blank=False)
    assignee = models.ForeignKey(
        Users,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='other_income_assigned'
    )

    reviewer = models.ForeignKey(
        Users,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='other_income_reviewed'
    )
    interest_income = models.CharField(max_length=255, null=False, blank=False,
                                       choices=[('Applicable', 'Applicable'), ('Not Applicable', 'Not Applicable')])

    def save(self, *args, **kwargs):
        # Default to service_request values if not set
        if not self.assignee and self.service_task.assignee:
            self.assignee = self.service_task.assignee
        if not self.reviewer and self.service_task.reviewer:
            self.reviewer = self.service_task.reviewer
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.service_request.id} - Other Income Details"


class InterestIncomeDocument(models.Model):
    interest_income = models.ForeignKey(InterestIncome, on_delete=models.CASCADE, related_name='documents')
    interest_type = models.CharField(max_length=30, choices=[('Savings Account', 'Savings Account'),
                                                             ('Recurring Deposit', 'Recurring Deposit'),
                                                             ('NRO Account', 'NRO Account'),
                                                             ('NRE Account', 'NRE Account'),
                                                             ('Other', 'Other')
                                                             ('Fixed Deposit', 'Fixed Deposit')])
    interest_earned = models.IntegerField(null=True, blank=True)
    bank_name = models.CharField(max_length=255, null=True, blank=True)
    file = models.FileField(upload_to=salary_income_details_file,
                            null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.interest_income.service_request.id} - {self.document_type}"


class DividendIncome(models.Model):
    service_request = models.ForeignKey(ServiceRequest, on_delete=models.CASCADE,
                                        related_name='other_income')
    service_type = models.CharField(
        max_length=20,
        default="Income Tax Returns",
        editable=False
    )
    service_task_id = models.IntegerField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=[('in progress', 'In Progress'), ('completed', 'Completed'),
                                                      ('sent for approval', 'Sent for Approval'),
                                                      ('revoked', 'Revoked')], null=False, blank=False)
    assignee = models.ForeignKey(
        Users,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='other_income_assigned'
    )

    reviewer = models.ForeignKey(
        Users,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='other_income_reviewed'
    )
    dividend_income = models.CharField(max_length=255, null=False, blank=False,
                                       choices=[('Applicable', 'Applicable'), ('Not Applicable', 'Not Applicable')])

    def save(self, *args, **kwargs):
        # Default to service_request values if not set
        if not self.assignee and self.service_task.assignee:
            self.assignee = self.service_task.assignee
        if not self.reviewer and self.service_task.reviewer:
            self.reviewer = self.service_task.reviewer
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.service_request.id} - Other Income Details"


class DividendIncomeDocument(models.Model):
    dividend_income = models.ForeignKey(DividendIncome, on_delete=models.CASCADE, related_name='documents')
    received_from = models.CharField(max_length=255, null=True, blank=True)
    dividend_received = models.IntegerField(null=True, blank=True)
    file = models.FileField(upload_to=salary_income_details_file,
                            null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.dividend_income.service_request.id}- {self.received_from}"


class GiftIncomeDetails(models.Model):
    service_request = models.ForeignKey(ServiceRequest, on_delete=models.CASCADE,
                                        related_name='gift_income')
    service_type = models.CharField(
        max_length=20,
        default="Income Tax Returns",
        editable=False
    )
    service_task_id = models.IntegerField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=[('in progress', 'In Progress'), ('completed', 'Completed'),
                                                      ('sent for approval', 'Sent for Approval'),
                                                      ('revoked', 'Revoked')], null=False, blank=False)
    assignee = models.ForeignKey(
        Users,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='gift_income_assigned'
    )

    reviewer = models.ForeignKey(
        Users,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='gift_income_reviewed'
    )
    gift_income = models.CharField(max_length=255, null=False, blank=False,
                                   choices=[('Applicable', 'Applicable'), ('Not Applicable', 'Not Applicable')])

    def save(self, *args, **kwargs):
        # Default to service_request values if not set
        if not self.assignee and self.service_task.assignee:
            self.assignee = self.service_task.assignee
        if not self.reviewer and self.service_task.reviewer:
            self.reviewer = self.service_task.reviewer
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.service_request.id} - Gift Income Details"


class GiftIncomeDocument(models.Model):
    gift_income = models.ForeignKey(GiftIncomeDetails, on_delete=models.CASCADE, related_name='gift_income_details')
    amount = models.IntegerField(null=True, blank=True)
    received_from = models.CharField(max_length=255, null=True, blank=True)
    relation = models.CharField(max_length=255, null=True, blank=True, choices=[('Relative', 'Relative'),
                                                                                ('Non Relative', 'Non Relative')])
    date_received = models.DateField(null=True, blank=True)
    was_it_marriage_related = models.CharField(max_length=255, null=True, blank=True,
                                               choices=[('Yes', 'Yes'), ('No', 'No')])

    def __str__(self):
        return f"{self.gift_income.service_request.id}- {self.relation}"


class FamilyPensionIncome(models.Model):
    service_request = models.ForeignKey(ServiceRequest, on_delete=models.CASCADE,
                                        related_name='family_pension_income')
    service_type = models.CharField(
        max_length=20,
        default="Income Tax Returns",
        editable=False
    )
    service_task_id = models.IntegerField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=[('in progress', 'In Progress'), ('completed', 'Completed'),
                                                      ('sent for approval', 'Sent for Approval'),
                                                      ('revoked', 'Revoked')], null=False, blank=False)
    assignee = models.ForeignKey(
        Users,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='family_pension_assigned'
    )

    reviewer = models.ForeignKey(
        Users,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='family_pension_reviewed'
    )
    family_pension_income = models.CharField(max_length=255, null=False, blank=False,
                                   choices=[('Applicable', 'Applicable'), ('Not Applicable', 'Not Applicable')])

    def save(self, *args, **kwargs):
        # Default to service_request values if not set
        if not self.assignee and self.service_task.assignee:
            self.assignee = self.service_task.assignee
        if not self.reviewer and self.service_task.reviewer:
            self.reviewer = self.service_task.reviewer
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.service_request.id} - Family Pension Income Details"


class FamilyPensionIncomeDocuments(models.Model):
    family_pension = models.ForeignKey(ServiceRequest, on_delete=models.CASCADE,
                                        related_name='family_pension_income')
    type_of_income = models.CharField(max_length=30, choices=[('Divident', 'Divident'),
                                                              ('Interest', 'Interest'),
                                                              ('Others', 'Others')])
    country = models.CharField(max_length=20)
    currency = models.CharField(max_length=3)
    amount = models.IntegerField()

    def __str__(self):
        return f"{self.family_pension.service_request.id}- {self.type_of_income}"


