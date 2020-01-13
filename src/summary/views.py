# from django.http import HttpResponse
import json
from django.views import View
from django.shortcuts import render
from pprint import pformat
import summary.logics
from summary.models import Folder


class SummaryView(View):
    def decorated_folder(self, f):
        try:
            heat_map = json.loads(f.heat_map_str)
        except json.JSONDecodeError:
            heat_map = []

        return {
            "dir": f.dir,
            "heat_map": heat_map,
        }

    def get(self, request):
        data = {}
        return render(
            request,
            "summary/get.html",
            {
                "folders": [self.decorated_folder(f) for f in Folder.objects.all()],
                "debug": pformat(data, indent=4),
            },
        )

    def post(self, request):
        action = request.POST["action"]
        if action == "reload_big_dir":
            summary.logics.reload_big_dir(request.POST["big_dir"])
        elif action == "generate_heat_map":
            summary.logics.generate_heat_map(request.POST["dir"])
        else:
            raise Exception("Invalid action")

        return self.get(request)
