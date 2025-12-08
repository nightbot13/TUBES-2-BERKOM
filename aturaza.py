import questionary, os, time, sqlite3
#from questionary import Style
from rich.console import Console
from rich.table import Table

console = Console()
tanggal = time.strftime("%Y-%m-%d", time.localtime(time.time()))

def ftanggal(x): # Formatting tanggal utk diprint
    thn=str(x[0:4])
    bln=str(x[5:7])
    hri=str(x[8:10])
    return(f"{hri}/{bln}/{thn}")

def clear(): # Clear terminal
    os.system("cls" if os.name == "nt" else "clear")

def title(x): # Formatting Judul
    clear()
    x = "\033[4m\033[1m"+x+"\033[0m"
    print(x)

def uang(x): # Formatting Rupiah
    if str(x) == 'None': return ""

    ans = f"Rp{x:,}".replace(",", ".")

    return ans+',00'

def random_rec(): # Rekomendasi Konsumsi Random
    clear()
    conn = sqlite3.connect("data.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM data_keuangan
        WHERE kategori = ?
        ORDER BY RANDOM()
        LIMIT 1
    """, ("Konsumsi",))
    row = cursor.fetchone()

    table = Table(title="Random Pick", caption="*Hanya kategori konsumsi", caption_justify="left")
    table.add_column("Tanggal", justify="center")
    table.add_column("Keterangan", justify="left")
    table.add_column("Lokasi/Subjek")
    #table.add_column("Kategori", justify="left")
    #table.add_column("Masuk", justify="right", style="green")
    table.add_column("Harga", justify="right", style="red")
    table.add_column("Catatan", justify="left")
    table.add_row(ftanggal(str(row[0])), str(row[1]), str(row[2]), uang(row[5]), str(row[6]))#'''
    
    console.print(table)
    conn.close()

    pick = questionary.select("Option:", choices=["Another One","Back"], qmark="").ask()
    if pick == "Another One": random_rec()
    else:
        return

def settings(): # Bagian Settings
    # Pilihan Menu
    set_menu = ["Add Kategori", "Clear Data", "<-"]
    
    while True:
        title("SETTINGS")
        pick = questionary.select("Options: ", choices=set_menu, qmark="").ask()
        if pick == "<-":
            return

        if pick == set_menu[0]:
            title("ADD KATEGORI")
            conn = sqlite3.connect('data.db')
            cursor = conn.cursor()
            masih = True
            pick = questionary.select("Add Kategori Apa? ", choices=["Pemasukan","Pengeluaran"], qmark="").ask()
            print("Masukkan nama kategori baru (ketik - untuk mengakhiri)")
            while masih:
                x = str(input(": "))
                if x=='-' or x=='':
                    conn.commit()
                    conn.close()
                    masih=False
                else:
                    cursor.execute("INSERT OR IGNORE INTO tab_kategori VALUES (?, ?)", ('in' if pick == "Pemasukan" else 'out',x))

        elif pick==set_menu[1]:
            title("CLEAR DATA")
            pick = questionary.select("Apakah anda yakin akan MENGHAPUS SEMUA DATA ", choices=["Ya", "Tidak"], qmark="").ask()
            if pick=="Ya":
                conn = sqlite3.connect("data.db")
                cursor = conn.cursor()
                cursor.execute("DELETE FROM dat_keuangan")
                conn.commit()
                cursor.execute("VACUUM")
                conn.commit()
                conn.close()

def stats(): # Bagian Statistic
    title("STATISTICS")
    
    # Connect ke database
    conn = sqlite3.connect("data.db")
    cursor = conn.cursor()

    # Average Spendings/Day
    cursor.execute("""
        SELECT AVG(total_harian) AS rata_harian
        FROM(SELECT tanggal, SUM(keluar) as total_harian
            FROM data_keuangan
            GROUP BY tanggal    
        )
                    """)

    rataan = cursor.fetchone()
    rerata = round(rataan[0])
    print(f"Rata-Rata Pengeluaran per Hari: {uang(rerata)}", end="\n\n")

    # Most Spent this Week
    cursor.execute("""
        SELECT tanggal, keterangan, subjek, kategori, keluar, catatan
        FROM data_keuangan
        WHERE tanggal >= date('now', 'weekday 0', '-6 days')
        ORDER BY keluar DESC
        LIMIT 1
                    """)

    terbanyak = cursor.fetchone()

    # Membuat tabel Most Spent this Week
    table = Table(title="Most Spent this Week", caption="*pengeluaran terbanyak minggu ini", caption_justify="left")

    table.add_column("Tanggal", justify="center")
    table.add_column("Keterangan", justify="left")
    table.add_column("Lokasi/Subjek")
    table.add_column("Kategori", justify="left")
    table.add_column("Keluar", justify="right", style="red")
    table.add_column("Catatan", justify="left")

    # Masukkan data ke dalam tabel
    table.add_row(ftanggal(str(terbanyak[0])), str(terbanyak[1]), str(terbanyak[2]), str(terbanyak[3]), uang(terbanyak[4]), str(terbanyak[5]))

    console.print(table)

    # Most Visited
    cursor.execute("""
        SELECT subjek, COUNT(*) AS freq
        FROM data_keuangan
        GROUP BY subjek
        ORDER BY freq DESC
        LIMIT 3
                    """)
    
    most_freq = cursor.fetchall()
    
    # Buat tabel Most Visited
    table = Table(title="Most Frequent", caption=" Most frequently interacted", caption_justify="left")

    table.add_column("Lokasi/Subjek")
    table.add_column("Frekuensi")

    for row in most_freq:
        table.add_row(str(row[0]), str(row[1]))
    
    console.print(table)
    conn.close()

    print("On progress...")

    questionary.press_any_key_to_continue().ask()
    return

def history(x): # History keuangan
    clear() # Bersihin

    # Pilihan Menu di History
    pilihan = ["Edit Data",f"Sort by {"Oldest" if x == "DESC" else "Newest"}","Back"]
    
    # Connect ke database
    conn = sqlite3.connect("data.db")
    cursor = conn.cursor()

    # Sort data berdasarkan tanggal (defaulnya dari yang terbaru)
    cursor.execute(f"SELECT tanggal, keterangan, subjek, kategori, masuk, keluar, catatan FROM data_keuangan ORDER BY rowid {x}")
    rows = cursor.fetchall()

    # Membuat Tabel
    table = Table(title="History", caption=f" SORTING: {"newest" if x == "DESC" else "oldest"}", caption_justify="left")

    table.add_column("Tanggal", justify="center")
    table.add_column("Keterangan", justify="left")
    table.add_column("Lokasi/Subjek")
    table.add_column("Kategori", justify="left")
    table.add_column("Masuk", justify="right", style="green")
    table.add_column("Keluar", justify="right", style="red")
    table.add_column("Catatan", justify="left")

    # Memasukkan data ke dalam tabel
    for row in rows:
        table.add_row(ftanggal(str(row[0])), str(row[1]), str(row[2]), str(row[3]), uang(row[4]), uang(row[5]), str(row[6]))

    # Print Tabel
    console.print(table)
    conn.close() # Mengakhiri koneksi dengan database

    # Pilih Menu
    pick = questionary.select("Option:", choices=pilihan, qmark="").ask()
    if pick == "Edit Data": 
        print("Fitur belum tersedia.") # SOON
        questionary.press_any_key_to_continue().ask()
        history(x)
    elif pick == pilihan[1]:
        history(f"{"ASC" if x == "DESC" else "DESC"}") # Ubah sorting tanggal
    elif pick == "Back":
        return

def others(): # Submenu Others
    # Pilihan Menu
    others_menu = ["History", "Statistics", "Settings","<-"]
    
    while True:
        title("OTHERS") # Judul

        # Pilih Menu
        pick = questionary.select("Options: ", choices=others_menu, qmark="").ask()
        if pick=='History':
            history("DESC") # History, defaultnya dari yang terbaru
        elif pick=="Statistics":
            stats()
        elif pick=="Settings":
            settings() 
        elif pick=="<-":
            return

def ingput(x): # Input Pengeluaran/Pemasukan
    # Cek Menu yang Dipilih
    if x == "Others":
        others()
        return
    elif x == "Random":
        random_rec()
        return
    
    # Convert x ke y
    y = ("keluar" if x=="Pengeluaran" else "masuk")

    title(x.upper()) # JUDUL

    # Ambil Kategori
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()

    cursor.execute("""
        SELECT nama FROM tab_kategori
        WHERE jenis = ?
                    """, ("in" if y == "masuk" else "out", ))

    kategori = cursor.fetchall()
    kategoris = [row[0] for row in kategori]

    # Autocomplete feature (subjek/lokasi)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT DISTINCT subjek
        FROM data_keuangan
                    """)
    
    sub_list = cursor.fetchall()
    subjeks = [row[0] for row in sub_list]

    # INPUT
    query = f'''INSERT INTO data_keuangan (tanggal, keterangan, subjek, kategori, {y}, catatan) VALUES (?, ?, ?, ?, ?, ?)'''

    a = str(questionary.text("Keterangan: ",qmark="").ask())
    b = questionary.autocomplete("Lokasi/Subjek: ",choices=subjeks, qmark="").ask()
    c = questionary.select("Kategori: ", choices=kategoris, qmark="").ask()
    d = int(questionary.text("Nominal: ",qmark="").ask())
    e = str(questionary.text("Catatan: ",qmark="").ask())

    isian = (tanggal, a, b, c, d, e)
    
    cursor = conn.cursor()
    cursor.execute(query,isian)
    conn.commit()

    conn.close()

    # Menu Setelah INPUT
    pick = questionary.select("\nINPUT DITERIMA", choices=["Tambahkan Lagi", "<-"], qmark="").ask()
    if pick == "<-": return
    else: ingput(x)

def database(): # Load/Buat database
    # Buat database
    conn = sqlite3.connect('data.db')
    tabel_keuangan = '''CREATE TABLE IF NOT EXISTS data_keuangan
            (tanggal TEXT, keterangan TEXT, subjek TEXT, kategori TEXT, masuk INT, keluar INT, catatan TEXT)
    '''
    tabel_kategori = '''CREATE TABLE IF NOT EXISTS tab_kategori
            (jenis TEXT, nama TEXT UNIQUE)
    '''
    # Buat Tabel Kategori
    conn.execute(tabel_keuangan)
    conn.execute(tabel_kategori)
    conn.commit()

    default_in = ["Gaji", "Bulanan", "Rezeki"]
    default_out = ["Konsumsi", "Transportasi", "Daily", "Hiburan", "Development"]

    cursor = conn.cursor()

    for i in default_in:
        cursor.execute("INSERT OR IGNORE INTO tab_kategori VALUES ('in', ?)", (i,))
    for i in default_out:
        cursor.execute("INSERT OR IGNORE INTO tab_kategori VALUES ('out', ?)", (i,))
    
    conn.commit()
    conn.close()

def main(): # Main Menu
    # Array Pilihan Menu
    menu = ["Pengeluaran", "Pemasukan", "Random", "Others", "=EXIT="]

    while True:
        title("ATURAZA") # JUDUL

        # Pilih Menu
        pick = questionary.select("Menu: ", choices=menu, qmark="").ask()
        if pick == menu[4]: # EXIT
            clear()
            print("Terima kasih!")
            time.sleep(0.5)
            return
        ingput(pick)

database()  # Load Database dulu
main()      # Main menu