import os
import json
import csv
from datetime import datetime
from typing import Dict, List, Optional

class InventoryItem:
    """Class untuk merepresentasikan item inventori"""
    def __init__(self, nama: str, stok: int, harga: float, item_id: Optional[str] = None):
        self.id = item_id or f"ITM{datetime.now().strftime('%Y%m%d%H%M%S')}"
        self.nama = nama
        self.stok = stok
        self.harga = harga
        self.tanggal_dibuat = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.tanggal_diupdate = self.tanggal_dibuat

    def to_dict(self) -> Dict:
        """Konversi item ke dictionary"""
        return {
            'id': self.id,
            'nama': self.nama,
            'stok': self.stok,
            'harga': self.harga,
            'tanggal_dibuat': self.tanggal_dibuat,
            'tanggal_diupdate': self.tanggal_diupdate
        }

    @classmethod
    def from_dict(cls, data: Dict):
        """Buat item dari dictionary"""
        item = cls(data['nama'], data['stok'], data['harga'], data['id'])
        item.tanggal_dibuat = data.get('tanggal_dibuat', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        item.tanggal_diupdate = data.get('tanggal_diupdate', item.tanggal_dibuat)
        return item

class InventoryManager:
    """Class utama untuk mengelola sistem inventori"""
    
    def __init__(self, data_file: str = "inventory_data.json"):
        self.data_file = data_file
        self.items: Dict[str, InventoryItem] = {}
        self.load_data()

    def load_data(self):
        """Memuat data dari file JSON"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for item_data in data:
                        item = InventoryItem.from_dict(item_data)
                        self.items[item.id] = item
                print(f"✅ Data berhasil dimuat dari {self.data_file}")
            else:
                print(f"📁 File {self.data_file} tidak ditemukan, memulai dengan data kosong")
        except Exception as e:
            print(f"❌ Error memuat data: {e}")

    def save_data(self):
        """Menyimpan data ke file JSON"""
        try:
            data = [item.to_dict() for item in self.items.values()]
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"✅ Data berhasil disimpan ke {self.data_file}")
        except Exception as e:
            print(f"❌ Error menyimpan data: {e}")

    def tambah_barang(self, nama: str, stok: int, harga: float) -> bool:
        """Menambahkan barang baru ke inventori"""
        try:
            # Cek apakah barang dengan nama yang sama sudah ada
            existing_item = self.cari_barang_by_nama(nama)
            if existing_item:
                print(f"⚠️  Barang '{nama}' sudah ada dengan ID {existing_item.id}")
                pilihan = input("Apakah ingin menambah stok barang yang ada? (y/n): ").lower()
                if pilihan == 'y':
                    return self.update_stok(existing_item.id, existing_item.stok + stok)
                return False
            
            item = InventoryItem(nama, stok, harga)
            self.items[item.id] = item
            print(f"✅ Barang '{nama}' berhasil ditambahkan dengan ID: {item.id}")
            self.save_data()
            return True
        except Exception as e:
            print(f"❌ Error menambah barang: {e}")
            return False

    def tampilkan_daftar_barang(self, show_details: bool = True):
        """Menampilkan daftar semua barang"""
        if not self.items:
            print("📦 Inventori kosong")
            return

        print("\n" + "="*80)
        print(f"{'ID':<15} {'NAMA BARANG':<25} {'STOK':<8} {'HARGA':<12} {'TOTAL NILAI':<15}")
        print("="*80)
        
        total_items = 0
        total_nilai = 0
        
        for item in sorted(self.items.values(), key=lambda x: x.nama):
            nilai_item = item.stok * item.harga
            total_items += item.stok
            total_nilai += nilai_item
            
            print(f"{item.id:<15} {item.nama:<25} {item.stok:<8} Rp{item.harga:>9,.0f} Rp{nilai_item:>12,.0f}")
            
            if show_details:
                print(f"{'':>15} Dibuat: {item.tanggal_dibuat} | Diupdate: {item.tanggal_diupdate}")
        
        print("="*80)
        print(f"{'TOTAL':<48} {total_items:<8} {'':>12} Rp{total_nilai:>12,.0f}")
        print("="*80)

    def edit_barang(self, item_id: str) -> bool:
        """Mengedit data barang"""
        if item_id not in self.items:
            print(f"❌ Barang dengan ID '{item_id}' tidak ditemukan")
            return False

        item = self.items[item_id]
        print(f"\n📝 Mengedit barang: {item.nama}")
        print(f"Data saat ini - Nama: {item.nama}, Stok: {item.stok}, Harga: Rp{item.harga:,.0f}")
        
        try:
            nama_baru = input(f"Nama baru (kosongkan untuk tidak mengubah): ").strip()
            if nama_baru:
                item.nama = nama_baru

            stok_input = input(f"Stok baru (kosongkan untuk tidak mengubah): ").strip()
            if stok_input:
                item.stok = int(stok_input)

            harga_input = input(f"Harga baru (kosongkan untuk tidak mengubah): ").strip()
            if harga_input:
                item.harga = float(harga_input)

            item.tanggal_diupdate = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            print(f"✅ Barang berhasil diupdate")
            self.save_data()
            return True
            
        except ValueError as e:
            print(f"❌ Input tidak valid: {e}")
            return False

    def hapus_barang(self, item_id: str) -> bool:
        """Menghapus barang dari inventori"""
        if item_id not in self.items:
            print(f"❌ Barang dengan ID '{item_id}' tidak ditemukan")
            return False

        item = self.items[item_id]
        print(f"⚠️  Akan menghapus barang: {item.nama} (Stok: {item.stok})")
        konfirmasi = input("Yakin ingin menghapus? (y/n): ").lower()
        
        if konfirmasi == 'y':
            del self.items[item_id]
            print(f"✅ Barang '{item.nama}' berhasil dihapus")
            self.save_data()
            return True
        else:
            print("❌ Penghapusan dibatalkan")
            return False

    def cari_barang(self, keyword: str) -> List[InventoryItem]:
        """Mencari barang berdasarkan nama atau ID"""
        results = []
        keyword = keyword.lower()
        
        for item in self.items.values():
            if keyword in item.nama.lower() or keyword in item.id.lower():
                results.append(item)
        
        return results

    def cari_barang_by_nama(self, nama: str) -> Optional[InventoryItem]:
        """Mencari barang berdasarkan nama exact match"""
        for item in self.items.values():
            if item.nama.lower() == nama.lower():
                return item
        return None

    def update_stok(self, item_id: str, stok_baru: int) -> bool:
        """Update stok barang"""
        if item_id not in self.items:
            print(f"❌ Barang dengan ID '{item_id}' tidak ditemukan")
            return False

        item = self.items[item_id]
        stok_lama = item.stok
        item.stok = stok_baru
        item.tanggal_diupdate = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        print(f"✅ Stok '{item.nama}' berhasil diupdate dari {stok_lama} menjadi {stok_baru}")
        self.save_data()
        return True

    def export_to_csv(self, filename: str = None):
        """Export data ke file CSV"""
        if not filename:
            filename = f"inventory_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['ID', 'Nama', 'Stok', 'Harga', 'Total Nilai', 'Tanggal Dibuat', 'Tanggal Diupdate']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                for item in self.items.values():
                    writer.writerow({
                        'ID': item.id,
                        'Nama': item.nama,
                        'Stok': item.stok,
                        'Harga': item.harga,
                        'Total Nilai': item.stok * item.harga,
                        'Tanggal Dibuat': item.tanggal_dibuat,
                        'Tanggal Diupdate': item.tanggal_diupdate
                    })
            
            print(f"✅ Data berhasil diekspor ke {filename}")
            return True
        except Exception as e:
            print(f"❌ Error ekspor data: {e}")
            return False

    def laporan_ringkas(self):
        """Menampilkan laporan ringkas inventori"""
        if not self.items:
            print("📦 Inventori kosong")
            return

        total_items = len(self.items)
        total_stok = sum(item.stok for item in self.items.values())
        total_nilai = sum(item.stok * item.harga for item in self.items.values())
        
        # Item dengan stok terendah
        item_stok_rendah = min(self.items.values(), key=lambda x: x.stok)
        
        # Item dengan nilai tertinggi
        item_nilai_tinggi = max(self.items.values(), key=lambda x: x.stok * x.harga)

        print("\n" + "="*60)
        print("📊 LAPORAN RINGKAS INVENTORI")
        print("="*60)
        print(f"Total Jenis Barang    : {total_items}")
        print(f"Total Stok Keseluruhan: {total_stok}")
        print(f"Total Nilai Inventori : Rp{total_nilai:,.0f}")
        print(f"Rata-rata Nilai/Item  : Rp{total_nilai/total_items:,.0f}")
        print("="*60)
        print(f"Stok Terendah         : {item_stok_rendah.nama} ({item_stok_rendah.stok} unit)")
        print(f"Nilai Tertinggi       : {item_nilai_tinggi.nama} (Rp{item_nilai_tinggi.stok * item_nilai_tinggi.harga:,.0f})")
        print("="*60)

def show_menu():
    """Menampilkan menu utama"""
    print("\n" + "="*50)
    print("🏪 SISTEM MANAJEMEN INVENTORI TOKO KECIL")
    print("="*50)
    print("1. Tambah Barang")
    print("2. Tampilkan Daftar Barang") 
    print("3. Edit Data Barang")
    print("4. Hapus Barang")
    print("5. Cari Barang")
    print("6. Update Stok")
    print("7. Export ke CSV")
    print("8. Laporan Ringkas")
    print("0. Keluar")
    print("="*50)

def main():
    """Fungsi utama aplikasi"""
    print("🚀 Memulai Sistem Manajemen Inventori...")
    inventory = InventoryManager()
    
    while True:
        show_menu()
        
        try:
            pilihan = input("Pilih menu (0-8): ").strip()
            
            if pilihan == '1':
                print("\n➕ TAMBAH BARANG BARU")
                nama = input("Nama barang: ").strip()
                if not nama:
                    print("❌ Nama barang tidak boleh kosong")
                    continue
                    
                stok = int(input("Jumlah stok: "))
                harga = float(input("Harga per unit: "))
                
                if stok < 0 or harga < 0:
                    print("❌ Stok dan harga tidak boleh negatif")
                    continue
                    
                inventory.tambah_barang(nama, stok, harga)
                
            elif pilihan == '2':
                print("\n📋 DAFTAR BARANG")
                detail = input("Tampilkan detail waktu? (y/n, default=y): ").lower()
                show_details = detail != 'n'
                inventory.tampilkan_daftar_barang(show_details)
                
            elif pilihan == '3':
                print("\n✏️  EDIT BARANG")
                inventory.tampilkan_daftar_barang(False)
                item_id = input("Masukkan ID barang yang akan diedit: ").strip()
                inventory.edit_barang(item_id)
                
            elif pilihan == '4':
                print("\n🗑️  HAPUS BARANG")
                inventory.tampilkan_daftar_barang(False)
                item_id = input("Masukkan ID barang yang akan dihapus: ").strip()
                inventory.hapus_barang(item_id)
                
            elif pilihan == '5':
                print("\n🔍 CARI BARANG")
                keyword = input("Masukkan nama atau ID barang: ").strip()
                if not keyword:
                    print("❌ Keyword pencarian tidak boleh kosong")
                    continue
                    
                results = inventory.cari_barang(keyword)
                if results:
                    print(f"\n✅ Ditemukan {len(results)} barang:")
                    print("="*60)
                    for item in results:
                        print(f"ID: {item.id} | {item.nama} | Stok: {item.stok} | Harga: Rp{item.harga:,.0f}")
                else:
                    print(f"❌ Tidak ditemukan barang dengan keyword '{keyword}'")
                    
            elif pilihan == '6':
                print("\n📦 UPDATE STOK")
                inventory.tampilkan_daftar_barang(False)
                item_id = input("Masukkan ID barang: ").strip()
                if item_id in inventory.items:
                    current_stock = inventory.items[item_id].stok
                    print(f"Stok saat ini: {current_stock}")
                    
                    print("Pilih jenis update:")
                    print("1. Set stok baru")
                    print("2. Tambah stok")
                    print("3. Kurangi stok")
                    
                    update_type = input("Pilihan (1-3): ").strip()
                    jumlah = int(input("Masukkan jumlah: "))
                    
                    if update_type == '1':
                        inventory.update_stok(item_id, jumlah)
                    elif update_type == '2':
                        inventory.update_stok(item_id, current_stock + jumlah)
                    elif update_type == '3':
                        new_stock = max(0, current_stock - jumlah)
                        inventory.update_stok(item_id, new_stock)
                        if new_stock == 0:
                            print("⚠️  Stok barang menjadi 0!")
                else:
                    print(f"❌ Barang dengan ID '{item_id}' tidak ditemukan")
                    
            elif pilihan == '7':
                print("\n💾 EXPORT DATA")
                filename = input("Nama file (kosongkan untuk auto): ").strip()
                inventory.export_to_csv(filename if filename else None)
                
            elif pilihan == '8':
                inventory.laporan_ringkas()
                
            elif pilihan == '0':
                print("\n👋 Terima kasih telah menggunakan Sistem Inventori!")
                print("📊 Data telah tersimpan otomatis.")
                break
                
            else:
                print("❌ Pilihan tidak valid, silakan pilih 0-8")
                
        except ValueError as e:
            print(f"❌ Input tidak valid: {e}")
        except KeyboardInterrupt:
            print("\n\n⚠️  Program dihentikan oleh user")
            break
        except Exception as e:
            print(f"❌ Terjadi error: {e}")
        
        input("\nTekan Enter untuk melanjutkan...")

if __name__ == "__main__":
    main()
