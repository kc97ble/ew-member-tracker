from django.shortcuts import render
from django.views import View

import pprint
from . import logics


class IndexView(View):
    def get(self, request):
        return render(request, "index.html", {})

    def post(self, request):
        dir = request.POST["dir"]
        data = logics.get_heat_map_from_dir(dir)
        return render(
            request,
            "index_result.html",
            {"heat_map": data, "debug": pprint.pformat(data, indent=4)},
        )
