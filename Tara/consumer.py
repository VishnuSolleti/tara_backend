# consumers.py
import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from django.utils.timezone import localdate
from channels.db import database_sync_to_async
from django.utils import timezone
from payroll.utils import format_time_style



class AttendanceConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Expect URL like ws://localhost:8000/ws/attendance/7/
        self.employee_id = self.scope["url_route"]["kwargs"]["employee_id"]

        # Join employee-specific group
        self.user_group = f"user_{self.employee_id}"
        await self.channel_layer.group_add(self.user_group, self.channel_name)

        # Optionally: also join their business group if needed
        # For now just user-based
        await self.accept()
        await self.send(text_data=json.dumps({
            "type": "ws_connected",
            "employee_id": self.employee_id
        }))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.user_group, self.channel_name)

    # Server push handler
    async def send_attendance_update(self, event):
        await self.send(text_data=json.dumps(event.get("payload", {})))



logger = logging.getLogger(__name__)

class LeaveNotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """Handle WebSocket connection with authentication"""
        try:
            # Get employee_id from URL route
            self.employee_id = self.scope["url_route"]["kwargs"]["employee_id"]
            logger.info(f"Connection attempt for employee_id: {self.employee_id}")


            # Set up group name and join
            self.user_group = f"user_{self.employee_id}"
            await self.channel_layer.group_add(self.user_group, self.channel_name)
            await self.accept()

            # Send initial data
            initial_notifications = await self.get_all_notifications()
            unread_count = await self.get_unread_count()
            
            await self.send(text_data=json.dumps({
                "type": "connection_established",
                "employee_id": self.employee_id,
                "notifications": initial_notifications,
                "unread_count": unread_count
            }))
            logger.info(f"WebSocket connected for employee_id: {self.employee_id}")

        except Exception as e:
            logger.error(f"Connection error: {str(e)}")
            await self.close()

    async def disconnect(self, close_code):
        """Handle WebSocket disconnection"""
        try:
            if hasattr(self, 'user_group'):
                await self.channel_layer.group_discard(self.user_group, self.channel_name)
                logger.info(f"WebSocket disconnected for employee_id: {self.employee_id}")
        except Exception as e:
            logger.error(f"Disconnect error: {str(e)}")

    async def receive(self, text_data):
        """Handle messages from WebSocket client"""
        try:
            data = json.loads(text_data)
            message_type = data.get('type')

            if message_type == 'mark_read':
                await self.handle_mark_read(data)
            else:
                logger.warning(f"Unknown message type: {message_type}")
                await self.send(text_data=json.dumps({
                    "type": "error",
                    "message": "Unknown message type"
                }))

        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                "type": "error",
                "message": "Invalid JSON format"
            }))
        except Exception as e:
            logger.error(f"Error in receive: {str(e)}")
            await self.send(text_data=json.dumps({
                "type": "error",
                "message": str(e)
            }))

    async def handle_mark_read(self, data):
        """Handle marking notifications as read"""
        notification_id = data.get('notification_id')
        try:
            notification = await self.get_notification(notification_id)
            if notification:
                await self.mark_notification_read(notification)
                await self.send_notification_update()
            else:
                await self.send(text_data=json.dumps({
                    "type": "error",
                    "message": "Notification not found"
                }))

        except Exception as e:
            logger.error(f"Error marking notification read: {str(e)}")
            await self.send(text_data=json.dumps({
                "type": "error",
                "message": "Failed to mark notification as read"
            }))

    async def send_notification_update(self):
        """Send updated notifications data"""
        try:
            notifications = await self.get_all_notifications()
            unread_count = await self.get_unread_count()

            await self.channel_layer.group_send(
                self.user_group,
                {
                    "type": "send_leave_notification",
                    "payload": {
                        "type": "leave_notifications_update",
                        "notifications": notifications,
                        "unread_count": unread_count,
                        "timestamp": format_time_style(timezone.now())
                    }
                }
            )
        except Exception as e:
            logger.error(f"Error sending notification update: {str(e)}")
            raise

    async def send_leave_notification(self, event):
        """Handle sending notifications through WebSocket"""
        try:
            await self.send(text_data=json.dumps(event["payload"]))
            logger.debug(f"Notification sent to employee_id: {self.employee_id}")
        except Exception as e:
            logger.error(f"Error sending notification: {str(e)}")
            await self.send(text_data=json.dumps({
                "type": "error",
                "message": "Error processing notification"
            }))


    @database_sync_to_async
    def get_all_notifications(self):
        """Get all notifications for the reviewer"""
        from payroll.models import LeaveNotification
        
        notifications = LeaveNotification.objects.select_related(
            'leave_application',
            'leave_application__employee',
            'leave_application__leave_type'
        ).prefetch_related(
            'leave_application__employee__designation',
            'leave_application__employee__department'
        ).filter(
            reviewer_id=self.employee_id
        ).order_by('-created_at')

        return [self.format_notification(notif) for notif in notifications]

    def format_notification(self, notif):
        """Format a single notification"""
        leave = notif.leave_application
        employee = leave.employee
            # Get time formatting
        created_time = format_time_style(notif.created_at)
        read_time = format_time_style(notif.read_at) if notif.read_at else None
        return {
            "type": "leave_notification",
            "action": "view_leave",
            "notification_id": notif.id,
            "title": f"{employee.first_name} {employee.last_name} - {leave.leave_type.name_of_leave} Request",
            "data": {
                "employee": {
                    "id": employee.id,
                    "name": f"{employee.first_name} {employee.last_name}",
                    "designation": employee.designation.designation_name if employee.designation else "N/A",
                    "department": employee.department.dept_name if employee.department else "N/A",
                    "role": "Reviewer" if leave.reviewer_id == self.employee_id else "CC"
                },
                "leave": {
                    "id": leave.id,
                    "type": leave.leave_type.name_of_leave,
                    "days": (leave.end_date - leave.start_date).days + 1,
                    "period": f"{leave.start_date.strftime('%d %b %Y')} to {leave.end_date.strftime('%d %b %Y')}",
                    "reason": leave.reason,
                    "status": leave.status
                }
            },
            "message": notif.message,
            "created_at": created_time,
            "is_read": notif.is_read,
            "read_at": read_time
        }

    @database_sync_to_async
    def get_notification(self, notification_id):
        """Get a single notification"""
        from payroll.models import LeaveNotification
        try:
            return LeaveNotification.objects.select_related(
                'leave_application',
                'leave_application__employee'
            ).get(
                id=notification_id,
                reviewer_id=self.employee_id
            )
        except LeaveNotification.DoesNotExist:
            return None

    @database_sync_to_async
    def mark_notification_read(self, notification):
        """Mark a notification as read"""
        notification.is_read = True
        notification.read_at = timezone.now()
        notification.save(update_fields=['is_read', 'read_at'])
        return notification

    @database_sync_to_async
    def get_unread_count(self):
        """Get count of unread notifications"""
        from payroll.models import LeaveNotification
        return LeaveNotification.objects.filter(
            reviewer_id=self.employee_id,
            is_read=False
        ).count()