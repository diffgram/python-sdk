from diffgram.core.core import Project
import json
import os
import requests
import io
import math
import uuid

class File3D:
    point_list: list
    client: Project

    def __init__(self, client, point_list = []):
        self.client = client
        self.point_list = point_list

    def add_point(self, x: float, y: float, z: float):
        self.point_list.append({
            'x': x,
            'y': y,
            'z': z
        })
        return self.point_list

    def upload(self, dataset_name = None):
        """
            Builds a JSON file from current point list and uploads it to
            Diffgram.
        :return:
        """
        file_data = {
            'point_list': self.point_list
        }
        headers = {
            'content-type': 'multipart/form-data',

        }
        json_data = json.dumps(file_data)

        endpoint = "/api/walrus/v1/project/{}/upload/large".format(
            self.client.project_string_id
        )
        # chunk_size = 5000000  # 5 MB chunks
        chunk_size = 1000000  # 1 MB chunks
        dataset_id = self.client.default_directory['id']
        if dataset_name is not None:
            dataset_id = self.client.directory.get(dataset_name).id

        with io.StringIO(json_data) as s:
            pos = s.tell()
            s.seek(0, os.SEEK_END)
            file_size =  s.tell()
            print('FILE SIZE', file_size)
            s.seek(pos)

            # requests.post('http://some.url/streamed', data = f)
            num_chunks = int(math.ceil(file_size / chunk_size))
            last_chunk_size = -1
            if file_size % chunk_size != 0:
                last_chunk_size = file_size % chunk_size

            print('Num chunks', num_chunks)
            print('chunk_size', chunk_size)
            print('last_chunk_size', last_chunk_size)
            uid_upload = str(uuid.uuid4())
            for i in range(0, num_chunks):
                # print('File Size: {} bytes.'.format(file_size))
                payload = {
                    'dzuid': uid_upload,
                    'dzchunkindex': i,
                    'dztotalfilesize': file_size,
                    'dzchunksize': chunk_size,
                    'dztotalchunkcount': num_chunks,
                    'dzchunkbyteoffset': i * chunk_size,
                    'directory_id': dataset_id,
                    'source': 'api',
                    'file': 'binary data here',
                }

                if i == (num_chunks - 1) and last_chunk_size != -1:
                    # Read last chunk size here...
                    payload['dzchunksize'] = last_chunk_size
                print(payload)
            return file_size
