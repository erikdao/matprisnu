python_sources(
    name="scrappers",
    sources=[
        "scrappers/**/*.py",
    ],
    dependencies=[
        "matprisnu/src/python/data_models/src::data_models",
    ],
)

python_distribution(
    name="dist",
    dependencies=[
        "3rdparty/python#python-dotenv",
        "3rdparty/python#tornado",
        "3rdparty/python#pymongo",
        "3rdparty/python#motor",
        "3rdparty/python#loguru",
    ],
    provides=python_artifact(
        name="scrappers",
        version="0.1.0",
        description="Scrappers for collecting data from Swedish supermarkets.",
        author="Erik Dao",
        author_email="cuong@neuraltalks.io",
        readme="README.md",
        classifiers=[
            "Programming Language :: Python :: 3.9",
        ],
    ),
    # Example of setuptools config, other build backends may have other config.
    wheel_config_settings={"--global-option": ["--python-tag", "py39"]},
    # Don't use setuptools with a generated setup.py.
    # You can also turn this off globally in pants.toml:
    #
    # [setup-py-generation]
    # generate_setup_default = false
    generate_setup=True,
)