import os
import pysrt
import subprocess

# --- CẤU HÌNH ĐƯỜNG DẪN ---
THU_MUC_DATA = "data"
THU_MUC_XUAT = "data/dataset_sach"


def xu_ly_hang_loat():
    print("1. Đang khởi động hệ thống Xử lý hàng loạt (Batch Processing)...")

    if not os.path.exists(THU_MUC_XUAT):
        os.makedirs(THU_MUC_XUAT)

    metadata_lines = []
    bien_dem_tong = 0  # Biến này giúp các file đếm nối tiếp nhau không bị đè

    # Quét tất cả các file có trong thư mục data
    danh_sach_file = os.listdir(THU_MUC_DATA)
    file_wavs = [f for f in danh_sach_file if f.endswith(".wav")]

    print(f"2. Phát hiện tổng cộng {len(file_wavs)} file âm thanh gốc cần xử lý.\n")

    for ten_file_wav in file_wavs:
        duong_dan_wav = os.path.join(THU_MUC_DATA, ten_file_wav)

        # Tự động suy luận tên file SRT tương ứng
        ten_file_srt = ten_file_wav.replace(".wav", ".srt")
        duong_dan_srt = os.path.join(THU_MUC_DATA, ten_file_srt)

        # Kiểm tra xem file SRT có tồn tại không
        if not os.path.exists(duong_dan_srt):
            print(f"[BỎ QUA] File {ten_file_wav} không có file {ten_file_srt} đi kèm.")
            continue

        print(f"--> Đang tiến hành băm nhỏ cặp file: {ten_file_wav} & {ten_file_srt}")
        subs = pysrt.open(duong_dan_srt, encoding='utf-8')

        for sub in subs:
            start_ms = (
                                   sub.start.hours * 3600 + sub.start.minutes * 60 + sub.start.seconds) * 1000 + sub.start.milliseconds
            end_ms = (sub.end.hours * 3600 + sub.end.minutes * 60 + sub.end.seconds) * 1000 + sub.end.milliseconds

            duration_sec = (end_ms - start_ms) / 1000.0
            start_sec = start_ms / 1000.0

            chunk_name = f"file_{bien_dem_tong:04d}.wav"
            chunk_path = os.path.join(THU_MUC_XUAT, chunk_name)

            cmd = [
                "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
                "-i", duong_dan_wav,
                "-ss", str(start_sec),
                "-t", str(duration_sec),
                "-ar", "22050", "-ac", "1", chunk_path
            ]

            subprocess.run(cmd, check=True)

            text_content = sub.text.replace('\n', ' ').strip()
            metadata_lines.append(f"{chunk_name}|{text_content}")

            bien_dem_tong += 1  # Tăng số thứ tự lên 1 cho câu tiếp theo

    # Lưu toàn bộ danh sách hàng ngàn câu vào 1 file metadata duy nhất
    with open(os.path.join(THU_MUC_XUAT, "metadata.csv"), "w", encoding="utf-8") as f:
        f.write("\n".join(metadata_lines))

    print(f"\n HOÀN TẤT CHIẾN DỊCH! Tổng cộng đã tạo ra {bien_dem_tong} file âm thanh nhỏ.")
    print(f" Toàn bộ dữ liệu hội tụ tại: {THU_MUC_XUAT}")


if __name__ == "__main__":
    xu_ly_hang_loat()