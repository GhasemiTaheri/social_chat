from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import TemplateView, CreateView

from chat.forms import ConversationCreateForm


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'chat/dashboard.html'


class GroupCreateView(LoginRequiredMixin, CreateView):
    form_class = ConversationCreateForm
    template_name = 'chat/create_group.html'
    success_url = reverse_lazy('chat:dashboard')

    def get_form_kwargs(self):
        kwargs = super(GroupCreateView, self).get_form_kwargs()
        kwargs.update({'request': self.request})
        return kwargs
