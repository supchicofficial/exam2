from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from .models import *


def home(request):
    return render(request, 'home.html')


def register(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        password2 = request.POST.get('password2', '')
        if not username:
            error = 'Введите имя пользователя.'
        elif password != password2:
            error = 'Пароли не совпадают.'
        elif CustomUser.objects.filter(username=username).exists():
            error = 'Это имя пользователя уже занято.'
        else:
            user = CustomUser.objects.create_user(
                username=username,
                password=password
            )
            login(request, user)
            return redirect('home')
        return render(request, 'register.html', {'error': error, 'username': username})
    return render(request, 'register.html')


def user_login(request):
    if request.method == 'POST':
        user = authenticate(
            request,
            username=request.POST.get('username', ''),
            password=request.POST.get('password', '')
        )
        if user:
            login(request, user)
            return redirect('home')
        return render(request, 'login.html', {'error': 'Неверное имя пользователя или пароль.'})
    return render(request, 'login.html')


@login_required
@require_POST
def user_logout(request):
    logout(request)
    return redirect('home')


@login_required
def fields(request):
    fields = Field.objects.filter(is_active=True)
    categories = Category.objects.filter(is_active=True)
    search = request.GET.get('search', '').strip()
    category = request.GET.get('category', '')
    if search:
        fields = fields.filter(Q(name__icontains=search) | Q(address__icontains=search))
    if category.isdigit() and categories.filter(pk=category).exists():
        fields = fields.filter(category_id=category)
    return render(request, 'fields.html', {
        'fields': fields,
        'categories': categories,
        'search': search,
        'selected_category': category
    })


@login_required
def field_detail(request, pk):
    field = get_object_or_404(Field, id=pk, is_active=True)
    return render(request, 'field_detail.html', {'field': field})


@login_required
@require_POST
def book_field(request, pk):
    with transaction.atomic():
        field = get_object_or_404(
            Field.objects.select_for_update(),id=pk,is_active=True)
        if not field.is_free:
            messages.error(request, 'Это поле уже занято.')
            return redirect('field_detail', pk=pk)
        team = request.POST.get('has_team')
        if team not in ('yes', 'no'):
            messages.error(request, 'Укажите, есть ли у вас команда.')
            return redirect('field_detail', pk=pk)
        try:
            players = int(request.POST.get('players_needed', '0'))
        except (TypeError, ValueError):
            messages.error(request, 'Количество игроков должно быть числом.')
            return redirect('field_detail', pk=pk)
        if players < 0:
            messages.error(request, 'Количество игроков не может быть отрицательным.')
            return redirect('field_detail', pk=pk)
        if team == 'yes':
            players = 0
        Booking.objects.create(user=request.user,field=field,has_team=team == 'yes',players_needed=players,status='active')
        field.is_free = False
        field.save(update_fields=['is_free'])
    return redirect('my_fields')


@login_required
def my_fields(request):
    bookings = Booking.objects.filter(user=request.user).select_related('field').order_by('-created_at')
    return render(request, 'my_fields.html', {'bookings': bookings})


@login_required
@require_POST
def cancel_booking(request, pk):
    with transaction.atomic():
        booking = get_object_or_404(
            Booking.objects.select_for_update().select_related('field'),id=pk,user=request.user)
        if booking.status == 'active':
            booking.status = 'cancelled'
            booking.save(update_fields=['status'])
            if not Booking.objects.filter(field=booking.field, status='active').exists():
                booking.field.is_free = True
                booking.field.save(update_fields=['is_free'])
    return redirect('my_fields')


@login_required
@require_POST
def finish_booking(request, pk):
    with transaction.atomic():
        booking = get_object_or_404(
            Booking.objects.select_for_update().select_related('field'),id=pk, user=request.user)
        if booking.status == 'active':
            booking.status = 'completed'
            booking.save(update_fields=['status'])
            if not Booking.objects.filter(field=booking.field, status='active').exists():
                booking.field.is_free = True
                booking.field.save(update_fields=['is_free'])
    return redirect('my_fields')


@login_required
def play_together(request):
    bookings = Booking.objects.filter(
        status='active',
        has_team=False
    ).select_related('user', 'field').prefetch_related('participants')
    return render(request, 'play_together.html', {'bookings': bookings})


@login_required
@require_POST
def join_booking(request, pk):
    booking = get_object_or_404(Booking, id=pk, status='active', has_team=False)
    if booking.user != request.user:
        Participant.objects.get_or_create(booking=booking,user=request.user)
    return redirect('play_together')


@login_required
def profile(request):
    return render(request, 'profile.html')


@login_required
def profile_edit(request):
    if request.method == 'POST':
        request.user.phone = request.POST.get('phone', '').strip()
        request.user.about = request.POST.get('about', '').strip()
        if request.FILES.get('photo'):
            request.user.photo = request.FILES['photo']
        request.user.save(update_fields=['phone', 'about', 'photo'])
        return redirect('profile')
    return render(request, 'profile_edit.html')


@login_required
def user_profile(request, pk):
    profile_user = get_object_or_404(CustomUser, id=pk, is_active=True)
    return render(request, 'user_profile.html', {'profile_user': profile_user})
