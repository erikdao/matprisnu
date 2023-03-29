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
        # Dependencies on code to be packaged into the distribution.
    ],
    provides=python_artifact(
        name="data_models",
        version="0.1.0",
        description="Data models for the matprisnu project.",
        author="Erik Dao",
        author_email="cuong@neuraltalks.io",
        readme="README.md",
        classifiers=[
            "Programming Language :: Python :: 3.7",
        ],
    ),
    # Example of setuptools config, other build backends may have other config.
    wheel_config_settings={"--global-option": ["--python-tag", "py39"]},
    # Don't use setuptools with a generated setup.py. 
    # You can also turn this off globally in pants.toml:
    #
    # [setup-py-generation]
    # generate_setup_default = false
    generate_setup = True,
)