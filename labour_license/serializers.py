from rest_framework import serializers
from .models import (
    BusinessIdentityStructure, SignatoryDetails, BusinessLocationProofs,
    AdditionalSpaceBusiness, BusinessRegistrationDocuments, ReviewFilingCertificate
)


class BusinessIdentityStructureSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessIdentityStructure
        fields = '__all__'


class SignatoryDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SignatoryDetails
        fields = '__all__'


class BusinessLocationProofsSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessLocationProofs
        fields = '__all__'


class AdditionalSpaceBusinessSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdditionalSpaceBusiness
        fields = '__all__'


class BusinessRegistrationDocumentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessRegistrationDocuments
        fields = '__all__'


class ReviewFilingCertificateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReviewFilingCertificate
        fields = '__all__'
