from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    # path('api/test/', include('testapi.urls')),      
    path('api/auth/', include('authentication.urls')),   # becomes /api/auth/signup/, /api/auth/login/, etc.
]
