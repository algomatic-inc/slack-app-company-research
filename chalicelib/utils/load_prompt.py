from jinja2 import Environment, FileSystemLoader


def load_prompt(template_path: str, **kwargs) -> str:
    dirname, filename = template_path.rsplit("/", 1)
    env = Environment(
        loader=FileSystemLoader(dirname),
        trim_blocks=True
    )
    prompt_template = env.get_template(filename)
    prompt = prompt_template.render(**kwargs)
    return prompt
