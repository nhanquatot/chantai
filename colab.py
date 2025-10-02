!sudo apt install openjdk-21-jdk
!wget "https://github.com/abdlhay/AbyssVideoDownloader/releases/download/v1.6.0/abyss-dl.jar"
from IPython.display import clear_output
clear_output()

# Chạy chương trình Java
!java -jar abyss-dl.jar "N5Up-LNIl" -o "tienvo134.mp4"
