from django.contrib import admin
from .models import Character


@admin.register(Character)
class CharacterAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'is_private')
    list_filter = ('is_private', 'owner')
    search_fields = ('name', 'description')
    ordering = ('name',)
