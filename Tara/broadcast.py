# broadcast.py
from asyncio.log import logger
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from payroll.models import EmployeeManagement

_channel = get_channel_layer()


def broadcast_to_employee(employee_id: int, payload: dict):
    """
    Sends payload to the employee-specific group.
    Your consumer must add connections to group: f"user_{employee_id}"
    """
    async_to_sync(_channel.group_send)(
        f"user_{employee_id}",
        {"type": "send_attendance_update", "payload": payload}
    )


def broadcast_to_business(business_id: int, payload: dict):
    """
    Sends payload to the whole business/team group.
    Your consumer must add connections to group: f"business_{business_id}"
    """
    async_to_sync(_channel.group_send)(
        f"business_{business_id}",
        {"type": "send_attendance_update", "payload": payload}
    )


def broadcast_leave_notification_to_employee(employee_id: int, payload: dict):
    """
    Sends leave notification to employee's WebSocket group
    Args:
        employee_id: EmployeeManagement ID (not User ID)
        payload: Notification data
    """
    try:
        # Validate employee exists
        employee = EmployeeManagement.objects.get(id=employee_id)
        
        channel_layer = get_channel_layer()
        group_name = f"user_{employee_id}"
        
        # Add employee info to payload
        payload.update({
            "employee_info": {
                "id": employee.id,
                "name": f"{employee.first_name} {employee.last_name}",
                "designation": employee.designation.designation_name if employee.designation else "N/A"
            }
        })

        async_to_sync(channel_layer.group_send)(
            group_name,
            {
                "type": "send_leave_notification",
                "payload": payload
            }
        )
    except EmployeeManagement.DoesNotExist:
        logger.error(f"Employee {employee_id} not found for notification")
    except Exception as e:
        logger.error(f"Error broadcasting notification: {str(e)}")