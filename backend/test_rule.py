from .rule import Rule
# from .rule import CSVItem
def cast_type_from_str_to_python(element):
    if element in ["True", "False"]:
        return bool(element)
    if element.isnumeric():
        return int(element)
    # elif "-" in element or ":" in  element:
    return element

def test_rule_001():
    """
    test init from a fake oneliner csv
    """
    header = "field,model,name_fr,name_en,section_order,section_name_fr,section_name_en,external_model_name,external_model_display_keys,is_controled,reference_table,vocab,inspire,translation,multiple,constraint,datatype,format,search,filter,admin,list,item,required,description_fr,description_en,example_fr,example_en,default_fr,comment,default_en"
    value = "environment_detail,dataset,Milieu,,4,Santé Environnement,Health and Environnement,reference,name|id,True,ref_environment_detail,dcat:themeTaxonomy: skos,,True,True,one of,string,,True,False,18,18,18,True,Ce champ permet de définir le milieu concerné par la ressource à partir d'un vocabulaire contrôlé interne,,N/D,N/D,N/D,champ par défault en cours de construction,"
    matrix = []
    for element in value.split(","):
        if "|" in element:
            matrix.append([cast_type_from_str_to_python(e) for e in element.split("|")])
        else:
            matrix.append(cast_type_from_str_to_python(element))
    rule_d = dict(zip(header.split(","),matrix))
    print(rule_d)
    r = Rule(**rule_d)
    assert r.is_controled
    assert r.multiple
    assert r.required
    assert r.filter
    assert r.search
    assert r.external_model_name == "reference"
    assert r.admin != -1