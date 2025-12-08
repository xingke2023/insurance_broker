"""
URL configuration for backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from .views import index_view, wechat_verify

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    # 微信域名验证
    path('ub10b8eAJx.txt', wechat_verify, name='wechat_verify'),
]

# 在开发环境中提供媒体文件服务
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Catch-all 路由：所有非 API/admin 的路由都返回前端的 index.html
# 这样可以支持前端的客户端路由（如 /document/43, /plan-management 等）
urlpatterns += [
    re_path(r'^.*$', index_view, name='index'),
]
