from rest_framework import viewsets, status
from rest_framework.response import Response

from rabbit_mq.rabbit_mq_provider import publish
from order.models import Order
from order.serializers import OrderSerializer


class OrderView(viewsets.ViewSet):
    def list(self, request):
        orders = Order.objects.all()
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)

    def create(self, request):
        serializer = OrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        publish('orders_q', serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None):
        recipe = Order.objects.get(id=pk)
        serializer = OrderSerializer(instance=recipe, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        publish('orders_q', serializer.data)
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)

    def destroy(self, request, pk=None):
        recipe = Order.objects.get(id=pk)
        recipe.delete()
        publish('orders_q', {'id': 'pk'})
        return Response(status=status.HTTP_204_NO_CONTENT)
