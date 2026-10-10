from django.shortcuts import render
from .models import OrderModel
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from permission import IsSuperUser
from drf_spectacular.utils import extend_schema, OpenApiParameter
from paginator import paginate
from order.serializer import OrderSerializer, PaginateOrderSerializer, SelectOrderSerializer, PaginateSelectOrderSerializer
from django.db.models import Q,Value
from django.db.models.functions import Concat
from rest_framework.exceptions import NotFound
from rest_framework import status
from rest_framework.permissions import AllowAny


# Create your views here.

class OrderViewSet(ViewSet):
    permission_classes = [IsSuperUser]
    http_method_names = ['get']
    paginator = paginate
    queryset = OrderModel.objects.all().select_related('user__profile').order_by('-created_at')

    @extend_schema(responses={200: PaginateOrderSerializer},description='**Statuses**\n\n - processing\n\n - shipped\n\n - delivered\n\n - cancelled',
                   parameters=[
                       OpenApiParameter('search',str,description='**جستجو در نام و ایمیل و شماره سغارش**'),
                       OpenApiParameter('status',str,description='**فیلتر بر اساس وضعیت**'),
                   ])
    def list(self, request):
        orders = self.queryset
        search = request.query_params.get('search')
        status = request.query_params.get('status')
        if search:
            orders = orders.annotate(fullname=Concat('user__profile__first_name',Value(' '),'user__profile__last_name')).filter(Q(fullname__icontains=search) | Q(user__profile__first_name__icontains=search) | Q(user__profile__last_name__icontains=search) | Q(order_number__icontains=search) | Q(user__email__icontains=search))
        if status:
            orders = orders.filter(status=status)
        paginator = self.paginator()
        page = paginator.paginate_queryset(queryset=orders, request=request, view=self)
        serializer = OrderSerializer(instance=page, many=True)
        return paginator.get_paginated_response(serializer.data)
    @extend_schema(responses={200: PaginateSelectOrderSerializer})
    def retrieve(self, request, pk=None):
        order = self.queryset.filter(order_number=pk).first()
        if not order:
            raise NotFound('Order was not found.')
        serializer = SelectOrderSerializer(instance=order)
        return Response(serializer.data,status=status.HTTP_200_OK)

