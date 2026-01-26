from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'library' 

urlpatterns = [
    # ================= User Biasa =================
    path('', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),

    # ================= Petugas =================
    path('login_petugas/', views.login_petugas, name='login_petugas'),
path('register_petugas/', views.register_petugas, name='register_petugas'),
path('dashboard-petugas/', views.dashboard_petugas, name='dashboard_petugas'),
path('logout_petugas/', views.logout_petugas, name='logout_petugas'),


    # ================= BARANG =================
    path('buku/', views.daftar_barang, name='daftar_barang'),
    path('pinjam/<int:id>/', views.pinjam_barang, name='pinjam'),

    # ================= PENGEMBALIAN =================
    path('pengembalian/', views.pengembalian_barang, name='pengembalian_buku'),
    path('pengembalian/<int:id>/konfirmasi/', views.proses_pengembalian, name='proses_pengembalian'),
    path('pengembalian/proses/<int:id>/', views.proses_pengembalian, name='proses_pengembalian'),
    path('pinjam-ajax/<int:id>/', views.pinjam_barang_ajax, name='pinjam_ajax'),

    # ================= PETUGAS LAIN =================
    path('petugas/peminjaman/', views.petugas_peminjaman, name='petugas_peminjaman'),
    path('petugas/konfirmasi/<int:id>/', views.konfirmasi_petugas, name='konfirmasi_petugas'),
    path('petugas/tolak/<int:id>/', views.tolak_petugas, name='tolak_petugas'),
    path('pantau-pengembalian/', views.pantau_pengembalian, name='pantau_pengembalian'),
    path('status-peminjaman/', views.status_peminjaman, name='status_peminjaman'),

    # ================= KATEGORI & ULASAN =================
    path('kategori/<int:kategori_id>/', views.barang_per_kategori, name='kategori_relasi'),
    path('ulasan/<int:id>/', views.ulasan_barang, name='ulasan'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
