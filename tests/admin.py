from django.contrib import admin

from .models import TestFileAndImageFieldModel, TestFileFieldVideoModel, TestFileFieldModel, TestWithoutMediaModel, \
    TestThirdPartyFieldModel

admin.site.register(TestFileAndImageFieldModel)
admin.site.register(TestFileFieldVideoModel)
admin.site.register(TestFileFieldModel)
admin.site.register(TestWithoutMediaModel)
admin.site.register(TestThirdPartyFieldModel)
