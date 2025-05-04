import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from xml.dom import minidom


@dataclass
class ClassAttributeDTO:
    name: str
    type: str


@dataclass
class ClassInternalConfigurationDTO:
    name: str
    attributes: list[ClassAttributeDTO]
    children: list["ClassInternalConfigurationDTO"]


class InternalConfigurationCreator:
    def __init__(self, input_file_path: str, output_file_path: str) -> None:
        self.input_file_path = input_file_path
        self.output_file_path = output_file_path

    def create(self) -> None:
        internal_configuration = self._parse_input_file()
        self._write_internal_configuration_to_xml(internal_configuration)

    def _parse_input_file(self) -> dict[str, ClassInternalConfigurationDTO]:
        tree = ET.parse(self.input_file_path)
        root = tree.getroot()

        classes_map: dict[str, ClassInternalConfigurationDTO] = {}

        for class_ in root.findall("Class"):
            name = class_.attrib["name"]
            attributes = [
                ClassAttributeDTO(name=attr.attrib["name"], type=attr.attrib["type"])
                for attr in class_.findall("Attribute")
            ]

            classes_map[name] = ClassInternalConfigurationDTO(
                name=name,
                attributes=attributes,
                children=[],
            )

        for agg in root.findall("Aggregation"):
            child = agg.attrib["source"]
            parent = agg.attrib["target"]
            classes_map[parent].children.append(classes_map[child])

        return classes_map

    def _write_internal_configuration_to_xml(
        self,
        internal_configuration: dict[str, ClassInternalConfigurationDTO],
    ) -> None:
        root = self._build_internal_configuration_tree("BTS", internal_configuration)
        pretty_xml_string = self._format_xml(ET.tostring(root, encoding="utf-8"))

        with open(self.output_file_path, "w", encoding="utf-8") as f:
            f.write(pretty_xml_string)

    def _build_internal_configuration_tree(
        self,
        class_name: str,
        internal_configuration: dict[str, ClassInternalConfigurationDTO],
    ) -> ET.Element:
        elem = ET.Element(class_name)

        for attr in internal_configuration[class_name].attributes:
            attr_elem = ET.SubElement(elem, attr.name)
            attr_elem.text = attr.type

        for child in internal_configuration[class_name].children:
            child_elem = self._build_internal_configuration_tree(child.name, internal_configuration)
            elem.append(child_elem)
        return elem

    @classmethod
    def _format_xml(cls, xml_string: str) -> str:
        pretty_xml = minidom.parseString(xml_string).toprettyxml(indent=" " * 4)
        pretty_xml = re.sub(r"^<\?xml[^>]*\?>\s*\n?", "", pretty_xml)  # убираем первую строку из xml
        return cls._convert_self_closing_tags(pretty_xml)

    @staticmethod
    def _convert_self_closing_tags(xml_text: str) -> str:
        # можно было и без этого, но т.к. в примере не было самозакрывающихся тегов, то я сделал
        def replacer(match: re.Match) -> str:
            indent = match.group(1)
            tag = match.group(2)
            return f"{indent}<{tag}>\n{indent}</{tag}>"

        pattern = r"^([ \t]*)<(\w+)([^>]*)\s*/>\s*$"
        return re.sub(pattern, replacer, xml_text, flags=re.MULTILINE)
