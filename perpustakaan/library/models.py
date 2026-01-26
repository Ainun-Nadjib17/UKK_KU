from django.db import models
from django.contrib.auth.models import User

# ===============================
# KATEGORI BARANG
# ===============================
class Kategori(models.Model):
    nama = models.CharField(max_length=100)

    def __str__(self):
        return self.nama

# ===============================
# DATA BARANG
# ===============================
class Barang(models.Model):
    nama_barang = models.CharField(max_length=200)
    kategori = models.ForeignKey(Kategori, on_delete=models.CASCADE)
    gambar = models.ImageField(upload_to='barang/')
    stok = models.IntegerField(default=1)

    def __str__(self):
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

    # 🔥 FIELD PENTING UNTUK PETUGAS
    diverifikasi_petugas = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} - {self.barang.nama_barang}"

# ===============================
# ULASAN BARANG
# ===============================
class Ulasan(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    barang = models.ForeignKey(Barang, on_delete=models.CASCADE)
    isi = models.TextField()
    tanggal = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.barang.nama_barang}"
