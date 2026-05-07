import cv2
import numpy as np
import pandas as pd
import os

#  1. Videoyu aç
video = cv2.VideoCapture("C:/Users/ASUS/Desktop/video.mp4")

if not video.isOpened():
    print(" Video açılamadı!")
    exit()

#  2. Süre bilgisi
fps = video.get(cv2.CAP_PROP_FPS)
frame_count = video.get(cv2.CAP_PROP_FRAME_COUNT)

if fps == 0:
    print(" FPS değeri 0, video bozuk olabilir.")
    exit()

duration = frame_count / fps
print(f" Video Süresi: {duration:.2f} saniye")

# 3. CSV oluştur
time_offsets = np.arange(0, duration, 0.5)
x_coords = np.random.randint(50, 500, size=len(time_offsets))
y_coords = np.random.randint(50, 500, size=len(time_offsets))

df = pd.DataFrame({
    'time_offset': time_offsets,
    'x': x_coords,
    'y': y_coords
})
df.to_csv('koordinatlar.csv', index=False)
print(" CSV oluşturuldu: koordinatlar.csv")

#  4. Sekansları oluştur
sequence_length = 20
num_sequences = len(df) - sequence_length + 1

for seq_index in range(num_sequences):
    seq_folder = f"seq_{seq_index+1:04d}"
    os.makedirs(seq_folder, exist_ok=True)

    with open(os.path.join(seq_folder, "coords.txt"), "w") as txt_file:
        for frame_index in range(sequence_length):
            row_index = seq_index + frame_index
            time_offset = df.loc[row_index, 'time_offset']
            x = df.loc[row_index, 'x']
            y = df.loc[row_index, 'y']

            # Zaman konumuna git ve kare al
            video.set(cv2.CAP_PROP_POS_MSEC, time_offset * 1000)
            success, frame = video.read()

            if success:
                frame_filename = f"frame{frame_index+1}.jpg"
                frame_path = os.path.join(seq_folder, frame_filename)
                cv2.imwrite(frame_path, frame)
                txt_file.write(f"{x},{y}\n")
            else:
                print(f" Frame alınamadı: {time_offset}s")

print(" Tüm sekanslar başarıyla oluşturuldu.")
