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
    @classmethod
    def create(cls, input_file: str, output_file: str) -> None:
        internal_configuration = cls._parse_input(input_file)
        cls._write_internal_configuration(internal_configuration, output_file)

    @staticmethod
    def _parse_input(input_file: str) -> dict[str, ClassInternalConfigurationDTO]:
        tree = ET.parse(input_file)
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

    @classmethod
    def _write_internal_configuration(
        cls, internal_configuration: dict[str, ClassInternalConfigurationDTO], output_file: str
    ) -> None:
        root = cls._build_internal_configuration_tree("BTS", internal_configuration)

        rough_string = ET.tostring(root, encoding="utf-8")
        pretty_xml = minidom.parseString(rough_string).toprettyxml(indent="    ")
        pretty_xml = re.sub(r"^<\?xml[^>]*\?>\s*\n?", "", pretty_xml)  # убираем первую строку из xml
        pretty_xml = cls._convert_self_closing_tags(pretty_xml)

        with open(output_file, "w", encoding="utf-8") as f:
            f.write(pretty_xml)

    @classmethod
    def _build_internal_configuration_tree(
        cls,
        class_name: str,
        internal_configuration: dict[str, ClassInternalConfigurationDTO],
    ) -> ET.Element:
        elem = ET.Element(class_name)

        for attr in internal_configuration[class_name].attributes:
            attr_elem = ET.SubElement(elem, attr.name)
            attr_elem.text = attr.type

        for child in internal_configuration[class_name].children:
            child_elem = cls._build_internal_configuration_tree(child.name, internal_configuration)
            elem.append(child_elem)
        return elem

    @staticmethod
    def _convert_self_closing_tags(xml_text: str) -> str:
        # можно было и без этого, но т.к. в примере не было самозакрывающихся тегов, то я сделал
        def replacer(match: re.Match) -> str:
            indent = match.group(1)
            tag = match.group(2)
            return f"{indent}<{tag}>\n{indent}</{tag}>"

        pattern = r"^([ \t]*)<(\w+)([^>]*)\s*/>\s*$"
        return re.sub(pattern, replacer, xml_text, flags=re.MULTILINE)
