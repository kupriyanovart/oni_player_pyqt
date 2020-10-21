from openni import openni2
import numpy as np


def get_video(file_name, progress_bar):
    openni2.initialize()
    frames_color = []
    frames_depth = []

    file = openni2.Device(file_name)
    # Открываем потоки для чтения данных из файла
    c_stream = openni2.VideoStream(file, openni2.SENSOR_COLOR)
    d_stream = openni2.VideoStream(file, openni2.SENSOR_DEPTH)

    c_stream.start()
    d_stream.start()

    progress_bar.setValue(1)
    progress_bar.setVisible(True)
    per_cent = d_stream.get_number_of_frames() // 100

    for i in range(d_stream.get_number_of_frames()):
        # Добавляем загруженные фреймы в общий список (frames_depth)
        depth_frame = d_stream.read_frame()

        # From https://stackoverflow.com/a/55539208/8245749
        depth_frame_data = depth_frame.get_buffer_as_uint16()
        depth_img = np.frombuffer(depth_frame_data, dtype=np.uint16)
        img8 = (depth_img / 256).astype(np.uint8)
        img8 = ((img8 - img8.min()) / (img8.ptp() / 255)).astype(np.uint8)
        frames_depth.append(img8.repeat(4))
        # добавляем загруженные фреймы в общий список (frames_color)
        color_frame = c_stream.read_frame()
        frames_color.append(color_frame)
        progress_bar.setValue(i // per_cent)

    c_stream.stop()
    d_stream.stop()

    return frames_color, frames_depth
