from diffgram.file.file_3d import File3D
from diffgram.core.core import Project
import numpy as np
import open3d as o3d


def read_pcd_o3d(file_name):
    pcd = o3d.io.read_point_cloud(file_name)
    out_arr = np.asarray(pcd.points)
    return out_arr


project = Project(project_string_id = "forestfox",
                  client_id = "LIVE__hyibdfom3kqia8ks6jcp",
                  client_secret = "zx0gzw4yznimtfg4x4gdyqoc0sq6t6d73uc6dvkys7f07k9mvt9mzffm101m",
                  debug = True)


def upload_test_file1():
    diffgram_3d_file = File3D(client = project, name = 'lidar_ascii_v5.pcd')

    points_arr = []
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
                points_arr.append(row)

    for i in range(0, len(points_arr)):
        point = points_arr[i]
        diffgram_3d_file.add_point(
            x = point[0],
            y = point[1],
            z = point[2],
            intensity = point[3]
        )
    diffgram_3d_file.upload()


# File 2 test
def upload_test_file2():
    points_arr = read_pcd_o3d('/home/pablo/Downloads/Zaghetto.pcd')

    diffgram_3d_file = File3D(client = project, name = 'face.pcd')

    for i in range(0, len(points_arr)):
        point = points_arr[i]
        diffgram_3d_file.add_point(
            x = point[0],
            y = point[1],
            z = point[2],
        )

    print('num points: {}'.format(len(diffgram_3d_file.point_list)))
    diffgram_3d_file.upload()
