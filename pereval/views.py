from django.shortcuts import render

from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import Pereval
from .serializers import PerevalSubmitSerializer, PerevalReadSerializer
from services.pereval_services import PerevalService


class SubmitDataView(APIView):
    def get(self, request):
        email = request.query_params.get('user__email')

        if not email:
            return Response(
                {
                    'status': 400,
                    'message': 'Не передан параметр user__email',
                    'id': None,
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        perevals = Pereval.objects.filter(user__email=email)
        serializer = PerevalReadSerializer(
            perevals,
            many=True,
            context={'request': request}
        )

        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = PerevalSubmitSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                {
                    'status': 400,
                    'message': serializer.errors,
                    'id': None,
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            pereval = PerevalService.create_pereval(serializer.validated_data)

            return Response(
                {
                    'status': 200,
                    'message': None,
                    'id': pereval.id,
                },
                status=status.HTTP_200_OK
            )

        except Exception as error:
            return Response(
                {
                    'status': 500,
                    'message': str(error),
                    'id': None,
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class SubmitDataDetailView(APIView):
    def get(self, request, pk):
        pereval = get_object_or_404(Pereval, pk=pk)

        serializer = PerevalReadSerializer(
            pereval,
            context={'request': request}
        )

        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, pk):
        pereval = get_object_or_404(Pereval, pk=pk)

        serializer = PerevalSubmitSerializer(
            data=request.data,
            partial=True
        )

        if not serializer.is_valid():
            return Response(
                {
                    'state': 0,
                    'message': serializer.errors,
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        result = PerevalService.update_pereval(
            pereval,
            serializer.validated_data
        )

        http_status = (
            status.HTTP_200_OK
            if result['state'] == 1
            else status.HTTP_400_BAD_REQUEST
        )

        return Response(result, status=http_status)