# Generated by Django 4.0.3 on 2022-03-25 10:22

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('Chats', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='chatmessage',
            options={'ordering': ['sent_at'], 'verbose_name': 'chat message', 'verbose_name_plural': 'chat messages'},
        ),
        migrations.AlterModelOptions(
            name='thread',
            options={'ordering': ['-updated'], 'verbose_name': 'threads', 'verbose_name_plural': 'thread'},
        ),
        migrations.RenameField(
            model_name='chatmessage',
            old_name='timestamp',
            new_name='sent_at',
        ),
        migrations.RemoveField(
            model_name='thread',
            name='first',
        ),
        migrations.RemoveField(
            model_name='thread',
            name='second',
        ),
        migrations.AddField(
            model_name='chatmessage',
            name='read_receipt',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='thread',
            name='name',
            field=models.CharField(choices=[('individual', 'Individual'), ('group', 'Group')], default='individual', max_length=20),
        ),
        migrations.AddField(
            model_name='thread',
            name='thread_type',
            field=models.CharField(choices=[('individual', 'Individual'), ('group', 'Group')], default='individual', max_length=20),
        ),
        migrations.AlterField(
            model_name='chatmessage',
            name='message',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='chatmessage',
            name='thread',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='msg_thread', to='Chats.thread'),
        ),
        migrations.AlterField(
            model_name='chatmessage',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='msg_sender', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterModelTable(
            name='chatmessage',
            table='in_chat_message',
        ),
        migrations.AlterModelTable(
            name='thread',
            table='in_thread',
        ),
        migrations.CreateModel(
            name='ThreadMember',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_grp_admin', models.BooleanField(default=False)),
                ('thread', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='thread_member', to='Chats.thread')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='thread_member_user', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'thread members',
                'verbose_name_plural': 'thread member',
                'db_table': 'in_thread_member',
            },
        ),
    ]
