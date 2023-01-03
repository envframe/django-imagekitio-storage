from rest_framework import serializers

from tests.models import TestFileFieldModel, TestFileAndImageFieldModel, TestWithoutMediaModel, TestFileFieldVideoModel, \
    TestThirdPartyFieldModel


class TestFileFieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestFileFieldModel
        fields = "__all__"


class TestFileAndImageFieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestFileAndImageFieldModel
        fields = "__all__"


class TestWithoutMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestWithoutMediaModel
        fields = "__all__"


class TestFileFieldVideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestFileFieldVideoModel
        fields = "__all__"


class TestThirdPartyFieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestThirdPartyFieldModel
        fields = "__all__"
