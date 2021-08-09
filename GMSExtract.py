"""
Script created by Martin Bienert.
Python version used: 3.8.5 (should be compatible with any 3.x, as no 'new' features were used)

This script is intended to be used for extracting the H-/P-/EUH-Statements
from chemicals' safety data sheets. The extracted Statements will be returned
as TAB-separated Lists of the COMMA-separated statements in order of their discovery
within the input.
e.g. H319, H335, H315	P261, P302 + P352, P280, P305 + P351 + P338, P271	EUH061

Input may be the path to a pdf file, finished with an empty input line.
If a path to a pdf file was recognized the program will confirm, that the input will be interpreted as such.
    > aceton.pdf
    >

    Interpreting input as path of pdf file.

Input may alternatively be the entire safety data sheet as text, finished with an empty input line.
    > Sicherheitsinformationen gemäß GHS Gefahrensymbol(e)￼
    > Gefahrenhinweis(e)
    > H315: Verursacht Hautreizungen.
    > H319: Verursacht schwere Augenreizung.
    > H335: Kann die Atemwege reizen.
    > Sicherheitshinweis(e)
    > P261: Einatmen von Staub/ Rauch/ Gas/ Nebel/ Dampf/ Aerosol vermeiden.
    > P271: Nur im Freien oder in gut belüfteten Räumen verwenden.
    > P280: Schutzhandschuhe/ Augenschutz/ Gesichtsschutz tragen.
    > P302 + P352: BEI BERÜHRUNG MIT DER HAUT: Mit viel Wasser waschen.
    > P305 + P351 + P338: BEI KONTAKT MIT DEN AUGEN: Einige Minuten lang behutsam mit Wasser spülen.
    > Eventuell vorhandene Kontaktlinsen nach Möglichkeit entfernen. Weiter spülen.
    > Ergänzende Gefahrenhinweise EUH061
    > SignalwortAchtungLagerklasse10 - 13 Sonstige Flüssigkeiten und
    > FeststoffeWGKWGK 1 schwach wassergefährdendEntsorgung3
    >

"""

from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.pdfpage import PDFPage
from pdfminer.layout import LAParams
from typing import List, Tuple
from io import StringIO
from glob import glob
import re


class GMSExtract:
    h_pattern = r"(?:(?<!EU)H[0-9]{3})(?:\s*\+\s*(?<!EU)H[0-9]{3})*"
    p_pattern = r"(?:P[0-9]{3})(?:\s*\+\s*P[0-9]{3})*"
    euh_pattern = r"(?:EUH[0-9]{3})(?:\s*\+\s*EUH[0-9]{3})*"

    @staticmethod
    def read_pdf(filename: str) -> str:
        """
        Code taken from @RattleyCooper and @Trenton McKinney at
        https://stackoverflow.com/questions/26494211/extracting-text-from-a-pdf-file-using-pdfminer-in-python

        Read content of pdf file to string

        :param filename: relative or absolute path of input pdf file
        :return: content of input pdf file as text
        """

        resource_manager = PDFResourceManager()
        params = LAParams()
        output_string = StringIO()
        codec = 'utf-8'
        device = TextConverter(resource_manager, output_string, codec=codec, laparams=params)
        interpreter = PDFPageInterpreter(resource_manager, device)

        fp = open(filename, 'rb')
        page_numbers = set()
        caching = True
        password = ""
        max_pages = 3

        for page in PDFPage.get_pages(fp, page_numbers, maxpages=max_pages, password=password, caching=caching,
                                      check_extractable=True):
            interpreter.process_page(page)

        content_text = output_string.getvalue()

        fp.close()
        device.close()
        output_string.close()

        return content_text

    @staticmethod
    def read_pdf_multiple(filenames: List[str]) -> List[str]:
        """
        Read contents of all files in filenames
        :param filenames: List containing filenames and paths to pdf files
        :return: List containing the contents of each of the passed pdf files as strings
        """
        file_contents: List[str] = []

        for filename in filenames:
            file_contents.append(GMSExtract.read_pdf(filename))

        return file_contents


    @staticmethod
    def normalize_string(string: str) -> str:
        """
        Replace all linebreaks with whitespaces and normalize amount of whitespaces around '+' to exactly one
        :param string: string that is to be normalized
        :return: normalized string
        """
        return re.sub(r"\n+", " ", re.sub(r"\s*\+\s*", " + ", string))

    @staticmethod
    def match_h(string: str) -> List[str]:
        """
        Find all matches for H-Statements in the given input string using regular expressions
        :param string: input string containing H-Statements
        :return: list of unique H-Statements as strings
        """
        return list(set(re.findall(GMSExtract.h_pattern, string)))

    @staticmethod
    def match_p(string: str) -> List[str]:
        """
        Find all matches for P-Statements in the given input string using regular expressions
        :param string: input string containing P-Statements
        :return: list of unique P-Statements as strings
        """
        return list(set(re.findall(GMSExtract.p_pattern, string)))

    @staticmethod
    def match_euh(string: str) -> List[str]:
        """
        Find all matches for EUH-Statements in the given input string using regular expressions
        :param string: input string containing EUH-Statements
        :return: list of unique EUH-Statements as strings
        """
        return list(set(re.findall(GMSExtract.euh_pattern, string)))

    @staticmethod
    def process(string: str) -> Tuple[List[str], List[str], List[str]]:
        """
        Find all matches for H-/P-/EUH-Statements in the given input string.
        :param string: input string containing H-/P-/EUH-Statements
        :return: tuple of three lists containing the H-/P-/EUH-Statements as described in the designated methods
        """
        normalized_string: str = GMSExtract.normalize_string(string)

        h_match = GMSExtract.match_h(normalized_string)
        p_match = GMSExtract.match_p(normalized_string)
        euh_match = GMSExtract.match_euh(normalized_string)

        return h_match, p_match, euh_match

    @staticmethod
    def print_excel(h_match: List[str], p_match: List[str], euh_match: List[str], filename: str) -> None:
        """
        Print the H-/P-/EUH-Statements in a manner that allow the output string to be copy + pasted into excel
        :param h_match: List containing all matches for H-Statements as described in match_h
        :param p_match: List containing all matches for P-Statements as described in match_p
        :param euh_match: List containing all matches for EUH-Statements as described in match_euh
        :param filename: Name of the file the H-/P-/EUH-Statements were taken from. Empty if not from file
        """
        if len(h_match) + len(p_match) + len(euh_match) == 0:
            print(f"\nFinished extracting. No Statements were found{(' in ' + filename) if filename != '' else ''}.")
            return

        prefix = filename + ": \t" if filename != "" else ""
        print("\nFinished extracting. The following line can be copy + pasted into excel.")
        print(prefix + "\t".join([", ".join(h_match), ", ".join(p_match), ", ".join(euh_match)]))


def get_input() -> Tuple[List[str], List[str]]:
    """
    Read text from input prompt until an empty line is sent and the input up to this point is non-empty.
    If the text input is recognized to be a path to a pdf file, there will be an attempt to open the file
    and return its contents as text. If the attempt fails or no path was recognized, the input text will
    be returned.
    :return: Tuple of a list of the plain input texts or contents of passed pdf file(s) as text and the filenames
    """
    input_buffer = ""

    print("Paste text or insert path to pdf ('*' may be used in filename). Finish input with empty line.")
    input_read: str = input("> ")
    input_buffer += input_read

    while input_read != "" or input_buffer.strip() == "":
        if input_read == "quit":
            print("\nExit keyword detected. Terminating.")
            quit()

        input_read = input("> ")
        input_buffer += input_read + " "

    input_buffer = input_buffer.strip()

    if input_buffer.split(".")[-1] == "pdf":
        print("\nInterpreting input as path to pdf file(s).")
        try:
            file_list = glob(input_buffer)

            if len(file_list) == 0:
                raise FileNotFoundError("No files found.")

            return GMSExtract.read_pdf_multiple(file_list), file_list
        except FileNotFoundError:
            print("File could not be found. Interpreting input as plain text.")
    return [input_buffer], [""]


if __name__ == '__main__':
    while True:
        text_inputs, input_files = get_input()

        print("\n" + "#" * 150)

        for name, text in zip(input_files, text_inputs):
            GMSExtract.print_excel(*GMSExtract.process(text), name)

        print("\n" + "#" * 150 + "\n")
