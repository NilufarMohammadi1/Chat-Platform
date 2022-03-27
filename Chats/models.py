# from django.db import models
# import uuid
# from Users.models import Users
# from Rooms.models import Rooms
#
# class Chats(models.Model):
#
#     class Meta:
#         db_table = 'Chats'
#
#     chat_id = models.UUIDField(primary_key=True, default=uuid.uuid4(),editable=False)
#     author = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='author_messgaes')
#     content = models.TextField(blank=False)
#     created_at = models.DateTimeField(auto_now_add=True)
#     modified_at = models.DateTimeField(auto_now=True)
#     room_id = models.ForeignKey(Rooms, on_delete=models.CASCADE)
#
#
#     def __str__(self):
#         return self.author.username

from django.db import models
from django.conf import settings
from django.db import models
from django.db.models import Q
from django.db.models.signals import post_save

from .utils import broadcast_msg_to_chat, trigger_welcome_message

class ThreadManager(models.Manager):
    def by_user(self, user):
        qlookup = Q(first=user) | Q(second=user)
        qlookup2 = Q(first=user) & Q(second=user)
        qs = self.get_queryset().filter(qlookup).exclude(qlookup2).distinct()
        return qs

    def get_or_new(self, user, other_username):  # get_or_create
        username = user.username
        if username == other_username:
            return None
        qlookup1 = Q(first__username=username) & Q(second__username=other_username)
        qlookup2 = Q(first__username=other_username) & Q(second__username=username)
        qs = self.get_queryset().filter(qlookup1 | qlookup2).distinct()
        if qs.count() == 1:
            return qs.first(), False
        elif qs.count() > 1:
            return qs.order_by('timestamp').first(), False
        else:
            Klass = user.__class__
            user2 = Klass.objects.get(username=other_username)
            if user != user2:
                obj = self.model(
                    first=user,
                    second=user2
                )
                obj.save()
                return obj, True
            return None, False

class Thread(models.Model):
    THREAD_TYPE = [
        ('individual', 'Individual'),
        ('group', 'Group')
    ]
    id = models.AutoField(primary_key=True,auto_created = True,)
    name = models.CharField(max_length=20, choices=THREAD_TYPE, default='New Chat')
    thread_type = models.CharField(max_length=20, choices=THREAD_TYPE, default='individual')
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    objects = ThreadManager()

    # first = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='chat_thread_first')
    # second = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='chat_thread_second')
    class Meta:
        db_table = 'Thread'
        verbose_name = 'threads'
        verbose_name_plural = 'thread'
        ordering = ['-updated']

    @property
    def room_group_name(self):
        return f'chat_{self.id}'


class ThreadMember(models.Model):
    thread = models.ForeignKey(Thread, on_delete=models.CASCADE, related_name='thread_member')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='thread_member_user')
    is_grp_admin = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.thread.name} > {self.user}'

    class Meta:
        db_table = 'ThreadMember'
        verbose_name = 'thread members'
        verbose_name_plural = 'thread member'


class ChatMessage(models.Model):
    thread = models.ForeignKey(Thread, on_delete=models.CASCADE, related_name='msg_thread')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='msg_sender')
    message = models.TextField(null=True, blank=True)
    sent_at = models.DateTimeField(auto_now_add=True)
    read_receipt = models.BooleanField(default=False)
    # msg_type = models.CharField(max_length=20, choices=MESSAGE_TYPE, default='text')

    def __str__(self):
        return f'{self.user} > {self.message}'

    class Meta:
        db_table = 'ChatMessage'
        verbose_name = 'chat message'
        verbose_name_plural = 'chat messages'
        ordering = ['sent_at']