from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.conf.urls import url
from rest_framework_swagger.views import get_swagger_view

schema_view = get_swagger_view(title='REST API')

urlpatterns = [
    path('', schema_view),
    path('admin/', admin.site.urls, name="home"),
    path('api/', include('users.urls')),
    path('note_api/', include('notes.urls'), name="note_main"),
    url(r'^oauth/', include('social_django.urls', namespace='social')),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT, )
