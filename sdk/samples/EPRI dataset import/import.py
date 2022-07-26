import os
import ast
import pandas as pd
from dotenv import load_dotenv
from diffgram import Project

load_dotenv()

image_list = os.listdir('images')

project = Project(
    project_string_id = os.getenv('PROJECT_STRING_ID'),
    client_id = os.getenv('CLIENT_ID'),
    client_secret = os.getenv('CLIENT_SECRET'),
    host = os.getenv('HOST')
)

number_of_images = None
while number_of_images is None:
    try:
        number_of_images_to_import = input("How many images do you want to import? (blank to import all) ")
        if not number_of_images_to_import:
            number_of_images = len(image_list)
        number_of_images = int(number_of_images_to_import)
    except:
        print("Invalid input: please input positive number")

image_list = image_list[:int(number_of_images_to_import)]

new_schema_name = None
while True:
    try:
        new_schema_name = input("Give a name for a new schema: ")
        schema = project.new_schema(name=new_schema_name)
        print("Schema successfully created")
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

imported_label_traker = []
lables_objects = {}

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