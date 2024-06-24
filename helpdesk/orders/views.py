import csv

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils.dateparse import parse_date
from openpyxl.workbook import Workbook

from accounts.models import CustomUser
from .forms import OrderProfileForm, OrderReassignmentForm, OrderStatusUpdateForm, ChatMessageForm, ProblemForm
from .models import Order, Problem, ChatMessage
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
from django.urls import reverse
from django.core.mail import send_mail
from django.utils import timezone
from django.db.models import Case, When, IntegerField


@login_required
def submit_order(request):
    problems = Problem.objects.all()
    building_choices = Order.BUILDING_CHOICES

    if request.method == 'POST':
        form = OrderProfileForm(request.POST, request.FILES)
        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.user
            order.save()
            print(request.user)
            send_mail(
                'Welcome to Our Site',
                'Thanks for signing up!',
                'from@example.com',
                ['36116@iitu.edu.kz'],
                fail_silently=False,
            )
            return redirect('orders:order_history')
    else:
        form = OrderProfileForm()

    return render(request, 'orders/submit_order.html', {
        'form': form,
        'problems': problems,
        'building_choices': building_choices
    })


@login_required
def order_detail(request, pk):
    order = get_object_or_404(Order, pk=pk)

    # Check if the user's role matches the department of the problem type or if the user is the creator
    can_modify_status = request.user.role.lower() == order.problem_type.department.lower() or request.user == order.user
    can_modify_executor = request.user.role.lower() == order.problem_type.department.lower()

    form, reassignment_form, message_form = None, None, None
    if request.method == 'POST':
        if 'status' in request.POST:
            form = OrderStatusUpdateForm(request.POST)
            if form.is_valid():
                order.status = form.cleaned_data['status']
                order.comments = form.cleaned_data['comment']
                order.save()
                return redirect('orders:order_detail', pk=order.pk)
        elif 'executor' in request.POST:
            reassignment_form = OrderReassignmentForm(request.POST, order=order, instance=order)
            if reassignment_form.is_valid():
                reassignment_form.save()
                return redirect('orders:order_detail', pk=order.pk)
        elif 'message' in request.POST:
            message_form = ChatMessageForm(request.POST)
            if message_form.is_valid():
                chat_message = message_form.save(commit=False)
                chat_message.order = order
                chat_message.user = request.user
                chat_message.save()
                return redirect('orders:order_detail', pk=order.pk)
    else:
        form = OrderStatusUpdateForm(initial={'status': order.status, 'comment': order.comments})
        reassignment_form = OrderReassignmentForm(order=order, instance=order)
        message_form = ChatMessageForm()

    chat_messages = ChatMessage.objects.filter(order=order)

    return render(request, 'orders/order_detail.html', {
        'order': order,
        'form': form,
        'reassignment_form': reassignment_form,
        'message_form': message_form,
        'chat_messages': chat_messages,
        'can_modify_status': can_modify_status,
        'can_modify_executor': can_modify_executor,
    })


@login_required
def send_message(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if request.method == 'POST':
        message_form = ChatMessageForm(request.POST)
        if message_form.is_valid():
            chat_message = message_form.save(commit=False)
            chat_message.order = order
            chat_message.user = request.user
            chat_message.save()
    return redirect('orders:order_detail', pk=order.pk)


@login_required
def order_history(request):
    user = request.user
    if user.role == 'admin':
        orders = Order.objects.all()
    elif user.role in ['ahd', 'dit']:
        orders = Order.objects.filter(problem_type__department=user.role.upper())
    else:
        orders = Order.objects.filter(user=user)

    urgency = request.GET.get('urgency')
    status = request.GET.get('status')

    if urgency:
        orders = orders.filter(urgency=urgency)
    if status:
        orders = orders.filter(status=status)

    # Sort orders by status
    orders = orders.annotate(
        status_order=Case(
            When(status='submitted', then=1),
            When(status='accepted', then=2),
            When(status='in_progress', then=3),
            When(status='completed', then=4),
            When(status='freeze', then=5),
            output_field=IntegerField(),
        )
    ).order_by('status_order')

    return render(request, 'orders/order_history.html', {
        'orders': orders,
        'urgency': urgency,
        'status': status,
    })


@login_required
def active_orders(request):
    user = request.user
    if user.role == 'admin':
        orders = Order.objects.filter(status__in=['accepted', 'in_progress', 'submitted'])
    elif user.role in ['ahd', 'dit']:
        orders = Order.objects.filter(problem_type__department=user.role.upper(),
                                      status__in=['accepted', 'in_progress', 'submitted'])
    else:
        orders = Order.objects.filter(user=user, status__in=['accepted', 'in_progress', 'submitted'])

    urgency = request.GET.get('urgency')
    status = request.GET.get('status')

    if urgency:
        orders = orders.filter(urgency=urgency)
    if status:
        orders = orders.filter(status=status)

    # Sort orders by status
    orders = orders.annotate(
        status_order=Case(
            When(status='submitted', then=1),
            When(status='accepted', then=2),
            When(status='in_progress', then=3),
            When(status='completed', then=4),
            When(status='freeze', then=5),
            output_field=IntegerField(),
        )
    ).order_by('status_order')

    return render(request, 'orders/active_orders.html', {
        'orders': orders,
        'urgency': urgency,
        'status': status,
    })


@login_required
def my_orders(request):
    orders = Order.objects.filter(executor=request.user).order_by('-created_at')
    return render(request, 'orders/my_orders.html', {'orders': orders})


@login_required
def update_order_status(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if request.user.is_staff:
        if request.method == 'POST':
            form = OrderStatusUpdateForm(request.POST)
            if form.is_valid():
                status = form.cleaned_data['status']
                comment = form.cleaned_data['comment']
                timestamp = form.cleaned_data['timestamp'] or timezone.now()

                order.status = status
                order.comment = comment
                order.updated_at = timestamp  # Update the general update timestamp

                if status == 'completed' and order.completed_at is None:
                    order.completed_at = timestamp  # Update completed time only if status is completed
                order.save()
                return HttpResponseRedirect(reverse('orders:order_detail', args=[order.id]))
        else:
            form = OrderStatusUpdateForm(initial={'status': order.status})
        return render(request, 'orders/update_order_status.html', {'form': form, 'order': order})
    else:
        return render(request, 'orders/order_detail.html', {'order': order, 'error': 'Unauthorized action'})


@login_required
def reports(request):
    if request.user.role != 'head':
        return redirect('orders:order_history')  # Redirect if user is not 'head'

    # Fetch filters from GET parameters
    problem_type_id = request.GET.get('problem_type')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    executor_id = request.GET.get('executor')
    building_type = request.GET.get('building')

    # Start with all completed orders
    orders = Order.objects.filter(status='completed')

    # Apply filters if provided
    if problem_type_id:
        orders = orders.filter(problem_type_id=problem_type_id)
    if start_date and end_date:
        start_date_parsed = parse_date(start_date)
        end_date_parsed = parse_date(end_date)
        orders = orders.filter(completed_at__range=[start_date_parsed, end_date_parsed])
    if executor_id:
        orders = orders.filter(executor_id=executor_id)
    if building_type:
        orders = orders.filter(building=building_type)

    if 'download' in request.GET:
        # Proceed with Excel file generation
        wb = Workbook()
        ws = wb.active
        ws.title = 'Completed Orders Report'

        headers = ['Order ID', 'Building', 'Room Number', 'Sender', 'Executor', 'Status', 'Urgency', 'Problem Type',
                   'Description', 'Completed At']
        ws.append(headers)

        for order in orders:
            row = [
                order.id,
                order.get_building_display(),
                order.room_number,
                order.user.username,
                order.executor.username if order.executor else 'None',
                order.get_status_display(),
                order.get_urgency_display(),
                order.problem_type.name if order.problem_type else 'None',
                order.description,
                order.completed_at.strftime('%Y-%m-%d %H:%M') if order.completed_at else 'Not completed'
            ]
            ws.append(row)

        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="completed_orders_report.xlsx"'
        wb.save(response)
        return response

    # Render the page with filters for user interaction
    problem_types = Problem.objects.all()
    executors = CustomUser.objects.filter(role__in=['ahd', 'dit'])
    buildings = dict(Order.BUILDING_CHOICES)

    return render(request, 'orders/reports.html', {
        'orders': orders,
        'problem_types': problem_types,
        'executors': executors,
        'buildings': buildings
    })


@login_required
def download_order_report(request, order_id):
    order = get_object_or_404(Order, pk=order_id)

    # Create an Excel workbook and sheet
    wb = Workbook()
    ws = wb.active
    ws.title = 'Order Detail Report'

    # Define column headers
    headers = ['Order ID', 'Building', 'Room Number', 'Sender', 'Executor', 'Status', 'Urgency', 'Description',
               'Created At', 'Completed At']
    ws.append(headers)

    # Prepare data row
    row = [
        order.id,
        order.get_building_display(),
        order.room_number,
        order.user.username,
        order.executor.username if order.executor else 'None',
        order.get_status_display(),
        order.get_urgency_display(),
        order.description,
        order.created_at.strftime('%Y-%m-%d %H:%M'),
        order.completed_at.strftime('%Y-%m-%d %H:%M') if order.completed_at else 'Not completed'
    ]
    ws.append(row)

    # Set HTTP response headers for downloading an Excel file
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="order_{order.id}_report.xlsx"'
    wb.save(response)
    return response


@login_required
def manage_problems(request):
    if request.user.role not in ['ahd', 'dit']:
        return redirect('orders:order_history')  # Redirect if user is not in the correct role

    problems = Problem.objects.filter(department=request.user.role.upper())
    problem_form = ProblemForm(request.POST or None)
    problem_to_edit = None

    if request.method == 'POST':
        if 'edit_problem' in request.POST:
            problem_id = request.POST.get('edit_problem')
            problem_to_edit = get_object_or_404(Problem, id=problem_id)
            problem_form = ProblemForm(request.POST, instance=problem_to_edit)
        else:
            problem_form = ProblemForm(request.POST)

        if problem_form.is_valid():
            problem_form.save()
            return redirect('orders:manage_problems')  # Redirect to the same page after saving

    return render(request, 'orders/settings.html', {
        'problems': problems,
        'problem_form': problem_form,
        'problem_to_edit': problem_to_edit,
        'user_role': request.user.role
    })
