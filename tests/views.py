from django.shortcuts import render
from rest_framework import viewsets

from tests.models import TestFileFieldModel, TestFileAndImageFieldModel, TestWithoutMediaModel, TestFileFieldVideoModel, \
    TestThirdPartyFieldModel
from tests.serializer import TestFileFieldSerializer, TestFileAndImageFieldSerializer, TestWithoutMediaSerializer, \
    TestFileFieldVideoSerializer, TestThirdPartyFieldSerializer


def index(request):
    return render(request, 'tests/index.html')


class TestFileFieldViewSet(viewsets.ModelViewSet):
    queryset = TestFileFieldModel.objects.all()
    serializer_class = TestFileFieldSerializer


class TestFileAndImageFieldViewSet(viewsets.ModelViewSet):
    queryset = TestFileAndImageFieldModel.objects.all()
    serializer_class = TestFileAndImageFieldSerializer


class TestWithoutMediaViewSet(viewsets.ModelViewSet):
    queryset = TestWithoutMediaModel.objects.all()
    serializer_class = TestWithoutMediaSerializer


class TestFileFieldVideoViewSet(viewsets.ModelViewSet):
    queryset = TestFileFieldVideoModel.objects.all()
    serializer_class = TestFileFieldVideoSerializer


class TestThirdPartyFieldViewSet(viewsets.ModelViewSet):
    queryset = TestThirdPartyFieldModel.objects.all()
    serializer_class = TestThirdPartyFieldSerializer
