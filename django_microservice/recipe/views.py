from rest_framework import viewsets, status
from rest_framework.response import Response

from rabbit_mq.rabbit_mq_provider import publish
from recipe.models import Recipe
from recipe.serializers import RecipeSerializer


class RecipeView(viewsets.ViewSet):
    def list(self, request):
        recipes = Recipe.objects.all()
        serializer = RecipeSerializer(recipes, many=True)
        return Response(serializer.data)

    def create(self, request):
        serializer = RecipeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        publish('recipes_q', serializer.data)
    
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None):
        recipe = Recipe.objects.get(id=pk)
        serializer = RecipeSerializer(instance=recipe, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        publish('recipes_q', serializer.data)

        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)

    def destroy(self, request, pk=None):
        recipe = Recipe.objects.get(id=pk)
        recipe.delete()

        publish('recipes_q', {'id': 'pk'})

        return Response(status=status.HTTP_204_NO_CONTENT)
