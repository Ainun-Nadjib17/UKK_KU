from django import forms
from .models import Ulasan, Peminjaman

class UlasanForm(forms.ModelForm):
    class Meta:
        model = Ulasan
        fields = ['isi']
        widgets = {
            'isi': forms.Textarea(attrs={
                'placeholder': 'Tulis ulasan...',
                'rows': 4
            })
        }


class PeminjamanForm(forms.ModelForm):
    tanggal_kembali = forms.DateField(
        required=False,
        widget=forms.HiddenInput()
    )

    class Meta:
        model = Peminjaman
        fields = [
            'nomor_wa',
            'kelas',
            'jurusan',
            'ttd_pinjam',
            'tanggal_kembali',
        ]
