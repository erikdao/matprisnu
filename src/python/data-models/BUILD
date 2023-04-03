python_sources(
    name="data_models",
    sources=[
        "src/data_models/**/*.py",
    ],
    dependencies=["3rdparty/python#pydantic"],
)

resource(name="pyproject", source="pyproject.toml")

python_distribution(
    name="dist",
    dependencies=[
        ":pyproject",
    ],
    provides=python_artifact(
        name="data_models",
        version="0.1.0",
    ),
    wheel_config_settings={"--build-option": ["--python-tag", "py39"]},
    generate_setup=False,
)
