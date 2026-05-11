from arches.app.models.models import ResourceInstance, TileModel
from django.http import JsonResponse
from django.views.generic import View
from django.shortcuts import render

class Audit(View):

    def get(self, request):
        data = {
            "resource_count": ResourceInstance.objects.count(),
            "tile_count": TileModel.objects.count(),
        }
        return JsonResponse(data)
    
