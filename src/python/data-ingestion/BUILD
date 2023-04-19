python_sources(
    name="data_ingestion",
    sources=[
        "src/data_ingestion/**/*.py",
    ],
    dependencies=["3rdparty/python#pydantic"],
)

resource(name="pyproject", source="pyproject.toml")

python_distribution(
    name="dist",
    dependencies=[
        ":data_ingestion",
        ":pyproject",
    ],
    provides=python_artifact(
        name="data_ingestion",
        version="0.1.0",
    ),
    wheel_config_settings={"--build-option": ["--python-tag", "py39"]},
    generate_setup=False,
)
