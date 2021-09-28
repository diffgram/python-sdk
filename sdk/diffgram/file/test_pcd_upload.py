
import numpy as np
import open3d as o3d
from diffgram.file.file_3d import File3D
from diffgram.core.core import Project



project = Project( project_string_id = "glorybiter",
                   debug= True,
                   client_id = "LIVE__6bn2dsiitc4vbmnwlihz",
                   client_secret = "kzwlrg20pdvjzfutz2oitx2aakqvf0216j201pv47i53nw8v52x1unqtjt3h")

diffgram_3d_file = File3D(client = project)

out_arr = []
with open('/home/pablo/Downloads/lidar_ascii_v5.pcd') as f:
    lines = f.readlines()
    is_on_points = False
    for line in lines:
        if not is_on_points:
            if line.startswith('DATA'):
                is_on_points = True
        else:
            data = line.split(' ')
            row = []
            for elm in data:
                row.append(float(elm))
            row[3] = min((row[3] / 100, 1.0))
            out_arr.append(row)

for i in range(0, len(out_arr)):
    point = out_arr[i]
    color = out_arr[i]
    diffgram_3d_file.add_point(
        x = point[0],
        y = point[1],
        z = point[2],
        intensity = point[3]
    )