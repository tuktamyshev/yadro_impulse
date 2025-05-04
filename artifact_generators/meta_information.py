import json
import xml.etree.ElementTree as ET
from dataclasses import dataclass


@dataclass
class ClassParameterDTO:
    name: str
    type: str


@dataclass
class ClassMetaInformationDTO:
    name: str
    documentation: str
    isRoot: bool
    max: str | None
    min: str | None
    parameters: list[ClassParameterDTO]


class MetaInformationCreator:
    def __init__(self, input_file_path: str, output_file_path: str) -> None:
        self.input_file_path = input_file_path
        self.output_file_path = output_file_path

    def create(self) -> None:
        meta_information = self._parse_input()
        self._write_meta_information(meta_information)

    def _parse_input(self) -> dict[str, ClassMetaInformationDTO]:
        tree = ET.parse(self.input_file_path)
        root = tree.getroot()

        classes_map: dict[str, ClassMetaInformationDTO] = {}

        for class_ in root.findall("Class"):
            name = class_.attrib["name"]
            classes_map[name] = ClassMetaInformationDTO(
                name=name,
                documentation=class_.attrib["documentation"],
                isRoot=class_.attrib["isRoot"] == "true",
                parameters=[],
                max=None,
                min=None,
            )

            for attr in class_.findall("Attribute"):
                classes_map[name].parameters.append(
                    ClassParameterDTO(
                        name=attr.attrib["name"],
                        type=attr.attrib["type"],
                    ),
                )

        for agg in root.findall("Aggregation"):
            child = agg.attrib["source"]
            parent = agg.attrib["target"]
            source_mult = agg.attrib["sourceMultiplicity"]

            if ".." in source_mult:
                min_val, max_val = source_mult.split("..")
            else:
                min_val = max_val = source_mult

            classes_map[child].min = min_val
            classes_map[child].max = max_val

            classes_map[parent].parameters.append(
                ClassParameterDTO(
                    type="class",
                    name=child,
                ),
            )

        return classes_map

    def _write_meta_information(self, meta_information: dict[str, ClassMetaInformationDTO]) -> None:
        result = []
        for _, class_ in meta_information.items():
            parameters = [{"name": param.name, "type": param.type} for param in class_.parameters]
            obj = {
                "class": class_.name,
                "documentation": class_.documentation,
                "isRoot": class_.isRoot,
                "parameters": parameters,
            }
            if class_.min is not None:
                obj["min"] = class_.min
            if class_.max is not None:
                obj["max"] = class_.max
            result.append(obj)

        with open(self.output_file_path, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=4, ensure_ascii=False)
