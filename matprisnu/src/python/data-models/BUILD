python_sources(
    name="data_models",
    sources=[
        "data_models/**/*.py",
    ],
    dependencies=["3rdparty/python#pydantic"],
)

python_distribution(
    name="dist",
    dependencies=[
        "3rdparty/python#pydantic",
    ],
    provides=python_artifact(
        name="data_models",
        version="0.1.0",
        description="Data models for the matprisnu project.",
        author="Erik Dao",
        author_email="cuong@neuraltalks.io",
        readme="README.md",
        classifiers=[
            "Programming Language :: Python :: 3.9",
        ],
    ),
    wheel_config_settings={"--global-option": ["--python-tag", "py39"]},
)
