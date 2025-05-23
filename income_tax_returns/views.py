from rest_framework.decorators import api_view, parser_classes
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from .serializers import *
import json
from .helpers import *
from rest_framework.decorators import api_view, permission_classes, parser_classes


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
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
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
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        record.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

