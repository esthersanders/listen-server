""" CurrentUser ViewSet Module"""
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.http import HttpResponseServerError
from rest_framework.viewsets import ViewSet
from rest_framework import serializers, status
from rest_framework.response import Response
from listenapi.models import Musician
from listenapi.views.musician import MusicianSerializer

class CurrentUser(ViewSet):
    """Musician Class"""

    def list(self, request):
        """ handles GET currently logged in user """

        #the code in the parentheses is like a WHERE clause in SQL
        user = Musician.objects.get(user=request.auth.user)

        #imported the MusicianSerializer from musician.py to use in this module
        serializer = MusicianSerializer(user, many=False, context={'request': request})
        return Response(serializer.data)