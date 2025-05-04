import json


class ConfigPatcher:
    def __init__(
        self,
        config_input_file: str,
        patched_config_input_file: str,
        delta_output_file: str,
        res_patched_config_output_file: str,
    ) -> None:
        self.config_input_file = config_input_file
        self.patched_config_input_file = patched_config_input_file
        self.delta_output_file = delta_output_file
        self.res_patched_config_output_file = res_patched_config_output_file

    def patch_config(self) -> None:
        self._create_delta_json()
        self._create_res_patched_config_json()

    def _create_delta_json(self) -> None:
        with open(self.config_input_file, "r") as f:
            original = json.load(f)

        with open(self.patched_config_input_file, "r") as f:
            patched = json.load(f)

        additions = []
        deletions = []
        updates = []

        for key in original:
            if key not in patched:
                deletions.append(key)
            elif original[key] != patched[key]:
                updates.append({"key": key, "from": original[key], "to": patched[key]})

        for key in patched:
            if key not in original:
                additions.append({"key": key, "value": patched[key]})

        delta = {"additions": additions, "deletions": deletions, "updates": updates}

        with open(self.delta_output_file, "w", encoding="utf-8") as f:
            json.dump(delta, f, indent=4, ensure_ascii=False)

    def _create_res_patched_config_json(self) -> None:
        with open(self.config_input_file, "r") as f:
            config = json.load(f)

        with open(self.delta_output_file, "r") as f:
            delta = json.load(f)

        for key in delta["deletions"]:
            config.pop(key)

        for update in delta["updates"]:
            config[update["key"]] = update["to"]

        for addition in delta["additions"]:
            config[addition["key"]] = addition["value"]

        with open(self.res_patched_config_output_file, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
