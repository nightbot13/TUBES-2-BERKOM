import questionary, os, time, sqlite3
from datetime import datetime
from questionary import Style, Choice
from rich import print as pr
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from prompt_toolkit.styles import Style as S
from pyfiglet import Figlet

# Setup
f = Figlet(font='standard')
console = Console()
tanggal = time.strftime("%Y-%m-%d", time.localtime(time.time()))
style = Style([("pointer", "bold yellow"), ("highlighted", "bold"), ("selected", "")])
tes = S([('red', 'fg:#ff0000'), ('green','fg:#00ff00')])
bulan = ["None", "Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli", "Agustus", "September", "Oktober", "November", "Desember"]

# Terminal
def clear(): # Clear terminal
    os.system("cls" if os.name == "nt" else "clear")

# Formatting
def title(x): # Formatting Judul
    clear()
    if x == "Pengeluaran":
        color = "red"
    elif x == "Pemasukan":
        color = "green"
    else:
        color = "white"
    console.print(
        Panel(Text(x.upper(),justify="center", style="bold"), border_style=color)
    )

def uang(x):        # Formatting Rupiah
    if str(x) == 'None': return ""

    ans = f"Rp{x:,}".replace(",", ".")

    return ans+',00'

def bold(x):
    return  "\033[1m"+x+"\033[0m"

def rtanggal(x): # Formatting utk menjadi data SQL
    t = datetime.strptime(x, "%d/%m/%Y")
    return t.strftime("%Y-%m-%d")

def ftanggal(x): # Formatting tanggal utk diprint
    t = datetime.strptime(x, "%Y-%m-%d")
    return t.strftime("%d/%m/%Y")

# Program
def settings():     # Bagian Settings
    # Pilihan Menu
    set_menu = ["Add Kategori", "Clear Data", "<-"]
    last = None

    while True:
        title("SETTINGS")
        pick = questionary.select("Options: ", choices=set_menu, qmark="", style=style, default=last).ask()
        if pick == "<-":
            return "Settings"

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
                    last = "Add Kategori"
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
                last = "Clear Data"

def plan():
    title("Financial Plan")
    
    conn = sqlite3.connect("data.db")
    cursor = conn.cursor()

    # Hitung Jumlah Bulan Total
    cursor.execute(
    """ 
        SELECT COUNT(DISTINCT strftime('%Y-%m', tanggal))
        FROM data_keuangan
    """
    )
    bulan = cursor.fetchone()[0]

    # Hitung Total Income
    cursor.execute("""
        SELECT SUM(masuk)
        FROM data_keuangan
        WHERE kategori IN (?, ?)
                    """, ("Gaji", "Bulanan"))

    jumlah = cursor.fetchone()[0]
    conn.close()

    income = round(jumlah/bulan, 2)

    print(f"Income per Bulan: {uang(income)}")

    questionary.press_any_key_to_continue().ask()

def stats():        # Bagian Statistic
    title("STATISTICS")
    
    # Connect ke database
    conn = sqlite3.connect("data.db")
    cursor = conn.cursor()

    # Cash Flow Bulan ini
    cursor.execute(
    """
        SELECT SUM(masuk)-SUM(keluar)
        FROM data_keuangan
        WHERE strftime('%Y-%m', tanggal) = strftime('%Y-%m', 'now')
    """
    )
    cash_flow = cursor.fetchone()[0]
    color = "red" if cash_flow<=0 else "green"
    bln = bulan[int(time.strftime("%m", time.localtime(time.time())))]
    pr(f"Cash Flow ({bln}): [bold {color}]{uang(cash_flow)}[/bold {color}]")
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
    print(f"Rerata Pengeluaran (per Hari): {bold(uang(rerata))}", end="\n\n")

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
    print("")

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
    print("")
    conn.close()

    print("On progress...\n")

    questionary.press_any_key_to_continue().ask()
    return "Statistics"

def history(x, selected_cats=None):     # History keuangan
    title("History")
    if selected_cats is None:
        selected_cats = []

    # Pilihan Menu di History
    pilihan = ["Edit Data", "Filter by Category", f"Sort by {"Oldest" if x == "DESC" else "Newest"}", "<-"]
    
    # Connect ke database
    conn = sqlite3.connect("data.db")
    cursor = conn.cursor()

    # Sort data berdasarkan tanggal (defaultnya dari yang terbaru)
    if selected_cats:
        placeholders = ",".join("?" * len(selected_cats))
        query = f"""
            SELECT tanggal, keterangan, subjek, kategori, masuk, keluar, catatan
            FROM data_keuangan
            WHERE kategori IN ({placeholders})
            ORDER BY tanggal {x}
        """
        cursor.execute(query, selected_cats)
        caption_text = "Filter: " + ", ".join(selected_cats)
    else:
        cursor.execute(f"""
            SELECT tanggal, keterangan, subjek, kategori, masuk, keluar, catatan
            FROM data_keuangan
            ORDER BY tanggal {x}
        """)
        caption_text = "Filter: -"

    rows = cursor.fetchall()

    # Membuat Tabel
    table = Table(caption=f"*Sorted by Date: {"Newest" if x == "DESC" else "Oldest"}\n{caption_text}",caption_justify="left")

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

    # Ambil data kategori
    cursor.execute(
    """
        SELECT nama
        FROM tab_kategori
    """
    )
    kategori = cursor.fetchall()
    kategoris = [row[0] for row in kategori]

    # Print Tabel
    console.print(table)
    conn.close() # Mengakhiri koneksi dengan database

    # Pilih Menu
    pick = questionary.select("\nOption:", choices=pilihan, qmark="", style=style).ask()
    if pick == "Edit Data": 
        print("Fitur belum tersedia.") # SOON
        questionary.press_any_key_to_continue().ask()
        history(x)
    elif pick == pilihan [1]:
        title("History")
        console.print(table)        
        
        checkbox_choices = [Choice(title=i, value=i, checked=(i in selected_cats)) for i in kategoris]
        fltr = questionary.checkbox("\nKategori:", choices=checkbox_choices, qmark="", style=style).ask()
        
        history(x, selected_cats=fltr)
    elif pick == pilihan[2]:
        history(f"{"ASC" if x == "DESC" else "DESC"}", selected_cats) # Ubah sorting tanggal
    elif pick == "<-":
        return "History"

def random_rec():   # Rekomendasi Konsumsi Random
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
    table.add_column("Harga", justify="right", style="red")
    table.add_column("Catatan", justify="left")
    table.add_row(ftanggal(str(row[0])), str(row[1]), str(row[2]), uang(row[5]), str(row[6]))#'''
    
    console.print(table)
    conn.close()

    pick = questionary.select("Option:", choices=["Ganti", "<-"], qmark="", style=style).ask()
    if pick == "Ganti":
        random_rec()
    else:
        return "Random"

def others():       # Submenu Others
    # Pilihan Menu
    others_menu = ["History", "Statistics", "Financial Plan", "Settings","<-"]
    last = None

    while True:
        title("OTHERS") # Judul 

        # Pilih Menu
        pick = questionary.select("Options: ", choices=others_menu, qmark="", style=style, default=last).ask()
        if pick == 'History':
            last = history("DESC") # History, defaultnya dari yang terbaru
        elif pick == "Statistics":
            last = stats()
        elif pick == "Financial Plan":
            last = plan()
        elif pick == "Settings":
            last = settings() 
        elif pick == "<-":
            return

def ingput(x):      # Input Pengeluaran/Pemasukan
    # Cek Menu yang Dipilih
    if x == "Others":
        others()
        return x
    elif x == "Random":
        random_rec()
        return x
    
    # Convert x ke y
    y = ("keluar" if x=="Pengeluaran" else "masuk")

    title(x) # JUDUL

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
    
    t = str(questionary.text("Tanggal: ", default=ftanggal(tanggal), qmark="").ask())   
    a = str(questionary.text("Keterangan: ",qmark="").ask())
    b = questionary.autocomplete("Lokasi/Subjek: ",choices=subjeks, qmark="").ask()
    c = questionary.select("Kategori: ", choices=kategoris, qmark="").ask()
    d = int(questionary.text("Nominal: ",qmark="").ask())
    e = str(questionary.text("Catatan: ",qmark="").ask())

    isian = (rtanggal(t), a, b, c, d, e)
    
    cursor = conn.cursor()
    cursor.execute(query,isian)
    conn.commit()

    conn.close()

    # Menu Setelah INPUT
    pick = questionary.select("\nINPUT DITERIMA", choices=["Tambahkan Lagi", "<-"], qmark="", style=style).ask()
    if pick == "<-":
        return x
    else:
        ingput(x)

def mutlak(x):      # Fungsi absolut()
    if x >= 0:
        return x
    else:
        return -x

def peringatan():   # Peringatan limit
    bulan_ini = time.strftime("%Y-%m")
    conn = sqlite3.connect("data.db")
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT SUM(masuk) FROM data_keuangan
        WHERE strftime('%Y-%m', tanggal) = ?
    """, (bulan_ini,))
    row_masuk = cursor.fetchone()
    total_masuk = row_masuk[0] if row_masuk[0] is not None else 0

    cursor.execute("""
        SELECT SUM(keluar) FROM data_keuangan
        WHERE strftime('%Y-%m', tanggal) = ?
    """, (bulan_ini,))
    row_keluar = cursor.fetchone()
    total_keluar = row_keluar[0] if row_keluar[0] is not None else 0

    conn.close()
    sisa = total_masuk - total_keluar
    batas_kritis = 100000
    
    if sisa < 0:
        pesan = f"[bold red]PERINGATAN KERAS![/bold red]\n"\
                f"Pengeluaran bulan ini melebihi pemasukan!\n\n" \
                f"Pemasukan : {uang(total_masuk)}\n" \
                f"Pengeluaran : {uang(total_keluar)}\n" \
                f"Defisit : [bold red]{uang(mutlak(sisa))}[/bold red]"
        console.print(Panel(pesan, title="⚠️ FINANCIAL WARNING", style="red"))
    
    elif sisa <= batas_kritis:
        pesan = f"[bold yellow]HATI-HATI![/bold yellow]\n"\
                f"Sisa uang bulan ini sudah menipis!\n\n" \
                f"Pemasukan : {uang(total_masuk)}\n" \
                f"Pengeluaran : {uang(total_keluar)}\n" \
                f"Sisa : [bold yellow]{uang(mutlak(sisa))}[/bold yellow]"
        console.print(Panel(pesan, title="⚠️ LOW BALANCE", style="yellow"))
    else :
        pesan = f"[bold green]KONDISI AMAN[/bold green]\n"\
                f"Cashflow bulan ini masih positif\n\n" \
                f"Sisa : [bold green]{uang(mutlak(sisa))}[/bold green]"
        console.print(Panel(pesan, title="✅ STATUS OK", style="green"))

def database():     # Load/Buat database
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

    default_in = ["Gaji", "Bulanan", "Bonus"]
    default_out = ["Konsumsi", "Transportasi", "Daily", "Hiburan", "Development"]

    cursor = conn.cursor()

    for i in default_in:
        cursor.execute("INSERT OR IGNORE INTO tab_kategori VALUES ('in', ?)", (i,))
    for i in default_out:
        cursor.execute("INSERT OR IGNORE INTO tab_kategori VALUES ('out', ?)", (i,))
    
    conn.commit()
    conn.close()

def main():         # Main Menu
    # Array Pilihan Menu
    menu = [Choice(title=[('red',"Pengeluaran")], value="Pengeluaran"),
            Choice(title=[('green',"Pemasukan")], value="Pemasukan"),
            "Random", "Others", "=EXIT="]
    last = None

    while True:
        clear()
        print(f.renderText("ATURAZA"), end="")
        peringatan()

        # Pilih Menu
        pick = questionary.select("Menu: ", choices=menu, qmark="", style=style, default=last).ask()
        
        if pick == menu[4]: # EXIT
            clear()
            print(f.renderText("Terima Kasih!"))
            time.sleep(0.5)
            return
        last=ingput(pick)

if __name__ == "__main__": # Memastikan sedang di main
    database()  # Load Database dulu
    main()      # Main menu