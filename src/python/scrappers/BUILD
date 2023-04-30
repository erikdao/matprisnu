python_sources(
    name="scrappers",
    sources=[
        "src/scrappers/**/*.py",
    ],
    dependencies=[
        "3rdparty/python#pydantic",
        "3rdparty/python#python-dotenv",
        "3rdparty/python#tornado",
        "3rdparty/python#motor",
        "3rdparty/python#pymongo",
        "3rdparty/python#click",
        "3rdparty/python#sentry-sdk",
        "3rdparty/python#loguru",
        "3rdparty/python#luigi",
        "3rdparty/python#couchdb",
        "3rdparty/python#genson",
        "3rdparty/python#boto3",
    ],
)

resource(name="pyproject", source="pyproject.toml")

python_distribution(
    name="dist",
    dependencies=[
        ":scrappers",
        ":pyproject",
    ],
    provides=python_artifact(
        name="scrappers",
        version="0.2.0",
    ),
    # Example of setuptools config, other build backends may have other config.
    wheel_config_settings={"--build-option": ["--python-tag", "py39"]},
    generate_setup=False,
)

pex_binary(
    name="scrappers-cli",
    entry_point="src/scrappers/cli.py:main",
    dependencies=[":pyproject", ":scrappers", "src/python/data-models:data_models"],
    output_path="scrappers-cli.pex",
)
