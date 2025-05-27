from rest_framework.decorators import api_view, parser_classes
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from .serializers import *
import json
from .helpers import *
from rest_framework.decorators import api_view, permission_classes, parser_classes


def handle_dynamic_tasks(personal_info_instance):
    income_tasks = {
        "salary_income": "Salary Income",
        "other_income": "Other Income",
        "house_property_income": "House Property Income",
        "foreign_income": "Foreign Income",
        "interest_income": "Interest Income",
        "dividend_income": "Dividend Income",
        "gift_income": "Gift Income",
        "family_pension_income": "Family Pension Income",
        "agriculture_income": "Agriculture Income",
        "winning_income": "Winning Income",
        "nri_details": "NRI Employee Salary",
    }

    for field, category_name in income_tasks.items():
        if getattr(personal_info_instance, field) == 'yes':
            exists = ServiceTask.objects.filter(
                service_request=personal_info_instance.service_request,
                service_type=personal_info_instance.service_type,
                category_name=category_name
            ).exists()

            if not exists:
                ServiceTask.objects.create(
                    service_request=personal_info_instance.service_request,
                    service_type=personal_info_instance.service_type,
                    category_name=category_name,
                    client=personal_info_instance.service_request.user,
                    assignee=personal_info_instance.assignee,
                    reviewer=personal_info_instance.reviewer,
                    status="in progress",
                    priority="medium"
                )


@api_view(['GET', 'POST'])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def personal_information_list(request):
    if request.method == 'GET':
        records = PersonalInformation.objects.all()
        serializer = PersonalInformationSerializer(records, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = PersonalInformationSerializer(data=request.data)
        if serializer.is_valid():
            personal_info = serializer.save()
            handle_dynamic_tasks(personal_info)
            return Response(PersonalInformationSerializer(personal_info).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def personal_information_detail(request, pk):
    try:
        record = PersonalInformation.objects.get(pk=pk)
    except PersonalInformation.DoesNotExist:
        return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = PersonalInformationSerializer(record)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = PersonalInformationSerializer(record, data=request.data, partial=True)
        if serializer.is_valid():
            personal_info = serializer.save()
            handle_dynamic_tasks(personal_info)
            return Response(PersonalInformationSerializer(personal_info).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        record.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def personal_information_by_service_request(request):
    service_request_id = request.query_params.get('service_request_id')
    service_task_id = request.query_params.get('service_task_id')

    if not service_request_id and not service_task_id:
        return Response(
            {"error": "Provide either 'service_request_id' or 'service_task_id' as a query parameter."},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        if service_request_id:
            instance = PersonalInformation.objects.get(service_request_id=service_request_id)
        else:
            instance = PersonalInformation.objects.get(service_task_id=service_task_id)
    except PersonalInformation.DoesNotExist:
        return Response({"error": "No matching BusinessLocationProofs found."}, status=status.HTTP_404_NOT_FOUND)

    serializer = PersonalInformationSerializer(instance)
    return Response(serializer.data)


@api_view(['GET', 'POST'])
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


@api_view(['GET'])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def get_review_filing_certificate(request):
    """
    Retrieve ReviewFilingCertificate based on either service_request_id or service_task_id.
    """
    service_request_id = request.query_params.get('service_request_id')
    service_task_id = request.query_params.get('service_task_id')

    if not service_request_id and not service_task_id:
        return Response(
            {"error": "Provide either 'service_request_id' or 'service_task_id' as a query parameter."},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        if service_request_id:
            instance = ReviewFilingCertificate.objects.get(service_request_id=service_request_id)
        else:
            instance = ReviewFilingCertificate.objects.get(service_task_id=service_task_id)
    except ReviewFilingCertificate.DoesNotExist:
        return Response({"error": "No matching ReviewFilingCertificate found."}, status=status.HTTP_404_NOT_FOUND)

    serializer = ReviewFilingCertificateSerializer(instance)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def service_request_tasks_views(request):
    try:
        service_request_id = request.query_params.get('service_request_id')
        service_request = ServiceRequest.objects.get(id=service_request_id)
        tasks = ServiceTask.objects.filter(service_request=service_request)
        serializer = ServiceTaskWithDataSerializer(tasks, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    except ServiceRequest.DoesNotExist:
        return Response(
            {'error': 'Service request not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


TASK_MODEL_SERIALIZER_MAP = {
    "Personal Information": (PersonalInformation, PersonalInformationSerializer, False),
    "Tax Paid Details": (TaxPaidDetails, TaxPaidDetailsSerializer, False),
    "Deductions": (Deductions, DeductionsSerializer, False),
    "Review Filing Certificate": (ReviewFilingCertificate, ReviewFilingCertificateSerializer, False),

    # Multiple entries expected
    "Other Income": (OtherIncomeDetails, OtherIncomeDetailsSerializer, True),
    "Gift Income": (GiftIncomeDetails, GiftIncomeDetailsSerializer, True),
    "Foreign Income": (ForeignIncome, ForeignIncomeSerializer, True),
    "Dividend Income": (DividendIncome, DividendIncomeSerializer, True),
    "Interest Income": (InterestIncome, InterestIncomeSerializer, True),
    "Salary Income": (SalaryIncome, SalaryIncomeSerializer, True),
    "NRI Employee Salary": (NRIEmployeeSalaryDetails, NRIEmployeeSalaryDetailsSerializer, True),
    "House Property Income": (HousePropertyIncomeDetails, HousePropertyIncomeDetailsSerializer, True),
    "Family Pension Income": (FamilyPensionIncome, FamilyPensionIncomeSerializer, True),
    "Winning Income": (WinningIncome, WinningIncomeSerializer, True),
    "Agriculture Income": (AgricultureIncome, AgricultureIncomeSerializer, True),
}


@api_view(['GET'])
def get_service_request_full_data(request, service_request_id):
    try:
        service_request = ServiceRequest.objects.get(pk=service_request_id)
    except ServiceRequest.DoesNotExist:
        return Response({'error': 'ServiceRequest not found'}, status=status.HTTP_404_NOT_FOUND)

    tasks = service_request.service_tasks.all()
    full_data = {}

    for task in tasks:
        category_name = task.category_name.strip()
        config = TASK_MODEL_SERIALIZER_MAP.get(category_name)

        task_info = {
            "task_id": task.id,
            "category_name": category_name,
            "status": task.status,
            "priority": task.priority,
            "due_date": task.due_date,
            "assignee": task.assignee.id if task.assignee else None,
            "reviewer": task.reviewer.id if task.reviewer else None,
            "data": None
        }

        if config:
            model_class, serializer_class, is_multiple = config

            queryset = model_class.objects.filter(
                service_request=service_request,
                service_task=task
            )

            if queryset.exists():
                task_info["data"] = (
                    serializer_class(queryset, many=True).data if is_multiple
                    else serializer_class(queryset.first()).data
                )
            else:
                task_info["data"] = [] if is_multiple else None
        else:
            task_info["data"] = "No model/serializer mapping defined"

        full_data[category_name] = task_info

    return Response({
        "service_request": service_request.id,
        "client": service_request.user.id,
        "tasks_data": full_data
    })

