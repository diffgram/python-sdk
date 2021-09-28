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

    def upload(self, dataset_name = None, chunk_size = 5000000):
        """
            Builds a JSON file from current point list and uploads it to
            Diffgram.
        :param dataset_name:
        :param chunk_size: Size of each chunk of the JSON file. Default is 5MB
        :return:
        """
        file_data = {
            'point_list': self.point_list
        }
        json_data = json.dumps(file_data)

        endpoint = "/api/walrus/project/{}/upload/large".format(
            self.client.project_string_id
        )
        chunk_size = 5000000  # 5 MB chunks
        dataset_id = self.client.default_directory['id']
        if dataset_name is not None:
            dataset_id = self.client.directory.get(dataset_name).id

        with io.StringIO(json_data) as s:
            pos = s.tell()
            s.seek(0, os.SEEK_END)
            file_size = s.tell()
            s.seek(pos)
            num_chunks = int(math.ceil(file_size / chunk_size))
            last_chunk_size = -1
            if file_size % chunk_size != 0:
                last_chunk_size = file_size % chunk_size

            uid_upload = str(uuid.uuid4())
            for i in range(0, num_chunks):
                # print('File Size: {} bytes.'.format(file_size))

                payload = {
                    'dzuuid': uid_upload,
                    'dzchunkindex': i,
                    'dztotalfilesize': file_size,
                    'dzchunksize': chunk_size,
                    'dztotalchunkcount': num_chunks,
                    'dzchunkbyteoffset': i * chunk_size,
                    'directory_id': dataset_id,
                    'source': 'from_sensor_fusion_json',
                }
                # Adjust final chunk size
                if i == (num_chunks - 1) and last_chunk_size != -1:
                    # Read last chunk size here...
                    payload['dzchunksize'] = last_chunk_size

                # Read file Chunk
                s.seek(payload['dzchunkbyteoffset'])
                file_chunk = s.read(payload['dzchunksize'])
                files = {'file': ('{}_sensor_fusion_file.json'.format(uid_upload), file_chunk)}
                # Make request to server
                url = self.client.host + endpoint
                response = self.client.session.post(url,
                                                    data = payload,
                                                    files = files)

                self.client.handle_errors(response)

            return True
