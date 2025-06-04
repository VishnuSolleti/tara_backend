from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.response import Response
from rest_framework import status
import os
import json

from .models import (
    BasicBusinessInfo,
    RegistrationInfo,
    PrincipalPlaceDetails,
    PromoterSignatoryDetails,
    GSTReviewFilingCertificate,
)
from .serializers import (
    BasicBusinessInfoSerializer,
    RegistrationInfoSerializer,
    PrincipalPlaceDetailsSerializer,
    PromoterSignatoryDetailsSerializer,
    GSTReviewFilingCertificateSerializer,
)


# BasicBusinessInfo Views
@api_view(['POST', 'GET'])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def basic_business_info_list_create(request):
    if request.method == 'POST':
        serializer = BasicBusinessInfoSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'GET':
        objs = BasicBusinessInfo.objects.all()
        serializer = BasicBusinessInfoSerializer(objs, many=True)
        return Response(serializer.data)


@api_view(['GET'])
def basic_business_info_by_service_request(request):
    service_request_id = request.query_params.get('service_request_id')
    if not service_request_id:
        return Response({"error": "Missing service_request_id"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        queryset = BasicBusinessInfo.objects.filter(service_request_id=service_request_id)
        if not queryset.exists():
            return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = BasicBusinessInfoSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    except Exception as e:
        return Response(
            {"error": "Something went wrong", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET', 'PUT', 'DELETE'])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def basic_business_info_detail(request, pk):
    try:
        instance = BasicBusinessInfo.objects.get(pk=pk)
    except BasicBusinessInfo.DoesNotExist:
        return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = BasicBusinessInfoSerializer(instance)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = BasicBusinessInfoSerializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        # Optional: delete related files if any (example)
        file_fields = ['some_file_field']  # replace with actual file fields if needed
        for field in file_fields:
            file_obj = getattr(instance, field, None)
            if file_obj and os.path.isfile(file_obj.path):
                os.remove(file_obj.path)

        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# RegistrationInfo Views

@api_view(['POST', 'GET'])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def registration_info_list_create(request):
    if request.method == 'POST':
        serializer = RegistrationInfoSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'GET':
        objs = RegistrationInfo.objects.all()
        serializer = RegistrationInfoSerializer(objs, many=True)
        return Response(serializer.data)


@api_view(['GET'])
def registration_info_by_service_request(request):
    service_request_id = request.query_params.get('service_request_id')
    if not service_request_id:
        return Response({"error": "Missing service_request_id"}, status=status.HTTP_400_BAD_REQUEST)
    try:
        instance = RegistrationInfo.objects.get(service_request_id=service_request_id)
        serializer = RegistrationInfoSerializer(instance)
        return Response(serializer.data)
    except RegistrationInfo.DoesNotExist:
        return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET', 'PUT', 'DELETE'])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def registration_info_detail(request, pk):
    try:
        instance = RegistrationInfo.objects.get(pk=pk)
    except RegistrationInfo.DoesNotExist:
        return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = RegistrationInfoSerializer(instance)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = RegistrationInfoSerializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        # Optional file cleanup here if needed
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# PrincipalPlaceDetails Views
@api_view(['POST', 'GET'])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def principal_place_details_list_create(request):
    if request.method == 'POST':
        # Convert request.data into a normal dict
        data = dict(request.data)

        # Since data values are lists (from MultiPartParser), flatten them
        for key in data:
            if isinstance(data[key], list) and len(data[key]) == 1:
                data[key] = data[key][0]

        val = data.get('principal_place')

        if val:
            if isinstance(val, dict):
                pass
            elif isinstance(val, str):
                try:
                    data['principal_place'] = json.loads(val)
                except json.JSONDecodeError:
                    return Response(
                        {"principal_place": ["Value must be valid JSON."]},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            else:
                return Response(
                    {"principal_place": ["Value must be a JSON object or string."]},
                    status=status.HTTP_400_BAD_REQUEST
                )

        serializer = PrincipalPlaceDetailsSerializer(data=data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'GET':
        objs = PrincipalPlaceDetails.objects.all()
        serializer = PrincipalPlaceDetailsSerializer(objs, many=True)
        return Response(serializer.data)

@api_view(['GET'])
def principal_place_details_by_service_request(request):
    service_request_id = request.query_params.get('service_request_id')
    if not service_request_id:
        return Response({"error": "Missing service_request_id"}, status=status.HTTP_400_BAD_REQUEST)

    objs = PrincipalPlaceDetails.objects.filter(service_request_id=service_request_id)
    if not objs.exists():
        return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)

    serializer = PrincipalPlaceDetailsSerializer(objs, many=True)
    return Response(serializer.data)


@api_view(['GET', 'PUT', 'DELETE'])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def principal_place_details_detail(request, pk):
    try:
        instance = PrincipalPlaceDetails.objects.get(pk=pk)
    except PrincipalPlaceDetails.DoesNotExist:
        return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = PrincipalPlaceDetailsSerializer(instance)
        return Response(serializer.data)

    elif request.method == 'PUT':
        data = request.data.copy()

        # Parse JSON again if updating principal_place
        if 'principal_place' in data and isinstance(data['principal_place'], str):
            try:
                data['principal_place'] = json.loads(data['principal_place'])
            except json.JSONDecodeError:
                return Response(
                    {"principal_place": ["Value must be valid JSON."]},
                    status=status.HTTP_400_BAD_REQUEST
                )

        serializer = PrincipalPlaceDetailsSerializer(instance, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# PromoterSignatoryDetails Views
@api_view(['POST', 'GET'])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def promoter_signatory_details_list_create(request):
    if request.method == 'POST':
        serializer = PromoterSignatoryDetailsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'GET':
        objs = PromoterSignatoryDetails.objects.all()
        serializer = PromoterSignatoryDetailsSerializer(objs, many=True)
        return Response(serializer.data)


@api_view(['GET'])
def promoter_signatory_details_by_service_request(request):
    service_request_id = request.query_params.get('service_request_id')
    if not service_request_id:
        return Response({"error": "Missing service_request_id"}, status=status.HTTP_400_BAD_REQUEST)

    queryset = PromoterSignatoryDetails.objects.filter(service_request_id=service_request_id)
    if not queryset.exists():
        return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)

    serializer = PromoterSignatoryDetailsSerializer(queryset, many=True)
    return Response(serializer.data)


@api_view(['GET', 'PUT', 'DELETE'])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def promoter_signatory_details_detail(request, pk):
    try:
        instance = PromoterSignatoryDetails.objects.get(pk=pk)
    except PromoterSignatoryDetails.DoesNotExist:
        return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = PromoterSignatoryDetailsSerializer(instance)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = PromoterSignatoryDetailsSerializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)



# GSTReviewFilingCertificate Views

@api_view(['POST', 'GET'])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def gst_review_filing_certificate_list_create(request):
    if request.method == 'POST':
        serializer = GSTReviewFilingCertificateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'GET':
        objs = GSTReviewFilingCertificate.objects.all()
        serializer = GSTReviewFilingCertificateSerializer(objs, many=True)
        return Response(serializer.data)


@api_view(['GET'])
def gst_review_filing_certificate_by_service_request(request):
    service_request_id = request.GET.get('service_request_id')

    if not service_request_id:
        return Response({"error": "Missing service_request_id"}, status=400)

    certificates = GSTReviewFilingCertificate.objects.filter(service_request_id=service_request_id)

    serializer = GSTReviewFilingCertificateSerializer(certificates, many=True)
    return Response(serializer.data)


@api_view(['GET', 'PUT', 'DELETE'])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def gst_review_filing_certificate_detail(request, pk):
    try:
        instance = GSTReviewFilingCertificate.objects.get(pk=pk)
    except GSTReviewFilingCertificate.DoesNotExist:
        return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = GSTReviewFilingCertificateSerializer(instance)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = GSTReviewFilingCertificateSerializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        # Cleanup file if any attached
        file_fields = ['certificate_file']  # replace with actual file field name if exists
        for field in file_fields:
            file_obj = getattr(instance, field, None)
            if file_obj and os.path.isfile(file_obj.path):
                os.remove(file_obj.path)

        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)