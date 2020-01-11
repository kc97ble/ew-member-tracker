from django.shortcuts import render
from django.views import View

import pprint
from . import logics


class IndexView(View):
    def get(self, request):
        return render(request, "index.html", {})

    def post(self, request):
        dir = request.POST["dir"]
        data = logics.get_file_list_ex(dir)
        return render(
            request, "index_result.html", {"debug": pprint.pformat(data, indent=4)},
        )
