import base64
import numpy as np
from django.utils.timezone import now, localtime, localdate
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import AttendanceLog, AttendanceGeoTag
from .serializers import AttendanceLogSerializer, AttendanceGeoTagSerializer
from rest_framework.decorators import api_view, permission_classes
from datetime import datetime, timedelta, date
from calendar import monthrange
from rest_framework import status
from collections import defaultdict
from usermanagement.models import Users
from Tara.broadcast import broadcast_to_employee, broadcast_to_business
from .attendance_controller import get_payroll_and_employee


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def geo_location_list_create(request):
    if request.method == 'GET':
        geos = AttendanceGeoTag.objects.all()
        serializer = AttendanceGeoTagSerializer(geos, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = AttendanceGeoTagSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_200_OK)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def geo_location_detail(request, pk):
    try:
        geo = AttendanceGeoTag.objects.get(pk=pk)
    except AttendanceGeoTag.DoesNotExist:
        return Response({"error": "GeoLocation not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = AttendanceGeoTagSerializer(geo)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = AttendanceGeoTagSerializer(geo, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_200_OK)

    elif request.method == 'DELETE':
        geo.delete()
        return Response({"message": "GeoLocation deleted"}, status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def geo_locations_details_based_on_payroll_and_worklocation(request):
    payroll_id = request.query_params.get("payroll")
    branch = request.query_params.get("work_location")

    if not payroll_id:
        return Response({"error": "Payroll ID is missing"}, status=status.HTTP_200_OK)

    try:
        geo_locations = AttendanceGeoTag.objects.get(payroll=payroll_id, branch=branch)
        if not geo_locations.exists():
            return Response({"error": "No GeoLocations found for the provided payroll ID."},
                            status=status.HTTP_404_NOT_FOUND)

        serializer = AttendanceGeoTagSerializer(geo_locations)
        return Response(serializer.data, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"error": f"Something went wrong: {str(e)}"}, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def geo_location_check_in(request):
    user = request.user

    if not isinstance(user, Users):
        return Response({'error': 'Invalid employee credentials'}, status=status.HTTP_401_UNAUTHORIZED)

    today = localtime(now()).date()
    location = request.data.get('location', '')
    device_info = request.data.get('device_info', '')

    payroll, employee, error_response = get_payroll_and_employee(request)
    if error_response:
        return error_response

    # Get the latest log for today
    last_log = AttendanceLog.objects.filter(
        employee=employee,
        date=today
    ).order_by('-check_in').first()

    # If last entry exists and not checked out yet — block duplicate check-in
    if last_log and last_log.check_in and not last_log.check_out:
        return Response({'message': 'You must check out before checking in again.'},
                        status=status.HTTP_400_BAD_REQUEST)

    # Else allow new check-in
    new_log = AttendanceLog.objects.create(
        employee=employee,
        date=today,
        check_in=localtime(now()),
        check_in_type='geo',
        location=location,
        device_info=device_info
    )
    # ✅ Send WebSocket notification
    payload = {
        "type": "attendance_update",
        "action": "check_in",
        "record": AttendanceLogSerializer(new_log).data,
    }

    # Push to this employee's devices AND to team viewers
    # 🔔 Broadcast to employee (all their devices)
    # NOTE: If your WS group uses employee_id, pass emp.id; if it uses user_id, pass emp.user_id.
    broadcast_to_employee(employee.id, payload)  # <-- if your consumer uses f"user_{employee_id}"
    # broadcast_to_employee(emp.user_id)   # <-- use this instead if your group is f"user_{user_id}"

    # 📣 Broadcast to the whole business/team
    # business_id = employee_credentials.employee.payroll.business_id
    # broadcast_to_business(business_id, payload)

    serializer = AttendanceLogSerializer(new_log)
    return Response({'message': 'Check-in successful', 'data': payload["record"]}, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def geo_location_check_out(request):
    user = request.user

    if not isinstance(user, Users):
        return Response({'error': 'Invalid employee credentials'}, status=status.HTTP_401_UNAUTHORIZED)

    today = localtime(now()).date()
    payroll, employee, error_response = get_payroll_and_employee(request)
    if error_response:
        return error_response

    # Get the latest check-in with no checkout
    attendance = AttendanceLog.objects.filter(
        employee=employee,
        date=today,
        check_out__isnull=True
    ).order_by('-check_in').first()

    if not attendance:
        return Response({'error': 'No active check-in record found for today'}, status=status.HTTP_404_NOT_FOUND)

    # Check out now
    attendance.check_out = localtime(now())
    attendance.save()
    payload = {
        "type": "attendance_update",
        "action": "check_out",
        "record": AttendanceLogSerializer(attendance).data,
    }

    broadcast_to_employee(employee.id, payload)

    return Response({'message': 'Check-out successful', 'data': payload["record"]}, status=status.HTTP_200_OK)
