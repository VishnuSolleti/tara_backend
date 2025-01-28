from rest_framework import serializers
from .models import (PayrollOrg, WorkLocations, Departments,
                     Designation, EPF, ESI, PF, Earnings, Benefits, Deduction, Reimbursement)

class PayrollOrgSerializer(serializers.ModelSerializer):
    class Meta:
        model = PayrollOrg
        fields = '__all__'  # Include all fields from PayrollOrg model

    def create(self, validated_data):
        """
        Create and return a new `PayrollOrg` instance, given the validated data.
        """
        # Create a new PayrollOrg instance using the validated data
        instance = self.Meta.model(**validated_data)
        instance.save()  # Save the instance to the database
        return instance

    def update(self, instance, validated_data):
        """
        Update and return an existing `PayrollOrg` instance, given the validated data.
        """
        # Update the instance attributes with the validated data
        for k, v in validated_data.items():
            setattr(instance, k, v)
        instance.save()  # Save the updated instance to the database
        return instance


class WorkLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkLocations
        fields = '__all__'

    def create(self, validated_data):
        """
        Create and return a new `WorkLocations` instance, given the validated data.
        """
        instance = WorkLocations(**validated_data)
        instance.save()
        return instance

    def update(self, instance, validated_data):
        """
        Update and return an existing `WorkLocations` instance, given the validated data.
        """
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class DepartmentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Departments
        fields = '__all__'

    def create(self, validated_data):
        """
        Create and return a new `Department` instance, given the validated data.
        """
        instance = self.Meta.model(**validated_data)
        instance.save()
        return instance

    def update(self, instance, validated_data):
        """
        Update and return an existing `Department` instance, given the validated data.
        """
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        return instance

class DesignationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Designation
        fields = ['id', 'payroll', 'designation_name', 'description']

    def create(self, validated_data):
        """
        Create and return a new `WorkLocations` instance, given the validated data.
        """
        instance = WorkLocations(**validated_data)
        instance.save()
        return instance

    def update(self, instance, validated_data):
        """
        Update and return an existing `WorkLocations` instance, given the validated data.
        """
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

class EPFSerializer(serializers.ModelSerializer):
    class Meta:
        model = EPF
        fields = ['id', 'payroll', 'epf_number', 'epf_contribution_rate', 'employer_actual_pf_wage',
                  'employer_actual_restricted_wage', 'employer_edli_contribution_in_ctc',
                  'admin_charge_in_ctc', 'allow_employee_level_override', 'prorate_restricted_pf_wage']

    def create(self, validated_data):
        """
        Create and return a new `WorkLocations` instance, given the validated data.
        """
        instance = WorkLocations(**validated_data)
        instance.save()
        return instance

    def update(self, instance, validated_data):
        """
        Update and return an existing `WorkLocations` instance, given the validated data.
        """
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

class ESISerializer(serializers.ModelSerializer):
    class Meta:
        model = ESI
        fields = ['id', 'payroll', 'esi_number', 'employee_contribution', 'employer_contribution',
                  'include_employer_contribution_in_ctc']

    def create(self, validated_data):
        """
        Create and return a new `WorkLocations` instance, given the validated data.
        """
        instance = WorkLocations(**validated_data)
        instance.save()
        return instance

    def update(self, instance, validated_data):
        """
        Update and return an existing `WorkLocations` instance, given the validated data.
        """
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class PFSerializer(serializers.ModelSerializer):
    class Meta:
        model = PF
        fields = ['id', 'payroll', 'location', 'state', 'pt_number', 'slab']

    def create(self, validated_data):
        """
        Create and return a new `PF` instance, given the validated data.
        """
        instance = PF.objects.create(**validated_data)
        return instance

    def update(self, instance, validated_data):
        """
        Update and return an existing `PF` instance, given the validated data.
        """
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class EarningsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Earnings
        fields = ['id', 'payroll', 'earning_name', 'earning_type', 'payslip_name', 'is_flat_amount',
                  'is_basic_percentage', 'amount_value', 'is_active', 'is_part_of_employee_salary_structure',
                  'is_taxable', 'is_pro_rate_basis', 'is_flexible_benefit_plan', 'includes_epf_contribution',
                  'includes_esi_contribution', 'is_included_in_payslip']

    def create(self, validated_data):
        """
        Create and return a new `Earnings` instance, given the validated data.
        """
        instance = Earnings.objects.create(**validated_data)
        return instance

    def update(self, instance, validated_data):
        """
        Update and return an existing `Earnings` instance, given the validated data.
        """
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

class BenefitsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Benefits
        fields = [
            'id',
            'payroll',
            'benefit_type',
            'associated_with',
            'payslip_name',
            'is_active',
            'is_pro_rated',
            'includes_employer_contribution',
            'frequency'
        ]

    # Adding validation for unique `payslip_name`
    def validate_payslip_name(self, value):
        if Benefits.objects.filter(payslip_name=value).exists():
            raise serializers.ValidationError("Payslip name must be unique.")
        return value


class DeductionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Deduction
        fields = [
            'id',
            'payroll',
            'deduction_type',
            'payslip_name',
            'is_active',
            'frequency'
        ]

    def validate_payslip_name(self, value):
        if Deduction.objects.filter(payslip_name=value).exists():
            raise serializers.ValidationError("Payslip name must be unique.")
        return value


class ReimbursementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reimbursement
        fields = [
            'id',
            'payroll',
            'reimbursement_type',
            'payslip_name',
            'include_in_flexible_benefit_plan',
            'unclaimed_reimbursement',
            'amount_value',
            'is_active'
        ]

    def validate_payslip_name(self, value):
        if Reimbursement.objects.filter(payslip_name=value).exists():
            raise serializers.ValidationError("Payslip name must be unique.")
        return value

    def validate_amount_value(self, value):
        if value <= 0:
            raise serializers.ValidationError("Reimbursement amount must be greater than zero.")
        return value
