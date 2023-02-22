from .compound_file import CompoundFile

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
            new_message_author_attribute = self.project.attribute.new(default_schema)
            self.project.attribute.update(
                new_message_author_attribute, 
                prompt="Author",
                kind="text",
                name="message_author",
                is_global = True,
                global_type = 'file'
            )

        if message_time_attribute is None:
            new_message_time_attribute = self.project.attribute.new(default_schema)
            self.project.attribute.update(
                new_message_time_attribute, 
                prompt="Time",
                kind="time",
                name="message_time",
                is_global = True,
                global_type = 'file'
            )

        if message_date_attribute is None:
            new_message_date_attribute = self.project.attribute.new(default_schema)
            self.project.attribute.update(
                new_message_date_attribute, 
                prompt="Date",
                kind="date",
                name="message_date",
                is_global = True,
                global_type = 'file'
            )

    def add_message(self, message_file, author=None, time=None, date=None):
        message_meta = {
            "author": author,
            "time": time,
            "date": date
        }

        self.messgaes_meta.append(message_meta)

        self.parent.add_child_from_local(path=message_file, ordinal=len(self.messgaes_meta))

    def upload(self):
        self.parent.upload()