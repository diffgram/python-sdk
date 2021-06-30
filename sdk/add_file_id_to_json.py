from diffgram.core.core import Project
import json

project = Project(project_string_id = "coco-dataset",
                  debug = True,
                  client_id = "LIVE__rj6whqkwxkups7oczqis",
                  client_secret = "fr5vy64v2096qad9av0dgw3fr0kjavt4c156soiwx51ntyv9qswpuxkhg0lf")


def find_file(file_list, name):
    for f in file_list:
        if f.original_filename == name:
            return f
    return None


with open('/home/pablo/Downloads/coco2017.json') as json_file:
    data = json.load(json_file)

    dataset_default = project.directory.get(name = "Default")

    page_num = 1
    all_files = []
    print('start')
    while page_num != None:
        print('Current page', page_num)
        diffgram_files = dataset_default.list_files(limit = 1000, page_num = page_num, file_view_mode = 'base')
        page_num = dataset_default.file_list_metadata['next_page']
        print('{} of {}'.format(page_num, dataset_default.file_list_metadata['total_pages']))
        all_files = all_files + diffgram_files

    print('')
    print('Files fetched: ', len(all_files))
    result = []
    for elm in data:
        file = find_file(all_files, name = elm['image_name'])
        if file:
            print('Adding file ID {} to {}'.format(file.id, elm['image_name']))
            elm['file_id'] = file.id
            result.append(elm)
        else:
            print(elm['image_name'], 'not found.')

    s = json.dumps(result).
    f = open('/home/pablo/Downloads/coco2017_with_ids.json', 'w')
    f.write(s)
