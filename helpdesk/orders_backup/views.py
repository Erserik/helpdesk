from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import OrderProfileForm, OrderStatusUpdateForm
from .models import Order, Problem
from django.http import HttpResponseRedirect
from django.urls import reverse

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
            return redirect('orders:order_history')
    else:
        form = OrderProfileForm()

    return render(request, 'orders/submit_order.html', {
        'form': form,
        'problems': problems,
        'building_choices': building_choices  
    })

@login_required
def order_history(request):
    user = request.user
    if user.role == 'admin':
        orders = Order.objects.all()
    else:
        orders = Order.objects.filter(user=user)
    
    urgency = request.GET.get('urgency')
    status = request.GET.get('status')

    if urgency:
        orders = orders.filter(urgency=urgency)
    if status:
        orders = orders.filter(status=status)

    return render(request, 'orders/order_history.html', {
        'orders': orders,
        'urgency': urgency,
        'status': status,
    })

@login_required
def order_detail(request, pk):
    order = get_object_or_404(Order, pk=pk)
    can_modify_status = request.user.role not in ["sender"]
    if request.method == 'POST':
        form = OrderStatusUpdateForm(request.POST)
        if form.is_valid():
            status = form.cleaned_data['status']
            comment = form.cleaned_data['comment']
            if status == 'freeze' and not comment:
                # Make sure there is a comment if the status is "freeze"
                form.add_error('comment', 'A comment is required when freezing the order.')
            else:
                order.status = status
                if comment:
                    order.comments = comment
                order.save()
                return redirect('orders:order_history')  # Redirect as needed
    else:
        form = OrderStatusUpdateForm(initial={'status': order.status, 'comment': order.comments})

    return render(request, 'orders/order_detail.html', {
        'order': order,
        'form': form,
        'can_modify_status': can_modify_status,
    })

@login_required
def active_orders(request):
    user = request.user
    # Filter out 'completed' orders from the query
    if user.role == 'admin':
        orders = Order.objects.exclude(status='completed')
    elif user.role in ['ahd', 'dit']:
        orders = Order.objects.filter(problem_type__department=user.role.upper()).exclude(status='completed')
    else:
        orders = Order.objects.filter(user=user).exclude(status='completed')

    urgency = request.GET.get('urgency')
    status = request.GET.get('status')

    if urgency:
        orders = orders.filter(urgency=urgency)
    if status:
        orders = orders.filter(status=status)

    return render(request, 'orders/active_orders.html', {
        'orders': orders,
        'urgency': urgency,
        'status': status,
    })

@login_required
def update_order_status(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if request.user.is_staff:
        # Check current status and update accordingly
        if order.status == 'submitted':
            order.status = 'accepted'
        elif order.status == 'accepted':
            order.status = 'completed'
        order.save()
        return HttpResponseRedirect(reverse('orders:order_detail', args=[order.id]))
    else:
        return render(request, 'orders/order_detail.html', {'order': order, 'error': 'Unauthorized action'})
