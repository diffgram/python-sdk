from diffgram.file.file_3d import File3D
from diffgram.core.core import Project
import time
import open3d as o3d
import numpy as np

"""
    
    This example show how you can upload a 3D point cloud into diffgram using the File3D object.

    Please make sure to replace the project_string_id, client_id and client_secret of your project.
"""


# For reading the PCD file
def read_pcd_o3d(file_name):
    pcd = o3d.io.read_point_cloud(file_name)
    out_arr = np.asarray(pcd.points)
    return out_arr


project = Project(project_string_id = "your_project_name",
                  client_id = "your_client_id",
                  client_secret = "your_client_secret")

points_arr = read_pcd_o3d('Zaghetto.pcd')

diffgram_3d_file = File3D(client = project, name = 'face{}.pcd'.format(time.time()))

for i in range(0, len(points_arr)):
    point = points_arr[i]
    diffgram_3d_file.add_point(
        x = point[0],
        y = point[1],
        z = point[2],
    )
diffgram_3d_file.upload()
