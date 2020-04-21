from django.contrib import admin


# Register your models here.


class CsvUploadAdmin(admin.ModelAdmin):
    allow_csv_upload = True

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['allow_csv_upload'] = self.allow_csv_upload
        print(extra_context)
        return super().changelist_view(
            request, extra_context=extra_context,
        )
