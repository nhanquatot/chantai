!sudo apt install openjdk-21-jdk
!wget "https://github.com/abdlhay/AbyssVideoDownloader/releases/download/v1.6.0/abyss-dl.jar"
from IPython.display import clear_output
clear_output()

# Chạy chương trình Java
!java -jar abyss-dl.jar "N5Up-LNIl" -o "tienvo134.mp4"
!pip install tqdm
from IPython.display import clear_output
clear_output()  
#GPU 
import os
import subprocess
import re
import sys
from tqdm import tqdm
import glob

# --- CẤU HÌNH ---
# Thư mục chứa video MP4 đầu vào
input_folder = "/content/content"
# Thư mục để lưu video H.265 đã chuyển đổi
output_folder = "/content/video"
# --- KẾT THÚC CẤU HÌNH ---

# Tạo thư mục đầu ra nếu nó chưa tồn tại
os.makedirs(output_folder, exist_ok=True)

# Lấy danh sách tất cả các file có đuôi .mp4 trong thư mục đầu vào
video_files = glob.glob(os.path.join(input_folder, '*.mp4'))

# Kiểm tra xem có video nào để xử lý không
if not video_files:
    print(f"Không tìm thấy video MP4 nào trong thư mục: {input_folder}")
    sys.exit()

print(f"Tìm thấy {len(video_files)} video để bắt đầu chuyển đổi.")

def get_duration(filename):
    """
    Sử dụng ffprobe để lấy tổng thời lượng của video (tính bằng giây).
    """
    cmd = [
        "ffprobe", "-v", "error", "-show_entries",
        "format=duration", "-of",
        "default=noprint_wrappers=1:nokey=1", filename
    ]
    try:
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        return float(result.stdout.strip())
    except (subprocess.CalledProcessError, FileNotFoundError):
        print(f"\nLỗi: Không thể lấy thời lượng của file '{filename}'. "
              f"Hãy chắc chắn rằng ffprobe đã được cài đặt và file tồn tại.")
        return None
    except ValueError:
        print(f"\nLỗi: Không thể đọc thời lượng từ output của ffprobe cho file '{filename}'.")
        return None

# Biểu thức chính quy (regex) để tìm chuỗi thời gian trong output của ffmpeg
time_pattern = re.compile(r"time=(\d{2}):(\d{2}):(\d{2})\.(\d{2})")

# Lặp qua từng file video để thực hiện chuyển đổi
for input_file in video_files:
    # Lấy tên file gốc để tạo tên file đầu ra
    basename = os.path.basename(input_file)
    output_file = os.path.join(output_folder, basename)

    print(f"\n{'='*50}\nBắt đầu chuyển đổi: {basename}\n{'='*50}")

    # 1. Lấy tổng thời lượng của video hiện tại
    duration = get_duration(input_file)
    if duration is None:
        print(f"Bỏ qua file {basename} vì không thể xác định được thời lượng.")
        continue

    # 2. Xây dựng lệnh ffmpeg
 
    cmd = [
        "ffmpeg", "-i", input_file,
        "-vf", "scale='min(iw, 1280)':-2",
        "-pix_fmt", "yuv420p",
        "-c:v", "hevc_nvenc",
        "-preset", "fast",
        output_file,
        "-y"
    ]

    # 3. Chạy ffmpeg và theo dõi tiến trình
    process = subprocess.Popen(
        cmd,
        stderr=subprocess.PIPE,
        stdout=subprocess.PIPE,
        text=True,
        universal_newlines=True,
        encoding='utf-8'
    )

    # Sử dụng tqdm để tạo và quản lý thanh tiến trình
    with tqdm(total=duration, unit="s", desc=f"Đang xử lý {basename}", bar_format="{l_bar}{bar}| {n:.2f}/{total:.2f}s [{elapsed}<{remaining}, {rate_fmt}{postfix}]") as pbar:
        # Đọc từng dòng output lỗi (stderr) của ffmpeg
        for line in process.stderr:
            # Tìm kiếm thông tin thời gian trong dòng hiện tại
            match = time_pattern.search(line)
            if match:
                # Nếu tìm thấy, chuyển đổi thời gian sang giây
                h, m, s, ms = match.groups()
                elapsed_time = int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 100.0
                # Cập nhật thanh tiến trình, đảm bảo không vượt quá tổng thời lượng
                pbar.n = min(elapsed_time, duration)
                pbar.refresh()

    process.wait()

    if process.returncode == 0:
        print(f"✅ Chuyển đổi thành công: {basename}")
    else:
        print(f"❌ Có lỗi xảy ra khi chuyển đổi: {basename}")
        # In ra lỗi để dễ dàng gỡ rối
        stderr_output = process.communicate()[1]
        if stderr_output:
            print("--- Thông báo lỗi từ ffmpeg ---")
            print(stderr_output)

print(f"\n🎉 Hoàn tất! Tất cả các video đã được xử lý và lưu vào thư mục: {output_folder}")
