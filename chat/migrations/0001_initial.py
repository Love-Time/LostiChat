# Generated by Django 4.1.2 on 2023-04-08 13:40

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Conversation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(choices=[('duo', 'Дуэт'), ('multi', 'Беседа')], default='', max_length=5, verbose_name='Тип')),
                ('name', models.CharField(blank=True, max_length=24, null=True, verbose_name='Название')),
                ('last_message', models.TextField(blank=True, null=True, verbose_name='Последнее сообщение')),
                ('members', models.ManyToManyField(related_name='members', to=settings.AUTH_USER_MODEL, verbose_name='Участники')),
            ],
        ),
        migrations.CreateModel(
            name='Dialog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.TextField()),
                ('read', models.BooleanField(default=0)),
                ('time', models.DateTimeField(auto_now_add=True)),
                ('answer', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='chat.dialog')),
            ],
            options={
                'ordering': ('-time',),
            },
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.TextField()),
                ('time', models.DateTimeField(auto_now_add=True)),
                ('conversation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='message', to='chat.conversation')),
                ('sender', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sender', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Сообщение',
                'verbose_name_plural': 'Сообщения',
                'ordering': ('-time',),
            },
        ),
        migrations.AddField(
            model_name='dialog',
            name='forward',
            field=models.ManyToManyField(blank=True, null=True, to='chat.dialog'),
        ),
        migrations.AddField(
            model_name='dialog',
            name='recipient',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recipient_duo', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='dialog',
            name='sender',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sender_duo', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='conversation',
            name='messages',
            field=models.ManyToManyField(blank=True, related_name='conv', through='chat.Message', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddConstraint(
            model_name='message',
            constraint=models.UniqueConstraint(fields=('sender', 'conversation'), name='unique_migrationMessage_sender_conversation'),
        ),
    ]