python_sources(
    name="scrappers",
    sources=[
        "src/scrappers/**/*.py",
    ],
    dependencies=[
        "src/python/data-models/src::data_models",
    ],
)

resource(name="pyproject", source="pyproject.toml")

python_distribution(
    name="dist",
    dependencies=[
        ":pyproject",
    ],
    provides=python_artifact(
        name="scrappers",
        version="0.1.0",
    ),
    # Example of setuptools config, other build backends may have other config.
    wheel_config_settings={"--build-option": ["--python-tag", "py39"]},
)
