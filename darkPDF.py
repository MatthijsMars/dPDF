import PyPDF2
from PyPDF2.generic import (
    ContentStream,
    DictionaryObject,
    FloatObject,
    IndirectObject,
    NameObject,
    NumberObject,
)

from PyPDF2.constants import PagesAttributes as PA

from typing import (
    Any,
    Dict,
    List,
    cast,
)

input_file = "long.pdf"
background_file = "background.pdf" # empty file with just a colored background
text_color = [FloatObject(0.847058824), FloatObject(0.870588235), FloatObject(0.91372549)]
bg_color = [FloatObject(0.180392157), FloatObject(0.203921569), FloatObject(0.250980392)]




def change_text_color(writer, ignore_byte_string_object: bool = False) -> None:
        """
        Remove text from this output.

        :param bool ignore_byte_string_object: optional parameter
            to ignore ByteString Objects.
        """

        pg_dict = cast(DictionaryObject, writer.get_object(writer._pages))
        pages = cast(List[IndirectObject], pg_dict[PA.KIDS])
        for page in pages:
            page_ref = cast(Dict[str, Any], writer.get_object(page))
            content = page_ref["/Contents"].get_object()
            if not isinstance(content, ContentStream):
                content = ContentStream(content, page_ref)
            
            i = 0
            while i < len(content.operations):
                operands, operator = content.operations[i]
                
                if operator in [b"TJ", b"Tj"]:
                    # add in color statement before every text field
                    content.operations.insert(i, (text_color, b'rg'))
                    content.operations.insert(i+1, (text_color, b'RG'))
                    i += 2                
                i += 1
            page_ref.__setitem__(NameObject("/Contents"), content)


def change_background_color(writer):
        """
        Changes the background color of a single-color empty pdf by prefixing color parameters to each page
        """

        pg_dict = cast(DictionaryObject, writer.get_object(writer._pages))
        pages = cast(List[IndirectObject], pg_dict[PA.KIDS])
        for page in pages:
            page_ref = cast(Dict[str, Any], writer.get_object(page))
            content = page_ref["/Contents"].get_object()
            if not isinstance(content, ContentStream):
                content = ContentStream(content, page_ref)
            
            commands = [
                (bg_color, b'rg'),
                (bg_color, b'RG'),
                ([NumberObject(0), NumberObject(0), NumberObject(612), NumberObject(792)], b're'),
                ([], b'f'),
            ]

            for i in range(len(commands)):
                content.operations.insert(i, commands[i])

            page_ref.__setitem__(NameObject("/Contents"), content)

def main():
    # input_pdf = open(input_file, "rb")
    input_pdf = PyPDF2.PdfReader(input_file)

    writer = PyPDF2.PdfWriter()
    for page in input_pdf.pages:
        writer.add_page(page)

    change_text_color(writer) # changes all text color
    change_background_color(writer) # adds background color to every page

    with open("new_output.pdf", "wb") as output_stream:
        writer.write(output_stream)


if __name__ == "__main__":
    main()