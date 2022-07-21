from csv import DictReader
from collections import defaultdict
import logging
from cocat.vocabulary import Vocabulary
from cocat.model import Model
from cocat.property import Property

LOGGER = logging.getLogger(__name__)

class CSVConfig:
    '''System init configuration from CSV file that list all the properties for the different model list and initialize Vocabualry Properties and Models'''
    def __init__(self, csv_file, conf_dir="./"):
        self.csv_file = csv_file
        
    @property
    def properties(self) -> list:
        properties = []
        with open(self.csv_file, "r") as f:
            reader = DictReader(f, delimiter=",")
            for row in reader:
                r = Property.parse_obj(row)
                properties.append(r)
        return properties
    @property
    def vocabularies(self) -> dict:
        vocabularies = dict()
        with open(self.csv_file, "r") as f:
            reader = DictReader(f, delimiter=",")
            
            
            for row in reader:
                if row["vocabulary_name"] is not None:
                    vocabularies[row["vocabulary_name"]] = row["vocabulary_filename"]
        for voc_name, voc_file in vocabularies.items():
            if voc_file not in ["", None] and voc_name not in ["", None]:
                voc_filepath = os.path.join(os.path.dirname(__file__),voc_file)
                if os.path.isfile(voc_filepath):
                    vocabularies[voc_name] = Vocabulary(name=voc_name, filename=voc_file, csv_file=voc_filepath)
                else:
                    LOGGER.warning(f"<Vocabulary(name={voc_name} is not initialized. Declare file doesn't exist")
                    vocabularies[voc_name] = Vocabulary(name=voc_name)
            
        return vocabularies
    
    @property
    def models(self) -> list:
        models = dict()
        d_models = defaultdict(list)
        with open(self.csv_file, "r") as f:
            reader = DictReader(f, delimiter=",")
            for row in reader:
                d_models[row["model"]].append(row)
        for model, rules in d_models.items():
            models[model] = Model(model, rules)
        return models
        #         
        # models[row["model"]] = []
        #     for row in reader:
        #         models[row["model"]].append(row)
        
        # for model, props in models.items():
        #     models[model] = Model(model,props)
        # return models