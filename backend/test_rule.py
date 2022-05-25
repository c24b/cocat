from csv import DictReader
import datetime
from .rule import Rule
# from .rule import CSVItem

def cast_type_from_str_to_python(element):
    if element in ["True", "False", 1, 0, "true", "false"]:
        return bool(element)
    if element.isnumeric():
        return int(element)
    if "-" in element and ":" in element:
        return datetime.datetime.strptime(element, "%Y-%M-%d %H:%m:%s")
    if "-" in element:
        return datetime.datetime.strptime(element, "%Y-%M-%d")
    return element

def test_rule_001():
    """
    test init from a fake oneliner csv
    """
    header = "field,model,name_fr,name_en,section_order,section_name_fr,section_name_en,external_model_name,external_model_display_keys,is_controled,reference_table,vocab,inspire,translation,multiple,constraint,datatype,format,search,filter,admin,list,item,required,description_fr,description_en,example_fr,example_en,default_fr,comment,default_en, issue_date"
    value = "environment_detail,dataset,Milieu,Environment,4,Santé Environnement,Health and Environment,reference,name|id,True,ref_environment_detail,dcat:themeTaxonomy: skos,,True,True,one of,string,,True,False,18,18,18,True,Ce champ permet de définir le milieu concerné par la ressource à partir d'un vocabulaire contrôlé interne,,N/D,N/D,N/D,champ par défault en cours de construction,N/D,2022-05-22"
    matrix = []
    for element in value.split(","):
        matrix.append(cast_type_from_str_to_python(element))
    rule_d = dict(zip(header.split(","),matrix))
    r = Rule(**rule_d)
    assert r.is_controled
    assert r.multiple
    assert r.required
    assert r.filter
    assert r.search
    assert r.external_model_name == "reference"
    assert r.external_model_display_keys == ["name", "id"]
    assert r.admin != -1
def test_rule_export_002():
    """test rules template generarion in csv"""
    header = "field,model,name_fr,name_en,section_order,section_name_fr,section_name_en,external_model_name,external_model_display_keys,is_controled,reference_table,vocab,inspire,translation,multiple,constraint,datatype,format,search,filter,admin,list,item,required,description_fr,description_en,example_fr,example_en,default_fr,comment,default_en, issue_date"
    value = "environment_detail,dataset,Milieu,Environment,4,Santé Environnement,Health and Environment,reference,name|id,True,ref_environment_detail,dcat:themeTaxonomy: skos,,True,True,one of,string,,True,False,18,18,18,True,Ce champ permet de définir le milieu concerné par la ressource à partir d'un vocabulaire contrôlé interne,,N/D,N/D,N/D,champ par défault en cours de construction,,2022/05/22"
    matrix = []
    # for element in value.split(","):
    #     matrix.append(cast_type_from_str_to_python(element))
    rule_d = dict(zip(header.split(","),value.split(",")))
    r = Rule(**rule_d)
    assert r._export("json") == "", r._export("json")
def test_rule_setter_003():
    """test with csv file"""
    with open("test_rules.csv", "r") as f:
        reader = DictReader(f, delimiter=",")
        for row in reader:
            rule_d = {}
            for k, v in row.items():
                if "|" in v:
                    v = [cast_type_from_str_to_python(e) for e in v.split("|")]
                    rule_d[k] = v
                else:
                    v = cast_type_from_str_to_python(v) 
                    rule_d[k] = v