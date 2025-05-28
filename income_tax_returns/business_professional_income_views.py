from rest_framework import status
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.response import Response
from django.db import transaction
from .models import BusinessProfessionalIncome, BusinessProfessionalIncomeDocument
from .serializers import *


@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def upsert_business_professional_income_with_files(request):
    service_request_id = request.data.get('service_request')
    if not service_request_id:
        return Response({"error": "Missing service_request"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        instance = BusinessProfessionalIncome.objects.get(service_request_id=service_request_id)
        serializer = BusinessProfessionalIncomeSerializer(instance, data=request.data, partial=True)
    except BusinessProfessionalIncome.DoesNotExist:
        serializer = BusinessProfessionalIncomeSerializer(data=request.data)

    if serializer.is_valid():
        with transaction.atomic():
            income_instance = serializer.save()

            doc_map = {
                'form26as_files': '26AS',
                'ais_files': 'AIS',
                'gst_returns_files': 'GST Returns',
                'bank_statements_files': 'Bank Statements',
                'other_files': 'Other'
            }

            for field_name, doc_type in doc_map.items():
                files = request.FILES.getlist(field_name)
                for file in files:
                    BusinessProfessionalIncomeDocument.objects.create(
                        business_professional_income=income_instance,
                        document_type=doc_type,
                        file=file
                    )

            return Response({
                "message": "Business Professional Income details saved successfully"
            }, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def get_business_professional_income(request, service_request_id):
    try:
        instance = BusinessProfessionalIncome.objects.get(service_request__id=service_request_id)
        serializer = BusinessProfessionalIncomeSerializer(instance)
        documents = instance.documents.all()
        document_serializer = BusinessProfessionalIncomeDocumentSerializer(documents, many=True)

        return Response({
            "data": serializer.data,
            "documents": document_serializer.data
        }, status=status.HTTP_200_OK)

    except BusinessProfessionalIncome.DoesNotExist:
        return Response({"error": "Data not found"}, status=status.HTTP_404_NOT_FOUND)


@api_view(['DELETE'])
def delete_business_professional_income(request, service_request_id):
    try:
        instance = BusinessProfessionalIncome.objects.get(service_request__id=service_request_id)
        instance.delete()
        return Response({"message": "Deleted successfully"}, status=status.HTTP_200_OK)

    except BusinessProfessionalIncome.DoesNotExist:
        return Response({"error": "Record not found"}, status=status.HTTP_404_NOT_FOUND)


@api_view(['DELETE'])
def delete_business_professional_income_file(request, file_id):
    try:
        file = BusinessProfessionalIncomeDocument.objects.get(id=file_id)
        file.delete()
        return Response({"message": "File deleted"}, status=status.HTTP_200_OK)

    except BusinessProfessionalIncomeDocument.DoesNotExist:
        return Response({"error": "File not found"}, status=status.HTTP_404_NOT_FOUND)
