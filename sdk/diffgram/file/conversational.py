from .compound_file import CompoundFile

class Conversational:
    def __init__(self, project, name):
        self.parent = CompoundFile(
            project=project, 
            name=name, 
            directory_id=project.default_directory.id
        )

        self.messgaes_meta = []

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