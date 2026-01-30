from django.contrib import admin

from .models import Character, Chat, Message


@admin.register(Character)
class CharacterAdmin(admin.ModelAdmin):
    list_display = ("name", "owner", "is_private")
    list_filter = ("is_private", "owner")
    search_fields = ("name", "description")
    ordering = ("name",)


@admin.register(Chat)
class ChatAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "owner",
        "character",
        "character_name",
        "is_active",
        "last_message_datetime",
        "created_at",
    )
    list_filter = (
        "is_active",
        "is_hidden_prompt",
        "created_at",
        "last_message_datetime",
    )
    search_fields = (
        "owner__username",
        "character__name",
        "character_name",
    )
    readonly_fields = (
        "created_at",
        "edited_at",
        "last_message_text",
        "last_message_datetime",
    )
    raw_id_fields = (
        "owner",
        "character",
        "last_message",
    )
    date_hierarchy = "last_message_datetime"
    ordering = ("-last_message_datetime",)


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "owner",
        "chat",
        "role",
        "media_type",
        "conducted",
        "is_active",
    )
    list_filter = ("role", "media_type", "is_active", "conducted")
    search_fields = ("owner__username", "chat__id", "message")
    date_hierarchy = "conducted"
    ordering = ["-conducted"]
    readonly_fields = ("created_at", "edited_at")
