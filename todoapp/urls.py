from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from tasks.views import index

urlpatterns = [
    path("", index, name="index"),
    path('tasks/', include('tasks.urls', namespace="tasks")),
    path('accounts/', include('accounts.urls')),
    path('admin/', admin.site.urls),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
