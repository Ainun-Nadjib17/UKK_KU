from django.db import models
# models → modul ORM Django untuk bikin tabel database

from django.contrib.auth.models import User
# User → model user bawaan Django (akun login)


# ===============================
# KATEGORI BARANG
# ===============================
class Kategori(models.Model):
    # Nama kategori barang (contoh: Elektronik, Buku, Alat Lab)
    nama = models.CharField(max_length=100)

    def __str__(self):
        # Ditampilkan di admin panel & shell Django
        return self.nama


# ===============================
# DATA BARANG
# ===============================
class Barang(models.Model):
    # Nama barang (contoh: Laptop Asus, Kamera Canon)
    nama_barang = models.CharField(max_length=200)

    # Relasi ke tabel Kategori
    # CASCADE → jika kategori dihapus, barang ikut terhapus
    kategori = models.ForeignKey(Kategori, on_delete=models.CASCADE)

    # Gambar barang
    # upload_to='barang/' → file disimpan di media/barang/
    gambar = models.ImageField(upload_to='barang/')

    # Stok barang
    # default=1 → kalau tidak diisi, stok awal = 1
    stok = models.IntegerField(default=1)

    def __str__(self):
        # Ditampilkan di admin panel & relasi foreign key
        return self.nama_barang


# ===============================
# PEMINJAMAN
# ===============================
class Peminjaman(models.Model):
    STATUS_CHOICES = [
        ('dipinjam', 'Dipinjam'),
        ('dikembalikan', 'Dikembalikan'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    barang = models.ForeignKey(Barang, on_delete=models.CASCADE)

    nomor_wa = models.CharField(max_length=15)
    kelas = models.CharField(max_length=20)
    jurusan = models.CharField(max_length=50)

    ttd_pinjam = models.TextField()

    tanggal_pinjam = models.DateField(auto_now_add=True)
    tanggal_kembali = models.DateField()
    tanggal_dikembalikan = models.DateField(null=True, blank=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='dipinjam'
    )

    denda = models.IntegerField(default=0)

    diverifikasi_petugas = models.BooleanField(default=False)

    # 🔥 TAMBAHAN: FOTO BUKTI PENGEMBALIAN
    bukti_pengembalian = models.ImageField(
        upload_to='bukti_pengembalian/',
        null=True,
        blank=True
    )

    def __str__(self):
        return f"{self.user.username} - {self.barang.nama_barang}"


# ===============================
# ULASAN BARANG
# ===============================
class Ulasan(models.Model):
    # User yang memberi ulasan
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    # Barang yang diulas
    barang = models.ForeignKey(Barang, on_delete=models.CASCADE)

    # Isi ulasan / komentar user
    isi = models.TextField()

    # Tanggal ulasan dibuat
    # auto_now_add=True → otomatis saat data dibuat
    tanggal = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        # Ditampilkan di admin panel
        return f"{self.user.username} - {self.barang.nama_barang}"
