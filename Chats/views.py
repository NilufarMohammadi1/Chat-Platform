from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404, HttpResponseForbidden, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.views.generic.edit import FormMixin, CreateView
from django.views.generic import DetailView, ListView
from .forms import ComposeForm
from .models import Thread, ChatMessage
from Users.models import Users
from .models import ThreadMember



class ThreadView(LoginRequiredMixin, FormMixin, DetailView):
    template_name = 'chat/thread.html'
    form_class = ComposeForm
    success_url = './'

    def get_queryset(self):
        return Thread.objects.by_user(self.request.user)

    def get_object(self, **kwargs):
        print('get_object', self.kwargs)
        # if "username" in self.kwargs:
        #     other_username = self.kwargs.get("username")
        #     obj = Thread.objects.get_or_new(self.request.user, other_username)
        #     # print('obj->', obj)
        #     obj, created = obj
        # else:
        #     obj = Thread.objects.get_or_new(self.request.user, "broadcast")
        #     # print('obj->', obj)
        #     obj, created = obj
        #
        # if obj is None:
        #     raise Http404
        # return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.get_form()
        return context

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseForbidden()
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        thread = self.get_object()
        user = self.request.user
        message = form.cleaned_data.get("message")
        ChatMessage.objects.create(user=user, thread=thread, message=message)
        return super().form_valid(form)


def getMessages(request):
    if request.method == "GET":
        user = request.user
        destination_username = request.GET.get('username')
        self_username = user.username

        # PATH1
        self_threads = ThreadMember.objects.select_related("thread") \
            .select_related("user").filter(user__username=self_username) \
            .filter(thread__thread_type='individual')
        #
        common_threads = ThreadMember.objects.select_related("thread") \
            .select_related("user").filter(user__username=destination_username) \
            .filter(thread__thread_type='individual')
        #
        ids = []

        for x in common_threads:
            ids.append(x.thread_id)
        #
        threads = list(self_threads.filter(thread__id__in=ids))
        chat_messages_thread_id = 1
        if len(threads) > 0:
            chat_messages_thread_id = threads[0].thread_id
        else:
            if destination_username != "1":
                new_thread = Thread.objects.create(name=f'{self_username}_{destination_username} Chat')
                ThreadMember.objects.create(thread=new_thread, user=Users.objects.get(username=self_username))
                ThreadMember.objects.create(thread=new_thread, user=Users.objects.get(username=destination_username))
                chat_messages_thread_id = new_thread.id
        #     # create thread for chat
        # PATH2

        if destination_username == "1":
            chat_messages = list(ChatMessage.objects.select_related("thread") \
                                 .select_related("user") \
                                 .filter(thread__thread_type='group') \
                                 .filter(thread_id=1).order_by("sent_at"))
        else:
            chat_messages = list(ChatMessage.objects.select_related("thread") \
                                 .select_related("user") \
                                 .filter(thread__thread_type='individual') \
                                 .filter(thread_id=chat_messages_thread_id) \
                                 # .filter(user__username__in=[destination_username, self_username]) \
                                 .order_by("sent_at"))

        # if len(chat_messages) > 0:
        #     chat_messages_thread_id = chat_messages[0].thread_id

        messages = []
        for chat_message in chat_messages:
            if destination_username == self_username:
                if chat_message.user.username == self_username:
                     messages.append({'sender': chat_message.user.username, 'message': chat_message.message
                                             , 'sent_at': chat_message.sent_at})
            else:
                messages.append({'sender': chat_message.user.username, 'message': chat_message.message
                                    ,'sent_at': chat_message.sent_at})

        return JsonResponse({"status": "ok", 'messages': messages, 'thread_id': chat_messages_thread_id})

    return JsonResponse({"status": "nok"}, status=200)

# print('my username ->', my_username)
# print('username ->', username)
# for eachthread1 in ThreadMember.objects.get(user=username):
#     for eachthread2 in ThreadMember.objects.get(user=my_username):
#         if eachthread1.id == eachthread2.id:
#             print('threadname->',eachthread1)
#             return eachthread1.name
# thread_id_myusername= ThreadMember.objects.get()
# print('thread_id_myusername - > ',thread_id_myusername)
# thread_id_username = ThreadMember.objects.get()
# if thread_id_myusername.id == thread_id_username.id:
#     return thread_id_myusername.name
#
# return JsonResponse({"status": "ok"}, status=200)
