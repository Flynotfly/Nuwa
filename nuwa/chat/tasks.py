import random

from celery import shared_task
from django.utils.timezone import timezone, datetime, now, timedelta


@shared_task
def generate_schedule_messages():
    from chat.models import ScheduledTask

    for task in ScheduledTask.objects.filter(is_active=True):
        generate_message_instance_for_task(task)


def generate_message_instance_for_task(task):
    from chat.models import ScheduledMessage

    already_exists = ScheduledMessage.objects.filter(
        task=task,
        is_sent=False,
    ).exists()
    if already_exists:
        return

    today = now().date()
    center_dt = datetime.combine(today, task.center_time, tzinfo=timezone(timedelta(0)))
    earliest = center_dt - timedelta(minutes=task.delta_minutes + 1)
    if now() > earliest:
        center_dt = center_dt + timedelta(days=1)

    offset = random.randint(-task.delta_minutes*60, task.delta_minutes*60)
    scheduled_at = center_dt + timedelta(seconds=offset)
    ScheduledMessage.objects.create(
        owner=task.owner,
        task=task,
        chat=task.chat,
        scheduled_at=scheduled_at,
    )


# @shared_task
# def process_scheduled_messages():
#     from chat.models import ScheduledMessage
#
#     messages = ScheduledMessage.objects.filter(
#         scheduled_at__lte=now(),
#         is_sent=False,
#     )
#     for message in messages:
#         send_bot_message.delay(message.id)
#
#
# @shared_task
# def send_bot_message(instance_id):
#     from chat.models import ScheduledMessage
#
#     try:
#         instance = ScheduledMessage.objects.select_related(
#             "task",
#             "owner",
#             "chat",
#         ).get(id=instance_id, is_sent=False)
#     except ScheduledMessage.DoesNotExist:
#         return
