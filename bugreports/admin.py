from django.contrib import admin

from . import models


@admin.register(models.BuggyProject)
class BuggyProjectAdmin(admin.ModelAdmin):
    pass


@admin.register(models.Bug)
class BugAdmin(admin.ModelAdmin):
    pass


@admin.register(models.Occasion)
class OccasionAdmin(admin.ModelAdmin):
    pass
