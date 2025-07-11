# Generated by Django 5.2.1 on 2025-05-30 12:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('media', '0002_alter_documentationfile_ai_documentation_file_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='documentationfile',
            name='doc_type',
            field=models.CharField(choices=[('django', 'Django'), ('javascript', 'JavaScript'), ('python', 'Python'), ('git', 'Git'), ('postman', 'Postman'), ('vscode', 'VS Code'), ('docker', 'Docker'), ('npm', 'NPM'), ('aws', 'AWS CLI'), ('github', 'GitHub'), ('react', 'React'), ('kubernetes', 'Kubernetes'), ('Pytest', 'Pytest'), ('fastapi', 'Fast API'), ('java', 'Java'), ('other', 'Other')], max_length=20),
        ),
    ]
