import customtkinter as ctk 
import tkinter as tk 
from tkinter import filedialog, messagebox, scrolledtext 
import os
import pandas as pd
import shutil
from PIL import Image 
import re 
# import requests # Tidak perlu requests di sini lagi, launcher yang menangani update
# import sys # Tidak perlu sys untuk update, tapi bisa dipakai untuk sys.executable jika dibutuhkan
# import subprocess # Tidak perlu subprocess untuk update

# --- Konfigurasi Tampilan CustomTkinter ---
ctk.set_appearance_mode("System")  # Modes: "System" (default), "Dark", "Light")
ctk.set_default_color_theme("blue")  # Themes: "blue" (default), "green", "dark-blue")

# --- Konfigurasi Aplikasi Utama ---
# Ini adalah versi aplikasi yang ada di file ini.
# Sesuaikan ini setiap kali Anda membuat perubahan besar pada kode dan mengunggahnya ke GitHub.
CURRENT_VERSION = "1.0.0" 

# --- Kelas Utama Aplikasi (GUI) ---
class SKURenamerApp(ctk.CTk): 
    def __init__(self):
        super().__init__() 

        self.title(f"SKU Renamer Tool v{CURRENT_VERSION}") # Tampilkan versi di judul
        self.geometry("780x750") 
        self.resizable(False, False)

        self.source_folder_path = ctk.StringVar(value="")
        self.excel_file_path = ctk.StringVar(value="")
        self.separator_choice = ctk.StringVar(value="hyphen") 
        self.enable_flexible_old_pattern = ctk.BooleanVar(value=False) 

        self.create_widgets()
        # self.check_for_updates() # <--- HAPUS BARIS INI! Launcher yang akan mengecek update.

    def create_widgets(self):
        # Frame untuk pemilihan folder sumber
        source_folder_frame = ctk.CTkFrame(self) 
        source_folder_frame.pack(pady=10, padx=10, fill="x")

        ctk.CTkLabel(source_folder_frame, text="Pilih Folder:").pack(side="left", padx=5, pady=5) 
        self.source_folder_entry = ctk.CTkEntry(source_folder_frame, textvariable=self.source_folder_path, width=50, state="readonly") 
        self.source_folder_entry.pack(side="left", padx=5, pady=5, expand=True, fill="x")
        ctk.CTkButton(source_folder_frame, text="Telusuri", command=self.browse_source_folder).pack(side="left", padx=5, pady=5) 

        # Frame untuk pemilihan file Excel
        excel_file_frame = ctk.CTkFrame(self) 
        excel_file_frame.pack(pady=10, padx=10, fill="x")

        ctk.CTkLabel(excel_file_frame, text="Pilih File Excel:").pack(side="left", padx=5, pady=5) 
        self.excel_file_entry = ctk.CTkEntry(excel_file_frame, textvariable=self.excel_file_path, width=50, state="readonly") 
        self.excel_file_entry.pack(side="left", padx=5, pady=5, expand=True, fill="x")
        ctk.CTkButton(excel_file_frame, text="Telusuri", command=self.browse_excel_file).pack(side="left", padx=5, pady=5) 

        # Frame untuk pilihan pola pemisah dan pola lama fleksibel
        options_frame = ctk.CTkFrame(self) 
        options_frame.pack(pady=10, padx=10, fill="x")

        # Pola pemisah baru
        separator_subframe = ctk.CTkFrame(options_frame) 
        separator_subframe.pack(side="left", padx=5, pady=5, fill="y")
        ctk.CTkLabel(separator_subframe, text="Pola Pemisah Nama File Baru:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=(5,0)) 
        ctk.CTkRadioButton(separator_subframe, text="Hyphen ( - )", variable=self.separator_choice, value="hyphen",
                           command=lambda: self.log_message("Pola pemisah baru diatur ke: Hyphen (-)")).pack(anchor="w", padx=10, pady=2) 
        ctk.CTkRadioButton(separator_subframe, text="Underscore ( _ )", variable=self.separator_choice, value="underscore",
                           command=lambda: self.log_message("Pola pemisah baru diatur ke: Underscore (_)")).pack(anchor="w", padx=10, pady=2) 
        
        # Checkbox untuk pola lama fleksibel
        flexible_pattern_subframe = ctk.CTkFrame(options_frame) 
        flexible_pattern_subframe.pack(side="left", padx=5, pady=5, fill="y", expand=True)
        ctk.CTkLabel(flexible_pattern_subframe, text="Deteksi Pola Nama Lama Fleksibel:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=(5,0)) 
        ctk.CTkCheckBox(flexible_pattern_subframe, text="Aktifkan deteksi: SKU1.jpg, SKU(1).jpg, dll.", 
                       variable=self.enable_flexible_old_pattern,
                       command=self.toggle_flexible_pattern_info).pack(anchor="w", padx=10, pady=5) 
        ctk.CTkLabel(flexible_pattern_subframe, text="Jika nonaktif, hanya SKU_1.jpg atau SKU-1.jpg yang dideteksi.", wraplength=250, justify="left").pack(anchor="w", padx=10)


        # Tombol Mulai Renaming dan Update (Hapus tombol Cek Update di sini)
        start_button_frame = ctk.CTkFrame(self) 
        start_button_frame.pack(pady=10, padx=10, fill="x")
        ctk.CTkButton(start_button_frame, text="Mulai Renaming", command=self.start_renaming_process, font=ctk.CTkFont(size=14, weight="bold")).pack(expand=True, padx=5, pady=5) 
        # ctk.CTkButton(start_button_frame, text="Cek Update", command=self.check_for_updates, font=ctk.CTkFont(size=14)).pack(side="right", expand=True, padx=(5,0), pady=5)

        # Frame untuk Log Aktivitas
        log_frame = ctk.CTkFrame(self) 
        log_frame.pack(pady=10, padx=10, fill="both", expand=True)
        
        current_appearance_mode = ctk.get_appearance_mode()
        if current_appearance_mode == "Dark":
            log_bg_color = "#2b2b2b"  
            log_fg_color = "#ffffff"  
        else:
            log_bg_color = "#ffffff"  
            log_fg_color = "#000000"  

        self.log_text = scrolledtext.ScrolledText(log_frame, height=15, state="disabled", wrap=tk.WORD,
                                                  bg=log_bg_color,
                                                  fg=log_fg_color,
                                                  insertbackground=log_fg_color) 
        self.log_text.pack(padx=5, pady=5, fill="both", expand=True)
        
    def toggle_flexible_pattern_info(self):
        if self.enable_flexible_old_pattern.get():
            self.log_message("Deteksi pola nama lama fleksibel AKTIF. Akan mencoba mencari nomor gambar setelah nama SKU, terlepas dari pemisah (contoh: SKU1.jpg, SKU(1).jpg).")
        else:
            self.log_message("Deteksi pola nama lama fleksibel NONAKTIF. Hanya pola SKU_N.jpg atau SKU-N.jpg yang akan dideteksi.", "info")


    def log_message(self, message, message_type="info"):
        self.log_text.config(state="normal")
        if message_type == "info":
            self.log_text.insert(tk.END, f"[INFO] {message}\n", "info")
        elif message_type == "success":
            self.log_text.insert(tk.END, f"[SUKSES] {message}\n", "success")
        elif message_type == "warning":
            self.log_text.insert(tk.END, f"[PERINGATAN] {message}\n", "warning")
        elif message_type == "error":
            self.log_text.insert(tk.END, f"[ERROR] {message}\n", "error")
        self.log_text.see(tk.END) 
        self.log_text.config(state="disabled")

        self.log_text.tag_config("info", foreground="black")
        self.log_text.tag_config("success", foreground="green")
        self.log_text.tag_config("warning", foreground="orange")
        self.log_text.tag_config("error", foreground="red")


    def browse_source_folder(self):
        folder_selected = filedialog.askdirectory() 
        if folder_selected:
            self.source_folder_path.set(folder_selected)
            self.log_message(f"Folder Sumber diatur: {folder_selected}")

    def browse_excel_file(self):
        file_selected = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx *.xls")]) 
        if file_selected:
            self.excel_file_path.set(file_selected)
            self.log_message(f"File Excel diatur: {file_selected}")

    def start_renaming_process(self):
        source_folder = self.source_folder_path.get()
        excel_file = self.excel_file_path.get()
        selected_separator = "-" if self.separator_choice.get() == "hyphen" else "_"
        enable_flexible_pattern = self.enable_flexible_old_pattern.get() 

        if not source_folder or not os.path.isdir(source_folder):
            messagebox.showerror("Error", "Silakan pilih folder sumber yang valid.") 
            self.log_message("Proses dibatalkan: Folder sumber tidak valid.", "error")
            return

        if not excel_file or not os.path.isfile(excel_file):
            messagebox.showerror("Error", "Silakan pilih file Excel yang valid.") 
            self.log_message("Proses dibatalkan: File Excel tidak valid.", "error")
            return
        
        confirmed = messagebox.askyesno("Konfirmasi Renaming & Konversi",
                                        "Anda akan memulai proses renaming dan MUNGKIN KONVERSI FORMAT gambar.\n"
                                        "PASTIKAN ANDA SUDAH MEMBUAT BACKUP data Anda.\n\n"
                                        "Lanjutkan?") 
        if not confirmed:
            self.log_message("Proses renaming dibatalkan oleh pengguna.", "warning")
            return

        self.log_message("Memulai proses renaming...", "info")
        self.log_text.config(state="normal")
        self.log_text.delete("1.0", tk.END) 
        self.log_text.config(state="disabled")

        try:
            df = pd.read_excel(excel_file)
            required_cols = ['SKU_LAMA', 'SKU_BARU'] 
            if not all(col in df.columns for col in required_cols):
                messagebox.showerror("Error Excel", f"File Excel harus memiliki kolom: {', '.join(required_cols)}.")
                self.log_message("Proses dibatalkan: Kolom Excel tidak sesuai.", "error")
                return

            renamed_folder_count = 0
            for index, row in df.iterrows():
                old_sku = str(row['SKU_LAMA']).strip()
                new_sku = str(row['SKU_BARU']).strip()
                
                new_extension_from_excel = str(row['EKSTENSI_BARU']).strip().lower() if 'EKSTENSI_BARU' in df.columns and pd.notna(row['EKSTENSI_BARU']) else ""
                if new_extension_from_excel and not new_extension_from_excel.startswith('.'):
                    new_extension_from_excel = '.' + new_extension_from_excel

                if not old_sku or not new_sku:
                    self.log_message(f"Baris {index + 2}: 'SKU_LAMA' atau 'SKU_BARU' kosong, dilewati.", "warning")
                    continue

                # Cek dulu folder SKU utama
                old_sku_folder_path = os.path.join(source_folder, old_sku)
                
                # --- BAGIAN BARU: Proses file yang langsung ada di dalam source_folder ---
                # Memproses file di root source_folder yang namanya cocok dengan old_sku
                # Menggunakan os.listdir untuk menghindari os.walk yang akan masuk ke subfolder yang mungkin tidak relevan
                for filename in os.listdir(source_folder):
                    file_full_path = os.path.join(source_folder, filename)
                    # Hanya proses file yang diawali dengan old_sku
                    if os.path.isfile(file_full_path) and filename.lower().startswith(old_sku.lower()):
                         self._process_single_file(file_full_path, old_sku, new_sku, selected_separator, new_extension_from_excel, enable_flexible_pattern)
                # --- AKHIR BAGIAN BARU ---

                # Proses folder SKU dan isinya
                if os.path.isdir(old_sku_folder_path):
                    self.log_message(f"Memproses folder SKU: '{old_sku}' -> '{new_sku}'", "info") 
                    
                    for root, _, files in os.walk(old_sku_folder_path):
                        for filename in files:
                            old_file_path = os.path.join(root, filename)
                            self._process_single_file(old_file_path, old_sku, new_sku, selected_separator, new_extension_from_excel, enable_flexible_pattern)

                    # Setelah semua file di dalam folder SKU diproses, baru rename foldernya
                    new_sku_folder_path = os.path.join(source_folder, new_sku)
                    if os.path.exists(new_sku_folder_path) and new_sku_folder_path != old_sku_folder_path:
                        self.log_message(f"  PERINGATAN: Folder tujuan '{new_sku}' sudah ada. Melewati renaming folder '{old_sku}'.", "warning")
                    else:
                        try:
                            os.rename(old_sku_folder_path, new_sku_folder_path)
                            self.log_message(f"  Folder SKU '{old_sku}' berhasil diubah menjadi '{new_sku}'", "success")
                            renamed_folder_count += 1
                        except Exception as e:
                            self.log_message(f"  ERROR mengubah nama folder '{old_sku}': {e}", "error")
                else:
                    self.log_message(f"Folder SKU '{old_sku}' tidak ditemukan di '{source_folder}'. Akan mencari file SKU di root folder saja jika ada.", "warning")
            
            messagebox.showinfo("Renaming Selesai", f"Proses renaming selesai! {renamed_folder_count} folder SKU berhasil diubah namanya.")
            self.log_message(f"PROSES RENAMING SELESAI. Total {renamed_folder_count} folder SKU berhasil diubah namanya.", "info")

        except FileNotFoundError:
            messagebox.showerror("Error", "File Excel tidak ditemukan. Pastikan jalur sudah benar.")
            self.log_message("Proses dibatalkan: File Excel tidak ditemukan.", "error")
        except pd.errors.EmptyDataError:
            messagebox.showerror("Error", "File Excel kosong atau tidak ada data.")
            self.log_message("Proses dibatalkan: File Excel kosong.", "error")
        except Exception as e:
            messagebox.showerror("Error", f"Terjadi kesalahan yang tidak terduga: {e}") # Menggunakan messagebox
            self.log_message(f"Terjadi kesalahan yang tidak terduga: {e}", "error") # Menggunakan log_message

    # --- FUNGSI BARU: Memproses satu file (dipisah agar kodenya bersih) ---
    def _process_single_file(self, file_path, old_sku, new_sku, selected_separator, new_extension_from_excel, enable_flexible_pattern):
        filename = os.path.basename(file_path) # Ambil hanya nama file dari jalur lengkap
        
        # Cek apakah ini file gambar
        if os.path.isfile(file_path) and filename.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp')):
            name_without_ext, current_extension = os.path.splitext(filename) 
            
            image_number = None
            
            if enable_flexible_pattern:
                # Regex yang lebih kuat:
                flexible_pattern_regex = re.escape(old_sku) + r'(?:[-_()]?\s*|\s*)?(\d+)(?:\)\s*)?$'
                match = re.match(flexible_pattern_regex, name_without_ext, re.IGNORECASE)
                
                if match:
                    image_number = match.group(1) 
                elif name_without_ext.lower() == old_sku.lower(): 
                    image_number = "" 
            else: # Logika lama (hanya _ atau - yang diikuti nomor)
                if name_without_ext.startswith(old_sku + '_'):
                    suffix = name_without_ext[len(old_sku) + 1:] 
                    if suffix.isdigit():
                        image_number = suffix
                elif name_without_ext.startswith(old_sku + '-'):
                    suffix = name_without_ext[len(old_sku) + 1:] 
                    if suffix.isdigit():
                        image_number = suffix
                elif name_without_ext == old_sku: 
                    image_number = "" 
                    self.log_message(f"    File '{filename}' cocok dengan SKU lama tanpa nomor.", "info")
            
            if image_number is None: # Jika tidak ada pola yang cocok sama sekali
                self.log_message(f"    Melewati file: '{filename}' (tidak cocok pola SKU lama yang diharapkan)", "info")
                return # Langsung keluar dari fungsi untuk file ini

            # Tentukan ekstensi baru yang akan digunakan
            final_extension = new_extension_from_excel if new_extension_from_excel else current_extension
            if not final_extension.startswith('.'):
                final_extension = '.' + final_extension
            
            # Bentuk nama file baru
            if image_number != "": 
                new_filename_base = f"{new_sku}{selected_separator}{image_number}" 
            else: 
                new_filename_base = f"{new_sku}"
            
            # Jalur baru di folder file saat ini
            new_file_path = os.path.join(os.path.dirname(file_path), f"{new_filename_base}{final_extension}") 

            # --- Image Conversion and Renaming ---
            if final_extension.lower() != current_extension.lower(): 
                self.log_message(f"    Mengkonversi '{filename}' ke '{final_extension}'...", "info")
                try: 
                    with Image.open(file_path) as img: 
                        if final_extension.lower() in ('.jpg', '.jpeg') and img.mode in ('RGBA', 'P'):
                            img = img.convert('RGB') 
                            self.log_message(f"      Mengkonversi mode gambar ke RGB untuk JPG/JPEG.", "info")
                        elif final_extension.lower() == '.png' and img.mode == 'RGB':
                            img = img.convert('RGBA') 

                        save_options = {}
                        if final_extension.lower() in ('.jpg', '.jpeg', '.webp'):
                            save_options['quality'] = 85 

                        img.save(new_file_path, **save_options) 
                        self.log_message(f"    Konversi '{filename}' ke '{os.path.basename(new_file_path)}' berhasil.", "success")
                        
                        os.remove(file_path) 
                        self.log_message(f"    File lama '{filename}' dihapus.", "info")

                except Exception as e: 
                    self.log_message(f"    ERROR saat mengkonversi '{filename}': {e}", "error")
                    return 
            else: # Jika ekstensi tidak berubah, hanya rename nama file saja
                if file_path != new_file_path: 
                    try: 
                        os.rename(file_path, new_file_path)
                        self.log_message(f"    File '{filename}' diubah menjadi '{os.path.basename(new_file_path)}'", "success")
                    except Exception as e: 
                        self.log_message(f"    ERROR mengubah nama file '{filename}': {e}", "error")
                else:
                    self.log_message(f"    Melewati file: '{filename}' (nama baru sama dengan nama lama)", "info")
        else: # Bukan file gambar atau bukan file
            self.log_message(f"    Melewati item: '{filename}' (bukan file gambar atau bukan file)", "info")

    # --- Bagian Update Otomatis ---
    def check_for_updates(self):
        self.log_message("Mengecek update...")
        try:
            response = requests.get(UPDATE_CHECK_URL, timeout=5)
            response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
            latest_version = response.text.strip()

            if self._version_string_to_tuple(latest_version) > self._version_string_to_tuple(CURRENT_VERSION):
                self.log_message(f"Update tersedia: v{latest_version}. Anda saat ini v{CURRENT_VERSION}.", "warning")
                confirmed = messagebox.askyesno("Update Tersedia", 
                                                f"Versi baru SKU Renamer v{latest_version} tersedia!\n"
                                                f"Anda saat ini menggunakan v{CURRENT_VERSION}.\n"
                                                f"Apakah Anda ingin mengunduh dan menginstal update sekarang?\n\n"
                                                f"(Aplikasi akan menutup dan meluncurkan ulang setelah update.)")
                if confirmed:
                    self.download_and_apply_update(latest_version)
                else:
                    self.log_message("Update dibatalkan oleh pengguna.", "info")
            else:
                self.log_message("Anda sudah menggunakan versi terbaru.", "info")
        except requests.exceptions.RequestException as e:
            self.log_message(f"Gagal mengecek update: {e}", "error")
        except Exception as e:
            self.log_message(f"Terjadi kesalahan saat mengecek update: {e}", "error")

    def _version_string_to_tuple(self, version_string):
        # Mengubah string versi "1.0.0" menjadi tuple (1, 0, 0) untuk perbandingan
        return tuple(map(int, version_string.split('.')))

    def download_and_apply_update(self, latest_version):
        download_url = ""
        if sys.platform == "win32":
            download_url = UPDATE_DOWNLOAD_URL_WINDOWS.format(latest_version=latest_version)
            target_filename = "sku_renamer_windows.exe"
        elif sys.platform == "darwin": # macOS
            download_url = UPDATE_DOWNLOAD_URL_MACOS.format(latest_version=latest_version)
            target_filename = "sku_renamer_macos.zip" # macOS .app usually comes in a .zip

        if not download_url:
            self.log_message("URL unduhan tidak ditemukan untuk sistem operasi Anda.", "error")
            messagebox.showerror("Update Gagal", "URL unduhan tidak ditemukan untuk sistem operasi Anda.")
            return

        self.log_message(f"Mengunduh update dari: {download_url}", "info")
        try:
            response = requests.get(download_url, stream=True, timeout=30)
            response.raise_for_status()
            
            # Mendapatkan path aplikasi yang sedang berjalan
            if getattr(sys, 'frozen', False): # True jika dijalankan dari PyInstaller executable
                app_path = os.path.abspath(sys.executable)
                if sys.platform == "darwin":
                    # For macOS .app bundle, sys.executable points to the executable inside the bundle
                    # We need to find the root of the .app bundle (e.g., sku_renamer.app)
                    # And then its parent directory to save the new zip
                    app_bundle_path = os.path.dirname(os.path.dirname(os.path.dirname(app_path)))
                    download_dir = os.path.dirname(app_bundle_path) # Save zip in parent of .app
                else:
                    download_dir = os.path.dirname(app_path) # For Windows .exe, save in its directory
            else: # Jika dijalankan dari script Python biasa (development mode)
                app_path = os.path.abspath(__file__)
                download_dir = os.path.dirname(app_path)

            temp_update_path = os.path.join(download_dir, f"update_{latest_version}_{os.getpid()}") # Use PID to make it unique
            
            # Simpan file yang diunduh ke lokasi sementara
            with open(temp_update_path + "." + target_filename.split('.')[-1], 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            final_downloaded_path = temp_update_path + "." + target_filename.split('.')[-1]
            self.log_message(f"Update berhasil diunduh ke: {final_downloaded_path}", "success")
            
            self.master.update_idletasks() # Pastikan GUI terupdate
            messagebox.showinfo("Update Selesai", "Update berhasil diunduh. Aplikasi akan menutup untuk instalasi.")
            self.log_message("Menutup aplikasi untuk instalasi update...", "info")

            # --- MELAKUKAN UPDATE SEBENARNYA (Mengganti file) ---
            # Ini memerlukan script eksternal atau cara OS-specific
            updater_script_name = "updater_script.py" # Ubah nama script agar lebih jelas
            updater_script_content = ""
            
            if sys.platform == "win32":
                updater_script_content = f"""
import os, sys, time, shutil, subprocess

# argv[1] = old_exe_path (path aplikasi yang sedang berjalan)
# argv[2] = new_exe_path (path aplikasi baru yang diunduh)

time.sleep(1) # Beri waktu aplikasi lama untuk menutup
try:
    old_exe = sys.argv[1]
    new_exe = sys.argv[2]
    
    # Perulangan untuk memastikan file lama tidak terkunci lagi
    # Mencoba menghapus file lama, jika gagal tunggu sebentar dan coba lagi
    max_retries = 10
    for i in range(max_retries):
        try:
            os.remove(old_exe)
            break # Berhasil menghapus, keluar dari loop
        except OSError as e:
            if i < max_retries - 1:
                time.sleep(0.5) # Tunggu sebentar sebelum mencoba lagi
            else:
                # Gagal setelah semua percobaan, log error dan keluar
                with open(os.path.join(os.path.dirname(old_exe), "update_error.log"), "a") as f:
                    f.write(f"[{time.ctime()}] Failed to remove old exe {old_exe}: {e}\\n")
                sys.exit(1) # Keluar dengan kode error

    os.rename(new_exe, old_exe) # Ganti dengan versi baru
    subprocess.Popen([old_exe]) # Luncurkan aplikasi baru
except Exception as e:
    with open(os.path.join(os.path.dirname(old_exe), "update_error.log"), "a") as f:
        f.write(f"[{time.ctime()}] Windows update script error: {{e}}\\n")
sys.exit()
"""
                updater_script_full_path = os.path.join(download_dir, updater_script_name)
                with open(updater_script_full_path, "w") as f:
                    f.write(updater_script_content)
                
                # Luncurkan script updater menggunakan python.exe dari aplikasi itu sendiri
                # Ini akan membuat updater berjalan di latar belakang setelah aplikasi saat ini ditutup
                subprocess.Popen([sys.executable, updater_script_full_path, app_path, final_downloaded_path], 
                                 creationflags=subprocess.DETACHED_PROCESS if sys.platform == "win32" else 0,
                                 close_fds=True)
                sys.exit(0) # Keluar dari aplikasi saat ini

            elif sys.platform == "darwin": # macOS (perlu unzip dan timpa .app bundle)
                # macOS lebih kompleks karena ini adalah bundle .app
                # Updater script harus berjalan dari luar .app bundle yang sedang di-update
                updater_script_content = f"""
import os, sys, time, shutil, subprocess, zipfile

time.sleep(3) # Beri waktu aplikasi lama untuk menutup
try:
    old_app_bundle_path = sys.argv[1]
    downloaded_zip_path = sys.argv[2]
    
    temp_extract_dir = old_app_bundle_path + "_temp_extract"
    
    if os.path.exists(temp_extract_dir):
        shutil.rmtree(temp_extract_dir)
        
    os.makedirs(temp_extract_dir) # Buat direktori sementara baru

    # Unzip file baru
    with zipfile.ZipFile(downloaded_zip_path, 'r') as zip_ref:
        zip_ref.extractall(temp_extract_dir)

    # Temukan nama folder .app di dalam zip yang diekstrak (misal 'sku_renamer.app')
    # Harusnya hanya ada satu folder .app di root zip
    extracted_app_name = None
    for f in os.listdir(temp_extract_dir):
        if f.lower().endswith('.app') and os.path.isdir(os.path.join(temp_extract_dir, f)):
            extracted_app_name = f
            break
    
    if not extracted_app_name:
        raise Exception("Tidak menemukan .app bundle di dalam zip yang diunduh.")

    extracted_app_path = os.path.join(temp_extract_dir, extracted_app_name)

    # Timpa aplikasi lama
    # Pastikan old_app_bundle_path adalah path ke sku_renamer.app
    if os.path.exists(old_app_bundle_path):
        # Mencoba menghapus aplikasi lama, dengan retry
        max_retries = 10
        for i in range(max_retries):
            try:
                shutil.rmtree(old_app_bundle_path)
                break
            except OSError as e:
                if i < max_retries - 1:
                    time.sleep(0.5)
                else:
                    raise e # Gagal setelah semua percobaan

    shutil.move(extracted_app_path, old_app_bundle_path) # Pindahkan yang baru

    os.remove(downloaded_zip_path) # Hapus zip yang diunduh
    shutil.rmtree(temp_extract_dir) # Hapus direktori sementara

    # Luncurkan aplikasi baru
    subprocess.Popen(['open', old_app_bundle_path])

except Exception as e:
    # Tulis error ke log file di home directory pengguna
    with open(os.path.expanduser("~/sku_renamer_update_error.log"), "a") as f:
        f.write(f"[{time.ctime()}] macOS update script error: {{e}}\\n")
sys.exit()
"""
                # Simpan script updater di direktori tempat aplikasi dijalankan (misal folder 'dist')
                updater_script_full_path = os.path.join(download_dir, updater_script_name)
                with open(updater_script_full_path, "w") as f:
                    f.write(updater_script_content)
                
                # Mendapatkan path ke root bundle .app (misal: /path/to/dist/sku_renamer.app)
                # sys.executable untuk .app bundle ada di Contents/MacOS/executable_name
                app_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(sys.executable))))

                # Jalankan script updater ini menggunakan bash (atau zsh) di Terminal secara terpisah
                # Ini penting agar updater tidak terikat dengan proses aplikasi GUI utama
                # > /dev/null 2>&1 & : untuk menjalankannya di latar belakang dan menyembunyikan outputnya
                subprocess.Popen(['/bin/bash', '-c', 
                                  f'python3 "{updater_script_full_path}" "{app_path}" "{final_downloaded_path}" > /dev/null 2>&1 &'])
                
                sys.exit(0) # Keluar dari aplikasi saat ini

            else:
                self.log_message("Update otomatis tidak didukung di OS ini.", "warning")
                messagebox.showinfo("Update Manual", "Silakan unduh update secara manual dan instal.")
                # Anda bisa membuka browser ke halaman rilis GitHub di sini
                # import webbrowser
                # webbrowser.open(f"https://github.com/YourUsername/YourRepoName/releases/latest")


        except requests.exceptions.RequestException as e:
            self.log_message(f"Gagal mengunduh update: {e}", "error")
            messagebox.showerror("Update Gagal", f"Gagal mengunduh update: {e}")
        except Exception as e:
            self.log_message(f"Terjadi kesalahan tak terduga saat update: {e}", "error")
            messagebox.showerror("Update Gagal", f"Terjadi kesalahan tak terduga saat update: {e}")


# --- Fungsi Utama untuk Menjalankan Aplikasi ---
if __name__ == "__main__":
    app = SKURenamerApp() 
    app.mainloop()