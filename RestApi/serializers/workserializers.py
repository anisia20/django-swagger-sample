from rest_framework import serializers


class WorkSerializer(serializers.Serializer):
    fileName = serializers.CharField()
    file = serializers.FileField()