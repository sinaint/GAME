from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0003_usersettings'),
    ]

    operations = [
        migrations.AddField(
            model_name='userpersona',
            name='age',
            field=models.CharField(blank=True, max_length=30),
        ),
        migrations.AddField(
            model_name='userpersona',
            name='appearance',
            field=models.TextField(blank=True, max_length=500),
        ),
        migrations.AddField(
            model_name='userpersona',
            name='personality',
            field=models.TextField(blank=True, max_length=500),
        ),
        migrations.AddField(
            model_name='userpersona',
            name='talent',
            field=models.TextField(blank=True, max_length=500),
        ),
        migrations.AlterField(
            model_name='userpersona',
            name='content',
            field=models.TextField(blank=True, max_length=1000),
        ),
    ]
