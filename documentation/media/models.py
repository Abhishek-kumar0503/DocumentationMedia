from django.db import models
import os

class DocumentationFile(models.Model):
    DOCUMENTATION_TYPES = [
        ('django', 'Django'),
        ('javascript', 'JavaScript'),
        ('python', 'Python'),
        ('git', 'Git'),
        ('postman', 'Postman'),
        ('vscode', 'VS Code'),
        ('docker', 'Docker'),
        ('awscli', 'AWS CLI'),
        ('github', 'GitHub'),
        ('react', 'React'),
        ('kubernetes', 'Kubernetes'),
        ('Pytest', 'Pytest'),
        ('fastapi', 'Fast API'),
        ('java', 'Java'),
        ('gitlab', 'GitLab'),
        ('c', 'C'),
        ('c++', 'C++'),
        ('flask', 'Flask'),
        ('vuejs', 'Vue.js'),
        ('tensorflow', 'TensorFlow'),
        ('kotlin', 'Kotlin'),
        ('postgresql', 'PostgreSQL'),
        ('mysql', 'MySQL'),
        ('linux', 'Linux'),
        ('other', 'Other'),
    ]
    
    name = models.CharField(max_length=100)
    doc_type = models.CharField(max_length=20, choices=DOCUMENTATION_TYPES)
    documentation_file = models.FileField(upload_to='documentation/', null=True, blank=True)
    ai_documentation_file = models.FileField(upload_to='ai_documentation/', null=True, blank=True)
    upload_date = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.get_doc_type_display()} - {self.name}"
    
    def filename(self):
        return os.path.basename(self.documentation_file.name)
        
    def ai_filename(self):
        if self.ai_documentation_file:
            return os.path.basename(self.ai_documentation_file.name)
        return "No AI file uploaded"
