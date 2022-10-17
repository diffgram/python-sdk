from diffgram import Project
from diffgram.file.compound_file import CompoundFile

project = Project(host = "https://diffgram.com",
		  project_string_id = "replace_with_project_string",
		  client_id = "replace_with_client_id",
		  client_secret = "replace_with_client_secret")

parent = CompoundFile(
    project=project, 
    name='myFirstCompoundFile', 
    directory_id=project.default_directory.id
)

parent.add_child_from_local(path='path/to/your_file.jpg')
parent.add_child_from_local(path='path/to/your_second_file.jpg')
parent.upload()