"""netshop2 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
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

from multiprocessing.managers import Server
from django.views.static import serve
from django.contrib import admin
from django.urls import path, re_path
from . import views
from netshop2.settings import DEBUG, MEDIA_ROOT

urlpatterns = [
    path("admin/", admin.site.urls),
    path("login/", views.login_view),
    path("user_info/", views.user_info, name="user_info"),
    path("user_dashboard/", views.user_dashboard, name="user_dashboard"),
    path("purchase_product/", views.purchase_product),
    path("user_orders/", views.user_orders),
    # # API端点
    path("ai_chat/", views.ai_chat_view, name="ai_chat"),
    path("clear_chat/", views.clear_chat, name="clear_chat"),
    path(
        "purchase_product/<int:product_id>/",
        views.purchase_product,
        name="purchase_product",
    ),
    # path('api/purchase/', cs_views.process_purchase, name='process_purchase'),
]
if DEBUG:
    urlpatterns += [
        re_path(r"^media/(?P<path>.*)$", serve, {"document_root": MEDIA_ROOT}),
    ]
