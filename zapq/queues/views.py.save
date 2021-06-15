from django.shortcuts import render
from django.views import View
from django.http import JsonResponse
import json
from .models import Queue
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt


@method_decorator(csrf_exempt, name='dispatch')
class QueueList(View):
    def post(self, request):

        data = json.loads(request.body.decode("utf-8"))
        product_data = {
            'queue_name': data.get('queue_name'),
            'queue_desc': data.get('queue_desc'),
            'queue_qty': data.get('queue_qty'),
            'queue_eta': data.get('queue_eta'),
            'queue_lat': data.get('queue_lat'),
            'queue_long': data.get('queue_long'),
        }

        queue = Queue.objects.create(**product_data)

        data = {
            "message": f"New queue added with id: {queue.id}"
        }
        return JsonResponse(data, status=201)

