"""View module for handling requests about excerpts"""
import base64
from django.core.files.base import ContentFile
from django.http import HttpResponseServerError
from django.contrib.auth.models import User
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import serializers
from rest_framework.decorators import action
from rest_framework import status
from listenapi.models import Excerpt, Musician
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.parsers import MultiPartParser, FormParser

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'email')

class MusicianSerializer(serializers.ModelSerializer):
    """Serializer for Musician info from an excerpt"""
    user = UserSerializer(many=False)

    class Meta:
        model = Musician
        fields = ('id', 'bio', 'user')

class ExcerptSerializer(serializers.ModelSerializer):
    """Serializer for excerpts"""
    musician = MusicianSerializer(many=False)
    class Meta:
        model = Excerpt
        fields = ('id', 'name', 'musician', 'done', 'created_by_current_user')
        depth = 2

class Excerpts(ViewSet):
    """Request handlers for excerpts"""
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def create(self, request):
        """
        @api {POST} /excerpts POST new excerpt
        @apiHeader {String} Authorization Auth token
        @apiHeaderExample {String} Authorization
            Token 9ba45f09651c5b0c404f37a2d2572c026c146611
        @apiParam {String} name Name of excerpt
        @apiParam {Number} musician_id Musician who created excerpt
        @apiParam {Boolean} done Whether excerpt is completed or not
        @apiParamExample {json} Input
            {
                "name": "Mozart 5",
                "musician_id": 1,
                "done": False
            }
        @apiSuccess (200) {Object} excerpt Created excerpt
        @apiSuccess (200) {id} excerpt.id Excerpt Id
        @apiSuccess (200) {String} excerpt.name Name of excerpt
        @apiSuccess (200) {Number} excerpt.musician_id Associated musician
        @apiSuccess (200) {Boolean} excerpt.done Completed or not
        @apiSuccessExample {json} Success
            {
                "id": 1,
                "name": "Mozart 5",
                "done": False,
                "musician": {
                    "id": 1,
                    "bio": "violinist",
                    "user": {
                        "id": 1,
                        "first_name": "Esther",
                        "last_name": "Sanders",
                        "email": "esther@esther.com",
                        "username": "estherviolin"
                    }
                }
            }
        """
        try:
            new_excerpt = Excerpt()
            new_excerpt.name = request.data["name"]
            new_excerpt.done = request.data["done"]

            related_musician = Musician.objects.get(user=request.auth.user)
            new_excerpt.musician = related_musician

            new_excerpt.save()

            serializer = ExcerptSerializer(new_excerpt, context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as ex:
            return Response({'message': ex.args[0]})

    def retrieve(self, request, pk=None):
        """
        @api {GET} /excerpts/:id GET excerpt
        @apiParam {id} id Excerpt Id
        @apiSuccess (200) {Object} excerpt Created excerpt
        @apiSuccess (200) {id} excerpt.id Excerpt Id
        @apiSuccess (200) {String} excerpt.name Name of excerpt
        @apiSuccess (200) {Number} excerpt.musician_id Associated musician
        @apiSuccess (200) {Boolean} excerpt.done Completed or not
        @apiSuccessExample {json} Success
            {
                "id": 1,
                "name": "Mozart 5",
                "done": False,
                "musician": {
                    "id": 1,
                    "bio": "violinist",
                    "user": {
                        "id": 1,
                        "first_name": "Esther",
                        "last_name": "Sanders",
                        "email": "esther@esther.com",
                        "username": "estherviolin"
                    }
                }
            }
        """

        try:
            excerpt = Excerpt.objects.get(pk=pk)
            if excerpt.musician.id == request.auth.user.id:
                excerpt.created_by_current_user = True
            else:
                excerpt.created_by_current_user = False
            serializer = ExcerptSerializer(excerpt, context={'request': request})
            return Response(serializer.data)
        except Excerpt.DoesNotExist as ex:
            return HttpResponseServerError(ex, status = status.HTTP_404_NOT_FOUND)

    def update(self, request, pk=None):
        """
        @api {PUT} /excerpts/:id PUT changes to Excerpt
        @apiHeader {String} Authorization Auth token
        @apiHeaderExample {String} Authorization
            Token 9ba45f09651c5b0c404f37a2d2572c026c146611
        @apiParam {id} id Excerpt Id to update
        @apiSuccessExample {json} Success
            HTTP/1.1 204 No Content
        """
        excerpt = Excerpt.objects.get(pk=pk)
        excerpt.name = request.data["name"]
        excerpt.done = request.data["done"]

        related_musician = Musician.objects.get(user=request.auth.user)
        excerpt.musician = related_musician
        
        excerpt.save()

        return Response({}, status=status.HTTP_204_NO_CONTENT)

    def destroy(self, request, pk=None):
        """
        @api {DELETE} /excerpts/:id DELETE excerpt
        @apiHeader {String} Authorization Auth token
        @apiHeaderExample {String} Authorization
            Token 9ba45f09651c5b0c404f37a2d2572c026c146611
        @apiParam {id} id Excerpt Id to delete
        @apiSuccessExample {json} Success
            HTTP/1.1 204 No Content
        """
        try:
            excerpt = Excerpt.objects.get(pk=pk)
            excerpt.delete()

            return Response({}, status=status.HTTP_204_NO_CONTENT)

        except Excerpt.DoesNotExist as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_404_NOT_FOUND)

        except Exception as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def list(self, request):
        """
        @api {GET} /excerpts GET all excerpts
        @apiSuccess (200) {Object[]} excerpts Array of excerpts
        @apiSuccessExample {json} Success
            [
                {
                "id": 1,
                "name": "Mozart 5",
                "done": False,
                "musician": {
                    "id": 1,
                    "bio": "violinist",
                    "user": {
                        "id": 1,
                        "first_name": "Esther",
                        "last_name": "Sanders",
                        "email": "esther@esther.com",
                        "username": "estherviolin"
                    }
                }
            }
            
            ]
        """
        excerpts = Excerpt.objects.all()

        for excerpt in excerpts:

            excerpt.created_by_current_user = None

            if excerpt.musician.id == request.auth.user.id:
                excerpt.created_by_current_user = True
            else:
                excerpt.created_by_current_user = False

        # Support filtering
        musician = self.request.query_params.get('musician', None)
        
        if musician is not None:
            musician = Musician.objects.get(pk=musician)
            excerpts = excerpts.filter(musician=musician) 

            for excerpt in excerpts:
                excerpt.created_by_current_user = None

                if excerpt.musician.id == request.auth.user.id:
                    excerpt.created_by_current_user = True
                else:
                    excerpt.created_by_current_user = False

        serializer = ExcerptSerializer(
            reversed(excerpts), many=True, context={'request': request})
        return Response(serializer.data)

        
    #'done' custom action
    @action(methods=['put'], detail=True)
    def done(self, request, pk=None):
        """Manage marking an excerpt as done"""

        if request.method == 'PUT':
            excerpt = Excerpt.objects.get(pk=pk)

            try:
                excerpt.done = True
                excerpt.save()

                serializer = ExcerptSerializer(excerpt, context={'request': request})
                return Response(serializer.data, status=status.HTTP_204_NO_CONTENT)

            except Excerpt.DoesNotExist:
                return Response(
                    {'message': 'Excerpt does not exist'},
                    status = status.HTTP_400_BAD_REQUEST
                )

    #'undone' custom action
    @action(methods=['put'], detail=True)
    def undone(self, request, pk=None):
        """Manage un-done excerpt"""

        if request.method == 'PUT':
            excerpt = Excerpt.objects.get(pk=pk)

            try:
                excerpt.done = False
                excerpt.save()

                serializer = ExcerptSerializer(excerpt, context={'request': request})
                return Response(serializer.data, status=status.HTTP_204_NO_CONTENT)

            except Excerpt.DoesNotExist:
                return Response(
                    {'message': 'Excerpt does not exist'},
                    status = status.HTTP_400_BAD_REQUEST
                )




        