from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render


class Index(LoginRequiredMixin, View):
    """
    Base index page
    """
    def get(self, request):
        """
        GET index
        """
        return render(request, "index.html")
