from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import Queue

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email')


class UserCreation(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    queue_pos = serializers.PositiveIntegerField()

    class Meta:
        model = User
        fields = ('username', 'email', 'password')

    def create(self, vd, *args, **kwargs):
        user = super(UserCreation, self).create(vd, *args, **kwargs)
        user.set_password(vd['password'])
        user.save()
        return user
