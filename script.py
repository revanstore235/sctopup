import os
import sys
import json
import time
import hashlib
import base64
import datetime
import subprocess
import requests as req
from urllib.parse import quote
import re

WHITE  = '\x1b[1;97m'
YELLOW  = '\x1b[38;5;226m'
RED  = '\x1b[38;5;196m'
BLACK  = '\x1b[38;5;8m'
GREEN = '\x1b[38;5;51m'
green = '\x1b[38;5;46m'
PURPLE = '\x1b[38;5;165m'

os.system('clear')

USER_LICENSE_NAME = "N/A"
USER_LICENSE_EXPIRY_INFO = "N/A"
DEVICE_ID_INFO = "N/A"

logo2_upper_part = """
\033[1;92m \x1b[38;5;196m██████╗░██╗░░░██╗░██████╗░██████╗██╗██████╗░
\033[1;92m \x1b[38;5;197m██╔══██╗██║░░░██║██╔════╝██╔════╝██║██╔══██╗
\033[1;92m \x1b[38;5;198m██████╦╝██║░░░██║╚█████╗░╚█████╗░██║██║░░██║
\033[1;92m \x1b[38;5;199m██╔══██╗██║░░░██║░╚═══██╗░╚═══██╗██║██║░░██║
\033[1;92m \x1b[38;5;200m██████╦╝╚██████╔╝██████╔╝██████╔╝██║██████╔╝
\033[1;92m \x1b[38;5;201m╚═════╝░░╚═════╝░╚═════╝░╚═════╝░╚═╝╚═════╝░
"""

logo1 = f"""
\033[1;92m \x1b[38;5;196m██████╗░██╗░░░██╗░██████╗░██████╗██╗██████╗░
\033[1;92m \x1b[38;5;197m██╔══██╗██║░░░██║██╔════╝██╔════╝██║██╔══██╗
\033[1;92m \x1b[38;5;198m██████╦╝██║░░░██║╚█████╗░╚█████╗░██║██║░░██║
\033[1;92m \x1b[38;5;199m██╔══██╗██║░░░██║░╚═══██╗░╚═══██╗██║██║░░██║
\033[1;92m \x1b[38;5;200m██████╦╝╚██████╔╝██████╔╝██████╔╝██║██████╔╝
\033[1;92m \x1b[38;5;201m╚═════╝░░╚═════╝░╚═════╝░╚═════╝░╚═╝╚═════╝░
"""

_ketik_active = True

def ketik(c, d=0.00003):
    global _ketik_active
    if not _ketik_active:
        print(c)
        return
    try:
        for e in c + "\n":
            sys.stdout.write(e)
            sys.stdout.flush()
            time.sleep(d)
    except KeyboardInterrupt:
        print(f"\n{RED}Proses dihentikan oleh pengguna (Ctrl+C). Keluar...{PURPLE}")
        _ketik_active = False
        raise

def get_visual_length(s):
    return len(re.sub(r'\x1b\[[0-9;]*[mK]', '', s))

def dev_id():
    props = [
        "ro.build.id", "ro.serialno", "ro.bootloader", "ro.product.model",
        "ro.product.manufacturer", "ro.product.cpu.abi", "ro.product.device",
        "ro.build.version.release", "ro.build.version.sdk"
    ]
    unique_str = "".join(
        subprocess.getoutput(f'getprop {prop}').strip() for prop in props
    )
    sha256_hash = hashlib.sha256(unique_str.encode()).hexdigest()
    return sha256_hash[:17]

def exp_date(expiry_date_str):
    try:
        expiry_date = datetime.datetime.strptime(expiry_date_str, "%d-%m-%Y").date()
        current_date = datetime.datetime.now().date()
        return (expiry_date - current_date).days
    except ValueError:
        print(f"Format tanggal kedaluwarsa tidak valid: {expiry_date_str}")
        return -1

def dec_b64(content):
    decoded_bytes = base64.b64decode(content)
    decoded_str = decoded_bytes.decode('utf-8')
    return json.loads(decoded_str)

def fetch_json(url, retries=3, delay=1):
    for attempt in range(retries):
        try:
            response = req.get(url, timeout=20)
            if response.status_code == 200:
                data = response.json()
                if "exit()" in str(data):
                    print(f"\n{RED}Lisensi Anda tidak valid. Silakan hubungi administrator.{PURPLE}")
                    sys.exit(0)
                return data
        except (req.RequestException, ValueError):
            pass
        time.sleep(delay)
    return None

def send_wa(build_id, nama_user="N/A", pesan_tambahan=""):
    message = f"Assalamualaikum min ini\nNama: {nama_user}\nId  : {build_id}"
    if pesan_tambahan:
        message += f"\n\n{pesan_tambahan}"
    encoded_message = quote(message)
    url = f"https://wa.me/+6289520418604?text={encoded_message}"
    os.system(f"xdg-open '{url}'")

def license_exp(build_id_hash, expiry_date_str):
    global USER_LICENSE_NAME
    
    nama_hari_id = {
        'Monday': 'Senin', 'Tuesday': 'Selasa', 'Wednesday': 'Rabu',
        'Thursday': 'Kamis', 'Friday': 'Jumat', 'Saturday': 'Sabtu', 'Sunday': 'Minggu'
    }
    nama_bulan_id = {
        'January': 'Januari', 'February': 'Februari', 'March': 'Maret',
        'April': 'April', 'May': 'Mei', 'June': 'Juni',
        'July': 'Juli', 'August': 'Agustus', 'September': 'September',
        'October': 'Oktober', 'November': 'November', 'December': 'Desember'
    }

    try:
        exp_datetime = datetime.datetime.strptime(expiry_date_str, "%d-%m-%Y")
        hari_en = exp_datetime.strftime('%A')
        bulan_en = exp_datetime.strftime('%B')
        hari_id = nama_hari_id.get(hari_en, hari_en)
        bulan_id = nama_bulan_id.get(bulan_en, bulan_en)
        tanggal_kedaluwarsa_lengkap = f"{hari_id}, {exp_datetime.day} {bulan_id} {exp_datetime.year}"
    except ValueError:
        tanggal_kedaluwarsa_lengkap = expiry_date_str

    while True:
        menu_perpanjangan = f"""
{PURPLE}╔═════════════════════════════════════════════════════╗
{PURPLE}║        {RED}Yah, Lisensi Anda Telah Kedaluwarsa!{PURPLE}         ║
{PURPLE}║        {RED}Kedaluwarsa pada: {tanggal_kedaluwarsa_lengkap}{PURPLE}         ║
{PURPLE}╟─────────────────────────────────────────────────────╢
{PURPLE}║  {YELLOW}Jangan khawatir, perpanjang lisensi Anda sekarang!{PURPLE} ║
{PURPLE}║               {YELLOW}Pilih paket di bawah ini:{PURPLE}             ║
{PURPLE}╟─────────────────────────────────────────────────────╢{WHITE}
{PURPLE}║ {RED}【{WHITE}1{RED}】 {YELLOW}Perpanjang 1 MINGGU   {green}Rp 10.000{PURPLE}               ║
{PURPLE}║ {RED}【{WHITE}2{RED}】 {YELLOW}Perpanjang 2 MINGGU   {green}Rp 25.000{PURPLE}               ║
{PURPLE}║ {RED}【{WHITE}3{RED}】 {YELLOW}Perpanjang 1 BULAN    {green}Rp 35.000{PURPLE}               ║
{PURPLE}║ {RED}【{WHITE}4{RED}】 {YELLOW}Perpanjang 2 BULAN    {green}Rp 40.000{PURPLE}               ║
{PURPLE}║ {RED}【{WHITE}5{RED}】 {YELLOW}Perpanjang 3 BULAN    {green}Rp 55.000{PURPLE}               ║
{PURPLE}║ {RED}【{WHITE}6{RED}】 {YELLOW}Lisensi PERMANEN      {green}Rp 80.000{PURPLE}               ║
{PURPLE}╟─────────────────────────────────────────────────────╢{WHITE}
{PURPLE}║ {RED}【{WHITE}0{RED}】 {YELLOW}Keluar{PURPLE}                                        ║
{PURPLE}╚═════════════════════════════════════════════════════╝
"""
        ketik(menu_perpanjangan, d=0.0001)
        
        pilihan = input(f'''{PURPLE}╭­\x1b[1;33;41m\x1b[1;37m✦ PILIH PAKET ✦\x1b[1;33m\x1b[0m\x1b[{PURPLE}
╰───{RED}▶ ''').strip()
        
        if pilihan in ["1", "2", "3", "4", "5", "6"]:
            qris_links = {
                "1": "https://www.mediafire.com/view/xpj410stees69tj/20251018_155618.jpg/file",
                "2": "https://www.mediafire.com/view/klhpsuh1f6316w0/20251018_155639.jpg/file",
                "3": "https://www.mediafire.com/view/mjhk2s1nhu3q8gs/20251018_155651.jpg/file",
                "4": "https://www.mediafire.com/view/kjn033iu9gfo5ol/20251018_155703.jpg/file",
                "5": "https://www.mediafire.com/view/ybgfjp9lowkm1d6/20251018_155715.jpg/file",
                "6": "https://www.mediafire.com/view/6f2yw0fpwqldygs/20251018_155730.jpg/file"
            }
            paket_info = {
                "1": "1 MINGGU (10K)", "2": "2 MINGGU (25K)", "3": "1 BULAN (35K)",
                "4": "2 BULAN (40K)", "5": "3 BULAN (55K)", "6": "PERMANEN (80K)"
            }
    
            selected_link = qris_links.get(pilihan)
            selected_paket = paket_info.get(pilihan)

            ketik(f"\n{PURPLE}Anda telah memilih paket perpanjangan: {YELLOW}{selected_paket}{PURPLE}")
            ketik(f"{PURPLE}Anda akan segera diarahkan ke browser untuk pembayaran...{PURPLE}")            
            time.sleep(1)

            try:
                os.system(f"xdg-open '{selected_link}'")
            except Exception as e:
                ketik(f"\n{RED}Gagal menampilkan gambar QRIS. Silakan buka tautan secara manual: {selected_link}", d=0.01)

            info_pembayaran = f"""
{PURPLE}====================================================={WHITE}
{YELLOW} ★★★ INSTRUKSI SELANJUTNYA ★★★ {WHITE}

{green}Setelah berhasil melakukan pembayaran,{WHITE}
{green}mohon konfirmasi kepada admin untuk pengaktifan lisensi Anda,{WHITE}
{green}Dan Mohon kirimkan bukti pembayaran kepada admin.{WHITE}
{PURPLE}====================================================={WHITE}"""
            ketik(info_pembayaran, d=0.001)
            
            while True:
                print(f"\n{PURPLE}[{WHITE}◆{PURPLE}] {YELLOW}Ketik '{green}1{YELLOW}' untuk Konfirmasi Pembayaran ke Admin,")
                konfirmasi = input(f"{PURPLE}[{WHITE}◆{PURPLE}] {YELLOW}Ketik '{RED}2{YELLOW}' untuk Kembali memilih pilihan paket Perpanjangan: {WHITE}").strip()
                
                if konfirmasi == '1':
                    pesan_wa = f"Saya ingin konfirmasi perpanjangan lisensi dengan detail:\nPaket: {selected_paket}"
                    ketik(f"\n{green}Terima kasih! Anda akan segera dialihkan ke Apk WhatsApp untuk menkonfirmasi Pembayaran Kepada Admin.", d=0.01)
                    
                    for i in range(10, 0, -1):
                        sys.stdout.write(f"\r{YELLOW}Membuka WhatsApp dalam {i} detik...{WHITE}   ")
                        sys.stdout.flush()
                        time.sleep(1)
                    
                    print("\n")
                    send_wa(build_id_hash, USER_LICENSE_NAME, pesan_wa)
                    time.sleep(3)
                    sys.exit(0)
                elif konfirmasi == '2':
                    os.system('clear')
                    ketik(logo2_upper_part, d=0.0001)
                    break 
                else:
                    ketik(f"{RED}Pilihan tidak valid. Silakan masukkan '1' atau '2'.{WHITE}")

        elif pilihan == "0":
            ketik(f"{YELLOW}Anda memilih untuk keluar. Sampai jumpa!{WHITE}")
            sys.exit(0)
        else:
            ketik(f"{RED}Pilihan tidak valid, silakan coba lagi.{WHITE}")
            time.sleep(2)
            os.system('clear')
            ketik(logo2_upper_part, d=0.0001)

def license_enol(build_id_hash):
    ketik(f"{PURPLE}[{YELLOW}◆{PURPLE}] {RED}Lisensi tidak terdaftar!{PURPLE}")
    ketik(f"{PURPLE}[{YELLOW}◆{PURPLE}] {RED}UserID: {green}{build_id_hash}{PURPLE}")

    nama_pengguna_lisensi = ""
    while not nama_pengguna_lisensi:
        nama_pengguna_lisensi = input(f"{PURPLE}[{WHITE}◆{PURPLE}] {YELLOW}Masukkan Nama Anda untuk permintaan lisensi:{WHITE} ").strip()
        if not nama_pengguna_lisensi:
            ketik(f"{RED}Nama tidak boleh kosong. Silakan masukkan nama Anda.{WHITE}")

    ketik(f"{PURPLE}[{YELLOW}◆{PURPLE}] {RED}Silakan hubungi admin untuk membeli lisensi!{PURPLE}")
    ketik(f"{PURPLE}[{YELLOW}◆{PURPLE}] {RED}Menghubungi Admin...{PURPLE}")
    time.sleep(3)
    send_wa(build_id_hash, nama_pengguna_lisensi, "Saya ingin membeli lisensi baru.")
    sys.exit(0)

def license_check():
    global USER_LICENSE_NAME, USER_LICENSE_EXPIRY_INFO, DEVICE_ID_INFO
    build_id_hash = dev_id()
    DEVICE_ID_INFO = build_id_hash
    url = f'https://api.github.com/repos/revanstore235/sctopup/contents/lisensi/{build_id_hash}.json'
    ketik(f"\n{PURPLE}[{YELLOW}◆{PURPLE}] {RED}Memeriksa lisensi Anda...{PURPLE}", d=0.01)
    time.sleep(2)

    file_data = fetch_json(url)
    if file_data:
        content_base64 = file_data.get('content')
        if content_base64:
            try:
                file_data_decoded = dec_b64(content_base64)
            except json.JSONDecodeError:
                ketik(f"{RED}Error mendekode data lisensi. Silakan hubungi admin.{PURPLE}")
                license_enol(build_id_hash)
                return
            except Exception:
                ketik(f"{RED}Error memproses data lisensi. Silakan hubungi admin.{PURPLE}")
                license_enol(build_id_hash)
                return

            name = file_data_decoded.get("name", "Pengguna Tidak Dikenal")
            expiry_date_str = file_data_decoded.get("expiry_date")
            role = file_data_decoded.get("role", "tidak diketahui")
        else:
            name = file_data.get("name", "Pengguna Tidak Dikenal")
            expiry_date_str = file_data.get("expiry_date")
            role = file_data.get("role", "tidak diketahui")
            if name is None and 'message' in file_data:
                 ketik(f"{RED}File lisensi tidak ditemukan atau masalah dengan path repositori.{PURPLE}")
                 license_enol(build_id_hash)
                 return

        USER_LICENSE_NAME = name
        ketik(f"{PURPLE}[{YELLOW}◆{PURPLE}] {RED}Hallo {green}{name}{RED}", d=0.01)
        if expiry_date_str:
            days_left = exp_date(expiry_date_str)
            if days_left > 0:
                USER_LICENSE_EXPIRY_INFO = f"{expiry_date_str} ({days_left} hari tersisa)"
                ketik(f"{PURPLE}[{YELLOW}◆{PURPLE}] {RED}Anda adalah {green}{role.upper()}{PURPLE}!", d=0.002)
                time.sleep(2)
            else:
                if days_left == 0:
                    USER_LICENSE_EXPIRY_INFO = f"Kedaluwarsa hari ini ({expiry_date_str})"
                    print(f"{PURPLE}[{YELLOW}◆{PURPLE}] {RED}Lisensi Anda habis {YELLOW}hari ini{PURPLE}! Silakan perbarui segera.{PURPLE}")
                else:
                    USER_LICENSE_EXPIRY_INFO = f"Kedaluwarsa pada {expiry_date_str} ({abs(days_left)} hari yang lalu)"
                    print(f"{PURPLE}[{YELLOW}◆{PURPLE}] {RED}Lisensi Anda telah kedaluwarsa {green}{abs(days_left)} {RED}hari yang lalu!")
                time.sleep(2)
                license_exp(build_id_hash, expiry_date_str)
        else:
            USER_LICENSE_EXPIRY_INFO = "Tanggal kedaluwarsa tidak ditentukan"
            ketik(f"{PURPLE}[{YELLOW}◆{PURPLE}] {RED}Data lisensi tidak lengkap (tidak ada tanggal kedaluwarsa).{PURPLE}")
            license_enol(build_id_hash)
    else:
        USER_LICENSE_NAME = "Tidak Terdaftar"
        USER_LICENSE_EXPIRY_INFO = "Tidak Terdaftar"
        license_enol(build_id_hash)

headers = {
    'Content-Type': 'application/json',
}

auth_input = ""

def login():
    global auth_input, headers
    try:
        if len(auth_input) > 25:
            headers['X-Authorization'] = auth_input
            return True

        login_data = {
            "AndroidDeviceID": auth_input, "TitleId": "4AE9", "CreateAccount": False}
        response = req.post("https://4AE9.playfabapi.com/Client/LoginWithAndroidDeviceID", headers=headers, json=login_data)
        if response.status_code == 200:
            response_data = response.json()
            if "data" in response_data and "SessionTicket" in response_data["data"]:
                auth_token = response_data["data"]["SessionTicket"]
                headers['X-Authorization'] = auth_token
                return True
            else:
                error_message = response_data.get("errorMessage", "Periksa Device ID Anda!")
                print(f"\n{RED}Login gagal. {error_message}")
                sys.exit(0)
        else:
            sys.exit(f"{RED} Error: Akun tidak ditemukan (Status: {response.status_code})")
    except req.exceptions.RequestException as e:
        sys.exit(f"{RED}Koneksi gagal. Periksa jaringan Anda. ({e})")
    except Exception as e:
        sys.exit(f"Terjadi kesalahan saat login: {e}")

def mxx_fetch_info():
    global headers
    data = json.dumps({"InfoRequestParameters": {"GetUserAccountInfo": True, "GetUserVirtualCurrency": True}})
    try:
        response = req.post(
            'https://4ae9.playfabapi.com/Client/GetPlayerCombinedInfo',
            headers=headers,
            data=data
        )
        response.raise_for_status()
        parser = response.json()
        if parser.get('code') == 200:
            info = parser['data']['InfoResultPayload']
            money = info['UserVirtualCurrency'].get('RP', 0)
            name = '[ganti nama]'
            try:
                name = info['AccountInfo']['TitleInfo']['DisplayName']
            except KeyError:
                pass
            return name, money
        else:
            return None, None
    except req.exceptions.RequestException:
        return None, None
    except Exception:
        return None, None

def mxx_display_info():
    nama_akun, saldo_akun = mxx_fetch_info()
    if nama_akun is not None and saldo_akun is not None:
        times = time.strftime('%H:%M:%S', time.localtime())

        border_char_mxx = "═"
        border_width_mxx = 33

        str_nama_display = f"👤 Nama akun: {nama_akun}"
        padding_nama = " " * max(0, (border_width_mxx - 3) - get_visual_length(str_nama_display))

        str_uang_display = f"💰 Uang: {saldo_akun:,}"
        padding_uang = " " * max(0, (border_width_mxx - 3) - get_visual_length(str_uang_display))

        str_jam_display = f"⏲️  Jam: {times}"
        padding_jam = " " * max(0, (border_width_mxx - 1) - get_visual_length(str_jam_display))

        info_akun_display = f""" {PURPLE}╔{border_char_mxx * border_width_mxx}╗
 {PURPLE}║ {WHITE}{str_nama_display}{padding_nama}{PURPLE} ║
 {PURPLE}║ {WHITE}{str_uang_display}{padding_uang}{PURPLE} ║
 {PURPLE}║ {WHITE}{str_jam_display}{padding_jam}{PURPLE} ║
 {PURPLE}╚{border_char_mxx * border_width_mxx}╝"""
        ketik(info_akun_display)
    else:
        ketik(f"{RED}Gagal memuat informasi akun saat ini.{WHITE}")

def tampilkan_detail_transaksi(nama_akun_display, nominal_transaksi, saldo_sebelum_rp, saldo_setelah_rp, berhasil, jenis_transaksi_override=None, nama_sebelum_ganti=None, nama_sesudah_ganti=None):
    sekarang = datetime.datetime.now()
    nama_hari_id = {
        'Monday': 'Senin', 'Tuesday': 'Selasa', 'Wednesday': 'Rabu',
        'Thursday': 'Kamis', 'Friday': 'Jumat', 'Saturday': 'Sabtu', 'Sunday': 'Minggu'
    }
    nama_bulan_id = {
        'January': 'Januari', 'February': 'Februari', 'March': 'Maret',
        'April': 'April', 'May': 'Mei', 'June': 'Juni',
        'July': 'Juli', 'August': 'Agustus', 'September': 'September',
        'October': 'Oktober', 'November': 'November', 'December': 'Desember'
    }

    tgl_str = ""
    try:
        import locale
        locale.setlocale(locale.LC_TIME, 'id_ID.UTF-8')
        tgl_str_raw = sekarang.strftime('%A, %d %B %Y')
        day_en_check = sekarang.strftime('%A')
        month_en_check = sekarang.strftime('%B')
        if day_en_check in nama_hari_id or month_en_check in nama_bulan_id:
            hari_id_val = nama_hari_id.get(day_en_check, day_en_check)
            bulan_id_val = nama_bulan_id.get(month_en_check, month_en_check)
            tgl_str = f"{hari_id_val}, {sekarang.day} {bulan_id_val} {sekarang.year}"
        else:
            tgl_str = tgl_str_raw
    except (locale.Error, UnicodeEncodeError, ImportError, AttributeError):
        hari_en = sekarang.strftime('%A')
        bulan_en = sekarang.strftime('%B')
        hari_id = nama_hari_id.get(hari_en, hari_en)
        bulan_id = nama_bulan_id.get(bulan_en, bulan_en)
        tgl_str = f"{hari_id}, {sekarang.day} {bulan_id} {sekarang.year}"

    jam_str = sekarang.strftime('%H:%M:%S')
    status_str = f"{green}Berhasil{WHITE}" if berhasil else f"{RED}Gagal{WHITE}"
    pesan = ""

    if jenis_transaksi_override == "Ganti Nama Akun":
        akun_display_final = nama_akun_display if nama_akun_display else (nama_sesudah_ganti if nama_sesudah_ganti else "N/A")
        nama_sebelum_final = nama_sebelum_ganti if nama_sebelum_ganti else "N/A"
        nama_sesudah_final = nama_sesudah_ganti if nama_sesudah_ganti else (akun_display_final if berhasil else nama_sebelum_final)

        pesan = f"""
{PURPLE}========================================={WHITE}
{YELLOW}ℹ️  Informasi {WHITE}

{YELLOW}👤 Akun:{green} {akun_display_final}{WHITE}
{YELLOW}🏷️ Jenis:{green} Ganti Nama{WHITE}
{YELLOW}👤 Nama Sebelum:{green} {nama_sebelum_final}{WHITE}
{YELLOW}👤 Nama Sesudah:{green} {nama_sesudah_final}{WHITE}
{YELLOW}🕒 Jam:{green} {jam_str}{WHITE}
{YELLOW}📅 Tgl:{green} {tgl_str}{WHITE}
{YELLOW}📈 Status: {status_str}
{YELLOW}ℹ️  Informasi Penting:{WHITE}
{YELLOW}╰┈➤ {green}Buka Bussid Nya Mas{WHITE}
{YELLOW}╰┈➤ {green}Cek Apakah Nama nya sudah tergantikan?{WHITE}
{YELLOW}╰┈➤ {green}Jika Akun Bussid nya terputus Login Ke akun Lama(Ganti Akun).{WHITE}
{YELLOW}╰┈➤ {green}Jangan Sambungkan Biar akun Bussid nya tidak hilang{WHITE}
{PURPLE}========================================={WHITE}"""
    elif jenis_transaksi_override == "Hapus Akun":
        info_penting_hapus_akun = ""
        if berhasil:
            info_penting_hapus_akun = f"""{YELLOW}╰┈➤ {green}Akun Anda telah berhasil diproses untuk penghapusan.{WHITE}
{YELLOW}╰┈➤ {green}Anda tidak akan bisa login lagi dengan akun ini.{WHITE}
{YELLOW}╰┈➤ {green}Silakan buat akun baru atau login dengan akun lain jika diperlukan.{WHITE}"""
        else:
            info_penting_hapus_akun = f"""{YELLOW}╰┈➤ {RED}Proses penghapusan akun tidak berhasil atau dibatalkan.{WHITE}
{YELLOW}╰┈➤ {green}Akun Anda seharusnya masih dapat diakses jika tidak dihapus.{WHITE}
{YELLOW}╰┈➤ {green}Jika Anda membatalkan, tidak ada perubahan pada akun Anda.{WHITE}"""
        pesan = f"""
{PURPLE}========================================={WHITE}
{YELLOW}ℹ️  Informasi {WHITE}

{YELLOW}👤 Akun:{green} {nama_akun_display if nama_akun_display else "N/A"}{WHITE}
{YELLOW}🏷️ Jenis:{green} Hapus Akun{WHITE}
{YELLOW}🕒 Jam:{green} {jam_str}{WHITE}
{YELLOW}📅 Tgl:{green} {tgl_str}{WHITE}
{YELLOW}📈 Status: {status_str}
{YELLOW}ℹ️  Informasi Penting:{WHITE}
{info_penting_hapus_akun}
{PURPLE}========================================={WHITE}"""
    else:
        nominal_display = "N/A"
        if nominal_transaksi is not None:
            try:
                nominal_display = f"{abs(nominal_transaksi):,}"
            except ValueError:
                 nominal_display = str(nominal_transaksi)

        saldo_sebelum_display = "N/A"
        if saldo_sebelum_rp is not None:
            try:
                saldo_sebelum_display = f"{saldo_sebelum_rp:,}"
            except ValueError:
                saldo_sebelum_display = str(saldo_sebelum_rp)

        saldo_setelah_display = "N/A"
        if saldo_setelah_rp is not None:
            try:
                saldo_setelah_display = f"{saldo_setelah_rp:,}"
            except ValueError:
                saldo_setelah_display = str(saldo_setelah_rp)

        jenis_transaksi_str_default = jenis_transaksi_override
        if jenis_transaksi_str_default is None:
            if nominal_transaksi is not None and isinstance(nominal_transaksi, (int, float)):
                if nominal_transaksi == 0 and not berhasil :
                     jenis_transaksi_str_default = "Cek Saldo (Sudah Habis)"
                elif nominal_transaksi == 0 and berhasil:
                     jenis_transaksi_str_default = "Cek Saldo (Sudah Habis)"
                else:
                     jenis_transaksi_str_default = "Top Up Instan" if nominal_transaksi > 0 else "Kuras Saldo Instan"
            else:
                jenis_transaksi_str_default = "Operasi Akun"

        nama_akun_final = nama_akun_display if nama_akun_display else "User Game (Gagal Deteksi)"
        pesan = f"""
{PURPLE}========================================={WHITE}
{YELLOW}ℹ️  INFORMASI {WHITE}

{YELLOW}👤 Akun:{green} {nama_akun_final}{WHITE}
{YELLOW}🏷️ Jenis:{green} {jenis_transaksi_str_default}{WHITE}
{YELLOW}💰 Nominal:{green} Rp {nominal_display}{WHITE}
{YELLOW}💰 Saldo Sebelum:{green} Rp {saldo_sebelum_display}{WHITE}
{YELLOW}💰 Saldo Sesudah:{green} Rp {saldo_setelah_display}{WHITE}
{YELLOW}🕒 Jam:{green} {jam_str}{WHITE}
{YELLOW}📅 Tgl:{green} {tgl_str}{WHITE}
{YELLOW}📈 Status: {status_str}
{YELLOW}ℹ️  Informasi Penting:{WHITE}
{YELLOW}╰┈➤ {green}Buka Bussid Nya Mas{WHITE}
{YELLOW}╰┈➤ {green}Ss Kan Di Garasi Ketik Done{WHITE}
{YELLOW}╰┈➤ {green}Jika Akun Bussid nya terputus Login Ke akun Lama(Ganti Akun).{WHITE}
{YELLOW}╰┈➤ {green}Jangan Sambungkan Biar Uang Bussid nya tidak hilang{WHITE}
{PURPLE}========================================={WHITE}"""
    ketik(pesan, d=0.0001)

Brp = 0

def ProssesUangInternal():
    global Brp, headers
    data = json.dumps({
        "FunctionName": "AddRp",
        "FunctionParameter": {"addValue": Brp},
        "RevisionSelection": "Live",
        "GeneratePlayStreamEvent": False
    })
    try:
        response = req.post("https://4ae9.playfabapi.com/Client/ExecuteCloudScript", headers=headers, data=data)
        response.raise_for_status()
        result = response.json()
        if 'Error' not in result and result.get('data', {}).get('FunctionName') == 'AddRp':
            return True
        else:
            return False
    except (req.exceptions.RequestException, Exception):
        return False

def Gas(jum):
    global Brp
    if jum == 0:
        return

    nama_akun_awal_batch, saldo_awal_batch = mxx_fetch_info()
    if nama_akun_awal_batch is None:
        ketik(f"{RED}Gagal mendapatkan info akun sebelum memulai transaksi.{WHITE}")
        tampilkan_detail_transaksi("Gagal Deteksi", Brp * jum if isinstance(Brp, (int, float)) else Brp, None, None, False,
                                   jenis_transaksi_override="Transaksi Gagal Total")
        return

    if jum == 1:
        ketik(f"{YELLOW}Memproses transaksi tunggal...{WHITE}", d=0.001)
        berhasil_tunggal = ProssesUangInternal()
        nama_akun_setelah, saldo_setelah = mxx_fetch_info()

        tampilkan_detail_transaksi(
            nama_akun_setelah if nama_akun_setelah else nama_akun_awal_batch,
            Brp,
            saldo_awal_batch,
            saldo_setelah if saldo_setelah is not None else (saldo_awal_batch + Brp if berhasil_tunggal and isinstance(Brp, (int,float)) else saldo_awal_batch),
            berhasil_tunggal
        )
        return

    total_nominal_berhasil = 0
    jumlah_berhasil = 0
    jumlah_gagal = 0

    for i in range(jum):
        ketik(f"{YELLOW}Memproses {i+1}-{jum}...{WHITE}", d=0.001)
        if ProssesUangInternal():
            jumlah_berhasil += 1
            if isinstance(Brp, (int, float)):
                total_nominal_berhasil += Brp
        else:
            jumlah_gagal += 1
            ketik(f"{RED}Sub-proses ke-{i+1} tidak berhasil.{WHITE}", d=0.001)

    nama_akun_setelah_batch, saldo_setelah_batch = mxx_fetch_info()

    status_keseluruhan_batch = False
    jenis_transaksi_batch_str = "Transaksi Batch"
    if isinstance(Brp, (int, float)) and Brp > 0:
        jenis_transaksi_batch_str = "Top Up Batch"
    elif isinstance(Brp, (int, float)) and Brp < 0:
        jenis_transaksi_batch_str = "Kuras Saldo Batch"

    if jumlah_berhasil == jum:
        status_keseluruhan_batch = True
        jenis_transaksi_batch_str += f" (Semua Berhasil: {jumlah_berhasil}/{jum})"
    elif jumlah_berhasil > 0:
        status_keseluruhan_batch = True
        jenis_transaksi_batch_str += f" (Sebagian Berhasil: {jumlah_berhasil}/{jum} sukses)"
    else:
        status_keseluruhan_batch = False
        jenis_transaksi_batch_str += " (Gagal Total)"

    tampilkan_detail_transaksi(
        nama_akun_setelah_batch if nama_akun_setelah_batch else nama_akun_awal_batch,
        total_nominal_berhasil,
        saldo_awal_batch,
        saldo_setelah_batch if saldo_setelah_batch is not None else (saldo_awal_batch + total_nominal_berhasil if isinstance(total_nominal_berhasil, (int,float)) else saldo_awal_batch),
        status_keseluruhan_batch,
        jenis_transaksi_override=jenis_transaksi_batch_str
    )

def kuras_semua_uang():
    global headers
    nama_akun_awal, saldo_awal = mxx_fetch_info()

    if nama_akun_awal is None:
        ketik(f"{RED}Gagal mendapatkan informasi saldo akun sebelum menguras.{WHITE}")
        tampilkan_detail_transaksi("Gagal Deteksi", None, None, None, False, jenis_transaksi_override="Kuras Semua Uang")
        return

    if saldo_awal == 0:
        ketik(f"\n{green}【{WHITE}✦{green}】{YELLOW}Uang sudah habis (0 RP). Tidak ada yang perlu dikuras.{WHITE}", d=0.003)
        tampilkan_detail_transaksi(nama_akun_awal, 0, saldo_awal, saldo_awal, True, jenis_transaksi_override="Kuras Semua Uang (Saldo Sudah 0)")
        return

    data_kuras = json.dumps({
        "FunctionName": "AddRp",
        "FunctionParameter": {"addValue": -saldo_awal},
        "RevisionSelection": "Live",
        "GeneratePlayStreamEvent": False
    })
    try:
        response_kuras = req.post("https://4ae9.playfabapi.com/Client/ExecuteCloudScript", headers=headers, data=data_kuras)
        response_kuras.raise_for_status()
        result_kuras = response_kuras.json()

        nama_akun_setelah, saldo_setelah = mxx_fetch_info()

        if 'Error' not in result_kuras:
            ketik(f"\n{RED}【{WHITE}✦{RED}】{green}Semua uang ({saldo_awal:,} RP) berhasil dikuras!", d=0.003)
            tampilkan_detail_transaksi(nama_akun_setelah if nama_akun_setelah else nama_akun_awal, -saldo_awal, saldo_awal, saldo_setelah if saldo_setelah is not None else 0, True, jenis_transaksi_override="Kuras Semua Uang")
        else:
            error_msg = result_kuras.get('Error', {}).get('Message', 'Error tidak diketahui')
            ketik(f"\n{RED}【{WHITE}✦{RED}】{RED}Gagal menguras uang: {error_msg}", d=0.003)
            tampilkan_detail_transaksi(nama_akun_awal, -saldo_awal, saldo_awal, saldo_awal, False, jenis_transaksi_override="Kuras Semua Uang")
    except req.exceptions.HTTPError as http_err:
        ketik(f"\n{RED}【{WHITE}✦{RED}】{RED}HTTP error saat menguras uang: {http_err}", d=0.003)
        tampilkan_detail_transaksi(nama_akun_awal, -saldo_awal, saldo_awal, saldo_awal, False, jenis_transaksi_override="Kuras Semua Uang")
    except Exception as e:
        ketik(f"\n{RED}【{WHITE}✦{RED}】{RED}Terjadi kesalahan saat menguras uang: {e}", d=0.003)
        tampilkan_detail_transaksi(nama_akun_awal, -saldo_awal, saldo_awal, saldo_awal, False, jenis_transaksi_override="Kuras Semua Uang")

def HapusAkun():
    global headers
    nama_akun_sebelum_fetch, saldo_sebelum_fetch = mxx_fetch_info()

    konfirmasi = input(f"{PURPLE}[{WHITE}◆{PURPLE}] {YELLOW}Apakah Anda yakin ingin menghapus akun '{nama_akun_sebelum_fetch if nama_akun_sebelum_fetch else 'ini'}'? Tindakan ini tidak dapat dibatalkan. (y/n):{WHITE} ").strip().lower()

    berhasil = False
    if konfirmasi == 'y':
        data = json.dumps({
            "FunctionName": "DeleteUsers",
            "FunctionParameter": {},
            "RevisionSelection": "Live",
            "GeneratePlayStreamEvent": False
        })
        try:
            response = req.post("https://4ae9.playfabapi.com/Client/ExecuteCloudScript", headers=headers, data=data)
            response.raise_for_status()
            result = response.json()
            if 'Error' not in result:
                ketik(f"\n{RED}【{WHITE}✦{RED}】{green}AKUN BERHASIL DIHAPUS (jika CloudScript berhasil)‼️{WHITE}", d=0.003)
                berhasil = True
            else:
                error_msg = result.get('Error', {}).get('Message', 'Gagal menghapus akun')
                ketik(f"\n{RED}【{WHITE}✦{RED}】{RED}Gagal Menghapus Akun: {error_msg}", d=0.003)
        except req.exceptions.HTTPError as http_err:
            ketik(f"\n{RED}【{WHITE}✦{RED}】{RED}HTTP error saat menghapus akun: {http_err}", d=0.003)
        except Exception as e:
            ketik(f"\n{RED}【{WHITE}✦{RED}】{RED}Terjadi kesalahan saat menghapus akun: {e}", d=0.003)
    else:
        ketik(f"{YELLOW}Penghapusan akun dibatalkan oleh pengguna.{WHITE}")
        berhasil = False

    nama_display_final = nama_akun_sebelum_fetch if nama_akun_sebelum_fetch else "N/A"
    if berhasil :
        nama_display_final = f"{nama_akun_sebelum_fetch if nama_akun_sebelum_fetch else 'Akun'} (Telah Dihapus)"

    tampilkan_detail_transaksi(nama_display_final, None, None, None, berhasil, jenis_transaksi_override="Hapus Akun")
    return berhasil

def ganti_nama_akun():
    global headers
    nama_akun_sebelum_fetch, _ = mxx_fetch_info()
    nama_untuk_prompt_sebelum = nama_akun_sebelum_fetch if nama_akun_sebelum_fetch else "[Nama Saat Ini Tidak Terdeteksi]"

    nama_baru = input(f"{PURPLE}[{WHITE}◆{PURPLE}] {YELLOW}Masukkan nama akun baru:{WHITE} ").strip()
    if not nama_baru:
        ketik(f"{RED}Nama akun tidak boleh kosong.{WHITE}")
        tampilkan_detail_transaksi(
            nama_untuk_prompt_sebelum,
            None, None, None, False,
            jenis_transaksi_override="Ganti Nama Akun",
            nama_sebelum_ganti=nama_untuk_prompt_sebelum,
            nama_sesudah_ganti=nama_untuk_prompt_sebelum
        )
        return

    konfirmasi = input(f"{PURPLE}[{WHITE}◆{PURPLE}] {YELLOW}Yakin ganti nama dari '{nama_untuk_prompt_sebelum}' menjadi '{nama_baru}'? (y/n):{WHITE} ").strip().lower()

    berhasil = False
    nama_aktual_setelah_operasi = nama_untuk_prompt_sebelum

    if konfirmasi == 'y':
        ketik(f"{PURPLE}[{WHITE}◆{PURPLE}] {YELLOW}Mengganti nama akun menjadi '{nama_baru}'...{WHITE}")
        payload = json.dumps({"DisplayName": nama_baru})
        try:
            response = req.post(
                "https://4ae9.playfabapi.com/Client/UpdateUserTitleDisplayName",
                headers=headers,
                data=payload
            )
            response.raise_for_status()
            if response.status_code == 200:
                ketik(f"{green}Nama akun berhasil diubah menjadi '{nama_baru}'.{WHITE}")
                berhasil = True
                nama_aktual_setelah_operasi = nama_baru
            else:
                error_data = response.json() if response.content else {}
                error_message = error_data.get('errorMessage', f"Gagal mengganti nama. Status: {response.status_code}")
                ketik(f"{RED}{error_message}{WHITE}")
        except req.exceptions.HTTPError as http_err:
            error_body = ""
            try:
                error_body = http_err.response.json()
                error_message = error_body.get('errorMessage', str(http_err))
                ketik(f"{RED}Gagal mengganti nama akun (HTTP Error): {error_message}{WHITE}")
            except json.JSONDecodeError:
                ketik(f"{RED}Gagal mengganti nama akun (HTTP Error): {http_err}{WHITE}")
        except req.exceptions.RequestException as e:
            ketik(f"{RED}Koneksi gagal saat mengganti nama akun: {e}{WHITE}")
        except Exception as e:
            ketik(f"{RED}Terjadi kesalahan tidak terduga saat mengganti nama: {e}{WHITE}")
    elif konfirmasi == 'n':
        ketik(f"{YELLOW}Penggantian nama akun dibatalkan.{WHITE}")
    else:
        ketik(f"{RED}Pilihan tidak valid. Harap ketik 'y' untuk ya atau 'n' untuk tidak.{WHITE}")

    nama_akun_display_terkini, _ = mxx_fetch_info()

    tampilkan_detail_transaksi(
        nama_akun_display_terkini if nama_akun_display_terkini else (nama_baru if berhasil else nama_untuk_prompt_sebelum),
        None, None, None, berhasil,
        jenis_transaksi_override="Ganti Nama Akun",
        nama_sebelum_ganti=nama_untuk_prompt_sebelum,
        nama_sesudah_ganti=nama_aktual_setelah_operasi if berhasil else nama_untuk_prompt_sebelum
    )

def format_expiry_for_display(expiry_info):
    try:
        if "(" in expiry_info and expiry_info.endswith(")"):
            parts = expiry_info.rsplit("(", 1)
            date_part = parts[0].strip()
            days_part = "(" + parts[1]
            return date_part, days_part
        else:
            return expiry_info, None
    except Exception:
        return expiry_info, None

def display_main_info_and_logo():
    global USER_LICENSE_NAME, USER_LICENSE_EXPIRY_INFO, DEVICE_ID_INFO
    os.system('clear')
    ketik(logo2_upper_part, d=0.0001)

    expiry_date_part, expiry_days_part_raw = format_expiry_for_display(USER_LICENSE_EXPIRY_INFO)

    actual_content_width = 49
    border_fill_main = "═" * actual_content_width
    separator_fill_main = "─" * actual_content_width

    expiry_line_2_content = ""
    if expiry_days_part_raw:
        line_payload_str = f"{WHITE}{' ' *19}{BLACK}»----{WHITE}➤ {green}{expiry_days_part_raw}"
        v_payload = get_visual_length(line_payload_str)
        padding_needed = actual_content_width - v_payload
        padding_str = " " * max(0, padding_needed)
        expiry_line_2_content = f"{line_payload_str}{padding_str}"
    else:
        expiry_line_2_content = " " * actual_content_width

    expiry_line_2_str = f"{PURPLE}║{expiry_line_2_content}{PURPLE}║"

    info_pembuat = f"""
{PURPLE}╔{border_fill_main}╗
{PURPLE}║{RED}【{WHITE}✦{RED}】{YELLOW}𝗡𝗔𝗠𝗔          {BLACK}»----{WHITE}➤ {green}{USER_LICENSE_NAME.ljust(23)}{PURPLE}║
{PURPLE}║{RED}【{WHITE}✦{RED}】{YELLOW}𝗞𝗘𝗗𝗔𝗟𝗨𝗔𝗥𝗦𝗔    {BLACK}»----{WHITE}➤ {green}{expiry_date_part.ljust(23)}{PURPLE}║
{expiry_line_2_str}
{PURPLE}║{RED}【{WHITE}✦{RED}】{YELLOW}𝗜𝗗 𝗟𝗜𝗦𝗘𝗡𝗦𝗜    {BLACK}»----{WHITE}➤ {green}{DEVICE_ID_INFO.ljust(23)}{PURPLE}║
{PURPLE}╟{separator_fill_main}╢{WHITE}
{PURPLE}║{RED}【{WHITE}✦{RED}】{YELLOW}𝗣𝗘𝗠𝗜𝗟𝗜𝗞       {BLACK}»----{WHITE}➤ {green}{"𝗥𝗘𝗩𝗔𝗡 𝗦𝗧𝗢𝗥𝗘".ljust(23)}{PURPLE}║
{PURPLE}║{RED}【{WHITE}✦{RED}】{YELLOW}𝗪𝗛𝗔𝗧𝗦𝗔𝗣𝗣      {BLACK}»----{WHITE}➤ {green}{"089520418604".ljust(23)}{PURPLE}║
{PURPLE}║{RED}【{WHITE}✦{RED}】{YELLOW}𝗧𝗘𝗟𝗘𝗚𝗥𝗔𝗠      {BLACK}»----{WHITE}➤ {green}{"𝘁.𝗺𝗲/𝗢𝗿𝗮𝗻𝗴".ljust(23)}{PURPLE}║
{PURPLE}║{RED}【{WHITE}✦{RED}】{YELLOW}𝗖𝗛𝗔𝗡𝗡𝗘𝗟 𝗬𝗧    {BLACK}»----{WHITE}➤ {green}{"𝗥𝗘𝗩𝗔𝗡 𝗦𝗧𝗢𝗥𝗘".ljust(23)}{PURPLE}║
{PURPLE}╚{border_fill_main}╝"""
    ketik(info_pembuat, d=0.0001)
    mxx_display_info()

def menus():
   menu_text = f'''{PURPLE}╔════════════════════════════════════════╗
{PURPLE}║          {YELLOW}MENU TOP UP SALDO{PURPLE}             ║
{PURPLE}╟────────────────────────────────────────╢{WHITE}
{PURPLE}║{RED}【{WHITE}𝟭{RED}】{YELLOW}  𝗧𝗢𝗣𝗨𝗣 𝗨𝗔𝗡𝗚    𝟱𝟬𝗝𝗧   ➤  {WHITE}【{RED} 𝗩𝗜𝗣 {WHITE}】{PURPLE}║
{PURPLE}║{RED}【{WHITE}𝟮{RED}】{YELLOW}  𝗧𝗢𝗣𝗨𝗣 𝗨𝗔𝗡𝗚    𝟳𝟬𝗝𝗧   ➤  {WHITE}【{RED} 𝗩𝗜𝗣 {WHITE}】{PURPLE}║
{PURPLE}║{RED}【{WHITE}𝟯{RED}】{YELLOW}  𝗧𝗢𝗣𝗨𝗣 𝗨𝗔𝗡𝗚   𝟭𝟱𝟬𝗝𝗧   ➤  {WHITE}【{RED} 𝗩𝗜𝗣 {WHITE}】{PURPLE}║
{PURPLE}║{RED}【{WHITE}𝟰{RED}】{YELLOW}  𝗧𝗢𝗣𝗨𝗣 𝗨𝗔𝗡𝗚   𝟮𝟱𝟬𝗝𝗧   ➤  {WHITE}【{RED} 𝗩𝗜𝗣 {WHITE}】{PURPLE}║
{PURPLE}║{RED}【{WHITE}𝟱{RED}】{YELLOW}  𝗧𝗢𝗣𝗨𝗣 𝗨𝗔𝗡𝗚   𝟯𝟱𝟬𝗝𝗧   ➤  {WHITE}【{RED} 𝗩𝗜𝗣 {WHITE}】{PURPLE}║
{PURPLE}║{RED}【{WHITE}𝟲{RED}】{YELLOW}  𝗧𝗢𝗣𝗨𝗣 𝗨𝗔𝗡𝗚   𝟱𝟬𝟬𝗝𝗧   ➤  {WHITE}【{RED} 𝗩𝗜𝗣 {WHITE}】{PURPLE}║
{PURPLE}║{RED}【{WHITE}𝟳{RED}】{YELLOW}  𝗧𝗢𝗣𝗨𝗣 𝗨𝗔𝗡𝗚   𝟲𝟬𝟬𝗝𝗧   ➤  {WHITE}【{RED} 𝗩𝗜𝗣 {WHITE}】{PURPLE}║
{PURPLE}║{RED}【{WHITE}𝟴{RED}】{YELLOW}  𝗧𝗢𝗣𝗨𝗣 𝗨𝗔𝗡𝗚   𝟳𝟬𝟬𝗝𝗧   ➤  {WHITE}【{RED} 𝗩𝗜𝗣 {WHITE}】{PURPLE}║
{PURPLE}║{RED}【{WHITE}𝟵{RED}】{YELLOW}  𝗧𝗢𝗣𝗨𝗣 𝗨𝗔𝗡𝗚   𝟴𝟬𝟬𝗝𝗧   ➤  {WHITE}【{RED} 𝗩𝗜𝗣 {WHITE}】{PURPLE}║
{PURPLE}║{RED}【{WHITE}𝟭𝟬{RED}】{YELLOW} 𝗧𝗢𝗣𝗨𝗣 𝗨𝗔𝗡𝗚   𝟵𝟬𝟬𝗝𝗧   ➤  {WHITE}【{RED} 𝗩𝗜𝗣 {WHITE}】{PURPLE}║
{PURPLE}║{RED}【{WHITE}𝟭𝟭{RED}】{YELLOW} 𝗧𝗢𝗣𝗨𝗣 𝗨𝗔𝗡𝗚      𝟭𝗠   ➤  {WHITE}【{RED} 𝗩𝗜𝗣 {WHITE}】{PURPLE}║
{PURPLE}║{RED}【{WHITE}𝟭𝟮{RED}】{YELLOW} 𝗧𝗢𝗣𝗨𝗣 𝗨𝗔𝗡𝗚    𝟭,𝟯𝗠   ➤  {WHITE}【{RED} 𝗩𝗜𝗣 {WHITE}】{PURPLE}║
{PURPLE}║{RED}【{WHITE}𝟭𝟯{RED}】{YELLOW} 𝗧𝗢𝗣𝗨𝗣 𝗨𝗔𝗡𝗚    𝟭,𝟲𝗠   ➤  {WHITE}【{RED} 𝗩𝗜𝗣 {WHITE}】{PURPLE}║
{PURPLE}║{RED}【{WHITE}𝟭𝟰{RED}】{YELLOW} 𝗧𝗢𝗣𝗨𝗣 𝗨𝗔𝗡𝗚    𝟭,𝟴𝗠   ➤  {WHITE}【{RED} 𝗩𝗜𝗣 {WHITE}】{PURPLE}║
{PURPLE}║{RED}【{WHITE}𝟭𝟱{RED}】{YELLOW} 𝗧𝗢𝗣𝗨𝗣 𝗨𝗔𝗡𝗚      𝟮𝗠   ➤  {WHITE}【{RED} 𝗩𝗜𝗣 {WHITE}】{PURPLE}║
{PURPLE}║{RED}【{WHITE}𝟭𝟲{RED}】{YELLOW} 𝗖𝗨𝗦𝗧𝗢𝗠 𝗧𝗢𝗣𝗨𝗣         {YELLOW}➤  {WHITE}【{RED} 𝗩𝗜𝗣 {WHITE}】{PURPLE}║
{PURPLE}╟────────────────────────────────────────╢{WHITE}
{PURPLE}║           {YELLOW}MENU KURAS SALDO{PURPLE}             ║
{PURPLE}╟────────────────────────────────────────╢{WHITE}
{PURPLE}║{RED}【{WHITE}𝟭𝟳{RED}】{RED} 𝗞𝗨𝗥𝗔𝗦          𝟱𝗝𝗧   {YELLOW}➤  {WHITE}【{RED} 𝗩𝗜𝗣 {WHITE}】{PURPLE}║
{PURPLE}║{RED}【{WHITE}𝟭𝟴{RED}】{RED} 𝗞𝗨𝗥𝗔𝗦         𝟭𝟬𝗝𝗧   {YELLOW}➤  {WHITE}【{RED} 𝗩𝗜𝗣 {WHITE}】{PURPLE}║
{PURPLE}║{RED}【{WHITE}𝟭𝟵{RED}】{RED} 𝗞𝗨𝗥𝗔𝗦         𝟱𝟬𝗝𝗧   {YELLOW}➤  {WHITE}【{RED} 𝗩𝗜𝗣 {WHITE}】{PURPLE}║
{PURPLE}║{RED}【{WHITE}𝟮𝟬{RED}】{RED} 𝗞𝗨𝗥𝗔𝗦        𝟭𝟬𝟬𝗝𝗧   {YELLOW}➤  {WHITE}【{RED} 𝗩𝗜𝗣 {WHITE}】{PURPLE}║
{PURPLE}║{RED}【{WHITE}𝟮𝟭{RED}】{RED} 𝗞𝗨𝗥𝗔𝗦           𝟭𝗠   {YELLOW}➤  {WHITE}【{RED} 𝗩𝗜𝗣 {WHITE}】{PURPLE}║
{PURPLE}║{RED}【{WHITE}𝟮𝟮{RED}】{RED} 𝗞𝗨𝗥𝗔𝗦         𝟭,𝟱𝗠   {YELLOW}➤  {WHITE}【{RED} 𝗩𝗜𝗣 {WHITE}】{PURPLE}║
{PURPLE}║{RED}【{WHITE}𝟮𝟯{RED}】{RED} 𝗞𝗨𝗥𝗔𝗦           𝟮𝗠   {YELLOW}➤  {WHITE}【{RED} 𝗩𝗜𝗣 {WHITE}】{PURPLE}║
{PURPLE}║{RED}【{WHITE}𝟮𝟰{RED}】{RED} 𝗖𝗨𝗦𝗧𝗢𝗠 𝗞𝗨𝗥𝗔𝗦         {YELLOW}➤  {WHITE}【{RED} 𝗩𝗜𝗣 {WHITE}】{PURPLE}║
{PURPLE}║{RED}【{WHITE}𝟮𝟱{RED}】{RED} 𝗞𝗨𝗥𝗔𝗦 𝗦𝗘𝗠𝗨𝗔 𝗨𝗔𝗡𝗚     {YELLOW}➤  {WHITE}【{RED} 𝗩𝗜𝗣 {WHITE}】{PURPLE}║
{PURPLE}╟────────────────────────────────────────╢{WHITE}
{PURPLE}║               {YELLOW}MENU AKUN{PURPLE}                ║
{PURPLE}╟────────────────────────────────────────╢{WHITE}
{PURPLE}║{RED}【{WHITE}𝟮𝟲{RED}】{RED} 𝗛𝗔𝗣𝗨𝗦 𝗔𝗞𝗨𝗡           {YELLOW}➤  {WHITE}【{RED} 𝗩𝗜𝗣 {WHITE}】{PURPLE}║
{PURPLE}║{RED}【{WHITE}𝟮𝟳{RED}】{YELLOW} 𝗚𝗔𝗡𝗧𝗜 𝗡𝗔𝗠𝗔 𝗔𝗞𝗨𝗡      {YELLOW}➤  {WHITE}【{RED} 𝗩𝗜𝗣 {WHITE}】{PURPLE}║
{PURPLE}╟────────────────────────────────────────╢{WHITE}
{PURPLE}║{RED}【{WHITE}𝟬{RED}】{YELLOW}  𝗕𝗔𝗧𝗔𝗟 / 𝗞𝗘𝗟𝗨𝗔𝗥       ➤  {WHITE}【{RED}  !  {WHITE}】{PURPLE}║
{PURPLE}╚════════════════════════════════════════╝
'''
   ketik(menu_text, d=0.0001)

def input_nominal(minus=False):
    while True:
        prompt_text = f"{RED}【{WHITE}✦{RED}】{YELLOW}𝗡𝗢𝗠𝗜𝗡𝗔𝗟 {'PENGURANGAN' if minus else 'TOP UP'}?{WHITE}: "
        nominal_input = input(prompt_text).strip()
        if nominal_input.isdigit():
            value = int(nominal_input)
            if value <= 0:
                 ketik(f"\n{PURPLE}[{YELLOW}◆{PURPLE}]{RED}Nominal harus lebih besar dari 0!{WHITE}\n", d=0.002)
                 continue
            return -value if minus else value
        ketik(f"\n{PURPLE}[{YELLOW}◆{PURPLE}]{RED}Harap masukkan nominal angka yang valid!{WHITE}\n", d=0.002)

def input_jumlah():
    while True:
        jumlah_input = input(f"\n{RED}【{WHITE}✦{RED}】{YELLOW}𝗝𝗨𝗠𝗟𝗔𝗛 PROSES:{RED} ").strip()
        if jumlah_input.isdigit():
            value = int(jumlah_input)
            if value > 0:
                return value
            else:
                ketik(f"\n{PURPLE}[{YELLOW}◆{PURPLE}]{RED}Jumlah proses harus lebih besar dari 0!{WHITE}\n", d=0.002)
        ketik(f"\n{PURPLE}[{YELLOW}◆{PURPLE}]{RED}Harap masukkan jumlah angka yang valid!{WHITE}\n", d=0.002)

def ask_continue_or_exit():
    while True:
        pilihan_lanjut = input(f"{PURPLE}[{WHITE}◆{PURPLE}] {YELLOW}Apakah Anda ingin melanjutkan (y) atau berhenti (n)?{WHITE} ").strip().lower()
        if pilihan_lanjut == 'y':
            return True
        elif pilihan_lanjut == 'n':
            return False
        else:
            ketik(f"{PURPLE}[{YELLOW}◆{PURPLE}]{RED}Pilihan tidak valid. Masukkan 'y' atau 'n'.{WHITE}")

def main():
    global Brp, auth_input

    ketik(logo1,d=0.00001)
    license_check()

    while True:
        auth_input_local = input(f"\n{PURPLE}[{WHITE}◆{PURPLE}] {PURPLE}𝗠𝗮𝘀𝘂𝗸𝗮𝗻 𝗱𝗲𝘃𝗶𝗰𝗲 𝗶𝗱 / 𝗫-𝗔𝘂𝘁𝗵 :{RED} ").strip()
        if not auth_input_local:
            ketik(f"\n{PURPLE}[{YELLOW}◆{PURPLE}] {RED}Error: Anda harus memasukkan Device ID atau X-Authorization.")
            continue
        auth_input = auth_input_local
        break

    if not login():
        ketik(f"{RED}Login Gagal. Program akan berhenti.{WHITE}")
        return

    while True:
        display_main_info_and_logo()
        menus()

        pilihan = input(f'''{PURPLE}╭­\x1b[1;33;41m\x1b[1;37m✦ 𝐏𝐈𝐋𝐈𝐇 ✦\x1b[1;33m\x1b[0m\x1b[{PURPLE}
╰───{RED}▶ ''').strip()

        jum = 1
        Brp = 0

        options_map = {
            "1": 50000000, "2": 70000000, "3": 150000000, "4": 250000000,
            "5": 350000000, "6": 500000000, "7": 600000000, "8": 700000000,
            "9": 800000000, "10": 900000000, "11": 1000000000, "12": 1300000000,
            "13": 1600000000, "14": 1800000000, "15": 2147483647,
            "17": -5000000, "18": -10000000, "19": -50000000, "20": -100000000,
            "21": -1000000000, "22": -1500000000, "23": -2147483647
        }

        no_input_jumlah_values = [
            1000000000, 1300000000, 1600000000, 1800000000, 2147483647,
            -1000000000, -1500000000, -2147483647
        ]

        if pilihan == "0":
            ketik(f"\n{PURPLE}[{YELLOW}◆{PURPLE}]{green}Terima kasih telah menggunakan script ini. Sampai jumpa!{WHITE}\n", d=0.002)
            break

        elif pilihan in options_map:
            Brp = options_map[pilihan]
            if Brp not in no_input_jumlah_values:
                jum = input_jumlah()
            else:
                jum = 1
            if jum > 0 :
                Gas(jum)
        elif pilihan == "16":
            Brp = input_nominal()
            jum = input_jumlah()
            if jum > 0 :
                 Gas(jum)
        elif pilihan == "24":
            Brp = input_nominal(minus=True)
            jum = input_jumlah()
            if jum > 0 :
                Gas(jum)
        elif pilihan == "25":
            kuras_semua_uang()
        elif pilihan == "26":
            if HapusAkun():
                ketik(f"\n{RED}【{WHITE}✦{RED}】{green}Proses penghapusan akun selesai.{WHITE}")
                ketik(f"{YELLOW}Karena akun mungkin telah dihapus, disarankan untuk keluar.{WHITE}")
                if not ask_continue_or_exit():
                    break
                else:
                    ketik(f"{YELLOW}Silakan jalankan ulang script untuk login dengan akun lain jika akun ini sudah terhapus.{WHITE}")
            else:
                ketik(f"\n{RED}【{WHITE}✦{RED}】{YELLOW}Proses penghapusan akun tidak berhasil sepenuhnya atau dibatalkan pengguna.{WHITE}")
        elif pilihan == "27":
            ganti_nama_akun()
        else:
            ketik(f"{PURPLE}[{YELLOW}◆{PURPLE}]{RED}Pilihan tidak valid! Silakan coba lagi.{WHITE}\n", d=0.002)
            time.sleep(1)
            continue

        if not ask_continue_or_exit():
            ketik(f"\n{PURPLE}[{YELLOW}◆{PURPLE}]{green}Terima kasih telah menggunakan script ini. Sampai jumpa!{WHITE}\n", d=0.002)
            break

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        if _ketik_active:
            ketik(f'\n{PURPLE}[{RED}!{PURPLE}]{RED} Program dihentikan paksa oleh pengguna....!!!!\n', d=0.002)
    except SystemExit:
        pass
    except Exception as e:
        if _ketik_active:
            ketik(f'\n{RED}Terjadi kesalahan tidak terduga: {e}\n', d=0.002)
    finally:
        if _ketik_active:
            ketik(f'{PURPLE}Program Selesai.{WHITE}', d=0.002)