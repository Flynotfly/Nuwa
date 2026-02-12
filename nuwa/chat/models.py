import os

from django.core.validators import MaxValueValidator
from django.conf import settings
from django.db import models


class Character(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="characters",
        on_delete=models.CASCADE,
    )
    name = models.CharField(max_length=50)
    system_prompt = models.TextField()
    description = models.TextField(
        blank=True,
        null=True,
    )
    is_private = models.BooleanField()
    is_hidden_prompt = models.BooleanField()
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    edited_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [models.Index(fields=["name"])]
        ordering = ["name"]

    def __str__(self):
        return self.name

    def __repr__(self):
        return (
            f"<{'Public' if not self.is_private else 'Private'}"
            f"character {self.name} of user {self.owner}>"
        )


class Chat(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="chats",
        on_delete=models.CASCADE,
    )
    character = models.ForeignKey(
        Character,
        related_name="chats",
        on_delete=models.CASCADE,
    )
    character_name = models.CharField(max_length=50)
    system_prompt = models.TextField()
    description = models.TextField(
        blank=True,
        null=True,
    )
    is_hidden_prompt = models.BooleanField()
    is_active = models.BooleanField(default=True)

    last_message = models.ForeignKey(
        "Message",
        related_name="+",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    last_message_text = models.TextField(blank=True, null=True)
    last_message_datetime = models.DateTimeField(blank=True, null=True)
    structure = models.JSONField(default=list)

    created_at = models.DateTimeField(auto_now_add=True)
    edited_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["-last_message_datetime"]),
            models.Index(fields=["owner", "-last_message_datetime"]),
        ]
        ordering = ["-last_message_datetime"]

    def __repr__(self):
        return (
            f"<Chat of user {self.owner.pk} and character "
            f"{self.character.pk} {self.character_name}"
        )


def chat_media_upload_path(instance, filename):
    return f"chat_media/user_{instance.owner.id}/chat_{instance.chat.id}/{filename}"


ROLE_CHOICES = {"user": "user", "assistant": "assistant"}
MEDIA_TYPE_CHOICES_WITH_TEXT = {
    "text": "text",
}
MEDIA_TYPE_CHOICES_WITHOUT_TEXT = {
    "image": "image",
    "video": "video",
}
MEDIA_TYPE_CHOICES = MEDIA_TYPE_CHOICES_WITH_TEXT | MEDIA_TYPE_CHOICES_WITHOUT_TEXT


class Message(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="messages",
        on_delete=models.CASCADE,
    )
    chat = models.ForeignKey(
        Chat,
        related_name="messages",
        on_delete=models.CASCADE,
    )
    role = models.CharField(
        max_length=9,
        choices=ROLE_CHOICES,
    )
    media_type = models.CharField(
        max_length=5,
        choices=MEDIA_TYPE_CHOICES,
    )
    message = models.TextField(
        blank=True,
        null=True,
    )
    media = models.FileField(
        upload_to=chat_media_upload_path,
        blank=True,
        null=True,
    )
    is_active = models.BooleanField(default=True)
    conducted = models.DateTimeField()
    history = models.JSONField(default=list)
    info = models.JSONField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    edited_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["chat", "-conducted"]),
            models.Index(fields=["owner", "chat", "-conducted"]),
        ]
        ordering = ["-conducted"]

    def __repr__(self):
        return (
            f"<Message of user {self.owner.pk} in chat "
            f"{self.chat.pk} at {self.conducted}"
        )


class ScheduledTask(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="scheduled_tasks",
        on_delete=models.CASCADE,
    )
    chat = models.ForeignKey(
        Chat,
        related_name="scheduled_tasks",
        on_delete=models.CASCADE,
    )
    center_time = models.TimeField(help_text="In UTC")
    delta_minutes = models.PositiveIntegerField(validators=[MaxValueValidator(360)])
    user_timezone = models.IntegerField(help_text="In minutes")
    prompt = models.TextField(
        blank=True,
        null=True,
    )
    use_time = models.BooleanField()
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    edited_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["-created_at"])
        ]
        ordering = ["-created_at"]

    def __repr__(self):
        return f"<ScheduledTask of user {self.owner.pk} at {self.center_time} +- {self.delta_minutes} minutes>"


class ScheduledMessage(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="scheduled_messages",
        on_delete=models.CASCADE,
    )
    task = models.ForeignKey(
        ScheduledTask,
        related_name="messages",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    chat = models.ForeignKey(
        Chat,
        related_name="scheduled_messages",
        on_delete=models.CASCADE,
    )
    scheduled_at = models.DateTimeField()
    is_sent = models.BooleanField(default=False)
    sent_at = models.DateTimeField(
        blank=True,
        null=True,
    )
    message = models.ForeignKey(
        Message,
        related_name="scheduled_message",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    edited_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["-scheduled_at"])
        ]
        ordering = ["-scheduled_at"]
        unique_together = ["task", "scheduled_at"]
