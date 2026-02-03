from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
# authenticate → ngecek username & password valid atau tidak
# login → menyimpan user ke session (login)
# logout → menghapus session user (logout)

from django.contrib.auth.decorators import login_required
# login_required → membatasi akses view hanya untuk user yang sudah login

from django.contrib.admin.views.decorators import staff_member_required
# staff_member_required → membatasi akses hanya untuk admin/staff (belum dipakai di sini)

from django.contrib.auth.models import User, Group
# User → model user bawaan Django
# Group → untuk role user (admin, petugas, dll)

from django.utils import timezone
# timezone → mengatur waktu berbasis timezone Django (belum dipakai di sini)

from django.contrib import messages
# messages → menampilkan pesan sementara (success / error) ke template

from django.http import HttpResponseForbidden
# HttpResponseForbidden → response 403 (akses ditolak) (belum dipakai)

from datetime import timedelta
# timedelta → manipulasi waktu (deadline, durasi, dll) (belum dipakai)

from .models import Barang, Peminjaman, Ulasan, Kategori
# Import model aplikasi (dipakai di view lain)

from .forms import PeminjamanForm, UlasanForm
# Import form aplikasi (dipakai di view lain)


# ======================
# AUTH
# ======================

def register_view(request):
    # View untuk registrasi user baru
    if request.method == "POST":
        # Ambil data dari form HTML
        username = request.POST.get("username")
        password = request.POST.get("password")
        
        # Cek apakah username sudah terdaftar
        if User.objects.filter(username=username).exists():
            # Jika sudah ada, tampilkan pesan error
            messages.error(request, "Username sudah digunakan, pilih username lain.")
            # Redirect kembali ke halaman register
            return redirect("library:register")
        
        # Jika username belum ada, buat user baru
        User.objects.create_user(username=username, password=password)
        # Tampilkan pesan sukses
        messages.success(request, "Registrasi berhasil!")
        # Redirect ke halaman login
        return redirect("library:login")
    
    # Jika request GET, tampilkan halaman register
    return render(request, "register.html")


def login_view(request):
    # View untuk login user
    if request.method == 'POST':
        # Autentikasi username & password
        user = authenticate(
            request,
            username=request.POST['username'],
            password=request.POST['password']
        )
        # Jika username & password benar
        if user:
            # Simpan user ke session (login)
            login(request, user)
            # Redirect ke dashboard
            return redirect('library:dashboard')
    
    # Jika GET atau login gagal, tampilkan halaman login
    return render(request, 'login.html')


def logout_view(request):
    # View untuk logout user
    # Menghapus session user
    logout(request)
    # Redirect ke halaman login
    return redirect('library:login')



# ======================
# DASHBOARD
# ======================

@login_required
# login_required → hanya user yang sudah login yang bisa akses dashboard
def dashboard(request):
    # Ambil semua data barang dari database
    barang_list = Barang.objects.all()
    
    # Kirim data barang ke template dashboard.html
    return render(request, 'dashboard.html', {
        'barang_list': barang_list
    })


# =========================
# REGISTER PETUGAS
# =========================

def register_petugas(request):
    # View untuk registrasi akun petugas
    if request.method == 'POST':
        # Ambil data dari form
        username = request.POST['username']
        password = request.POST['password']
        confirm = request.POST['confirm']

        # Cek apakah password dan konfirmasi sama
        if password != confirm:
            # Jika tidak sama, tampilkan pesan error
            messages.error(request, "Password tidak sama!")
            # Redirect kembali ke halaman register petugas
            return redirect('library:register_petugas')

        # Cek apakah username sudah digunakan
        if User.objects.filter(username=username).exists():
            # Jika sudah ada, tampilkan pesan error
            messages.error(request, "Username sudah dipakai!")
            # Redirect kembali ke halaman register petugas
            return redirect('library:register_petugas')

        # =====================
        # BUAT AKUN PETUGAS
        # =====================

        # Membuat user baru
        user = User.objects.create_user(username=username, password=password)
        
        # Ambil atau buat group "petugas"
        petugas_group, created = Group.objects.get_or_create(name='petugas')
        # Masukkan user ke group petugas
        user.groups.add(petugas_group)
        
        # Simpan perubahan user
        user.save()

        # Tampilkan pesan sukses
        messages.success(request, "Akun petugas berhasil dibuat, silakan login!")
        # Redirect ke halaman login petugas
        return redirect('library:login_petugas')

    # Jika request GET, tampilkan halaman register petugas
    return render(request, 'petugas/register_petugas.html')
    # path template sesuai struktur folder: templates/petugas/register_petugas.html


# =========================
# LOGIN PETUGAS
# =========================

def login_petugas(request):
    # View untuk login khusus akun petugas
    if request.method == 'POST':
        # Ambil username & password dari form
        username = request.POST['username']
        password = request.POST['password']

        # Autentikasi username & password
        user = authenticate(request, username=username, password=password)

        # =====================
        # VALIDASI PETUGAS
        # =====================

        # Cek:
        # 1. User ada (username & password benar)
        # 2. User termasuk ke group "petugas"
        if user is not None and user.groups.filter(name='petugas').exists():
            # Jika valid, simpan user ke session (login)
            login(request, user)
            # Redirect ke dashboard petugas
            return redirect('library:dashboard_petugas')
        else:
            # Jika gagal (salah password atau bukan petugas)
            messages.error(request, "Username/password salah atau bukan petugas!")
            # Redirect kembali ke halaman login petugas
            return redirect('library:login_petugas')

    # Jika request GET, tampilkan halaman login petugas
    return render(request, 'petugas/login_petugas.html')
    # path template: templates/petugas/login_petugas.html


# =========================
# LOGOUT PETUGAS
# =========================

def logout_petugas(request):
    # Menghapus session petugas yang sedang login
    logout(request)
    # Redirect ke halaman login petugas
    return redirect('login_petugas')



# =========================
# DASHBOARD PETUGAS
# =========================

@login_required(login_url='login-petugas')  
# login_required → hanya user login yang bisa akses
# login_url → kalau belum login, diarahkan ke halaman login petugas
def dashboard_petugas(request):
    # =====================
    # CEK ROLE PETUGAS
    # =====================

    # Pastikan user yang login termasuk group "petugas"
    if not request.user.groups.filter(name='petugas').exists():
        # Jika bukan petugas, tampilkan pesan error
        messages.error(request, "Hanya petugas yang bisa mengakses halaman ini!")
        # Redirect ke halaman register petugas
        return redirect('library:register_petugas')
    
    # Ambil semua data barang dari database
    barang_list = Barang.objects.all()
    
    # Kirim data barang ke template dashboard_petugas.html
    return render(request, 'dashboard_petugas.html', {
        'barang_list': barang_list
    })


# =========================
# PINJAM BARANG (AJAX)
# =========================

@login_required
# login_required → hanya user yang sudah login boleh meminjam
def pinjam_barang_ajax(request, id):
    # Pastikan request datang dari method POST (AJAX)
    if request.method != "POST":
        # Jika bukan POST, kembalikan response gagal
        return JsonResponse({"success": False})

    # Ambil data barang berdasarkan ID
    # Jika ID tidak ditemukan, otomatis 404
    barang = get_object_or_404(Barang, id=id)

    # =====================
    # CEK STOK BARANG
    # =====================

    # Jika stok habis
    if barang.stok <= 0:
        return JsonResponse({
            "success": False,
            "message": "Stok habis"
        })

    # =====================
    # UPDATE STOK (AMAN)
    # =====================

    # transaction.atomic → memastikan update stok aman (anti race condition)
    with transaction.atomic():
        # Kurangi stok barang
        barang.stok -= 1
        # Simpan perubahan ke database
        barang.save()

    # Response sukses + stok terbaru (buat update UI tanpa reload)
    return JsonResponse({
        "success": True,
        "stok": barang.stok
    })




# ======================
# BARANG
# ======================

@login_required
# login_required → hanya user yang sudah login bisa melihat daftar barang
def daftar_barang(request):
    # Ambil semua data barang dari database
    barang = Barang.objects.all()
    
    # Kirim data barang ke template daftar_barang.html
    return render(request, 'daftar_barang.html', {
        'barang': barang
    })


@login_required
# login_required → user harus login untuk melihat barang per kategori
def barang_per_kategori(request, kategori_id):
    # Ambil data kategori berdasarkan ID
    # Jika tidak ditemukan, otomatis 404
    kategori = get_object_or_404(Kategori, id=kategori_id)
    
    # Ambil semua barang yang termasuk kategori tersebut
    barang = Barang.objects.filter(kategori=kategori)
    
    # Kirim data ke template kategori_relasi.html
    return render(request, 'kategori_relasi.html', {
        'kategori': kategori,
        'barang': barang
    })


# ======================
# PEMINJAMAN
# ======================

from django.utils import timezone
# timezone → waktu aware (aman timezone Django)

from datetime import time
# time → manipulasi jam (di sini tidak dipakai langsung)

from django.contrib.auth.decorators import login_required
# login_required → hanya user login boleh meminjam

from django.shortcuts import get_object_or_404, redirect, render
# get_object_or_404 → ambil data atau 404
# redirect → pindah halaman
# render → render template


@login_required
def pinjam_barang(request, id):
    # Ambil data barang berdasarkan ID
    barang = get_object_or_404(Barang, id=id)

    # =====================
    # SET WAKTU PEMINJAMAN
    # =====================

    # Waktu pinjam = waktu sekarang
    tanggal_pinjam = timezone.now()

    # Default waktu kembali = hari ini jam 16:00 WIB
    tanggal_kembali = timezone.localtime().replace(
        hour=16,
        minute=0,
        second=0,
        microsecond=0
    )

    # Jika waktu sekarang sudah lewat jam 16:00,
    # maka waktu kembali otomatis digeser ke besok jam 16:00
    if tanggal_pinjam >= tanggal_kembali:
        tanggal_kembali += timezone.timedelta(days=1)

    # =====================
    # PROSES FORM
    # =====================

    if request.method == 'POST':
        # Ambil data dari form peminjaman
        form = PeminjamanForm(request.POST, request.FILES)
        
        # Validasi form
        if form.is_valid():
            # Jangan langsung simpan ke DB
            pinjam = form.save(commit=False)
            
            # Set relasi user & barang
            pinjam.user = request.user
            pinjam.barang = barang
            
            # Set status peminjaman
            pinjam.status = 'dipinjam'
            
            # Set tanggal pinjam & kembali
            pinjam.tanggal_pinjam = tanggal_pinjam
            pinjam.tanggal_kembali = tanggal_kembali
            
            # Simpan ke database
            pinjam.save()
            
            # Setelah berhasil, redirect ke dashboard
            return redirect('library:dashboard')
    else:
        # Jika GET, tampilkan form kosong
        form = PeminjamanForm()

    # =====================
    # RENDER HALAMAN
    # =====================

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
        return redirect('library:pengembalian_buku')

    # =====================
    # PROSES PENGEMBALIAN
    # =====================
    pinjam.status = 'dikembalikan'
    pinjam.tanggal_dikembalikan = timezone.now().date()

    # 🔥 SIMPAN FOTO BUKTI
    if request.method == 'POST' and 'bukti' in request.FILES:
        pinjam.bukti_pengembalian = request.FILES['bukti']

    # =====================
    # HITUNG DENDA
    # =====================
    if pinjam.tanggal_dikembalikan > pinjam.tanggal_kembali:
        telat = (pinjam.tanggal_dikembalikan - pinjam.tanggal_kembali).days
        pinjam.denda = telat * 2000
    else:
        pinjam.denda = 0

    pinjam.save()

    messages.success(request, "Pengembalian berhasil, menunggu verifikasi petugas.")
    return redirect('library:pengembalian_buku')

# ======================
# PANTAU PENGEMBALIAN
# ======================

def pantau_pengembalian(request):
    # Ambil semua data peminjaman
    # yang sudah dikembalikan (tanggal_dikembalikan tidak null)
    data = Peminjaman.objects.filter(
        tanggal_dikembalikan__isnull=False
    ).order_by('-tanggal_dikembalikan')
    # Urutkan dari yang terbaru

    # Kirim data ke template pantau_pengembalian.html
    return render(
        request,
        'library/pantau_pengembalian.html',
        {
            'pengembalian': data
        }
    )


#-----------------------|
#-------- PETUGAS ------|
#-----------------------|

from django.contrib.admin.views.decorators import staff_member_required
# staff_member_required → pembatasan khusus admin Django (belum dipakai di bawah)

from django.shortcuts import get_object_or_404, redirect, render
# get_object_or_404 → ambil data atau otomatis 404
# redirect → pindah halaman
# render → render template HTML

from .models import Peminjaman
# Import model Peminjaman


@login_required(login_url='login_petugas')
# login_required → hanya user login yang bisa akses
# login_url → jika belum login, diarahkan ke login petugas
def petugas_peminjaman(request):
    # Cek apakah user termasuk grup "Petugas"
    if not request.user.groups.filter(name='Petugas').exists():
        # Kalau bukan petugas, redirect ke halaman login petugas
        return redirect('login_petugas')

    # Ambil semua peminjaman:
    # - status masih dipinjam
    # - belum diverifikasi petugas
    peminjaman = Peminjaman.objects.filter(
        status='dipinjam',
        diverifikasi_petugas=False
    )

    # Kirim data ke template petugas_peminjaman.html
    return render(request, 'petugas_peminjaman.html', {
        'peminjaman': peminjaman
    })


@login_required(login_url='login_petugas')
def konfirmasi_petugas(request, id):
    # Cek apakah user bukan petugas
    if not request.user.groups.filter(name='Petugas').exists():
        # Jika bukan petugas, paksa ke login petugas
        return redirect('login_petugas')

    # Ambil data peminjaman berdasarkan ID
    pinjam = get_object_or_404(Peminjaman, id=id)

    # Jika request POST (klik tombol konfirmasi)
    if request.method == 'POST':
        # Set status diverifikasi oleh petugas
        pinjam.diverifikasi_petugas = True
        # Simpan perubahan ke database
        pinjam.save()

    # Kembali ke halaman daftar peminjaman petugas
    return redirect('library:petugas_peminjaman')


@login_required(login_url='login_petugas')
def tolak_petugas(request, id):
    # Cek apakah user bukan petugas
    if not request.user.groups.filter(name='Petugas').exists():
        return redirect('login_petugas')

    try:
        # Ambil data peminjaman berdasarkan ID
        pinjam = Peminjaman.objects.get(id=id)
    except Peminjaman.DoesNotExist:
        # Jika data tidak ditemukan, kembali ke dashboard petugas
        return redirect('library:petugas_peminjaman')

    # Jika request POST (klik tombol tolak)
    if request.method == 'POST':
        # Hapus data peminjaman dari database
        pinjam.delete()

    # Kembali ke halaman daftar peminjaman petugas
    return redirect('library:petugas_peminjaman')



# ======================
# ULASAN
# ======================

@login_required
# login_required → hanya user login yang bisa memberi ulasan
def ulasan_barang(request, id):
    # Ambil data barang berdasarkan ID
    barang = get_object_or_404(Barang, id=id)

    if request.method == 'POST':
        # Ambil data ulasan dari form
        form = UlasanForm(request.POST)
        if form.is_valid():
            # Jangan langsung simpan ke DB
            ulasan = form.save(commit=False)
            # Set user yang memberi ulasan
            ulasan.user = request.user
            # Set barang yang diulas
            ulasan.barang = barang
            # Simpan ulasan ke database
            ulasan.save()
            # Setelah sukses, kembali ke dashboard
            return redirect('library:dashboard')
    else:
        # Jika GET, tampilkan form kosong
        form = UlasanForm()

    # Render halaman ulasan
    return render(request, 'ulasan.html', {
        'barang': barang,
        'form': form
    })


# ======================
# STATUS PEMINJAMAN (USER)
# ======================

# persetujuan petugas (status peminjaman user)
@login_required
def status_peminjaman(request):
    # Ambil semua peminjaman milik user yang sedang login
    peminjaman = Peminjaman.objects.filter(user=request.user)

    # Kirim data ke template status_peminjaman.html
    return render(request, 'status_peminjaman.html', {
        'peminjaman': peminjaman
    })
