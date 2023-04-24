# Generated by Django 4.1.2 on 2023-04-24 17:10

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0002_forward_alter_dialog_forward'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dialog',
            name='message',
            field=models.TextField(blank=True, max_length=4000, null=True),
        ),
        migrations.CreateModel(
            name='Image',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(blank=True, null=True, upload_to='chat/image/%Y/%m/%d/')),
                ('dialog', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='chat.dialog')),
            ],
        ),
    ]
