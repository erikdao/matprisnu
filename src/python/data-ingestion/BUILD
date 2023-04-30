python_sources(
    name="data_ingestion",
    sources=[
        "src/data_ingestion/**/*.py",
    ],
    dependencies=[
        "3rdparty/python#polars",
        "3rdparty/python#pyarrow",
        "3rdparty/python#sqlalchemy",
        "3rdparty/python#pandas",
        "3rdparty/python#psycopg2-binary",
        "3rdparty/python#loguru",
        "3rdparty/python#genson",
    ],
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

pex_binary(
    name="ingestion-cli",
    entry_point="src/data_ingestion/cli.py:main",
    dependencies=[
        ":pyproject",
        ":data_ingestion",
        "src/python/data-models:data_models",
    ],
    output_path="ingestion-cli.pex",
)
