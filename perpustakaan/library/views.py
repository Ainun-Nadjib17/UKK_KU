from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User, Group
from django.utils import timezone
from django.contrib import messages
from django.http import HttpResponseForbidden
from datetime import timedelta

from .models import Barang, Peminjaman, Ulasan, Kategori
from .forms import PeminjamanForm, UlasanForm


# ======================
# AUTH
# ======================

def register_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        
        # Cek dulu apakah username sudah ada
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username sudah digunakan, pilih username lain.")
            return redirect("library:register")  # ganti dengan nama url register
        
        # Jika belum ada, buat user baru
        User.objects.create_user(username=username, password=password)
        messages.success(request, "Registrasi berhasil!")
        return redirect("library:login")  # ganti dengan url login
    
    return render(request, "register.html")

def login_view(request):
    if request.method == 'POST':
        user = authenticate(
            request,
            username=request.POST['username'],
            password=request.POST['password']
        )
        if user:
            login(request, user)
            return redirect('library:dashboard')
    return render(request, 'login.html')


def logout_view(request):
    logout(request)
    return redirect('library:login')


# ======================
# DASHBOARD
# ======================

@login_required
def dashboard(request):
    barang_list = Barang.objects.all()
    return render(request, 'dashboard.html', {
        'barang_list': barang_list
    })


# =========================
# REGISTER PETUGAS
# =========================
def register_petugas(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        confirm = request.POST['confirm']

        if password != confirm:
            messages.error(request, "Password tidak sama!")
            return redirect('library:register_petugas')  # pakai nama URL

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username sudah dipakai!")
            return redirect('library:register_petugas')

        # Buat user baru
        user = User.objects.create_user(username=username, password=password)
        petugas_group, created = Group.objects.get_or_create(name='petugas')
        user.groups.add(petugas_group)
        user.save()
        messages.success(request, "Akun petugas berhasil dibuat, silakan login!")
        return redirect('library:login_petugas')

    return render(request, 'petugas/register_petugas.html')  # path template sesuai folder


# =========================
# LOGIN PETUGAS
# =========================
def login_petugas(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)
        if user is not None and user.groups.filter(name='petugas').exists():
            login(request, user)
            return redirect('library:dashboard_petugas')
        else:
            messages.error(request, "Username/password salah atau bukan petugas!")
            return redirect('library:login_petugas')

    return render(request, 'petugas/login_petugas.html')  # path template sesuai folder


# =========================
# LOGOUT PETUGAS
# =========================
def logout_petugas(request):
    logout(request)
    return redirect('login_petugas')


# =========================
# DASHBOARD PETUGAS
# =========================
@login_required(login_url='login-petugas')  # pakai nama URL
def dashboard_petugas(request):
    # Cek apakah user termasuk petugas
    if not request.user.groups.filter(name='petugas').exists():
        messages.error(request, "Hanya petugas yang bisa mengakses halaman ini!")
        return redirect('library:register_petugas')
    
    barang_list = Barang.objects.all()  # ambil semua barang
    return render(request, 'dashboard_petugas.html', {'barang_list': barang_list})

@login_required
def pinjam_barang_ajax(request, id):
    if request.method != "POST":
        return JsonResponse({"success": False})

    barang = get_object_or_404(Barang, id=id)

    if barang.stok <= 0:
        return JsonResponse({
            "success": False,
            "message": "Stok habis"
        })

    with transaction.atomic():
        barang.stok -= 1
        barang.save()

    return JsonResponse({
        "success": True,
        "stok": barang.stok
    })




# ======================
# BARANG
# ======================

@login_required
def daftar_barang(request):
    barang = Barang.objects.all()
    return render(request, 'daftar_barang.html', {'barang': barang})


@login_required
def barang_per_kategori(request, kategori_id):
    kategori = get_object_or_404(Kategori, id=kategori_id)
    barang = Barang.objects.filter(kategori=kategori)
    return render(request, 'kategori_relasi.html', {
        'kategori': kategori,
        'barang': barang
    })


# ======================
# PEMINJAMAN
# ======================

from django.utils import timezone
from datetime import time
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

@login_required
def pinjam_barang(request, id):
    barang = get_object_or_404(Barang, id=id)

    # waktu sekarang
    tanggal_pinjam = timezone.now()

    # hari ini jam 16:00 WIB
    tanggal_kembali = timezone.localtime().replace(
        hour=16,
        minute=0,
        second=0,
        microsecond=0
    )

    # kalau sekarang sudah lewat jam 16:00,
    # otomatis geser ke besok jam 16:00 (AMAN)
    if tanggal_pinjam >= tanggal_kembali:
        tanggal_kembali += timezone.timedelta(days=1)

    if request.method == 'POST':
        form = PeminjamanForm(request.POST, request.FILES)
        if form.is_valid():
            pinjam = form.save(commit=False)
            pinjam.user = request.user
            pinjam.barang = barang
            pinjam.status = 'dipinjam'
            pinjam.tanggal_pinjam = tanggal_pinjam
            pinjam.tanggal_kembali = tanggal_kembali
            pinjam.save()
            return redirect('library:dashboard')
    else:
        form = PeminjamanForm()

    return render(request, 'peminjaman.html', {
        'barang': barang,
        'form': form,
        'tanggal_pinjam': tanggal_pinjam,
        'tanggal_kembali': tanggal_kembali
    })

# ======================
# PENGEMBALIAN
# ======================

@login_required
def pengembalian_barang(request):
    peminjaman = Peminjaman.objects.filter(
        user=request.user,
        status='dipinjam'
    )
    return render(request, 'pengembalian.html', {
        'peminjaman': peminjaman
    })


@login_required
def proses_pengembalian(request, id):
    try:
        pinjam = Peminjaman.objects.get(
            id=id,
            user=request.user,
            status='dipinjam'
        )
    except Peminjaman.DoesNotExist:
        messages.error(
            request,
            "Peminjaman tidak ditemukan atau sudah dikembalikan!"
        )
        return redirect('library:pengembalian_buku')  # ✅ FIX

    pinjam.status = 'dikembalikan'
    pinjam.tanggal_dikembalikan = timezone.now().date()

    # hitung denda
    if pinjam.tanggal_dikembalikan > pinjam.tanggal_kembali:
        telat = (pinjam.tanggal_dikembalikan - pinjam.tanggal_kembali).days
        pinjam.denda = telat * 2000
    else:
        pinjam.denda = 0

    pinjam.save()
    messages.success(request, "Pengembalian berhasil!")
    return redirect('library:pengembalian_buku')  # ✅ FIX


def pantau_pengembalian(request):
    data = Peminjaman.objects.filter(
        tanggal_dikembalikan__isnull=False
    ).order_by('-tanggal_dikembalikan')

    return render(
        request,
        'library/pantau_pengembalian.html',
        {'pengembalian': data}
    )


#-----------------------|
#--------PETUGAS -------|
#-----------------------|

from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import get_object_or_404, redirect, render
from .models import Peminjaman


@login_required(login_url='login_petugas')
def petugas_peminjaman(request):
    if not request.user.groups.filter(name='Petugas').exists():
        # Kalau user bukan di grup Petugas, redirect ke login_petugas
        return redirect('login_petugas')

    peminjaman = Peminjaman.objects.filter(
        status='dipinjam',
        diverifikasi_petugas=False
    )
    return render(request, 'petugas_peminjaman.html', {
        'peminjaman': peminjaman
    })


@login_required(login_url='login_petugas')
def konfirmasi_petugas(request, id):
    # Cek kalau user bukan petugas
    if not request.user.groups.filter(name='Petugas').exists():
        return redirect('login_petugas')

    pinjam = get_object_or_404(Peminjaman, id=id)

    if request.method == 'POST':
        pinjam.diverifikasi_petugas = True
        pinjam.save()

    return redirect('petugas_peminjaman')


@login_required(login_url='login_petugas')
def tolak_petugas(request, id):
    # Cek kalau user bukan petugas
    if not request.user.groups.filter(name='Petugas').exists():
        return redirect('login_petugas')

    pinjam = get_object_or_404(Peminjaman, id=id)

    if request.method == 'POST':
        pinjam.delete()

    return redirect('petugas_peminjaman')


# ======================
# ULASAN
# ======================

@login_required
def ulasan_barang(request, id):
    barang = get_object_or_404(Barang, id=id)

    if request.method == 'POST':
        form = UlasanForm(request.POST)
        if form.is_valid():
            ulasan = form.save(commit=False)
            ulasan.user = request.user
            ulasan.barang = barang
            ulasan.save()
            return redirect('dashboard')
    else:
        form = UlasanForm()

    return render(request, 'ulasan.html', {
        'barang': barang,
        'form': form
    })

#persetujuan Petugas
@login_required
def status_peminjaman(request):
    peminjaman = Peminjaman.objects.filter(user=request.user)

    return render(request, 'status_peminjaman.html', {
        'peminjaman': peminjaman
    })

