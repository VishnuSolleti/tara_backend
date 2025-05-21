from rest_framework.decorators import api_view, parser_classes
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from .serializers import *
import json
from .helpers import IsPlatformOrAssociatedUser
from rest_framework.decorators import api_view, permission_classes, parser_classes


# 1. Entrepreneur Details Views
@api_view(['GET', 'POST'])
@permission_classes([IsPlatformOrAssociatedUser])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def business_identity_structure_list(request):
    if request.method == 'GET':
        records = BusinessIdentityStructure.objects.all()
        serializer = BusinessIdentityStructureSerializer(records, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        serializer = BusinessIdentityStructureSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsPlatformOrAssociatedUser])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def business_identity_structure_detail(request, pk):
    try:
        record = BusinessIdentityStructure.objects.get(pk=pk)
    except BusinessIdentityStructure.DoesNotExist:
        return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = BusinessIdentityStructureSerializer(record)
        return Response(serializer.data)
    elif request.method == 'PUT':
        serializer = BusinessIdentityStructureSerializer(record, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        record.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# 2. Establishment Details Views
@api_view(['GET', 'POST'])
@permission_classes([IsPlatformOrAssociatedUser])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def signatory_details_list(request):
    if request.method == 'GET':
        records = SignatoryDetails.objects.all()
        serializer = SignatoryDetailsSerializer(records, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        data = request.data.copy()
        if 'address' in data and isinstance(data['address'], str):
            try:
                data['address'] = json.loads(data['address'])
            except json.JSONDecodeError:
                return Response({"error": "Invalid JSON for address"}, status=status.HTTP_400_BAD_REQUEST)
        serializer = SignatoryDetailsSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsPlatformOrAssociatedUser])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def signatory_details_detail(request, pk):
    try:
        record = SignatoryDetails.objects.get(pk=pk)
    except SignatoryDetails.DoesNotExist:
        return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = SignatoryDetailsSerializer(record)
        return Response(serializer.data)
    elif request.method == 'PUT':
        data = request.data.copy()
        if 'address' in data and isinstance(data['address'], str):
            try:
                data['address'] = json.loads(data['address'])
            except json.JSONDecodeError:
                return Response({"error": "Invalid JSON for address"}, status=status.HTTP_400_BAD_REQUEST)
        serializer = SignatoryDetailsSerializer(record, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        record.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET', 'POST'])
@permission_classes([IsPlatformOrAssociatedUser])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def business_location_proofs_list(request):
    if request.method == 'GET':
        records = BusinessLocationProofs.objects.all()
        serializer = BusinessLocationProofsSerializer(records, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        data = request.data.copy()
        if 'principal_place_of_business' in data and isinstance(data['principal_place_of_business'], str):
            try:
                data['principal_place_of_business'] = json.loads(data['principal_place_of_business'])
            except json.JSONDecodeError:
                return Response({"error": "Invalid JSON"}, status=status.HTTP_400_BAD_REQUEST)
        serializer = BusinessLocationProofsSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsPlatformOrAssociatedUser])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def business_location_proofs_detail(request, pk):
    try:
        record = BusinessLocationProofs.objects.get(pk=pk)
    except BusinessLocationProofs.DoesNotExist:
        return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = BusinessLocationProofsSerializer(record)
        return Response(serializer.data)
    elif request.method == 'PUT':
        data = request.data.copy()
        if 'principal_place_of_business' in data and isinstance(data['principal_place_of_business'], str):
            try:
                data['principal_place_of_business'] = json.loads(data['principal_place_of_business'])
            except json.JSONDecodeError:
                return Response({"error": "Invalid JSON"}, status=status.HTTP_400_BAD_REQUEST)
        serializer = BusinessLocationProofsSerializer(record, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        record.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET', 'POST'])
@permission_classes([IsPlatformOrAssociatedUser])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def additional_space_business_list(request):
    if request.method == 'GET':
        records = AdditionalSpaceBusiness.objects.all()
        serializer = AdditionalSpaceBusinessSerializer(records, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        data = request.data.copy()
        if 'address' in data and isinstance(data['address'], str):
            try:
                data['address'] = json.loads(data['address'])
            except json.JSONDecodeError:
                return Response({"error": "Invalid JSON"}, status=status.HTTP_400_BAD_REQUEST)
        serializer = AdditionalSpaceBusinessSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsPlatformOrAssociatedUser])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def additional_space_business_detail(request, pk):
    try:
        record = AdditionalSpaceBusiness.objects.get(pk=pk)
    except AdditionalSpaceBusiness.DoesNotExist:
        return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = AdditionalSpaceBusinessSerializer(record)
        return Response(serializer.data)
    elif request.method == 'PUT':
        data = request.data.copy()
        if 'address' in data and isinstance(data['address'], str):
            try:
                data['address'] = json.loads(data['address'])
            except json.JSONDecodeError:
                return Response({"error": "Invalid JSON"}, status=status.HTTP_400_BAD_REQUEST)
        serializer = AdditionalSpaceBusinessSerializer(record, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        record.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET', 'POST'])
@permission_classes([IsPlatformOrAssociatedUser])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def business_registration_documents_list(request):
    if request.method == 'GET':
        records = BusinessRegistrationDocuments.objects.all()
        serializer = BusinessRegistrationDocumentsSerializer(records, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        serializer = BusinessRegistrationDocumentsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsPlatformOrAssociatedUser])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def business_registration_documents_detail(request, pk):
    try:
        record = BusinessRegistrationDocuments.objects.get(pk=pk)
    except BusinessRegistrationDocuments.DoesNotExist:
        return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = BusinessRegistrationDocumentsSerializer(record)
        return Response(serializer.data)
    elif request.method == 'PUT':
        serializer = BusinessRegistrationDocumentsSerializer(record, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        record.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET', 'POST'])
@permission_classes([IsPlatformOrAssociatedUser])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def review_filing_certificate_list(request):
    if request.method == 'GET':
        records = ReviewFilingCertificate.objects.all()
        serializer = ReviewFilingCertificateSerializer(records, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        serializer = ReviewFilingCertificateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsPlatformOrAssociatedUser])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def review_filing_certificate_detail(request, pk):
    try:
        record = ReviewFilingCertificate.objects.get(pk=pk)
    except ReviewFilingCertificate.DoesNotExist:
        return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = ReviewFilingCertificateSerializer(record)
        return Response(serializer.data)
    elif request.method == 'PUT':
        serializer = ReviewFilingCertificateSerializer(record, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        record.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
