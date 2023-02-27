from .compound_file import CompoundFile
from uuid import uuid4
import operator

class Conversational:
    def __init__(self, project, name):
        self.parent = CompoundFile(
            project=project, 
            name=name, 
            directory_id=project.default_directory.id,
            file_type="compound/conversational"
        )
        self.project = project
        self.messgaes_meta = []

        self.add_conversationa_attributes_if_doesnt_exist()

    def add_conversationa_attributes_if_doesnt_exist(self):
        default_schema = self.project.schema.default_schema()
        attribute_list = self.project.attribute.list(default_schema)

        message_author_attribute = None
        message_time_attribute = None
        message_date_attribute = None

        for attribute in attribute_list['attribute_group_list']:
            if attribute['name'] == 'message_author':
                message_author_attribute = attribute
            elif attribute['name'] == 'message_time':
                message_time_attribute = attribute
            elif attribute['name'] == 'message_date':
                message_date_attribute = attribute

        if message_author_attribute is None:
            message_author_attribute = self.project.attribute.new(default_schema)
            self.project.attribute.update(
                message_author_attribute, 
                prompt="Author",
                kind="text",
                name="message_author",
                is_global = True,
                global_type = 'file',
                is_read_only=True
            )

        if message_time_attribute is None:
            message_time_attribute = self.project.attribute.new(default_schema)
            self.project.attribute.update(
                message_time_attribute, 
                prompt="Time",
                kind="time",
                name="message_time",
                is_global = True,
                global_type = 'file',
                is_read_only=True
            )

        if message_date_attribute is None:
            message_date_attribute = self.project.attribute.new(default_schema)
            self.project.attribute.update(
                message_date_attribute, 
                prompt="Date",
                kind="date",
                name="message_date",
                is_global = True,
                global_type = 'file',
                is_read_only=True
            )

        self.author_attribute = message_author_attribute
        self.time_attribute = message_time_attribute
        self.date_attribute = message_date_attribute

    def add_message(self, message_file, author=None, time=None, date=None):
        message_meta = {
            "author": author,
            "time": time,
            "date": date
        }

        self.messgaes_meta.append(message_meta)

        self.parent.add_child_from_local(path=message_file, ordinal=len(self.messgaes_meta))

    def _new_global_instance(self):
        return {
            "creation_ref_id": str(uuid4()),
            "type": "global",
            "attribute_groups": {}
        }


    def upload(self):
        self.parent.upload()
        child_files = self.parent.fetch_child_files()
        child_files.sort(key=operator.attrgetter('id'))

        for index in range(0, len(child_files)):
            global_instance_for_child = self._new_global_instance()

            if self.messgaes_meta[index]["author"] is not None:
                global_instance_for_child["attribute_groups"][self.author_attribute["id"]] = self.messgaes_meta[index]["author"]
            if self.messgaes_meta[index]["time"] is not None:
                global_instance_for_child["attribute_groups"][self.time_attribute["id"]] = self.messgaes_meta[index]["time"]
            if self.messgaes_meta[index]["date"] is not None:
                global_instance_for_child["attribute_groups"][self.date_attribute["id"]] = self.messgaes_meta[index]["date"]

            payload = {
                "instance_list": [global_instance_for_child],
                "and_complete": False,
                "child_file_save_id": child_files[index].id
            }
            
            response = self.project.session.post(url=self.project.host + f"/api/project/{self.project.project_string_id}/file/{child_files[index].id}/annotation/update", json=payload)
            self.project.handle_errors(response)