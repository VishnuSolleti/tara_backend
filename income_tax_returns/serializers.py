from rest_framework import serializers
from .models import *
from servicetasks.models import ServiceTask


class PersonalInformationSerializer(serializers.ModelSerializer):
    class Meta:
        model = PersonalInformation
        fields = '__all__'


class TaxPaidDetailsFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaxPaidDetailsFile
        fields = ['id', 'tax_paid', 'document_type', 'file', 'uploaded_at']
        read_only_fields = ['uploaded_at']


class TaxPaidDetailsSerializer(serializers.ModelSerializer):
    assignee = serializers.PrimaryKeyRelatedField(queryset=Users.objects.all(), required=False, allow_null=True)
    reviewer = serializers.PrimaryKeyRelatedField(queryset=Users.objects.all(), required=False, allow_null=True)
    service_request = serializers.PrimaryKeyRelatedField(queryset=ServiceRequest.objects.all())
    service_task = serializers.PrimaryKeyRelatedField(queryset=ServiceTask.objects.all())
    tax_paid_documents = TaxPaidDetailsFileSerializer(many=True, read_only=True)

    class Meta:
        model = TaxPaidDetails
        fields = [
            'id',
            'service_request',
            'service_type',
            'service_task',
            'status',
            'assignee',
            'reviewer',
            'tax_paid_documents'
        ]
        read_only_fields = ['service_type']


class SalaryDocumentFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalaryDocumentFile
        fields = ['id', 'document_type', 'file', 'uploaded_at']


class SalaryIncomeSerializer(serializers.ModelSerializer):
    documents = SalaryDocumentFileSerializer(many=True, read_only=True)

    class Meta:
        model = SalaryIncome
        fields = [
            'id',
            'service_request',
            'service_type',
            'service_task',
            'status',
            'assignee',
            'reviewer',
            'documents',
        ]


# class OtherIncomeDetailFileSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = OtherIncomeDetailsData
#         fields = [
#             'id',
#             'other_income',
#             'details',
#             'amount',
#             'file',
#             'notes',
#             'uploaded_at',
#         ]
#         read_only_fields = ['id', 'uploaded_at']


class OtherIncomeDetailsSerializer(serializers.ModelSerializer):


    class Meta:
        model = OtherIncomeDetails
        fields = [
            'id',
            'service_request',
            'service_type',
            'service_task',
            'status',
            'assignee',
            'reviewer',
            'details',
            'amount',
            'notes',
            'file'
        ]
        read_only_fields = ['id', 'service_type']


class ForeignEmployeeSalaryDetailsFilesSerializer(serializers.ModelSerializer):
    class Meta:
        model = ForeignEmployeeSalaryDetailsFiles
        fields = ['id', 'document_type', 'file', 'uploaded_at']


class NRIEmployeeSalaryDetailsSerializer(serializers.ModelSerializer):
    assignee_name = serializers.SerializerMethodField()
    reviewer_name = serializers.SerializerMethodField()

    class Meta:
        model = NRIEmployeeSalaryDetails
        fields = [
            'id',
            'service_request',
            'service_type',
            'service_task',
            'status',
            'assignee',
            'assignee_name',
            'reviewer',
            'reviewer_name',
            'country_of_employment',
            'salary_received',
            'employment_start_date',
            'employment_end_date'
        ]

    def get_assignee_name(self, obj):
        return obj.assignee.get_full_name() if obj.assignee else None

    def get_reviewer_name(self, obj):
        return obj.reviewer.get_full_name() if obj.reviewer else None


class HousePropertyIncomeDetailsSerializer(serializers.ModelSerializer):
    assignee_name = serializers.SerializerMethodField()
    reviewer_name = serializers.SerializerMethodField()
    property_address = serializers.JSONField(required=False, allow_null=True, default=dict)
    municipal_tax_receipt_url = serializers.SerializerMethodField()
    loan_statement_url = serializers.SerializerMethodField()
    loan_interest_certificate_url = serializers.SerializerMethodField()

    class Meta:
        model = HousePropertyIncomeDetails
        fields = [
            'id',
            'service_request',
            'service_type',
            'service_task',
            'status',
            'assignee',
            'assignee_name',
            'reviewer',
            'reviewer_name',
            'type_of_property',
            'property_address',
            'owned_property',
            'ownership_percentage',
            'country',
            'is_it_property_let_out',
            'annual_rent_received',
            'rent_received',
            'pay_municipal_tax',
            'municipal_tax_paid',
            'municipal_tax_receipt',
            'municipal_tax_receipt_url',
            'home_loan_on_property',
            'interest_during_financial_year',
            'principal_during_financial_year',
            'loan_statement',
            'loan_statement_url',
            'upload_loan_interest_certificate',
            'loan_interest_certificate_url',
        ]

    def get_assignee_name(self, obj):
        parts = [obj.assignee.first_name, obj.assignee.last_name]
        # Filter out None or empty strings, then join with space
        return " ".join(part for part in parts if part).strip()

    def get_reviewer_name(self, obj):
        parts = [obj.reviewer.first_name, obj.reviewer.last_name]
        # Filter out None or empty strings, then join with space
        return " ".join(part for part in parts if part).strip()

    def get_municipal_tax_receipt_url(self, obj):
        return obj.municipal_tax_receipt.url if obj.municipal_tax_receipt else None

    def get_loan_statement_url(self, obj):
        return obj.loan_statement.url if obj.loan_statement else None

    def get_loan_interest_certificate_url(self, obj):
        return obj.upload_loan_interest_certificate.url if obj.upload_loan_interest_certificate else None


class InterestIncomeSerializer(serializers.ModelSerializer):
    class Meta:
        model = InterestIncome
        fields = '__all__'


class InterestIncomeDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = InterestIncomeDocument
        fields = '__all__'


class DividendIncomeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DividendIncome
        fields = '__all__'
        read_only_fields = ('service_type',)


class DividendIncomeDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = DividendIncomeDocument
        fields = '__all__'


class GiftIncomeDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = GiftIncomeDetails
        fields = '__all__'  # or list fields explicitly if preferred


class GiftIncomeDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = GiftIncomeDocument
        fields = '__all__'


class FamilyPensionIncomeSerializer(serializers.ModelSerializer):
    class Meta:
        model = FamilyPensionIncome
        fields = '__all__'


class FamilyPensionIncomeDocumentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = FamilyPensionIncomeDocuments
        fields = '__all__'


class ReviewFilingCertificateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReviewFilingCertificate
        fields = '__all__'