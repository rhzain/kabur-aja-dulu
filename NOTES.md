# Preprocessing Data Komentar YouTube

Notebook ini melakukan preprocessing data komentar dengan pipeline yang **TELAH DIPERBAIKI** dan **OPTIMAL** untuk analisis sentimen.

---

## 📋 Pipeline Preprocessing (6 Tahap):

### **Tahap 1: Filter Konteks & Noise**
- **Filter Noise**: Buang spam, "wkwk", "hadir gan", terlalu pendek
- **Filter Konteks**: Strategi LONGGAR - pertahankan jika mengandung minimal 1 keyword
- **Output**: ~641 komentar relevan

### **Tahap 2: Cleaning**
- Hapus URL dan HTML tags
- **Hapus Emoji**: Semua emoji dihapus dari teks
- Normalisasi Unicode (font aneh)
- Lowercase
- **Normalisasi Slang** (indoNLP): "gpp" → "tidak apa apa"
- **Normalisasi Elongasi** (indoNLP): "capeeeek" → "capek"
- Hapus tanda baca dan angka
- **Output**: Teks bersih (string)

### **Tahap 3: Tokenisasi & Negation Tagging**
- **3a. Tokenisasi**: Pecah kalimat jadi list kata
- **3b. Negation Tagging**: Gabung negasi dengan kata berikutnya
  - Contoh: `['gaji', 'ga', 'naik']` → `['gaji', 'TIDAK_naik']`
- **Output**: List tokens dengan tag negasi

### **Tahap 4: Stemming** ⭐ (Dilakukan SEBELUM Stopword Removal)
- Ubah kata ke bentuk dasar menggunakan Sastrawi
- **SKIP stemming untuk**:
  - Keyword penting (pajak, gaji, pemerintah, dll)
  - Tag `TIDAK_xxx`
  - Tag `_EMOJI_xxx`
- **Output**: List tokens ter-stem

### **Tahap 5: Stopword Removal** (Dilakukan SETELAH Stemming)
- Hapus kata umum (Indo, Inggris, Gaul, Rojak)
- **PRESERVE (JANGAN hapus)**:
  - Kata negasi (tidak, ga, gak, belum, dll)
  - Tag `TIDAK_xxx` (negation tagging)
  - Keyword penting (pajak, gaji, dll)
- **Output**: List tokens paling bersih

### **Tahap 6: Gabung Kembali**
- Join list tokens menjadi string kalimat final
- **Output**: `teks_final` siap untuk labeling

---

## ✅ Perbaikan yang Diterapkan:

| No | Perbaikan | Status | Keterangan |
|----|-----------|--------|------------|
| 1 | **Urutan Pipeline** | ✅ | Stemming → Stopword Removal (urutan yang BENAR) |
| 2 | **Negasi Dipertahankan** | ✅ | Kata negasi TIDAK dihapus di stopwords |
| 3 | **Negation Tagging** | ✅ | "ga naik" → "TIDAK_naik" (fitur sentimen kuat) |
| 4 | **Kata Rojak** | ✅ | government, tax, salary → masuk stopwords |
| 5 | **Emoji → Tag** | ✅ | Emoji jadi `_EMOJI_POSITIF_` / `_EMOJI_NEGATIF_` |
| 5 | **Hapus Emoji** | ✅ | Semua emoji dihapus dari data |
| 7 | **Slang & Elongasi** | ✅ | Normalisasi dengan indoNLP* |

*) Jika library indoNLP terinstall

---

## 📝 Catatan untuk Fase Modelling:

⚠️ **PENTING**: Saat melakukan TF-IDF Vectorization, gunakan:

```python
from sklearn.feature_extraction.text import TfidfVectorizer

vectorizer = TfidfVectorizer(ngram_range=(1, 2))
```

**Alasan**: 
- `ngram_range=(1, 2)` akan menangkap **unigram** (1 kata) DAN **bigram** (2 kata)
- Ini penting untuk menangkap frasa seperti:
  - "biaya hidup" (bukan hanya "biaya" dan "hidup" terpisah)
  - "TIDAK_naik" (sudah jadi 1 token karena negation tagging)
  - "luar negeri", "generasi sandwich", dll

---

## 🎯 Hasil yang Diharapkan:

✅ Sentimen **negatif** dapat dideteksi dengan baik (karena negasi di-preserve)  
✅ Konteks **topik** tetap terjaga (karena keyword tidak di-stem)  
✅ **Emoji** berkontribusi sebagai sinyal sentimen  
✅ **Slang** sudah dinormalisasi  
✅ Data **lebih bersih** tanpa kehilangan informasi penting
