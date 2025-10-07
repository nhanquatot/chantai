!sudo apt install openjdk-21-jdk
!wget "https://github.com/abdlhay/AbyssVideoDownloader/releases/download/v1.6.0/abyss-dl.jar"
from IPython.display import clear_output
clear_output()

# Chạy chương trình Java
!java -jar abyss-dl.jar "N5Up-LNIl" -o "tienvo134.mp4"
!pip install tqdm
from IPython.display import clear_output
clear_output()  
#GPU convert video  
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
##tạo link tải  
import os

# Tên file TXT chứa danh sách
file_name = "yeuthan.txt"

# Lệnh cơ sở (Phần "java -jar abyss-dl.jar")
base_command = "java -jar abyss-dl.jar"

# Biến để lưu trữ các lệnh hoàn chỉnh
download_commands = []

try:
    # Mở và đọc nội dung file
    with open(file_name, 'r', encoding='utf-8') as f:
        # Đọc từng dòng trong file
        for line in f:
            # Loại bỏ khoảng trắng thừa ở đầu/cuối dòng (ví dụ: '\n')
            line = line.strip()

            # Bỏ qua dòng trống
            if not line:
                continue

            # Tách chuỗi:
            # 1. Tìm vị trí của khoảng trắng cuối cùng trong dòng.
            # 2. Phần bên trái là TÊN PHIM (Bao gồm khoảng trắng).
            # 3. Phần bên phải là MÃ (Không có khoảng trắng).
            last_space_index = line.rfind(' ')

            if last_space_index != -1:
                # Tên phim (Bên trái khoảng trắng cuối cùng)
                ten_phim = line[:last_space_index].strip()

                # Mã (Bên phải khoảng trắng cuối cùng)
                ma_video = line[last_space_index+1:].strip()

                # Xây dựng tên file đầu ra (.mp4)
                output_file = f'"{ten_phim}.mp4"'

                # Xây dựng câu lệnh hoàn chỉnh
                # Định dạng: java -jar abyss-dl.jar "MÃ" -o "TÊN PHIM.mp4"
                full_command = f'{base_command} "{ma_video}" -o {output_file}'

                download_commands.append(full_command)
            else:
                print(f"Bỏ qua dòng không đúng định dạng: {line}")

    # --- HIỂN THỊ KẾT QUẢ ---
    print(f"Đã tạo {len(download_commands)} lệnh tải xuống từ file {file_name}:\n")

    # In ra tất cả các lệnh đã tạo
    for cmd in download_commands:
        print(cmd)

    # TUỲ CHỌN: Nếu bạn muốn chạy các lệnh này tự động trong Colab,
    # bạn có thể tạo một file bash script để thực thi:
    # script_content = '\n'.join(f'!{cmd}' for cmd in download_commands)
    # print("\n--- Mã Bash Script cho Colab ---")
    # print(script_content)

except FileNotFoundError:
    print(f"LỖI: Không tìm thấy file '{file_name}'. Hãy đảm bảo file đã được tải lên cùng thư mục.")
except Exception as e:
    print(f"Đã xảy ra lỗi: {e}")
##xem thông tin video  
import os
import ffmpeg

# --- CẤU HÌNH ---
# Thay đổi đường dẫn này thành thư mục chứa video của bạn
VIDEO_FOLDER = r"E:\download\video" 
# Thêm các phần mở rộng video bạn muốn kiểm tra
VIDEO_EXTENSIONS = ('.mp4', '.mkv', '.avi', '.mov', '.webm') 
# Tên file đầu ra
OUTPUT_FILE = "video_info_report.txt"
# ----------------

def get_video_metadata(file_path):
    """
    Sử dụng ffmpeg-python để lấy metadata chi tiết của video.
    """
    # ... (giữ nguyên hàm này từ code trước) ...
    try:
        probe_data = ffmpeg.probe(file_path)
        format_info = probe_data.get('format', {})
        file_format = format_info.get('format_name', 'N/A')
        
        video_codec = 'N/A'
        audio_codec = 'N/A'
        
        streams = probe_data.get('streams', [])
        for stream in streams:
            codec_type = stream.get('codec_type')
            codec_name = stream.get('codec_name', 'N/A')
            codec_long_name = stream.get('codec_long_name', 'N/A')
            
            if codec_type == 'video' and video_codec == 'N/A':
                video_codec = f"{codec_name} ({codec_long_name})"
            elif codec_type == 'audio' and audio_codec == 'N/A':
                audio_codec = f"{codec_name} ({codec_long_name})"

        return {
            "format": file_format,
            "video_codec": video_codec,
            "audio_codec": audio_codec
        }
    except ffmpeg.Error as e:
        return {
            "format": f"Lỗi: Không thể đọc file. {e.stderr.decode('utf8').strip()}",
            "video_codec": "N/A",
            "audio_codec": "N/A"
        }
    except FileNotFoundError:
        return {
            "format": "Lỗi: Không tìm thấy ffprobe. Đảm bảo FFmpeg đã được cài đặt.",
            "video_codec": "N/A",
            "audio_codec": "N/A"
        }
    except Exception as e:
        return {
            "format": f"Lỗi không xác định: {e}",
            "video_codec": "N/A",
            "audio_codec": "N/A"
        }

def process_folder(folder_path, output_file):
    """
    Duyệt qua thư mục, lấy thông tin và ghi vào file văn bản.
    """
    report_content = ""
    separator = "=" * 80 + "\n"
    
    report_content += "BÁO CÁO THÔNG TIN VIDEO\n"
    report_content += f"Thư mục quét: {folder_path}\n"
    report_content += f"Thời gian: {os.stat(os.path.abspath(__file__)).st_mtime}\n"
    report_content += separator

    # Bắt đầu quét thư mục
    for dirpath, dirnames, filenames in os.walk(folder_path):
        for filename in filenames:
            # Kiểm tra file video
            if filename.lower().endswith(VIDEO_EXTENSIONS):
                file_path = os.path.join(dirpath, filename)
                metadata = get_video_metadata(file_path)
                
                # Định dạng nội dung cho từng video
                report_content += f"TÊN FILE: {filename}\n"
                report_content += f"ĐƯỜNG DẪN: {dirpath}\n"
                report_content += f"CONTAINER (FORMAT): {metadata['format']}\n"
                report_content += f"VIDEO CODEC: {metadata['video_codec']}\n"
                report_content += f"AUDIO CODEC: {metadata['audio_codec']}\n"
                report_content += "-" * 50 + "\n" # Dấu gạch ngắn ngăn cách các file

    # Ghi nội dung đã thu thập vào file
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        print(f"\n✅ Đã hoàn tất việc quét.")
        print(f"File báo cáo đã được tạo tại: {os.path.abspath(output_file)}")
        print(f"Kiểm tra file '{output_file}' để xem chi tiết.")
        
    except Exception as e:
        print(f"\n❌ Lỗi khi ghi file: {e}")

# Chạy chương trình
if __name__ == "__main__":
    process_folder(VIDEO_FOLDER, OUTPUT_FILE)
