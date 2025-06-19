from django.contrib import admin
from django.utils.html import format_html
from .models import DocumentationFile

class DocumentationFileAdmin(admin.ModelAdmin):
    list_display = ('name', 'doc_type', 'display_doc_file', 'display_ai_file', 'upload_date', 'last_updated')
    list_filter = ('doc_type', 'upload_date')
    search_fields = ('name', 'doc_type')
    
    def display_doc_file(self, obj):
        if obj.documentation_file:
            return format_html('<a href="{}" target="_blank">{}</a>', obj.documentation_file.url, obj.filename())
        return "No file"
    display_doc_file.short_description = 'Documentation File'
    
    def display_ai_file(self, obj):
        if obj.ai_documentation_file:
            return format_html('<a href="{}" target="_blank">{}</a>', obj.ai_documentation_file.url, obj.ai_filename())
        return "No AI file"
    display_ai_file.short_description = 'AI Documentation File'

admin.site.register(DocumentationFile, DocumentationFileAdmin)
