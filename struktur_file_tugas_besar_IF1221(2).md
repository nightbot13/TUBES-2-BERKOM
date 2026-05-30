# Struktur File Modular — Tugas Besar IF1221 Logika Komputasional 2025/2026
# Permainan UNI (Prolog)

---

> **Legenda Status:**
> - ✅ **Sudah diimplementasi**
> - ⚠️ **Sebagian diimplementasi** (ada predicate yang belum lengkap)
> - ❌ **Belum diimplementasi**

---

## Analisis Komponen Utama

**State yang di-track secara dinamis:**
giliran aktif, urutan pemain, arah permainan, tangan tiap pemain, discard pile top, draw pile, warna aktif, status UNI

**Catatan konvensi kode:**
Implementasi menggunakan **camelCase berbahasa Indonesia** (misal: `giliranSelanjutnya`, `kartuPemain`) dan direktif `:- include(...)` (bukan `:- consult(...)`).

---

## Struktur File Aktual

```
uni_game/
├── state.pl           ← Layer 0: tidak bergantung pada apapun  ✅
├── utils.pl           ← Layer 0: tidak bergantung pada apapun  ✅
├── deck.pl            ← Layer 1 (include state.pl, utils.pl)   ✅
├── player.pl          ← Layer 2 (include deck.pl)              ✅
├── turn.pl            ← Layer 2 (include player.pl)            ✅
├── rule.pl            ← Layer 2 (include deck.pl)              ✅
├── display.pl         ← Layer 3 (include deck.pl)              ✅
├── scoring.pl         ← Layer 4 (include player.pl, display.pl)✅
├── action.pl          ← Layer 4 (include turn.pl, rule.pl)     ✅
└── main.pl            ← Layer 5 (include action.pl, scoring.pl)⚠️
```

**File yang belum dibuat (ada di rencana awal, belum diimplementasi):**
```
uni_game/
├── effects.pl         ← Layer 3  ❌ (logika efek kartu masih tertanam di action.pl)
├── file_io.pl         ← Layer 4  ❌ (save/load game)
└── bonus.pl           ← Layer 5  ❌ (fitur bonus)
```

**Load order via include chain (otomatis dari main.pl):**
`state → utils → deck → player → turn → rule.pl → display → scoring → action → main`

**Tidak ada circular dependency** karena setiap lapisan hanya bergantung ke lapisan di bawahnya.

---

## Detail Tiap File

---

### 1. `state.pl` ✅
**Bergantung pada:** *(tidak ada)*

Pusat seluruh **dynamic facts** permainan.

**Sudah diimplementasi:**

```prolog
:- dynamic(giliran/1).          % giliran(NamaPemain)
:- dynamic(urutanPemain/1).     % urutanPemain([P1, P2, ...])
:- dynamic(arahPermainan/1).    % arahPermainan(kanan/kiri)
:- dynamic(discardTop/1).       % discardTop(kartu(Warna, Jenis))
:- dynamic(warnaAktif/1).       % warnaAktif(Warna)
:- dynamic(kartuPemain/2).      % kartuPemain(NamaPemain, [kartu(...), ...])
:- dynamic(deck/1).             % deck([kartu(...), ...])
:- dynamic(uniStatus/1).        % uniStatus([NamaPemain, ...])
```

**Belum diimplementasi di state.pl** *(dibutuhkan untuk fitur lanjutan)*:
```prolog
% :- dynamic(kartuAksiTerakhir/3).  % untuk fitur bonus Mimic
% :- dynamic(kartuTersembunyi/2).   % untuk fitur bonus Hidden Card
% :- dynamic(modePermainan/1).      % untuk fitur bonus Tournament
% :- dynamic(tim/2).                % untuk fitur bonus Tournament
% :- dynamic(godsHandDigunakan/1).  % untuk fitur bonus God's Hand
% :- dynamic(pendingDraw/2).        % efek draw_two/wildDrawFour menunggu
```

> **Catatan:** `gameRunning/1` saat ini dideklarasikan di `main.pl`, sebaiknya dipindah ke sini.

---

### 2. `utils.pl` ✅
**Bergantung pada:** *(tidak ada)*

Kumpulan **predicate pembantu murni** tanpa side-effect pada state permainan.

**Sudah diimplementasi:**
- `h_FormatCard(+Kartu)` — cetak kartu dalam format `warna-jenis`
- `h_Shuffle(+List, -ListAcak)` — acak urutan list menggunakan random pick
- `h_ListLength(+List, -N)` — hitung panjang list
- `h_ListAppendElement(+List, +Elemen, -HasilList)` — tambah elemen di akhir list
- `h_ListAppendList(+List1, +List2, -HasilList)` — gabungkan dua list
- `h_ListReverse(+List, -ListTerbalik)` — balik urutan list
- `h_ListIndexOf(+List, +Elemen, -Indeks)` — cari indeks elemen (0-based)
- `h_ListAtIndex(+List, +Indeks, -Elemen)` — alias untuk `h_ListGetElement`
- `h_ListInsertAtIndex(+List, +Indeks, +Elemen, -HasilList)` — sisipkan elemen pada indeks tertentu
- `h_ListRemoveAtIndex(+List, +Indeks, -HasilList)` — hapus elemen pada indeks tertentu
- `h_ListGetElement(+List, +Indeks, -Elemen)` — ambil elemen pada indeks tertentu (0-based)
- `h_ListIsMember(+Elemen, +List)` — cek keanggotaan elemen dalam list
- `testInit/0` — helper untuk keperluan testing (inisialisasi state manual)

**Belum diimplementasi:**
- Input validator: `h_ReadIntInRange(+Min, +Max, -N)` — baca integer dengan validasi rentang dan loop bila invalid
- Input reader: `h_ReadLineAtom(-Atom)` — baca satu baris input user sebagai atom
- `h_PrintNumberedList(+List)` — cetak list dengan nomor urut

---

### 3. `deck.pl` ✅
**Bergantung pada:** `state.pl`, `utils.pl`

Segala sesuatu tentang **kartu dan komposisi dek**.

**Sudah diimplementasi:**

*Fakta statis definisi kartu:*
- `warnaDasar(-List)` → `[merah, kuning, hijau, biru]`
- `jenisKartu(-List)` → list 25 elemen: angka 0–9 (0 sekali, 1–9 dua kali) + skip×2, reverse×2, drawTwo×2
- `kartuHitam(-List)` → 4× `kartu(hitam, wild)` + 4× `kartu(hitam, wildDrawFour)`

*Nilai kartu:*
- `nilaiKartu(+Jenis, -Poin)` — angka→face value (0→1), skip/reverse/drawTwo→10, wild/wildDrawFour→20

*Format & parse:*
- `formatKartu(+Kartu, -Atom)` — konversi `kartu(merah, 5)` → atom `merah-5`
- `parseKartu(+Atom, -Kartu)` — kebalikannya (untuk loadGame)

*Build & setup dek:*
- `kombinasiSatuWarna(+Warna, +ListJenis, -ListKartu)` — hasilkan list kartu untuk satu warna
- `kombinasiSemuaWarna(+ListWarna, +ListJenis, -ListKartu)` — kombinasi semua warna
- `loadKartu(-DaftarKartu)` — bangun 108 kartu standar (belum di-shuffle; shuffle dilakukan di `main.pl`)
- `initDiscard(+Deck, -SisaDeck)` — ambil kartu awal yang valid (non-hitam, angka ≤ 9) untuk discard pile; assert `discardTop/1` dan `warnaAktif/1`
- `isKartuAksi(+Kartu)` — true jika jenis adalah skip/reverse/drawTwo/wild/wildDrawFour

**Belum diimplementasi:**
- Definisi kartu bonus Mimic (`kartu(hitam, mimic)`) belum ada di `jenisKartu` maupun `kartuHitam`

---

### 4. `player.pl` ✅
**Bergantung pada:** `deck.pl` (transitif: `state.pl`, `utils.pl`)

Manajemen **inisialisasi pemain** dan pembagian kartu awal.

**Sudah diimplementasi:**
- `inisialisasiPemain(+JumlahPemain, -DaftarPemain)` — input nama pemain, acak urutan, assert `urutanPemain/1` dan `giliran/1`
- `inputNama(+Sisa, +Akumulasi, -Hasil)` — rekursif; validasi nama duplikat; baca satu nama per iterasi
- `bagiKartu(+ListPemain, +Deck, -SisaDeck)` — distribusi 7 kartu ke semua pemain; assert `kartuPemain/2`
- `ambilKartuAwal(-ListKartu, +Jumlah, +Deck, -SisaDeck)` — helper rekursif untuk mengambil N kartu dari deck

**Belum diimplementasi:**
- `reshuffleDeck/0` — ambil semua kartu di discard pile (kecuali top), shuffle, jadikan deck baru; diperlukan saat deck habis
- Pengambilan kartu saat deck kosong belum ditangani (tidak ada pengecekan di `ambilSejumlahKartu` di `action.pl`)

---

### 5. `turn.pl` ✅
**Bergantung pada:** `player.pl` (transitif: `deck.pl`, `state.pl`, `utils.pl`)

Manajemen **alur giliran** dan perpindahan antar pemain.

**Sudah diimplementasi:**
- `giliranSelanjutnya/0` — pindah giliran ke pemain berikutnya berdasarkan `urutanPemain` + `arahPermainan`; update `giliran/1`; cetak nama pemain berikutnya
- `giliranSebelumnya(-Nama)` — hitung dan kembalikan nama pemain yang main sebelum giliran ini (untuk keperluan tantang); **tidak mengubah state**

**Belum diimplementasi:**
- `lewatiGiliran/0` (skip next turn) — lewati satu pemain; saat ini efek kartu skip dihandle langsung di `giliranSelanjutnya` dengan memanggil dua kali, bukan predicate tersendiri
- `balikArah/0` (reverse direction) — saat ini logika reverse belum ada; `arahPermainan` diinisialisasi tapi tidak pernah diubah selama permainan
- Efek 2-pemain untuk reverse (berlaku seperti skip) belum ditangani
- `getPemainPadaOffset(+N, -Nama)` — dapatkan pemain ke-N setelah pemain aktif
- `urutanPemainSekarang(-List)` — daftar pemain mulai dari giliran sekarang sesuai arah

---

### 6. `rule.pl` ✅
**Bergantung pada:** `deck.pl` (transitif: `state.pl`, `utils.pl`)

> **Catatan nama file:** Rencana awal `rules.pl`, implementasi aktual `rule.pl`.

**Aturan validitas** kartu yang boleh dimainkan. Murni logika/query — tidak mengubah state.

**Sudah diimplementasi:**
- `kartuMainValid(+Kartu)` — apakah kartu bisa dimainkan di atas discard top saat ini:
  - Kartu berwarna: cocok warna aktif ATAU cocok jenis dengan discard top
  - Wild: selalu bisa (kecuali di atas wild)
  - WildDrawFour: selalu bisa (kecuali di atas wildDrawFour)
- `canPlayWildDrawFour(+Pemain)` — true jika pemain **tidak** punya kartu yang cocok warna/jenis aktif (syarat pakai wildDrawFour secara sah)
- `cekAdaKartuValid(+ListKartu)` — helper rekursif; true jika ada minimal satu kartu di list yang cocok warna/jenis aktif

**Belum diimplementasi:**
- Validasi ketat wildDrawFour: kondisi `Jenis = wildDrawFour, JenisDiscard \= wildDrawFour` di `kartuMainValid` memungkinkan wildDrawFour dimainkan bahkan ketika pemain masih punya kartu lain yang cocok — ini inkonsisten dengan `canPlayWildDrawFour`
- `adaKartuBisaMain(+Pemain)` — wrapper boolean untuk `cekAdaKartuValid` (dibutuhkan `main.pl` untuk logika game loop)

---

### 7. `effects.pl` ❌ **BELUM DIBUAT**
**Seharusnya bergantung pada:** `state.pl`, `deck.pl`, `player.pl`, `turn.pl`

File ini **belum ada**. Logika efek kartu saat ini **tertanam langsung di `action.pl`** (di dalam `mainkanKartu` dan `uni`) dan belum dipisahkan.

**Yang perlu diimplementasi:**
- `terapkanEfek(+Kartu, +Pemain)` — dispatcher utama berdasarkan jenis kartu:
  - `terapkanEfekAngka(+Kartu)` — update `discardTop` dan `warnaAktif`; tidak ada efek lain
  - `terapkanEfekSkip/0` — lewati giliran pemain berikutnya
  - `terapkanEfekReverse/0` — balik `arahPermainan`; untuk 2 pemain berlaku seperti skip
  - `terapkanEfekDrawTwo(+Pemain)` — pemain berikutnya wajib ambil 2 kartu
  - `terapkanEfekWild(+Pemain)` — minta input warna baru, update `warnaAktif`
  - `terapkanEfekWildDrawFour(+Pemain)` — minta warna baru + pemain berikutnya wajib ambil 4 kartu
- `setDiscardTop(+Kartu)` — update `discardTop`; untuk kartu non-hitam juga update `warnaAktif`
- `pilihWarnaBaru(+Pemain, -Warna)` — loop input warna valid dari pemain (merah/kuning/hijau/biru)
- `updateKartuAksiTerakhir(+Kartu, +Pemain)` — simpan riwayat kartu aksi untuk bonus Mimic

> **Dampak ketiadaan file ini:** Efek skip, reverse, draw two, dan pemilihan warna untuk wild card **belum diimplementasi** (kartu-kartu tersebut bisa dimainkan tapi tidak ada efek yang terjadi). Saat ini `action.pl` hanya update `warnaAktif` untuk kartu non-hitam dan memanggil `giliranSelanjutnya` tanpa efek khusus.

---

### 8. `display.pl` ✅
**Bergantung pada:** `deck.pl` (transitif: `state.pl`, `utils.pl`)

Semua **output/cetak ke layar**. Tidak mengubah state.

**Sudah diimplementasi:**
- `daftarAksiUtama(-List)` — fakta list aksi utama yang tersedia
- `daftarAksiPendukung(-List)` — fakta list aksi pendukung yang tersedia
- `lihatCommand/0` — cetak semua aksi utama dan pendukung yang tersedia
- `printList(+List, +NomorAwal)` — cetak list bernomor mulai dari `NomorAwal`
- `printAksiUtama/0` — cetak daftar aksi utama
- `printAksiPendukung/0` — cetak daftar aksi pendukung
- `lihatKartu(+ListKartu, +NomorAwal)` — cetak kartu tangan dengan nomor urut
- `lihatKartu/0` — cetak kartu tangan pemain aktif (wrapper publik)
- `formatUrutanSisa(+List)` — helper format urutan pemain (elemen ke-2 dst)
- `formatUrutan(+List)` — format urutan pemain lengkap
- `printUrutan(+List, +N)` — cetak nama dan jumlah kartu tiap pemain
- `cekInfo/0` — cetak info permainan: discard top, urutan pemain, jumlah kartu tiap pemain
- `printKartu(+ListKartu)` — cetak list kartu dalam format `A + B + C = ` (untuk scoring)
- `printPoin(+ListKartu)` — cetak nilai poin tiap kartu dalam format `p1 + p2 + ...`
- `printSkor(+ListPoinTuple)` — cetak baris skor tiap pemain beserta detail kartu
- `printPeringkat(+ListPoinTuple, +Peringkat)` — cetak urutan pemenang bernomor

**Belum diimplementasi:**
- Tampilan kartu tersembunyi `(disembunyikan)` — untuk fitur bonus Hidden Card
- `printHandTeman(+Pemain)` — cetak tangan pemain lain untuk mode turnamen
- `printHasilAkhirTurnamen(+RankingTim)` — tampilkan hasil akhir mode turnamen
- `printAvailableCommands` yang konteks-sensitif (misal: hanya tampilkan `tantang` jika discard top adalah wildDrawFour)

---

### 9. `action.pl` ✅
**Bergantung pada:** `turn.pl`, `rule.pl` (transitif: `player.pl`, `deck.pl`, `state.pl`, `utils.pl`)

> **Catatan nama file:** Rencana awal `actions.pl`, implementasi aktual `action.pl`.

Implementasi **semua aksi** yang dapat dipanggil pemain.

**Sudah diimplementasi:**

*Aksi Utama:*
- `mainkanKartu(+Indeks)` — mainkan kartu ke-Indeks (0-based) dari tangan pemain aktif; validasi dengan `kartuMainValid`; update `discardTop`, `warnaAktif`, `kartuPemain`; hapus status UNI jika sisa kartu ≠ 1; panggil `giliranSelanjutnya`
- `ambilKartu/0` — pemain aktif ambil kartu dari deck; jumlah disesuaikan dengan jenis discard top (1 normal, 2 untuk drawTwo, 4 untuk wildDrawFour); panggil `giliranSelanjutnya`
- `ambilSejumlahKartu(+Jumlah, -ListKartu)` — helper; ambil N kartu dari `deck`, update fakta `deck/1`
- `prosesAmbil(+N, +Deck, -SisaDeck, -Ambilan)` — helper rekursif untuk `ambilSejumlahKartu`
- `uni(+Indeks)` — mainkan kartu ke-Indeks saat tangan berisi tepat 2 kartu; assert `uniStatus`; jika tidak valid (kartu tidak cocok atau tangan bukan 2), pemain kena 1 kartu penalti
- `tantang/0` — tantang validitas wildDrawFour dari pemain sebelumnya:
  - Berhasil: pemain sebelumnya kena 4 kartu, penantang lolos
  - Gagal: penantang kena 6 kartu
  - Invalid (discard bukan wildDrawFour): cetak pesan error

*Aksi Pendukung:*
- `tangkap(+NamaPemain)` — tangkap pemain yang lupa berkata UNI (tangan 1 kartu, tidak ada di `uniStatus`); jika valid: target kena 2 kartu; jika invalid: pemanggil kena 1 kartu

*Helper UNI Status:*
- `tambahStatusUni(+Pemain)` — tambah pemain ke list `uniStatus`
- `hapusStatusUni(+Pemain)` — hapus pemain dari list `uniStatus`

**Belum diimplementasi / kurang lengkap:**
- Efek kartu skip, reverse, drawTwo tidak diterapkan — kartu-kartu ini bisa dimainkan tapi tidak ada efek (skip tidak lewat giliran, reverse tidak balik arah, drawTwo tidak beri hukuman otomatis)
- Pilihan warna untuk kartu wild dan wildDrawFour belum ada — warna aktif tidak diperbarui saat wild dimainkan
- `pending_draw` tidak diimplementasi — `ambilKartu` langsung cek jenis discard top, bukan state pending
- Pemilihan indeks `uni` saat ini menggunakan `h_ListGetElement` untuk mengambil kartu tapi `h_ListLength` untuk validasi, sedangkan `mainkanKartu` menggunakan `h_ListAtIndex`; tidak konsisten (keduanya setara tapi sebaiknya seragam)

---

### 10. `file_io.pl` ❌ **BELUM DIBUAT**
**Seharusnya bergantung pada:** `state.pl`, `player.pl`, `utils.pl`, `deck.pl`

File ini **belum ada**.

**Yang perlu diimplementasi:**
- `saveGame/0`:
  1. Minta input nama file dari user
  2. Buka file `NamaFile.txt` untuk ditulis
  3. Tulis seluruh state dalam format teks:
     ```
     urutanPemain:[william,razi,adinda]
     giliran:razi
     discardTop:merah-6
     kartu_william:[merah-5,biru-3,hijau-reverse,hitam-wild]
     kartu_razi:[biru-3,hijau-2,kuning-4]
     arahPermainan:kanan
     warnaAktif:merah
     statusUNI:[william]
     ```
  4. Tutup file dan cetak konfirmasi
- `loadGame/0`:
  1. Minta input nama file dari user
  2. Buka file → jika gagal, cetak error
  3. Baca semua baris file
  4. `retractall` semua dynamic facts lama
  5. Parse setiap baris dan `assert` kembali ke state
  6. Cetak konfirmasi
- `parseGameFile(+Lines)` — parsing rekursif tiap baris
- `serializeCardList(+List, -Atom)` — konversi list kartu → atom teks
- `parseCardList(+Atom, -List)` — kebalikannya
- `serializeCard(+Kartu, -Atom)` — konversi satu kartu ke atom via `formatKartu`

---

### 11. `scoring.pl` ✅
**Bergantung pada:** `player.pl`, `display.pl` (transitif: `deck.pl`, `state.pl`, `utils.pl`)

Logika **perhitungan skor dan peringkat** akhir permainan.

**Sudah diimplementasi:**
- `hitungPoinHelper(+ListKartu, -TotalPoin)` — jumlahkan nilai semua kartu via `nilaiKartu/2` secara rekursif
- `hitungPoinPemain(+Pemain, -Poin)` — ambil tangan pemain, hitung poin
- `hitungPoinSemuaHelper(+ListPemain, -ListTuple)` — iterasi semua pemain hasilkan `[(Pemain, Poin), ...]`
- `hitungPoinSemua(-DaftarPoin)` — wrapper publik; baca `urutanPemain`, panggil helper
- `insertSorted(+Tuple, +ListUrut, -HasilUrut)` — insertion ke list terurut dengan tiga kriteria:
  1. Poin lebih kecil → peringkat lebih tinggi
  2. Poin sama → jumlah kartu lebih sedikit → peringkat lebih tinggi
  3. (Tie-breaking ketiga belum diimplementasi: urutan di `urutanPemain`)
- `insertionSort(+List, -ListUrut)` — insertion sort rekursif
- `peringkatPemain(+DaftarPoin, -PeringkatPoin)` — wrapper untuk `insertionSort`
- `endGame/0` — cetak pemenang, hitung dan tampilkan skor semua pemain via `printSkor` + `printPeringkat`
- `cekGameOver(-Pemenang)` — true jika ada pemain dengan 0 kartu di tangan

**Belum diimplementasi:**
- `hitungPoinTim(+Tim, -Poin)` — jumlah poin kedua anggota tim (untuk mode turnamen)
- `endGameTurnamen/0` — versi endGame untuk mode turnamen
- `game_loop` tidak memanggil `cekGameOver` secara otomatis setelah setiap aksi (karena `game_loop` belum ada di `main.pl`)

---

### 12. `bonus.pl` ❌ **BELUM DIBUAT**
**Seharusnya bergantung pada:** `state.pl`, `deck.pl`, `player.pl`, `turn.pl`, `effects.pl`, `display.pl`, `scoring.pl`

File ini **belum ada**. Semua fitur bonus di bawah ini belum diimplementasi.

**God's Hand (3 poin):**
- `godsHand/0` — aksi utama: probabilitas 10–20% mencuri kartu acak dari pemain lain
- `tryGodsHandAuto/0` — dipanggil otomatis di awal setiap giliran

**Mimic Card (5 poin):**
- `terapkanEfekMimic(+Pemain)` — salin efek kartu aksi terakhir yang dimainkan

**Kartu Tersembunyi (3 poin):**
- `sembunyikanKartu(+N)` — tandai kartu ke-N sebagai tersembunyi di state
- `tampilkanKartu/0` — hapus status tersembunyi kartu

**Mode Turnamen (9 poin):**
- `initTournamentMode(+ListPemain)` — bagi 4 pemain jadi 2 tim; atur urutan selang-seling
- `getTeman(+Pemain, -Teman)` — cari anggota tim yang sama
- `swapKartu(+N, +M)` — tukar kartu ke-N milik pemain aktif dengan kartu ke-M milik teman setim
- `endGameTurnamen/0` — hitung dan tampilkan hasil akhir mode turnamen

---

### 13. `main.pl` ⚠️
**Bergantung pada:** `action.pl`, `scoring.pl` (transitif: semua file)

**Entry point** permainan.

**Sudah diimplementasi:**
- `:- include('action.pl')` dan `:- include('scoring.pl')` — load semua file via chain
- `:- dynamic(gameRunning/1)` — flag status permainan (lebih baik dipindah ke `state.pl`)
- `:- initialization(main)` — auto-run saat file di-consult
- `main/0` — memanggil `startGame`
- `startGame/0`:
  - Reset semua state dengan `retractall`
  - Tampilkan banner selamat datang
  - Panggil `inputJumlahPemain` lalu `inisialisasiPemain`
  - Bangun dan acak deck via `loadKartu` + `h_Shuffle`
  - Bagi kartu via `bagiKartu`
  - Inisialisasi discard pile via `initDiscard`
  - Assert `deck/1`, `arahPermainan(kanan)`, `uniStatus([])`
  - Cetak konfirmasi setup selesai
- `inputJumlahPemain(-N)` — baca integer 2–4 dari input; validasi dan loop jika invalid

**Belum diimplementasi:**
- `gameLoop/0` — loop utama permainan; saat ini permainan berhenti setelah setup dan tidak ada loop untuk menerima input pemain
- `playerTurnLoop(+Pemain)` — loop aksi dalam satu giliran; baca command, dispatch, ulangi jika aksi pendukung
- `validateCommand(+Input, -TipeAksi)` — parse input string menjadi predicate call
- Pengecekan `cekGameOver` setelah setiap aksi utama belum terintegrasi ke loop
- Pilihan mode permainan (klasik/turnamen) belum ada

---

## Ringkasan Dependency Graph (Aktual)

```
state.pl ──────────────────────────────────────────┐
utils.pl ──────────────────────────────────────────┤
  deck.pl (include: state, utils) ─────────────────┤
    player.pl (include: deck) ───────────────────────┤
      turn.pl (include: player) ────────────────────┤──→ main.pl
    rule.pl (include: deck) ─────────────────────────┤
    display.pl (include: deck) ──────────────────────┤
      scoring.pl (include: player, display) ─────────┤
    action.pl (include: turn, rule) ─────────────────┘
```

> Semua dependency saat ini menggunakan `:- include(...)` (textual inclusion), bukan `:- consult(...)`. Ini berarti semua predicate masuk ke namespace global dan tidak ada enkapsulasi modul.

---

## Tabel Ringkasan Status Implementasi

| File | Layer | Tanggung Jawab | Status | Catatan |
|---|---|---|---|---|
| `state.pl` | 0 | Deklarasi semua dynamic facts | ✅ | Dynamic bonus belum ada |
| `utils.pl` | 0 | Utilitas list, random, format | ✅ | Input validator belum ada |
| `deck.pl` | 1 | Definisi kartu, nilai, format | ✅ | Kartu bonus Mimic belum ada |
| `player.pl` | 2 | Inisialisasi pemain, bagi kartu | ✅ | `reshuffleDeck` belum ada |
| `turn.pl` | 2 | Alur giliran, perpindahan | ⚠️ | Reverse & skip belum ada |
| `rule.pl` | 2 | Validitas kartu yang dimainkan | ✅ | Validasi WDF kurang ketat |
| `effects.pl` | 3 | Efek kartu pada state | ❌ | **Belum dibuat** |
| `display.pl` | 3 | Output cetak ke layar | ✅ | Tampilan bonus belum ada |
| `action.pl` | 4 | Semua aksi pemain | ⚠️ | Efek kartu aksi belum jalan |
| `scoring.pl` | 4 | Hitung skor dan ranking | ✅ | Versi turnamen belum ada |
| `file_io.pl` | 4 | Save dan load permainan | ❌ | **Belum dibuat** |
| `bonus.pl` | 5 | Semua fitur bonus | ❌ | **Belum dibuat** |
| `main.pl` | 5 | Entry point dan game loop | ⚠️ | `gameLoop` belum ada |

---

## Prioritas Pengerjaan yang Disarankan

1. **`effects.pl`** — paling kritis; tanpa ini kartu skip/reverse/drawTwo/wild tidak berfungsi
2. **`main.pl` — `gameLoop` + `playerTurnLoop`** — tanpa ini permainan tidak bisa dimainkan end-to-end
3. **`turn.pl` — `balikArah` + `lewatiGiliran`** — dibutuhkan oleh `effects.pl`
4. **`file_io.pl`** — save/load game
5. **`bonus.pl`** — fitur bonus (God's Hand, Mimic, Hidden Card, Tournament)
