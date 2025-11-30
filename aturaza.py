import questionary, os, time, sqlite3
from questionary import Style
from rich.console import Console
from rich.table import Table

console = Console()
tanggal = time.strftime("%d/%m/%Y", time.localtime(time.time()))
menu = ["Pengeluaran", "Pemasukan", "Random", "Others", "=EXIT="]
kat_in = ["Gaji", "Bulanan", "Rezeki"]
kat_out = ["Konsumsi", "Transportasi", "Daily", "Hiburan", "Development"]

# Tes github

def clear():
    os.system("cls" if os.name == "nt" else "clear")

def title(x):
    clear()
    x = "\033[4m\033[1m"+x+"\033[0m"
    print(x)

def uang(x):
    if str(x) == 'None': return ""

    ans = f"Rp{x:,}".replace(",", ".")

    return ans+',00'

def random_rec():
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

    #'''
    table = Table(title="Random Pick", caption="*Hanya kategori konsumsi", caption_justify="left")
    table.add_column("Tanggal", justify="center")
    table.add_column("Keterangan", justify="left")
    table.add_column("Lokasi/Subjek")
    #table.add_column("Kategori", justify="left")
    #table.add_column("Masuk", justify="right", style="green")
    table.add_column("Harga", justify="right", style="red")
    table.add_column("Catatan", justify="left")
    table.add_row(str(row[0]), str(row[1]), str(row[2]), uang(row[5]), str(row[6]))#'''
    
    console.print(table)
    conn.close()

    pick = questionary.select("Option:", choices=["Another One","Back"], qmark="").ask()
    if pick == "Another One": random_rec()
    else: main()

def settings():
    set_menu = ["Add Kategori Pengeluaran", "Add Kategori Pemasukan", "Clear Data", "<-"]
    
    title("SETTINGS")
    pick = questionary.select("Options: ", choices=set_menu, qmark="").ask()
    if pick == "<-":
        others()
        return

    if pick == set_menu[0]:
        # Belum store di database
        title("KATEGORI PENGELUARAN")
        print("Masukkan nama kategori baru (ketik - untuk mengakhiri)")
        masih = True
        while masih:
            x = str(input(": "))
            if x=='-': masih=False
            else: kat_out.append(x)
    elif pick == set_menu[1]:
        # Belum store di database
        title("KATEGORI PEMASUKAN")
        print("Masukkan nama kategori baru (ketik - untuk mengakhiri)")
        masih = True
        while masih:
            x = str(input(": "))
            if x=='-': masih=False
            else: kat_in.append(x)
    elif pick==set_menu[2]:
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
    settings()

def stats():
    title("STATISTICS")
    
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
    print(f"Rata-Rata Pengeluaran per Hari: {uang(rerata)}", end="\n")

    # Most Visited
    cursor.execute("""
        SELECT subjek, COUNT(*) AS freq
        FROM data_keuangan
        GROUP BY subjek
        ORDER BY freq DESC
        LIMIT 3
                    """)
    
    most_freq = cursor.fetchall()
    
    table = Table(title="Most Frequent", caption=" Most frequently interacted", caption_justify="left")

    table.add_column("Lokasi/Subjek")
    table.add_column("Frekuensi")

    for row in most_freq:
        table.add_row(str(row[0]), str(row[1]))
    
    console.print(table)
    conn.close()

    print("On progress...")

    questionary.press_any_key_to_continue().ask()
    others()

def history(x):
    clear()
    pilihan = ["Edit Data",f"Sort by {"Oldest" if x == "DESC" else "Newest"}","Back"]
    conn = sqlite3.connect("data.db")
    cursor = conn.cursor()

    # Sort data berdasarkan tanggal
    cursor.execute(f"SELECT tanggal, keterangan, subjek, kategori, masuk, keluar, catatan FROM data_keuangan ORDER BY rowid {x}")
    rows = cursor.fetchall()

    # Tabel
    table = Table(title="History", caption=f" SORTING: {"newest" if x == "DESC" else "oldest"}", caption_justify="left")

    table.add_column("Tanggal", justify="center")
    table.add_column("Keterangan", justify="left")
    table.add_column("Lokasi/Subjek")
    table.add_column("Kategori", justify="left")
    table.add_column("Masuk", justify="right", style="green")
    table.add_column("Keluar", justify="right", style="red")
    table.add_column("Catatan", justify="left")

    for row in rows:
        table.add_row(str(row[0]), str(row[1]), str(row[2]), str(row[3]), uang(row[4]), uang(row[5]), str(row[6]))

    console.print(table)
    conn.close()

    pick = questionary.select("Option:", choices=pilihan, qmark="").ask()
    if pick == "Edit Data": 
        print("Fitur belum tersedia.")
        questionary.press_any_key_to_continue().ask()
        history(x)
    elif pick == pilihan[1]: history(f"{"ASC" if x == "DESC" else "DESC"}")
    elif pick == "Back": others()

def others():
    others_menu = ["History", "Statistics", "Settings","<-"]
    
    title("OTHERS")
    pick = questionary.select("Options: ", choices=others_menu, qmark="").ask()
    if pick=='History': history("DESC")
    elif pick=="Statistics": stats()
    elif pick=="Settings": settings() 
    elif pick=="<-":
        main()
        return

def ingput(x):
    if x == "Others":
        others()
        return
    elif x == "Random":
        random_rec()
        return
    
    y = ("keluar" if x=="Pengeluaran" else "masuk")

    title(x.upper())

    conn = sqlite3.connect('data.db')
    table_create_query = '''CREATE TABLE IF NOT EXISTS data_keuangan
            (tanggal TEXT, keterangan TEXT, subjek TEXT, kategori TEXT, masuk INT, keluar INT, catatan TEXT)
    '''
    #Autocomplete feature
    cursor = conn.cursor()

    cursor.execute("""
        SELECT subjek
        FROM data_keuangan
                    """)
    
    sub_list = cursor.fetchall()
    subjeks = [row[0] for row in sub_list]
    conn.execute(table_create_query)
    query = f'''INSERT INTO data_keuangan (tanggal, keterangan, subjek, kategori, {y}, catatan) VALUES (?, ?, ?, ?, ?, ?)'''

    #a = str(input("Keterangan: " ))
    a = questionary.text("Keterangan: ").ask()
    #b = str(input("Lokasi/Subjek: "))
    b = questionary.autocomplete("Lokasi/Subjek: ",choices=subjeks, qmark="").ask()
    c = questionary.select("Kategori: ", choices=kat_out, qmark="").ask()
    d = int(input("Nominal: "))
    e = str(input("Catatan: "))

    isian = (tanggal, a, b, c, d, e)
    
    cursor = conn.cursor()
    cursor.execute(query,isian)
    conn.commit()

    conn.close()

    #print("INPUT DITERIMA")
    pick = questionary.select("INPUT DITERIMA", choices=["Tambahkan Lagi", "<-"], qmark="").ask()
    if pick == "<-": main()
    else: ingput(x)

def main():
    title("ATURAZA")
    pick = questionary.select("Menu: ", choices=menu, qmark="").ask()
    if pick == menu[4]:
        clear()
        print("Terima kasih!")
        time.sleep(0.5)
        return
    ingput(pick)

main()