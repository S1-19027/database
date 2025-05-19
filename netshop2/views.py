# 伪代码，需根据实际项目结构调整
import os
from django.shortcuts import render, redirect
from django.contrib.auth.hashers import check_password
from userapp.models import User
from consultapp.models import Human_CustomerService


def login_view(request):
    if request.method == "GET":
        return render(request, "login.html")
    username = request.POST.get("username")
    password = request.POST.get("password")
    user_type = request.POST.get("user_type")

    if user_type == "user":
        try:
            user = User.objects.get(nickname=username)
            if check_password(password, user.password):
                request.session["user_id"] = user.user_id
                # 登录成功后保存 user_id 到 session
                return redirect("user_dashboard")
            else:
                return render(request, "login.html", {"error": "密码错误"})
        except User.DoesNotExist:
            return render(request, "login.html", {"error": "用户不存在"})
    elif user_type == "staff":
        try:
            staff = Human_CustomerService.objects.get(username=username)
            if check_password(password, staff.password):
                return redirect("customer_service_dashboard", staff_id=staff.staff_id)
            else:
                return render(request, "login.html", {"error": "密码错误"})
        except Human_CustomerService.DoesNotExist:
            return render(request, "login.html", {"error": "客服不存在"})
    return render(request, "login.html")


# views.py
from django.shortcuts import render
from productsapp.models import Product
from ordersapp.models import Order
from django.utils import timezone
from consultapp.models import Consultation, ConversationRecord


def user_dashboard(request):
    user_id = request.session.get("user_id")
    if not user_id:
        return redirect("login")
    user = User.objects.get(user_id=user_id)
    products = Product.objects.all()
    consultation = Consultation.objects.create(
        user=user, consultation_time=timezone.now()
    )
    consultation_id = request.session.get("consultation_id")

    if request.method == "POST":
        # 处理消息发送
        message = request.POST["message"]
        # 保存消息到数据库

    chat_history = []
    if consultation_id:
        consultation = Consultation.objects.get(consultation_id=consultation_id)
        chat_history = ConversationRecord.objects.filter(
            consultation=consultation
        ).order_by("time")
    return render(
        request,
        "user_dashboard.html",
        {
            "user": user,
            "products": products,
            "chat_history": chat_history,
        },
    )


# views.py
def purchase_product(request, product_id):
    user_id = request.session.get("user_id")
    if not user_id:
        return redirect("login")
    user = User.objects.get(user_id=user_id)
    product = Product.objects.get(product_id=product_id)

    if request.method == "POST":
        quantity = int(request.POST["quantity"])
        address = request.POST["address"]

        total_amount = product.price * quantity
        order = Order(
            user=user,
            product=product,
            quantity=quantity,
            total_amount=total_amount,
            valid_status="valid",
        )
        order.save()

        return redirect("payment", order_id=order.order_id)

    return render(request, "purchase_product.html", {"product": product})


def user_orders(request):
    orders = Order.objects.filter(user=request.user)
    return render(request, "user_orders.html", {"orders": orders})


def user_info(request):
    user_id = request.session.get("user_id")
    if not user_id:
        return redirect("login")
    user = User.objects.get(user_id=user_id)
    return render(request, "user_info.html", {"user": user})


from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from volcenginesdkarkruntime import Ark
from consultapp.models import ConversationRecord
from django.utils import timezone
import json


# @login_required
def ai_chat_view(request):
    if request.method == "POST":
        message = request.POST.get("message", "").strip()
        user_id = request.session.get("user_id")
        if not user_id:
            return JsonResponse({"success": False, "error": "未登录"}, status=401)
        user = User.objects.get(user_id=user_id)
        consultation_id = request.session.get("consultation_id")
        if not consultation_id:
            return JsonResponse({"success": False, "error": "会话未初始化"}, status=400)
        consultation = Consultation.objects.get(consultation_id=consultation_id)
        # 调用AI接口
        if not message:
            return JsonResponse({"success": False, "error": "消息不能为空"})
        if message:
            try:

                # 保存用户消息
                ConversationRecord.objects.create(
                    user=user,
                    content=message,
                    time=timezone.now(),
                    consultation=consultation,
                    role="user",
                )
                client = Ark(
                    api_key=os.environ.get("ARK_API_KEY"),
                )
                completion = client.chat.completions.create(
                    model="doubao-1-5-thinking-pro-250415",
                    messages=[{"role": "user", "content": message}],
                )
                ai_response = completion.choices[0].message.content

                # 保存AI回复
                ConversationRecord.objects.create(
                    user=user,
                    content=ai_response,
                    time=timezone.now(),
                    consultation=consultation,
                    role="ai",
                )

                return JsonResponse(
                    {"success": True, "response": ai_response}
                )  # 返回AI回复内容

            except Exception as e:
                return JsonResponse(
                    {
                        "success": False,
                        "error": str(e),
                    },
                    status=500,
                )
        return JsonResponse({"success": False, "error": "仅支持POST请求"}, status=405)

    # 获取对话历史
    # chat_history = ConversationRecord.objects.filter(user=request.user).order_by(
    #     "timestamp"
    # )[:20]
    # return render(request, "ai_chat.html", {"chat_history": chat_history})


@login_required
@csrf_exempt
def clear_chat(request):
    if request.method == "POST":
        ConversationRecord.objects.filter(user=request.user).delete()
        return JsonResponse({"success": True})
    return JsonResponse({"success": False, "error": "Invalid request"})
