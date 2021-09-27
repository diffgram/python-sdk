
import numpy as np
import open3d as o3d
from diffgram.file.file_3d import File3D
from diffgram.core.core import Project

pcd = o3d.io.read_point_cloud("/home/pablo/Downloads/lidar_ascii_v5.pcd")
out_arr = np.asarray(pcd.points)

project = Project( project_string_id = "glorybiter",
                   debug= True,
                   client_id = "LIVE__6bn2dsiitc4vbmnwlihz",
                   client_secret = "kzwlrg20pdvjzfutz2oitx2aakqvf0216j201pv47i53nw8v52x1unqtjt3h")

diffgram_3d_file = File3D(client = project)

for point in out_arr:
    diffgram_3d_file.add_point(
        x = point[0],
        y = point[1],
        z = point[2],
    )