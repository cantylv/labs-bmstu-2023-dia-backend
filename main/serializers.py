from .models import *
from rest_framework import serializers


class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = '__all__'


class BidSerializer(serializers.ModelSerializer):
    services = ServiceSerializer(many=True)
    user = UserSerializer()
    moderator = UserSerializer()

    class Meta:
        model = Bid
        fields = '__all__'