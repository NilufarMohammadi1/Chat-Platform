from django.urls import path, re_path
from .views import ThreadView, getMessages
from . import views
app_name = 'Chats'

urlpatterns = [
    path("getMessages", views.getMessages, name='getMessages'),
    re_path("", ThreadView.as_view(), name='threadAllMessage'),
    re_path(r"^(?P<thread_id>[\w.@+-]+)/$", ThreadView.as_view(), name='thread')

]