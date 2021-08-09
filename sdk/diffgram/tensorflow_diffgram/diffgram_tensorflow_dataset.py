from diffgram.core.diffgram_dataset_iterator import DiffgramDatasetIterator
import os


class DiffgramTensorflowDataset(DiffgramDatasetIterator):

    def __init__(self, project, diffgram_file_id_list = None):
        """

        :param project (sdk.core.core.Project): A Project object from the Diffgram SDK
        :param diffgram_file_list (list): An arbitrary number of file ID's from Diffgram.
        :param transform (callable, optional): Optional transforms to be applied on a sample
        """
        super(DiffgramDatasetIterator, self).__init__(project, diffgram_file_id_list)
        global tf
        try:
            import tensorflow as tf  # type: ignore
        except ModuleNotFoundError:
            raise ModuleNotFoundError(
                "'tensorflow' module should be installed to convert the Dataset into tensorflow format"
            )
        self.diffgram_file_id_list = diffgram_file_id_list

        self.project = project
        self.__validate_file_ids()

    def int64_feature(self, value):
        return tf.train.Feature(int64_list = tf.train.Int64List(value = [value]))

    def int64_list_feature(self, value):
        return tf.train.Feature(int64_list = tf.train.Int64List(value = value))

    def bytes_feature(self, value):
        return tf.train.Feature(bytes_list = tf.train.BytesList(value = [value]))

    def bytes_list_feature(self, value):
        return tf.train.Feature(bytes_list = tf.train.BytesList(value = value))

    def float_feature(self, value):
        return tf.train.Feature(float_list = tf.train.FloatList(value = [value]))

    def float_list_feature(self, value):
        return tf.train.Feature(float_list = tf.train.FloatList(value = value))

    def __validate_file_ids(self):
        result = self.project.file.file_list_exists(self.diffgram_file_id_list)
        if not result:
            raise Exception(
                'Some file IDs do not belong to the project. Please provide only files from the same project.')

    def __iter__(self):
        self.current_file_index = 0
        return self

    def __next__(self):
        file_id = self.diffgram_file_id_list[self.current_file_index]
        diffgram_file = self.project.file.get_by_id(file_id, with_instances = True)
        instance_data = self.get_file_instances(diffgram_file)
        filename, file_extension = os.path.splitext(instance_data['diffgram_file']['image']['original_filename'])
        print('instance_data', instance_data)
        tf_example_dict = {
            'image/height': self.int64_feature(instance_data['diffgram_file']['height']),
            'image/width': self.int64_feature(instance_data['diffgram_file']['width']),
            'image/filename': self.bytes_feature(filename),
            'image/source_id': self.bytes_feature(filename),
            'image/encoded': self.bytes_feature(instance_data['image']),
            'image/format': self.bytes_feature(file_extension),
            'image/object/bbox/xmin': self.float_list_feature(instance_data['x_min_list']),
            'image/object/bbox/xmax': self.float_list_feature(instance_data['x_max_list']),
            'image/object/bbox/ymin': self.float_list_feature(instance_data['y_min_list']),
            'image/object/bbox/ymax': self.float_list_feature(instance_data['y_max_list']),
            'image/object/class/text': self.bytes_list_feature(instance_data['label_name_list']),
            'image/object/class/label': self.int64_list_feature(instance_data['label_id_list']),
        }
        tf_example = tf.train.Example(features = tf.train.Features(feature = tf_example_dict))
        self.current_file_index += 1
        return tf_example

    def get_dataset_obj(self):
        return tf.data.Dataset.from_generator(self.__iter__)