import os
from jinja2 import Environment, FileSystemLoader, select_autoescape, exceptions

def load_template(template_name, template_dirname="templates"):
    """load Jinja2 template"""
    template_dir = os.path.join(os.path.dirname(__file__), template_dirname)
    env = Environment(
        loader=FileSystemLoader(template_dir), autoescape=select_autoescape()
    )
    return env.get_template(template_name)
