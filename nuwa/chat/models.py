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

#
# class Chat(models.Model):
#     owner = models.ForeignKey(
#         settings.AUTH_USER_MODEL,
#         related_name="characters",
#         on_delete=models.CASCADE,
#     )
#     character = models.ForeignKey(
#         Character,
#         related_name="chats",
#         on_delete=models.CASCADE,
#     )