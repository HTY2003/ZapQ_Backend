from django.shortcuts import render
from django.views import View
from django.http import JsonResponse
import json
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.core import serializers
from django.contrib.auth import get_user_model, authenticate
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.authtoken.models import Token
from .models import *
from .serializers import *
from .tauth import tauth

User = get_user_model()


@method_decorator(csrf_exempt, name='dispatch')
class QueueMake(View):
    def post(self, request):

        data = json.loads(request.body.decode("utf-8"))
        product_data = {
            'name': data.get('name'),
            'desc': data.get('desc'),
            'eta': data.get('eta'),
            'lati': data.get('lati'),
            'longi': data.get('longi'),
            'creator': User.objects.get(username=data.get('username')),
            'paused': False
            'ended': False
        }

        queue = Queue.objects.create(**product_data)

        data = {
            "queue_id": f"{queue.id}"
        }
        return JsonResponse(data, status=201)


@method_decorator(csrf_exempt, name='dispatch')
class QueueCreator(View):
    def post(self, request):

        data = json.loads(request.body.decode("utf-8"))
        queue_id = data.get('queue_id')
        queue = Queue.objects.get(id=queue_id)
        data = {
            "creator": f"{queue.creator.username}"
        }
        return JsonResponse(data, status=201)


@method_decorator(csrf_exempt, name='dispatch')
class QueueNext(View):
    def post(self, request):
        data = json.loads(request.body.decode("utf-8"))
        queue_id = data.get('queue_id')
        queue = Queue.objects.get(id=queue_id)
        user_to_remove = queue.users.all()[0]
        queue.users.remove(user_to_remove)
        data = {}
        return JsonResponse(data, status=201)


@method_decorator(csrf_exempt, name='dispatch')
class QueueDel(View):
    def post(self, request):
        data = json.loads(request.body.decode("utf-8"))
        queue_id = data.get('queue_id')
        queue = Queue.objects.get(id=queue_id)
        queue.ended = True
        data = {}
        return JsonResponse(data, status=201)


@method_decorator(csrf_exempt, name='dispatch')
class QueuePause(View):
    def post(self, request):
        data = json.loads(request.body.decode("utf-8"))
        queue_id = data.get('queue_id')
        queue = Queue.objects.get(id=queue_id)
        queue.paused = True
        data = {}
        return JsonResponse(data, status=201)


@method_decorator(csrf_exempt, name='dispatch')
class UserJoinQueue(View):
    def post(self, request):
        data = json.loads(request.body.decode("utf-8"))
        queue_id = data.get('queue_id')
        username = data.get('username')
        queue = Queue.objects.get(id=queue_id)
        if !queue.paused and !queue.ended:
            user = User.objects.get(username=username)
            queue.users.add(user)
            queue.allusers.add(user)
        data = {}
        return JsonResponse(data, status=201)


@method_decorator(csrf_exempt, name='dispatch')
class UserLeaveQueue(View):
    def post(self, request):
        data = json.loads(request.body.decode("utf-8"))
        queue_id = data.get('queue_id')
        username = data.get('username')
        queue = Queue.objects.get(id=queue_id)
        user = User.objects.get(username=username)
        queue.users.remove(user)
        data = {}
        return JsonResponse(data, status=201)


@method_decorator(csrf_exempt, name='dispatch')
class UserInQueue(View):
    def post(self, request):
        data = json.loads(request.body.decode("utf-8"))
        username = data.get('username')
        user = User.objects.get(username=username)
        queues = user.queues.filter(ended=False)
        data = {queue.id for queue in queues}
        data = {
            "queue_id_list": data
        }
        return JsonResponse(data, status=201)


@method_decorator(csrf_exempt, name='dispatch')
class UserAllQueues(View):
    def post(self, request):
        data = json.loads(request.body.decode("utf-8"))
        username = data.get('username')
        queues = user.allqueues.filter()
        data = {queue.id for queue in queues}
        data = {
            "queue_id_list": data
        }
        return JsonResponse(data, status=201)


@method_decorator(csrf_exempt, name='dispatch')
class UserNearQueues(View):
    def post(self, request):
        data = json.loads(request.body.decode("utf-8"))
        lati = data.get('lati')
        longi = data.get('longi')
        data = {queue.id for queue in Queue.objects.filter(
            lati__range=[lati-0.1, lati+0.1], longi__range=[longi-0.1, longi+0.1], ended=False, paused=False)}
        data = {
            "queue_id_list": data
        }
        return JsonResponse(data, status=201)


class usernameavail(APIView):
    def get(self, request):
        usernamecheck = self.request.GET.get('username')
        if User.objects.filter(username=usernamecheck).exists():
            return Response({'check': 'False'})
        else:
            return Response({'check': 'True'})


class usercall(APIView):
    def get(self, request):
        specuser = self.request.GET.get('username')
        if specuser == "ALL":
            return Response(UserSerializer(User.objects.all(), many=True).data)
        userlist = User.objects.filter(username=specuser)
        serializer = UserSerializer(userlist, many=True)
        return Response(serializer.data)


class create_account(APIView):
    def post(self, request):
        usersignup = UserCreation(data=self.request.data)
        if usersignup.is_valid():
            usersignup.save()
            username = request.data.get('username')
            password = request.data.get('password')
            UserLogin = authenticate(username=username, password=password)
            logintoken = Token.objects.create(user=UserLogin)
            return Response({'token': logintoken.key, 'state': 'Success'}, status=status.HTTP_200_OK)
        return Response({'errors': usersignup.errors, 'state': 'Denied'}, status=status.HTTP_400_BAD_REQUEST)


class delete_account(APIView):
    def post(self, request):
        vtoken = self.request.data.get('Token')
        username = self.request.data.get('username')
        password = self.request.data.get('password')
        UserVerify = authenticate(username=username, password=password)
        if not UserVerify:
            return Response({'error': 'Invalid login details. Account refuses to be deleted.', 'state': 'Denied'}, status=status.HTTP_401_UNAUTHORIZED)
        if not tauth(vtoken, UserVerify.username)['status']:
            return Response({'error': 'Invalid login token! Account refuses to be deleted.', 'state': 'Denied'}, status=status.HTTP_401_UNAUTHORIZED)
        UserVerify.delete()
        return Response({'state': 'Success'})


class logout(APIView):
    def get(self, request):
        stoken = self.request.GET.get('Token')
        if not Token.objects.filter(key=stoken).exists():
            return Response({'error': 'No user logged in with this token!', 'state': 'Denied'}, status=status.HTTP_400_BAD_REQUEST)
        logoutuser = Token.objects.get(key=stoken).user
        Token.objects.get(key=stoken).delete()
        return Response({'user': logoutuser.username, 'state': 'Success'})


class login(APIView):
    def post(self, request):
        username = self.request.data.get('username')
        password = self.request.data.get('password')
        if username is None or password is None or username == '' or password == '':
            return Response(
                {
                    'error': 'Please enter both a Username and Password!',
                    'state': 'Denied'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        UserLogin = authenticate(username=username, password=password)
        if not UserLogin:
            return Response(
                {
                    'error': 'Your Username or Password is invalid!',
                    'state': 'Denied'
                },
                status=status.HTTP_401_UNAUTHORIZED
            )
        if Token.objects.filter(user=UserLogin).exists():
            Token.objects.filter(user=UserLogin).delete()
        usertoken = Token.objects.create(user=UserLogin)
        return Response({'token': usertoken.key, 'state': 'Success'}, status=status.HTTP_200_OK)
