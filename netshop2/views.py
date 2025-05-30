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
                consultation = Consultation.objects.create(
                    user=user, consultation_time=timezone.now()
                )
                request.session["consultation_id"] = consultation.consultation_id
                return redirect("user_dashboard")
            else:
                return render(request, "login.html", {"error": "密码错误"})
        except User.DoesNotExist:
            return render(request, "login.html", {"error": "用户不存在"})
    elif user_type == "staff":
        try:
            staff = Human_CustomerService.objects.get(username=username)
            if check_password(password, staff.password):
                request.session["staff_id"] = staff.staff_id
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

    consultation_id = request.session.get("consultation_id")
    if not consultation_id:
        consultation = Consultation.objects.create(
            user=user, consultation_time=timezone.now()
        )
        request.session["consultation_id"] = consultation.consultation_id
        return render(
            request, "user_dashboard.html", {"error": "当前没有会话，请先发起咨询"}
        )
    try:
        consultation = Consultation.objects.get(consultation_id=consultation_id)
    except Consultation.DoesNotExist:
        return render(
            request, "user_dashboard.html", {"error": "会话不存在，请重新发起咨询"}
        )
    orders = Order.objects.filter(user=user).order_by("order_id")
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
            "orders": orders,
            "consultation": consultation,
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
        user_id = request.session.get("user_id")
        consultation_id = request.session.get("consultation_id")
        if not user_id or not consultation_id:
            return JsonResponse({"success": False, "error": "未登录或会话未初始化"})
        user = User.objects.get(user_id=user_id)
        consultation = Consultation.objects.create(
            user=user, consultation_time=timezone.now()
        )
        request.session["consultation_id"] = consultation.consultation_id
        return JsonResponse({"success": True})
    return JsonResponse({"success": False, "error": "Invalid request"})


def payment(request, order_id):
    user_id = request.session.get("user_id")
    if not user_id:
        return redirect("login")
    user = User.objects.get(user_id=user_id)
    # orders = Order.objects.filter(pk=order_id, user=user).order_by("order_id")
    orders = Order.objects.all().order_by("order_id")  # 查询所有订单
    return render(request, "payment.html", {"orders": orders})


from ordersapp.models import Order
from consultapp.models import ConversationRecord, Consultation
from django.http import JsonResponse
from django.utils import timezone


def send_order_to_chat(request):
    if request.method == "POST":
        user_id = request.session.get("user_id")
        if not user_id:
            return JsonResponse({"success": False, "error": "未登录"}, status=401)
        order_id = request.POST.get("order_id")
        try:
            order = Order.objects.get(pk=order_id, user__user_id=user_id)
            consultation_id = request.session.get("consultation_id")
            consultation = Consultation.objects.get(consultation_id=consultation_id)
            # 构造订单信息
            order_info = f"订单号: {order.order_id}\n商品: {order.product.name}\n数量: {order.quantity}\n总价: ¥{order.total_amount}\n状态: {order.valid_status}"
            # 保存到对话
            ConversationRecord.objects.create(
                user=order.user,
                content=order_info,
                time=timezone.now(),
                consultation=consultation,
                role="user",
            )
            return JsonResponse({"success": True})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=400)
    return JsonResponse({"success": False, "error": "仅支持POST请求"}, status=405)


from consultapp.models import Consultation, ConversationRecord, Human_CustomerService
from django.shortcuts import render, redirect
from django.utils import timezone


def customer_service_dashboard(request, staff_id):
    # 只允许人工客服账号访问
    staff_id = request.session.get("staff_id")
    if not staff_id:
        return redirect("login")
    staff = Human_CustomerService.objects.get(staff_id=staff_id)
    # 查询所有等待人工客服的会话
    waiting_consultations = Consultation.objects.filter(
        customer_service__isnull=True, is_hidden=False
    ).order_by("consultation_time")
    # 查询当前客服正在处理的会话
    my_consultations = Consultation.objects.filter(customer_service=staff)
    return render(
        request,
        "customer_service_dashboard.html",
        {
            "staff": staff,
            "waiting_consultations": waiting_consultations,
            "my_consultations": my_consultations,
        },
    )


def accept_consultation(request, consultation_id):
    staff_id = request.session.get("staff_id")
    if not staff_id:
        return redirect("login")
    staff = Human_CustomerService.objects.get(staff_id=staff_id)
    consultation = Consultation.objects.get(consultation_id=consultation_id)
    consultation.customer_service = staff
    consultation.save()
    return redirect("cs_chat", consultation_id=consultation_id)


def cs_chat(request, consultation_id):
    staff_id = request.session.get("staff_id")
    if not staff_id:
        return redirect("login")
    staff = Human_CustomerService.objects.get(staff_id=staff_id)
    consultation = Consultation.objects.get(consultation_id=consultation_id)
    chat_history = ConversationRecord.objects.filter(
        consultation=consultation
    ).order_by("time")
    if request.method == "POST":
        message = request.POST.get("message", "").strip()
        if message:
            ConversationRecord.objects.create(
                user=consultation.user,
                customer_service=staff,
                content=message,
                time=timezone.now(),
                consultation=consultation,
                role="human",
            )
        return redirect("cs_chat", consultation_id=consultation_id)
    return render(
        request,
        "cs_chat.html",
        {
            "staff": staff,
            "consultation": consultation,
            "chat_history": chat_history,
        },
    )


from django.http import JsonResponse


def request_human_service(request):
    if request.method == "POST":
        consultation_id = request.session.get("consultation_id")
        if not consultation_id:
            return JsonResponse({"success": False, "error": "会话未初始化"})
        consultation = Consultation.objects.get(consultation_id=consultation_id)
        consultation.customer_service = None  # 标记为等待人工客服
        consultation.save()
        return JsonResponse({"success": True})
    return JsonResponse({"success": False, "error": "仅支持POST请求"}, status=405)


from django.http import JsonResponse


def request_human_service(request):
    if request.method == "POST":
        consultation_id = request.session.get("consultation_id")
        if not consultation_id:
            return JsonResponse({"success": False, "error": "会话未初始化"})
        consultation = Consultation.objects.get(consultation_id=consultation_id)
        consultation.customer_service = None  # 标记为等待人工客服
        consultation.save()
        return JsonResponse({"success": True})
    return JsonResponse({"success": False, "error": "仅支持POST请求"}, status=405)


# def human_chat(request):
#     if request.method == "POST":
#         user_id = request.session.get("user_id")
#         consultation_id = request.session.get("consultation_id")
#         message = request.POST.get("message", "").strip()
#         if user_id and consultation_id and message:
#             consultation = Consultation.objects.get(consultation_id=consultation_id)
#             ConversationRecord.objects.create(
#                 user=consultation.user,
#                 customer_service=consultation.customer_service,
#                 content=message,
#                 time=timezone.now(),
#                 consultation=consultation,
#                 role="user",
#             )
#             return JsonResponse({"success": True})
#         # return JsonResponse({"success": False, "error": "参数错误"})
#     return JsonResponse({"success": False, "error": "仅支持POST请求"}, status=405)


from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse


@csrf_exempt
def send_order_to_cs_chat(request):
    if request.method == "POST":
        order_id = request.POST.get("order_id")
        consultation_id = request.POST.get("consultation_id")
        try:
            order = Order.objects.get(order_id=order_id)
            consultation = Consultation.objects.get(consultation_id=consultation_id)
            staff_id = request.session.get("staff_id")
            staff = Human_CustomerService.objects.get(staff_id=staff_id)
            order_info = f"订单号: {order.order_id}\n商品: {order.product.name}\n数量: {order.quantity}\n总价: ¥{order.total_amount}\n状态: {order.valid_status}"
            ConversationRecord.objects.create(
                user=order.user,
                customer_service=staff,
                content=order_info,
                time=timezone.now(),
                consultation=consultation,
                role="human",
            )
            return JsonResponse({"success": True})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=400)
    return JsonResponse({"success": False, "error": "仅支持POST请求"}, status=405)


from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def human_chat(request, consultation_id):
    consultation = Consultation.objects.get(consultation_id=consultation_id)
    if request.method == "POST":
        message = request.POST.get("message", "").strip()
        # 判断是用户还是客服发的
        user_id = request.session.get("user_id")
        staff_id = request.session.get("staff_id")
        if user_id and consultation.user.user_id == user_id:
            role = "user"
            sender = consultation.user
            staff = consultation.customer_service
        elif (
            staff_id
            and consultation.customer_service
            and consultation.customer_service.staff_id == staff_id
        ):
            role = "human"
            sender = consultation.customer_service
            staff = consultation.customer_service
        else:
            return JsonResponse({"success": False, "error": "无权限"})
        if message:
            ConversationRecord.objects.create(
                user=consultation.user,
                customer_service=staff,
                content=message,
                time=timezone.now(),
                consultation=consultation,
                role=role,
            )
            return JsonResponse({"success": True})
        return JsonResponse({"success": False, "error": "消息不能为空"})
    chat_history = ConversationRecord.objects.filter(
        consultation=consultation
    ).order_by("time")
    return render(
        request,
        "user_dashboard.html",
        {
            "consultation": consultation,
            "chat_history": chat_history,
            # 其它上下文...
        },
    )
    # return JsonResponse({"success": False, "error": "仅支持POST请求"}, status=405)


# views.py
def get_chat_history(request, consultation_id):
    consultation = Consultation.objects.get(consultation_id=consultation_id)
    chat_history = ConversationRecord.objects.filter(
        consultation=consultation
    ).order_by("time")
    return render(request, "chat_history_fragment.html", {"chat_history": chat_history})


from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse


@csrf_exempt
def end_consultation(request, consultation_id):
    if request.method == "POST":
        rating = request.POST.get("rating")
        try:
            consultation = Consultation.objects.get(consultation_id=consultation_id)
            consultation.customer_service = None  # 结束人工客服，回到AI
            if rating:
                consultation.user_rating = float(rating)
            consultation.save()
            return JsonResponse({"success": True})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=400)
    return JsonResponse({"success": False, "error": "仅支持POST请求"}, status=405)


from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse


@csrf_exempt
def end_consultation_by_staff(request, consultation_id):
    if request.method == "POST":
        try:
            consultation = Consultation.objects.get(consultation_id=consultation_id)
            consultation.customer_service = None  # 让会话回到AI或待接入状态
            # consultation.status = "ended"  # 如果有状态字段可以加上
            consultation.save()
            return JsonResponse({"success": True})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=400)
    return JsonResponse({"success": False, "error": "仅支持POST请求"}, status=405)


@csrf_exempt
def hide_consultation(request, consultation_id):
    if request.method == "POST":
        try:
            consultation = Consultation.objects.get(consultation_id=consultation_id)
            if consultation.customer_service is None:
                consultation.is_hidden = True
                consultation.save()
                return JsonResponse({"success": True})
            else:
                return JsonResponse({"success": False, "error": "只能隐藏未接入的会话"})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=400)
    return JsonResponse({"success": False, "error": "仅支持POST请求"}, status=405)
