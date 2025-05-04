import os
from pathlib import Path

from artifact_generators.config_patcher import ConfigPatcher
from artifact_generators.internal_configuration import (
    InternalConfigurationCreator,
)
from artifact_generators.meta_information import (
    MetaInformationCreator,
)


def generate_artifacts(input_dir: str, output_dir: str) -> None:
    InternalConfigurationCreator.create(
        os.path.join(
            input_dir,
            "impulse_test_input.xml",
        ),
        os.path.join(
            output_dir,
            "config.xml",
        ),
    )
    MetaInformationCreator.create(
        os.path.join(
            input_dir,
            "impulse_test_input.xml",
        ),
        os.path.join(
            output_dir,
            "meta.json",
        ),
    )
    ConfigPatcher.patch_config(
        os.path.join(
            input_dir,
            "config.json",
        ),
        os.path.join(
            input_dir,
            "patched_config.json",
        ),
        os.path.join(
            output_dir,
            "delta.json",
        ),
        os.path.join(
            output_dir,
            "res_patched_config.json",
        ),
    )


if __name__ == "__main__":
    BASE_DIR = Path(__file__).resolve().parent
    output_dir = os.path.join(
        BASE_DIR,
        "out",
    )
    input_dir = os.path.join(
        BASE_DIR,
        "input",
    )
    os.makedirs(output_dir, exist_ok=True)

    generate_artifacts(input_dir, output_dir)
