from django.contrib import admin
from django.utils import timezone
from .models import Kategori, Barang, Peminjaman, Ulasan


@admin.register(Peminjaman)
class PeminjamanAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'nama_peminjam',
        'nama_barang',
        'barang_id',
        'kelas',
        'jurusan',
        'nomor_wa',
        'tanggal_pinjam',
        'tanggal_kembali',
        'tanggal_dikembalikan',
        'status',
        'denda',
        'keterangan_denda',
    )

    list_filter = ('status', 'tanggal_pinjam')
    search_fields = ('user__username', 'barang__nama_barang')
    list_editable = ('status',)

    def save_model(self, request, obj, form, change):
        if obj.status == 'dikembalikan' and obj.tanggal_dikembalikan is None:
            obj.tanggal_dikembalikan = timezone.now().date()

            if obj.tanggal_dikembalikan > obj.tanggal_kembali:
                telat_hari = (obj.tanggal_dikembalikan - obj.tanggal_kembali).days
                obj.denda = telat_hari * 2000
            else:
                obj.denda = 0

        super().save_model(request, obj, form, change)

    # ===== CUSTOM COLUMN =====
    def nama_peminjam(self, obj):
        return obj.user.username

    def nama_barang(self, obj):
        return obj.barang.nama_barang

    def barang_id(self, obj):
        return obj.barang.id

    def keterangan_denda(self, obj):
        if obj.denda > 0:
            return f"Telat – Denda Rp {obj.denda}"
        return "Tidak kena denda"

    nama_peminjam.short_description = "Nama Peminjam"
    nama_barang.short_description = "Nama Barang"
    barang_id.short_description = "Barang ID"
    keterangan_denda.short_description = "Keterangan"

    # 🔐 ADMIN HANYA LIHAT YANG SUDAH DISETUJUI PETUGAS
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(diverifikasi_petugas=True)


@admin.register(Barang)
class BarangAdmin(admin.ModelAdmin):
    list_display = ('id', 'nama_barang', 'kategori', 'stok')
    search_fields = ('nama_barang',)


admin.site.register(Kategori)
admin.site.register(Ulasan)
