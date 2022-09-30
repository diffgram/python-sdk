from diffgram.core.core import Project
from typing import List
from diffgram.file.file import File
from diffgram.job.job import Job


class CompoundChildFile:
    path: str
    url: str
    blob_path: str
    file_name: str
    bucket_name: str
    child_file_type: str
    connection_id: int
    media_type: str
    job: Job
    job_id: int
    directory_id: int
    instance_list: list
    frame_packet_map: dict
    assume_new_instances_machine_made: bool
    convert_names_to_label_files: bool
    video_split_duration: int

    def __init__(self,
                 child_file_type: str,
                 path: str = None,
                 url: str = None,
                 blob_path: str = None,
                 file_name: str = None,
                 bucket_name: str = None,
                 connection_id: int = None,
                 media_type: str = None,
                 job: Job = None,
                 job_id: int = None,
                 directory_id: int = None,
                 instance_list: list = None,
                 frame_packet_map: dict = None,
                 assume_new_instances_machine_made: bool = None,
                 convert_names_to_label_files: bool = None,
                 video_split_duration: int = None):
        self.child_file_type = child_file_type
        self.path = path
        self.url = url
        self.blob_path = blob_path
        self.file_name = file_name
        self.bucket_name = bucket_name
        self.connection_id = connection_id
        self.media_type = media_type
        self.job = job
        self.job_id = job_id
        self.directory_id = directory_id
        self.instance_list = instance_list
        self.frame_packet_map = frame_packet_map
        self.assume_new_instances_machine_made = assume_new_instances_machine_made
        self.convert_names_to_label_files = convert_names_to_label_files
        self.video_split_duration = video_split_duration


class CompoundFile:
    project: Project
    parent_file_data: dict
    child_files_to_upload: List[CompoundChildFile]

    def __init__(self, project: Project, name: str, directory_id: int):
        self.project = project
        self.name = name
        self.directory_id = directory_id
        self.child_files_to_upload = []

    def remove_compound_file(self, child_file: CompoundChildFile) -> List[CompoundChildFile]:
        self.child_files_to_upload.remove(child_file)
        return self.child_files_to_upload

    def __create_compound_parent_file(self):
        url = f'/api/v1/project/{self.project.project_string_id}/file/new-compound'
        data = {
            'name': self.name,
            'directory_id': self.directory_id
        }
        response = self.project.session.post(url = self.project.host + url,
                                             json = data)
        self.project.handle_errors(response)
        data = response.json()
        self.parent_file_data = data.get('file')
        print('self,', self.parent_file_data)
        return data.get('file')

    def __create_child_file(self, child_file: CompoundChildFile):
        if child_file.child_file_type == 'from_local':
            return self.project.file.from_local(
                path = child_file.path,
                directory_id = self.directory_id,
                instance_list = child_file.instance_list,
                frame_packet_map = child_file.frame_packet_map,
                assume_new_instances_machine_made = child_file.assume_new_instances_machine_made,
                convert_names_to_label_files = child_file.convert_names_to_label_files,
                parent_file_id = self.parent_file_data.get('id')
            )
        elif child_file.child_file_type == 'from_url':
            return self.project.file.from_url(
                url = child_file.path,
                media_type = child_file.media_type,
                job_id = child_file.job_id,
                job = child_file.job,
                video_split_duration = child_file.video_split_duration,
                instance_list = child_file.instance_list,
                frame_packet_map = child_file.frame_packet_map,
                parent_file_id = self.parent_file_data.get('id')
            )
        elif child_file.child_file_type == 'from_blob_path':
            return self.project.file.from_blob_path(
                blob_path = child_file.blob_path,
                bucket_name = child_file.bucket_name,
                connection_id = child_file.connection_id,
                media_type = child_file.media_type,
                instance_list = child_file.instance_list,
                file_name = child_file.file_name,
                frame_packet_map = child_file.frame_packet_map,
                parent_file_id = self.parent_file_data.get('id')
            )

    def add_child_from_local(self,
                             path: str,
                             instance_list: list = None,
                             frame_packet_map: dict = None,
                             assume_new_instances_machine_made: bool = True,
                             convert_names_to_label_files: bool = True):
        new_child_file = CompoundChildFile(
            child_file_type = "from_local",
            path = path,
            directory_id = self.directory_id,
            instance_list = instance_list,
            frame_packet_map = frame_packet_map,
            assume_new_instances_machine_made = assume_new_instances_machine_made,
            convert_names_to_label_files = convert_names_to_label_files
        )
        self.child_files_to_upload.append(new_child_file)
        return new_child_file

    def add_child_file_from_url(self,
                                url: str,
                                media_type: str = "image",
                                job: Job = None,
                                job_id: int = None,
                                video_split_duration: int = None,
                                instance_list: list = None,
                                frame_packet_map: dict = None):
        new_child_file = CompoundChildFile(
            child_file_type = "from_url",
            url = url,
            media_type = media_type,
            job = job,
            directory_id = self.directory_id,
            job_id = job_id,
            video_split_duration = video_split_duration,
            instance_list = instance_list,
            frame_packet_map = frame_packet_map,
        )
        self.child_files_to_upload.append(new_child_file)
        return new_child_file

    def add_child_from_blob_path(self,
                                 blob_path: str,
                                 bucket_name: str,
                                 connection_id: int,
                                 media_type: str = 'image',
                                 instance_list: list = None,
                                 file_name: str = None,
                                 frame_packet_map: dict = None
                                 ):
        new_child_file = CompoundChildFile(
            child_file_type = "from_blob_path",
            blob_path = blob_path,
            bucket_name = bucket_name,
            connection_id = connection_id,
            directory_id = self.directory_id,
            media_type = media_type,
            instance_list = instance_list,
            file_name = file_name,
            frame_packet_map = frame_packet_map,
        )
        self.child_files_to_upload.append(new_child_file)
        return new_child_file

    def upload(self):
        parent_file_data: dict = self.__create_compound_parent_file()
        for child_file in self.child_files_to_upload:
            self.__create_child_file(child_file)
        return parent_file_data
