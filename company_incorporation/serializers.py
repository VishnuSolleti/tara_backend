from rest_framework import serializers
from .models import (
    ProposedCompanyDetails,
    RegisteredOfficeAddressDetails,
    AuthorizedPaidUpShareCapital,
    Directors,
    DirectorsDetails,
    Shareholders,
    ShareholdersDetails,
    ReviewFilingCertificate
)
from decimal import Decimal


class ProposedCompanyDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProposedCompanyDetails
        fields = '__all__'

class RegisteredOfficeAddressDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = RegisteredOfficeAddressDetails
        fields = '__all__'


class AuthorizedPaidUpShareCapitalSerializer(serializers.ModelSerializer):

    class Meta:
        model = AuthorizedPaidUpShareCapital
        fields = '__all__'


class DirectorsDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = DirectorsDetails
        fields = '__all__'

class DirectorsSerializer(serializers.ModelSerializer):
    directors_list = DirectorsDetailsSerializer(many=True, required=False)
    class Meta:
        model = Directors
        fields = '__all__'


class ShareholdersSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shareholders
        fields = '__all__'

class ShareholdersDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShareholdersDetails
        fields = '__all__'

class ReviewFilingCertificateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReviewFilingCertificate
        fields = '__all__'