
from diffgram import Project
import random

project = Project()

name_list = [str(random.random()) for i in range(3)]
last_id = None

for name in name_list:

	project.directory.new(name)
	project.set_directory_by_name(name)
	id_set = project.session.headers.get('directory_id')
	print(id_set)
	assert last_id != id_set
	last_id = id_set
