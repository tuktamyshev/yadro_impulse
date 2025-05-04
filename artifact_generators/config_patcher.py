class ConfigPatcher:
    @classmethod
    def patch_config(cls, input_file: str, output_file: str) -> None:
        cls._create_delta_json()
        cls._create_res_patched_config_json()

    @staticmethod
    def _create_delta_json() -> None:
        pass

    @staticmethod
    def _create_res_patched_config_json() -> None:
        pass
