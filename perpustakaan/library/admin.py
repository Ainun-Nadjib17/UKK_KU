from django.contrib import admin
from django.utils import timezone
from django.utils.html import format_html
from .models import Kategori, Barang, Peminjaman, Ulasan


@admin.register(Peminjaman)
class PeminjamanAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'nama_peminjam',
        'nama_barang',
        'kelas',
        'jurusan',
        'tanggal_pinjam',
        'tanggal_kembali',
        'tanggal_dikembalikan',
        'status',
        'denda',
        'lihat_bukti',
        'keterangan_denda',
    )

    list_filter = ('status', 'tanggal_pinjam')
    search_fields = ('user__username', 'barang__nama_barang')
    list_editable = ('status',)

    def save_model(self, request, obj, form, change):
        if obj.status == 'dikembalikan' and obj.tanggal_dikembalikan is None:
            obj.tanggal_dikembalikan = timezone.now().date()

            if obj.tanggal_dikembalikan > obj.tanggal_kembali:
                telat = (obj.tanggal_dikembalikan - obj.tanggal_kembali).days
                obj.denda = telat * 2000
            else:
                obj.denda = 0

        super().save_model(request, obj, form, change)

    def nama_peminjam(self, obj):
        return obj.user.username

    def nama_barang(self, obj):
        return obj.barang.nama_barang

    def lihat_bukti(self, obj):
        if obj.bukti_pengembalian:
            return format_html(
                '<a href="{}" target="_blank">Lihat</a>',
                obj.bukti_pengembalian.url
            )
        return "Belum ada"

    def keterangan_denda(self, obj):
        if obj.denda > 0:
            return f"Telat – Denda Rp {obj.denda}"
        return "Tidak kena denda"

    nama_peminjam.short_description = "Peminjam"
    nama_barang.short_description = "Barang"
    lihat_bukti.short_description = "Bukti"
    keterangan_denda.short_description = "Keterangan"

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(diverifikasi_petugas=True)


@admin.register(Barang)
class BarangAdmin(admin.ModelAdmin):
    list_display = ('id', 'nama_barang', 'kategori', 'stok')


admin.site.register(Kategori)
admin.site.register(Ulasan)
