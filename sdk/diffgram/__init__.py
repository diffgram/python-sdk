import os
__name__ = "diffgram"
__version__ = os.getenv('DIFFGRAM_SDK_VERSION')

from diffgram.core.core import Project
from diffgram.file.file import File
from diffgram.task.task import Task
from diffgram.models.base_model import DiffgramBaseModel
from diffgram.models.model_interfaces import  DiffgramFile, Prediction, Attribute, Instance
