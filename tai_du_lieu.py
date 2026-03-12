import os
import zipfile
import subprocess
import sys


def cai_dat_gdown():
    try:
        import gdown
    except ImportError:
        print("🔧 Máy tính chưa có gdown. Đang tự động cài đặt...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "gdown"])
        import gdown
    return gdown


def tai_va_giai_nen():
    gdown = cai_dat_gdown()

    # THUẬT TOÁN TỐI ƯU: Chỉ dùng đúng mã ID, không kèm râu ria
    FILE_ID = "1PXVQq_iWQwb4RNQuUxwx91EwWP6WLPPZ"
    output_zip = 'dataset_sach.zip'
    thu_muc_dich = 'data/'

    print("1. 🚀 Bắt đầu tải bộ Data từ Drive về máy...")

    # Dùng fuzzy=True để tự động vượt qua trang web cảnh báo virus của Google
    gdown.download(id=FILE_ID, output=output_zip, quiet=False, fuzzy=True)

    print("\n2. 📦 Tải xong! Đang kiểm tra và bung nén (Unzip)...")
    if not os.path.exists(thu_muc_dich):
        os.makedirs(thu_muc_dich)

    # Bẫy lỗi an toàn: Kiểm tra xem file tải về có đúng là Zip thật không
    try:
        with zipfile.ZipFile(output_zip, 'r') as zip_ref:
            zip_ref.extractall(thu_muc_dich)

        print("\n3. 🧹 Đang dọn dẹp rác...")
        os.remove(output_zip)
        print(f"\n🎉 HOÀN TẤT TUYỆT ĐỐI! Toàn bộ 1597 file âm thanh đã nằm sẵn trong thư mục '{thu_muc_dich}'.")

    except zipfile.BadZipFile:
        print("\n❌ LỖI NGHIÊM TRỌNG: File tải về bị lỗi (Không phải Zip thật).")
        print("👉 NGUYÊN NHÂN: Em quên chưa mở quyền truy cập trên Google Drive!")
        print(
            "👉 CÁCH SỬA: Lên Google Drive -> Chuột phải vào file zip -> Chọn Chia sẻ (Share) -> Đổi thành 'Bất kỳ ai có liên kết' (Anyone with the link).")


if __name__ == "__main__":
    tai_va_giai_nen()