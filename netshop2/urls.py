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
    path("payment/<int:order_id>/", views.payment, name="payment"),
    path("send_order_to_chat/", views.send_order_to_chat, name="send_order_to_chat"),
    path(
        "customer_service_dashboard/<int:staff_id>/",
        views.customer_service_dashboard,
        name="customer_service_dashboard",
    ),
    path(
        "request_human_service/",
        views.request_human_service,
        name="request_human_service",
    ),
    path(
        "send_order_to_cs_chat/",
        views.send_order_to_cs_chat,
        name="send_order_to_cs_chat",
    ),
    path("human_chat/<int:consultation_id>/", views.human_chat, name="human_chat"),
    path(
        "accept_consultation/<int:consultation_id>/",
        views.accept_consultation,
        name="accept_consultation",
    ),
    path("cs_chat/<int:consultation_id>/", views.cs_chat, name="cs_chat"),
    path(
        "request_human_service/",
        views.request_human_service,
        name="request_human_service",
    ),
    path(
        "get_chat_history/<int:consultation_id>/",
        views.get_chat_history,
        name="get_chat_history",
    ),
    path(
        "end_consultation/<int:consultation_id>/",
        views.end_consultation,
        name="end_consultation",
    ),
    path(
        "end_consultation_by_staff/<int:consultation_id>/",
        views.end_consultation_by_staff,
        name="end_consultation_by_staff",
    ),

    path(
        "hide_consultation/<int:consultation_id>/",
        views.hide_consultation,
        name="hide_consultation",
    ),
    path("human_chat/", views.human_chat, name="human_chat"),
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
