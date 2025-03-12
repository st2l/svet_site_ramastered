from django.contrib import admin
from .models import MainSection, Subsection, FinalSection, Lamp
from django.urls import path
from django.shortcuts import reverse
from django.utils.html import format_html
from django.template.response import TemplateResponse

@admin.register(Lamp)
class LampAdmin(admin.ModelAdmin):
    list_display = ['model', 'brand', 'price']
    
    change_list_template = 'admin/lamp_changelist.html'
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('upload-excel/', self.upload_excel_view, 
                 name='%s_%s_upload_excel' % (self.model._meta.app_label, self.model._meta.model_name)),
        ]
        return custom_urls + urls
    
    def upload_excel_view(self, request):
        from .views import upload_excel
        return upload_excel(request)
        
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        return super().changelist_view(request, extra_context=extra_context)

admin.site.register(MainSection)
admin.site.register(Subsection)
admin.site.register(FinalSection)
