import os
import ast
import pandas as pd
from dotenv import load_dotenv
from diffgram import Project
import time

start_time = time.time()

load_dotenv()

image_list = os.listdir('images')

project = Project(
    project_string_id = os.getenv('PROJECT_STRING_ID'),
    client_id = os.getenv('CLIENT_ID'),
    client_secret = os.getenv('CLIENT_SECRET'),
    host = os.getenv('HOST')
)

list = project.directory.get(name="Default").list_files()

for file in list:
    original_filename = file.__dict__['original_filename']
    initia_filename = original_filename.replace('_', ' (').replace('.', ').')
    if initia_filename in image_list:
        image_list.remove(initia_filename)

shema_list = project.get_label_schema_list()

number_of_images = None
while True:
    try:
        number_of_images_to_import = input("How many images do you want to import? (blank to import all) ")
        if number_of_images_to_import == '':
            number_of_images = len(image_list)
            break
        number_of_images = int(number_of_images_to_import)
        break
    except:
        print("Invalid input: please input positive number")

image_list = image_list[:number_of_images]

new_schema_name = None
imported_label_traker = []
lables_objects = {}
while True:
    try:
        new_schema_name = input("Shema name (if shema with this name already exists - it will be used, otherwise new shema will be created): ")
        shema_list = project.get_label_schema_list()
        schema = [existing_schema for existing_schema in shema_list if existing_schema.get('name') == new_schema_name]
        if not schema:
            schema = project.new_schema(name=new_schema_name)
            print("Schema successfully created")
        else:
            schema = schema[0]
            schema_label_list = project.get_label_list(schema.get('id'))
            for label in schema_label_list:
                imported_label_traker.append(label['label']['name'])
                lables_objects[label['label']['name']] = label
            pass
        break
    except:
        print("Seems like schema with this name already exists")

df = None
while True:
    try:
        annotation_file_name = input("What is the name of the file with annotations? (leave blank to use default Overhead-Distribution-Labels.csv)")
        if not annotation_file_name:
            df = pd.read_csv ('Overhead-Distribution-Labels.csv')
            break
        df = pd.read_csv (annotation_file_name)
        break
    except:
        print("Seems like annotation file is not here")

succeslully_imported = []
import_errors = []

for image in image_list:
    image_relate_df = df[df['External ID'] == image]
    labels = image_relate_df['Label']
    external_id = image_relate_df['External ID']

    instance_list = []

    for label in labels:
        label_dict = ast.literal_eval(label)

        for object in label_dict['objects']:
            label = {}

            if object['value'] not in imported_label_traker:
                label = project.label_new({'name': object['value']}, schema.get('id'))
                lables_objects[label['label']['name']] = label
            else:
                label = lables_objects[object['value']]

            polygone = object.get('polygon')
            line = object.get('line')

            if polygone:
                instance_list.append({
                    "type": 'polygon',
                    "points": polygone,
                    "label_file_id": label['id']
                })
            elif line:
                pass
            else:
                pass

            imported_label_traker.append(object['value'])
        
        try:
            result = project.file.from_local(
                path=f'./images/{image}', 
                instance_list = instance_list,
                convert_names_to_label_files=False
            )

            succeslully_imported.append(image)

            print(f'{image} has been imported with {len(instance_list)} annotation(s)')
        except:
            import_errors.append(image)
            print(f'Error ocurred while importing {image}')

print(f"Successfully imported {len(succeslully_imported)} file(s): ", succeslully_imported)
print(f"Errors while importing {len(succeslully_imported)} file(s): ", import_errors)

print("--- %s seconds ---" % (time.time() - start_time))