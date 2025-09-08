from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from schedule import logger
from .models import LeaveApplication, EmployeeLeaveBalance, EmployeeReportingManager, EmployeeCredentials, current_financial_year
from .serializers import LeaveApplicationSerializer, EmployeeLeaveBalanceSerializer
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from datetime import datetime, timedelta
import calendar
from datetime import date
from Tara.broadcast import broadcast_leave_notification_to_employee
from .utils import format_time_style
from django.db import transaction
import logging
from payroll.models import (
    LeaveManagement, LeaveApplication, EmployeeManagement,
    PayrollOrg, LeaveNotification
)
from payroll.serializers import (
    LeaveManagementSerializer, LeaveApplicationSerializer, LeaveNotificationSerializer
)
from usermanagement.models import Users

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_leave_notifications(request):
    """Get all leave notifications for the reviewer"""
    try:
        # Get employee record for logged-in user
        employee = EmployeeManagement.objects.get(
            user=request.user,
            payroll__business=request.user.active_context.business
        )

        # Get notifications using employee instead of user
        notifications = LeaveNotification.objects.select_related(
            'leave_application',
            'leave_application__employee',
            'leave_application__leave_type',
            'reviewer'  # Add reviewer to select_related
        ).filter(
            reviewer=employee  # Filter by employee instead of user
        ).order_by('-created_at')

        response_data = []
        for notification in notifications:
            leave = notification.leave_application
            leave_employee = leave.employee  # This is EmployeeManagement instance

            created_time = format_time_style(notification.created_at)
            read_time = format_time_style(notification.read_at) if notification.read_at else None

            notification_data = {
                "type": "leave_notification",
                "action": "view_leave",
                "notification_id": notification.id,
                "title": f"{leave_employee.first_name} {leave_employee.last_name} - {leave.leave_type.name_of_leave} Request",
                "data": {
                    "employee": {
                        "id": leave_employee.id,
                        "name": f"{leave_employee.first_name} {leave_employee.last_name}",
                        "designation": leave_employee.designation.designation_name if leave_employee.designation else "N/A",
                        "department": leave_employee.department.dept_name if leave_employee.department else "N/A"
                    },
                    "leave": {
                        "id": leave.id,
                        "type": leave.leave_type.name_of_leave,
                        "days": (leave.end_date - leave.start_date).days + 1,
                        "start_date": leave.start_date.strftime("%d %b %Y"),
                        "end_date": leave.end_date.strftime("%d %b %Y"),
                        "reason": leave.reason,
                        "status": leave.status
                    },
                    "created_at": created_time
                },
                "message": notification.message,
                "is_read": notification.is_read,
                "read_at": read_time,
            }
            response_data.append(notification_data)

        return Response({
            "employee_id": employee.id,
            "notifications": response_data,
            "unread_count": sum(1 for n in notifications if not n.is_read)
        })

    except Exception as e:
        logger.error(f"Error fetching notifications: {str(e)}", exc_info=True)
        return Response(
            {
                "type": "error",
                "message": "Failed to fetch notifications",
                "detail": str(e)
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

def get_unread_count_for_reviewer(employee_id):
    """Get unread count for an employee"""
    return LeaveNotification.objects.filter(
        reviewer_id=employee_id, 
        is_read=False
    ).count()

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def unread_leave_notification_count(request):
    try:
        employee = EmployeeManagement.objects.get(
            user=request.user,
            payroll__business=request.user.active_context.business
        )
        count = LeaveNotification.objects.filter(
            reviewer=employee,  # Use employee instead of user
            is_read=False
        ).count()
        return Response({
            "employee_id": employee.id,
            "unread_count": count
        })
    except EmployeeManagement.DoesNotExist:
        return Response(
            {"error": "Employee record not found"}, 
            status=status.HTTP_404_NOT_FOUND
        )

def create_notification_data(notif, recipient_employee):
    """Format notification data for a single notification"""
    leave_app = notif.leave_application
    emp = leave_app.employee  # This is already EmployeeManagement instance
    is_reviewer = leave_app.reviewer_id == recipient_employee.id

    return {
        "type": "leave_notification",
        "action": "new_leave",
        "notification_id": notif.id,
        "title": f"{emp.first_name} {emp.last_name} - {leave_app.leave_type.name_of_leave} Request",
        "data": {
            "employee": {
                "id": emp.id,
                "name": f"{emp.first_name} {emp.last_name}",
                "designation": emp.designation.designation_name if emp.designation else "N/A",
                "department": emp.department.dept_name if emp.department else "N/A",
                "role": "Reviewer" if is_reviewer else "CC"
            },
            "leave": {
                "id": leave_app.id,
                "type": leave_app.leave_type.name_of_leave,
                "days": (leave_app.end_date - leave_app.start_date).days + 1,
                "period": f"{leave_app.start_date.strftime('%d %b %Y')} to {leave_app.end_date.strftime('%d %b %Y')}",
                "reason": leave_app.reason,
                "status": leave_app.status
            }
        },
        "message": notif.message,
        "created_at": format_time_style(notif.created_at),
        "is_read": notif.is_read,
        "read_at": format_time_style(notif.read_at) if notif.read_at else None
    }

def get_notification_message(leave, employee_name, employee_designation, employee_department, days):
    """Create notification message"""
    return (
        f"{employee_name}, {employee_designation} from the {employee_department} department, "
        f"has requested {days} day{'s' if days > 1 else ''} of {leave.leave_type.name_of_leave}. "
        f"The leave period is from {leave.start_date.strftime('%d %b %Y')} to {leave.end_date.strftime('%d %b %Y')}. "
        f"Reason for leave: {leave.reason}"
    )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@transaction.atomic
def apply_leave(request):
    try:
        # Get employee record for applicant
        employee = EmployeeManagement.objects.get(
            user=request.user,
            payroll__business=request.user.active_context.business
        )

        # Validate employee
        if str(employee.id) != str(request.data.get('employee')):
            return Response(
                {'error': 'You are not allowed to apply leave for another employee.'},
                status=status.HTTP_403_FORBIDDEN
            )

        # Get reviewing team with proper error handling
        reviewing_team = EmployeeReportingManager.objects.select_related(
            'reporting_manager',
            'head_of_department'
        ).get(employee=employee)

        if not reviewing_team.reporting_manager:
            return Response({
                'error': 'No reporting manager assigned.',
                'message': 'Please contact HR to set up your reporting manager.',
                'employee_id': employee.id
            }, status=status.HTTP_400_BAD_REQUEST)

        # Prepare data with reviewer's EmployeeManagement record
        data = request.data.copy()
        manager = reviewing_team.reporting_manager  # This is already EmployeeManagement
        data['reviewer'] = manager.id  # Use EmployeeManagement ID

        # Set CC list with EmployeeManagement IDs
        cc_list = []
        if reviewing_team.head_of_department and reviewing_team.head_of_department.id != manager.id:
            cc_list.append(reviewing_team.head_of_department.id)
        data.setlist('cc_to', cc_list)

        # Validate and save leave application
        serializer = LeaveApplicationSerializer(data=data, context={'request': request})
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            # Save leave application
            leave = serializer.save(employee=employee)
            
            # Get reviewer and CC recipients (all EmployeeManagement instances)
            reviewer = leave.reviewer
            cc_recipients = leave.cc_to.all()

            if not (reviewer or cc_recipients.exists()):
                raise ValueError("No reviewer or CC recipients specified")

            # Create notification message
            detailed_message = get_notification_message(
                leave=leave,
                employee_name=f"{employee.first_name} {employee.last_name}",
                employee_designation=employee.designation.designation_name if employee.designation else "N/A",
                employee_department=employee.department.dept_name if employee.department else "N/A",
                days=(leave.end_date - leave.start_date).days + 1
            )

            # Create notifications for all recipients
            recipients_to_notify = set(cc_recipients)
            if reviewer:
                recipients_to_notify.add(reviewer)

            # Bulk create notifications
            notifications = [
                LeaveNotification(
                    leave_application=leave,
                    reviewer=recipient,  # Using EmployeeManagement instance
                    message=detailed_message
                )
                for recipient in recipients_to_notify
            ]
            created_notifications = LeaveNotification.objects.bulk_create(notifications)
            for recipient in recipients_to_notify:
                try:
                    # Create payload for WebSocket
                    payload = {
                        "type": "leave_notification",
                        "action": "new_leave",
                        "notification_id": created_notifications[0].id,
                        "data": {
                            "leave": {
                                "id": leave.id,
                                "type": leave.leave_type.name_of_leave,
                                "days": (leave.end_date - leave.start_date).days + 1,
                                "start_date": leave.start_date.strftime("%d %b %Y"),
                                "end_date": leave.end_date.strftime("%d %b %Y"),
                                "status": leave.status,
                                "reason": leave.reason
                            },
                            "employee": {
                                "id": employee.id,
                                "name": f"{employee.first_name} {employee.last_name}",
                                "designation": employee.designation.designation_name if employee.designation else "N/A",
                                "department": employee.department.dept_name if employee.department else "N/A"
                            }
                        },
                        "message": detailed_message,
                        "created_at": format_time_style(timezone.now())
                    }

                    # Get current unread count for recipient
                    unread_count = LeaveNotification.objects.filter(
                        reviewer=recipient,
                        is_read=False
                    ).count()

                    # Add unread count to payload
                    payload["unread_count"] = unread_count

                    # Broadcast using employee ID from EmployeeManagement
                    from Tara.broadcast import broadcast_leave_notification_to_employee
                    broadcast_leave_notification_to_employee(recipient.id, payload)

                    logger.info(f"Sent notification to employee {recipient.id}")

                except Exception as e:
                    logger.error(f"Failed to send WebSocket notification to {recipient.id}: {str(e)}")
                    continue

            return Response({
                "data": LeaveNotificationSerializer(created_notifications[0]).data,
                "id": leave.id,
                "message": "Leave application submitted successfully.",
                "status": leave.status
            }, status=status.HTTP_201_CREATED)

    except EmployeeReportingManager.DoesNotExist:
        return Response({
            'error': 'Reporting structure not found.',
            'message': 'Please contact HR to set up your reporting manager.',
            'employee_id': employee.id if 'employee' in locals() else None
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"Error processing leave application: {str(e)}", exc_info=True)
        return Response({
            "error": f"Failed to process leave application: {str(e)}"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def current_financial_year_range():
    today = date.today()
    year = today.year
    if today.month < 4:
        start = date(year - 1, 4, 1)
        end = date(year, 3, 31)
    else:
        start = date(year, 4, 1)
        end = date(year + 1, 3, 31)
    return start, end


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_leave_applications(request):
    try:
        user = request.user
        payroll = PayrollOrg.objects.get(business=user.active_context.business)
        employee = EmployeeManagement.objects.get(payroll=payroll, user=user)
    except (PayrollOrg.DoesNotExist, EmployeeManagement.DoesNotExist):
        return Response({'error': 'Invalid employee credentials'}, status=status.HTTP_401_UNAUTHORIZED)

    start_date, end_date = current_financial_year_range()

    # Add proper select_related for all related fields
    leaves = LeaveApplication.objects.select_related(
        'employee',
        'leave_type',
        'reviewer'
    ).prefetch_related(
        'cc_to'  # For ManyToMany relationship
    ).filter(
        employee=employee,  # Use employee instance directly
        applied_on__date__gte=start_date,
        applied_on__date__lte=end_date
    ).order_by('-applied_on')

    serializer = LeaveApplicationSerializer(leaves, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def handle_leave_action(request, leave_id):
    try:
        # Get employee management record for the logged-in user
        employee = EmployeeManagement.objects.get(
            user=request.user,
            payroll__business=request.user.active_context.business
        )
    except EmployeeManagement.DoesNotExist:
        return Response(
            {'error': 'No employee record found for logged in user'}, 
            status=status.HTTP_404_NOT_FOUND
        )

    try:
        # Get leave application with all related data
        leave = LeaveApplication.objects.select_related(
            'employee', 
            'reviewer',
            'leave_type'
        ).prefetch_related(
            'cc_to'
        ).get(id=leave_id)
    except LeaveApplication.DoesNotExist:
        return Response(
            {'error': 'Leave application not found.'}, 
            status=status.HTTP_404_NOT_FOUND
        )

    action = request.data.get('action')
    comment = request.data.get('comment', '')

    if action not in ['approve', 'reject', 'cancel']:
        return Response(
            {'error': 'Invalid action. Must be approve, reject, or cancel.'}, 
            status=status.HTTP_400_BAD_REQUEST
        )

    # Debug logging
    logger.info(f"Action request details:")
    logger.info(f"Employee ID: {employee.id}")
    logger.info(f"Leave reviewer ID: {leave.reviewer_id}")
    logger.info(f"Leave employee ID: {leave.employee_id}")
    logger.info(f"CC list: {list(leave.cc_to.values_list('id', flat=True))}")

    # Handle rejection or approval
    if action in ['approve', 'reject']:
        # Check if user is reviewer
        if leave.reviewer_id == employee.id:
            is_authorized = True
        # Check if user is in CC list
        elif leave.cc_to.filter(id=employee.id).exists():
            is_authorized = True
        # Check if user is reporting manager of the leave applicant
        else:
            try:
                is_reporting_manager = EmployeeReportingManager.objects.filter(
                    employee=leave.employee,
                    reporting_manager=employee
                ).exists()
                is_authorized = is_reporting_manager
            except Exception as e:
                logger.error(f"Error checking reporting manager: {e}")
                is_authorized = False

        if not is_authorized:
            return Response({
                'error': 'You are not authorized to perform this action.',
                'employee_id': employee.id,
                'reviewer_id': leave.reviewer_id,
                'cc_list': list(leave.cc_to.values_list('id', flat=True))
            }, status=status.HTTP_403_FORBIDDEN)

        if leave.status != 'pending':
            return Response(
                {'error': f'Cannot {action} a leave with status {leave.status}.'}, 
                status=status.HTTP_400_BAD_REQUEST
            )


        leave.reviewer = employee
        leave.reviewed_on = timezone.now()
        leave.reviewer_comment = comment

        if action == 'approve':
            # Check leave balance before approval
            leave_days = (leave.end_date - leave.start_date).days + 1
            try:
                leave_balance = EmployeeLeaveBalance.objects.get(
                    employee=leave.employee,
                    leave_type=leave.leave_type,
                    financial_year=current_financial_year()
                )

                if leave_balance.leave_remaining < leave_days:
                    return Response({
                        'error': 'Insufficient leave balance',
                        'available_balance': leave_balance.leave_remaining,
                        'requested_days': leave_days
                    }, status=status.HTTP_400_BAD_REQUEST)

            except EmployeeLeaveBalance.DoesNotExist:
                return Response({
                    'error': 'No leave balance found for this leave type'
                }, status=status.HTTP_400_BAD_REQUEST)

            leave.status = 'approved'
            message = 'Leave approved successfully.'
        else:
            if not comment:
                return Response(
                    {'error': 'Comment is required for rejection.'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            leave.status = 'rejected'
            message = 'Leave rejected successfully.'

    # Handle cancellation
    elif action == 'cancel':
        if leave.employee_id != employee.id:
            return Response(
                {'error': 'You can only cancel your own leave.'}, 
                status=status.HTTP_403_FORBIDDEN
            )

        if leave.status != 'pending':
            return Response(
                {'error': 'Only pending leaves can be cancelled.'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        leave.status = 'cancelled'
        message = 'Leave cancelled successfully.'

    # Save changes
    with transaction.atomic():
        leave.reviewer = employee
        leave.reviewed_on = timezone.now()
        leave.reviewer_comment = comment
        leave.save()

        # Create notification
        if action in ['approve', 'reject']:
            notification_message = f"Your leave has been {action}ed"
            if comment:
                notification_message += f"\nComment: {comment}"

            LeaveNotification.objects.create(
                leave_application=leave,
                reviewer=leave.employee,
                message=notification_message
            )

            # For approvals, add leave balance info to notification
            if action == 'approve':
                try:
                    updated_balance = EmployeeLeaveBalance.objects.get(
                        employee=leave.employee,
                        leave_type=leave.leave_type,
                        financial_year=current_financial_year()
                    )
                    notification_message += f"\nRemaining balance: {updated_balance.leave_remaining} days"
                except EmployeeLeaveBalance.DoesNotExist:
                    pass

    serializer = LeaveApplicationSerializer(leave)
    return Response({
        'message': message,
        'data': serializer.data,
        'leave_days': leave_days if action == 'approve' else None,
        'remaining_balance': updated_balance.leave_remaining if action == 'approve' else None
    }, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def reject_leave(request, leave_id):
    try:
        # Get employee management record for the logged-in user
        employee = EmployeeManagement.objects.get(
            user=request.user,
            payroll__business=request.user.active_context.business
        )
    except EmployeeManagement.DoesNotExist:
        return Response(
            {'error': 'No employee record found for logged in user'}, 
            status=status.HTTP_404_NOT_FOUND
        )

    try:
        leave = LeaveApplication.objects.select_related(
            'employee',
            'reviewer'
        ).prefetch_related(
            'cc_to'
        ).get(id=leave_id)
    except LeaveApplication.DoesNotExist:
        return Response(
            {'error': 'Leave application not found.'}, 
            status=status.HTTP_404_NOT_FOUND
        )

    # Check if the employee is reviewer or in cc list
    is_reviewer = leave.reviewer_id == employee.id
    is_cc = leave.cc_to.filter(id=employee.id).exists()
    
    # Check if employee is reporting manager
    is_reporting_manager = EmployeeReportingManager.objects.filter(
        employee=leave.employee,
        reporting_manager=employee
    ).exists()

    if not (is_reviewer or is_cc or is_reporting_manager):
        return Response({
            'error': 'You are not authorized to reject this leave.',
            'employee_id': employee.id,
            'reviewer_id': leave.reviewer_id,
            'cc_list': list(leave.cc_to.values_list('id', flat=True))
        }, status=status.HTTP_403_FORBIDDEN)

    # Only allow rejection if leave is still pending
    if leave.status != 'pending':
        return Response(
            {'error': f'Cannot reject a leave with status {leave.status}.'}, 
            status=status.HTTP_400_BAD_REQUEST
        )

    rejection_reason = request.data.get('comment', 'Rejected by reviewer.')
    if not rejection_reason:
        return Response(
            {'error': 'Comment is required for rejection.'}, 
            status=status.HTTP_400_BAD_REQUEST
        )

    # Use transaction to ensure data consistency
    with transaction.atomic():
        # Update leave status
        leave.status = 'rejected'
        leave.reviewer = employee
        leave.reviewer_comment = rejection_reason
        leave.reviewed_on = timezone.now()
        leave.save()

        # Create notification for leave applicant
        notification_message = "Your leave has been rejected"
        if rejection_reason:
            notification_message += f"\nComment: {rejection_reason}"

        LeaveNotification.objects.create(
            leave_application=leave,
            reviewer=leave.employee,  # Send to leave applicant
            message=notification_message
        )

    serializer = LeaveApplicationSerializer(leave)
    return Response({
        'message': 'Leave application rejected successfully.',
        'data': serializer.data
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cancel_leave(request, leave_id):
    try:
        # Get employee management record for logged-in user
        employee = EmployeeManagement.objects.get(
            user=request.user,
            payroll__business=request.user.active_context.business
        )
    except EmployeeManagement.DoesNotExist:
        return Response(
            {'error': 'No employee record found for logged in user'}, 
            status=status.HTTP_404_NOT_FOUND
        )

    try:
        # Get leave application with employee relationship
        leave = LeaveApplication.objects.select_related(
            'employee',
            'leave_type'
        ).get(
            pk=leave_id,
            employee=employee  # Use employee instance instead of user
        )
    except LeaveApplication.DoesNotExist:
        return Response(
            {'error': 'Leave application not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )

    # Check if leave is pending
    if leave.status != 'pending':
        return Response(
            {'error': 'Only pending leaves can be cancelled'}, 
            status=status.HTTP_400_BAD_REQUEST
        )

    # Use transaction for data consistency
    with transaction.atomic():
        # Update leave status
        leave.status = 'cancelled'
        leave.reviewed_on = timezone.now()
        leave.save(update_fields=['status', 'reviewed_on'])

        # Create notification for reviewers and CC
        notification_message = f"Leave application cancelled by {employee.first_name} {employee.last_name}"
        
        # Get all recipients (reviewer and CC)
        recipients = set(leave.cc_to.all())
        if leave.reviewer:
            recipients.add(leave.reviewer)

        # Create notifications
        for recipient in recipients:
            LeaveNotification.objects.create(
                leave_application=leave,
                reviewer=recipient,
                message=notification_message
            )

    serializer = LeaveApplicationSerializer(leave)
    return Response({
        'message': 'Leave cancelled successfully',
        'data': serializer.data
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_monthly_leaves(request, year, month):
    """Get leaves for specific month (format: YYYY/MM)"""
    try:
        # Get employee record for the logged-in user
        employee = EmployeeManagement.objects.get(
            user=request.user,
            payroll__business=request.user.active_context.business
        )
    except EmployeeManagement.DoesNotExist:
        return Response(
            {'error': 'Employee record not found for logged in user'}, 
            status=status.HTTP_401_UNAUTHORIZED
        )

    try:
        # Validate month/year
        month_start = datetime(year=year, month=month, day=1).date()
        next_month = month + 1 if month < 12 else 1
        next_year = year if month < 12 else year + 1
        month_end = datetime(year=next_year, month=next_month, day=1).date() - timedelta(days=1)
    except ValueError:
        return Response(
            {'error': 'Invalid month/year'}, 
            status=status.HTTP_400_BAD_REQUEST
        )

    # Get leaves with optimized queries
    leaves = LeaveApplication.objects.select_related(
        'leave_type',
        'reviewer'
    ).filter(
        employee=employee,
        start_date__lte=month_end,
        end_date__gte=month_start
    ).order_by('-start_date')  # Most recent first

    serializer = LeaveApplicationSerializer(leaves, many=True)
    
    return Response({
        'month': f"{year}-{month:02d}",
        'employee_id': employee.id,
        'count': leaves.count(),
        'results': serializer.data
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_current_month_leaves(request):
    """Get leaves for current month"""
    today = timezone.now().date()
    return get_monthly_leaves(request._request, today.year, today.month)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_leave_summary(request, year=None):
    """Get monthly leave summary for a year"""
    try:
        # Get employee through EmployeeManagement
        employee = EmployeeManagement.objects.get(
            user=request.user,
            payroll__business=request.user.active_context.business
        )
    except EmployeeManagement.DoesNotExist:
        return Response(
            {'error': 'Employee record not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )

    year = int(year or timezone.now().year)
    
    # Use employee instance in filter
    leaves = LeaveApplication.objects.filter(
        employee=employee,
        start_date__year=year
    ).select_related('leave_type')  # Optimize query

    summary = []
    for month in range(1, 13):
        month_leaves = leaves.filter(start_date__month=month)
        approved = month_leaves.filter(status='approved')

        # Get the first and last date of the month
        start_of_month = datetime(year, month, 1).date()
        last_day = calendar.monthrange(year, month)[1]
        end_of_month = datetime(year, month, last_day).date()

        # Calculate total days for approved leaves
        total_days = sum(
            (min(leave.end_date, end_of_month) - max(leave.start_date, start_of_month)).days + 1
            for leave in approved
            if leave.end_date >= start_of_month and leave.start_date <= end_of_month
        )

        summary.append({
            'month': f"{year}-{month:02d}",
            'total_leaves': month_leaves.count(),
            'approved_leaves': approved.count(),
            'pending_leaves': month_leaves.filter(status='pending').count(),
            'rejected_leaves': month_leaves.filter(status='rejected').count(),
            'total_days': total_days,
            'leaves': [{
                'id': leave.id,
                'leave_type': leave.leave_type.name_of_leave,
                'start_date': leave.start_date,
                'end_date': leave.end_date,
                'status': leave.status
            } for leave in month_leaves]  # Added leave details
        })

    return Response({
        'year': year,
        'employee_id': employee.id,
        'summary': summary
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_my_leave_balances(request):
    """Get leave balances for the currently authenticated employee."""
    try:
        # Get employee record
        employee = EmployeeManagement.objects.get(
            user=request.user,
            payroll__business=request.user.active_context.business
        )
    except EmployeeManagement.DoesNotExist:
        return Response(
            {'error': 'Employee record not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )

    current_fy = current_financial_year()

    try:
        # Get all available leave types for the employee's payroll
        leave_types = LeaveManagement.objects.filter(
            payroll=employee.payroll
        )

        # Get existing leave balances
        leave_balances = EmployeeLeaveBalance.objects.select_related(
            'leave_type'
        ).filter(
            employee=employee,
            financial_year=current_fy
        )

        # Create missing leave balances
        existing_leave_type_ids = leave_balances.values_list('leave_type_id', flat=True)
        
        for leave_type in leave_types:
            if leave_type.id not in existing_leave_type_ids:
                # Calculate pro-rated leaves if applicable
                total_leaves = leave_type.number_of_leaves or 0
                
                if (leave_type.pro_rate_leave_balance_of_new_joinees_based_on_doj 
                    and employee.doj 
                    and total_leaves > 0):
                    
                    start_year, end_year = current_fy.split('-')
                    fy_start = date(int(start_year), 4, 1)
                    fy_end = date(int(end_year), 3, 31)

                    if employee.doj > fy_start:
                        remaining_months = (fy_end.year - employee.doj.year) * 12 + (fy_end.month - employee.doj.month) + 1
                        if leave_type.employee_leave_period == "Monthly":
                            total_leaves = total_leaves * (remaining_months / 12)
                        else:  # Annual
                            total_leaves = round((total_leaves / 12) * remaining_months)

                # Create new balance record
                EmployeeLeaveBalance.objects.create(
                    employee=employee,
                    leave_type=leave_type,
                    financial_year=current_fy,
                    leave_entitled=total_leaves,
                    leave_used=0,
                    leave_remaining=total_leaves
                )

        # Get updated balances
        updated_balances = EmployeeLeaveBalance.objects.select_related(
            'leave_type'
        ).filter(
            employee=employee,
            financial_year=current_fy
        )

        serializer = EmployeeLeaveBalanceSerializer(updated_balances, many=True)
        
        return Response({
            'employee_id': employee.id,
            'employee_name': f"{employee.first_name} {employee.last_name}",
            'financial_year': current_fy,
            'balances': serializer.data
        })

    except Exception as e:
        logger.error(f"Error fetching leave balances: {str(e)}", exc_info=True)
        return Response({
            'error': 'Failed to fetch leave balances',
            'detail': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)