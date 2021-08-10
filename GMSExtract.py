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
import sys
import re


class GMSExtract:
    h_pattern = re.compile(r"(?:(?<!EU)H[0-9]{3})(?:\s*\+\s*(?<!EU)H[0-9]{3})*")
    p_pattern = re.compile(r"(?:P[0-9]{3})(?:\s*\+\s*P[0-9]{3})*")
    euh_pattern = re.compile(r"(?:EUH[0-9]{3})(?:\s*\+\s*EUH[0-9]{3})*")
    wgk_pattern = re.compile(r"WGK.*?[0-3]")
    WGK_pattern = re.compile(r"[Ww]assergefährdungsklasse.*?[0-3]")

    OUTPUT_SEP = ";"

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
        max_pages = 12

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
        return list(set(GMSExtract.h_pattern.findall(string)))

    @staticmethod
    def match_p(string: str) -> List[str]:
        """
        Find all matches for P-Statements in the given input string using regular expressions

        :param string: input string containing P-Statements
        :return: list of unique P-Statements as strings
        """
        return list(set(GMSExtract.p_pattern.findall(string)))

    @staticmethod
    def match_euh(string: str) -> List[str]:
        """
        Find all matches for EUH-Statements in the given input string using regular expressions

        :param string: input string containing EUH-Statements
        :return: list of unique EUH-Statements as strings
        """
        return list(set(GMSExtract.euh_pattern.findall(string)))

    @staticmethod
    def match_wgk(string: str) -> str:
        """
        Find first match for WGK (Wassergefährdungsklasse) in the given input string using regular expressions

        :param string: input string containing WGK information
        :return: WGK as string, empty if none found
        """
        match: List[str] = GMSExtract.wgk_pattern.findall(string) + GMSExtract.WGK_pattern.findall(string)
        return "" if match == [] else match[0][-1]

    @staticmethod
    def process(string: str) -> Tuple[List[str], List[str], List[str], str]:
        """
        Find all matches for H-/P-/EUH-Statements and WGK (Wassergefährdungsklasse) in the given input string.

        :param string: input string containing H-/P-/EUH-Statements
        :return: three lists containing the H-/P-/EUH-Statements as described in the designated methods and WGK
        """
        normalized_string: str = GMSExtract.normalize_string(string)

        h_match = GMSExtract.match_h(normalized_string)
        p_match = GMSExtract.match_p(normalized_string)
        euh_match = GMSExtract.match_euh(normalized_string)
        wgk_match = GMSExtract.match_wgk(normalized_string)

        return h_match, p_match, euh_match, wgk_match

    @staticmethod
    def process_all(strings: List[str]) -> Tuple[List[List[str]], List[List[str]], List[List[str]], List[str]]:
        """
        Process each string in the passed list of strings as described in the process method

        :param strings: list of input strings containing H-/P-/EUH-Statements
        :return: three lists containing the lists of H-/P-/EUH-Statements from each file and a list of WGKs
        """

        matches: Tuple[List[List[str]], List[List[str]], List[List[str]], List[str]] = ([], [], [], [])

        for string in strings:
            for index, match in enumerate(GMSExtract.process(string)):
                matches[index].append(match)

        return matches

    @staticmethod
    def print_excel(h_match: List[str], p_match: List[str], euh_match: List[str], wgk: str, filename: str) -> None:
        """
        Print the H-/P-/EUH-Statements and the WGK (Wassergefährdungsklasse) in a manner that allow the output
        string to be copy + pasted into excel

        :param h_match: List containing all matches for H-Statements as described in match_h
        :param p_match: List containing all matches for P-Statements as described in match_p
        :param euh_match: List containing all matches for EUH-Statements as described in match_euh
        :param wgk: String of WGK ("Wassergefährdungsklasse") value, empty if non found
        :param filename: Name of the file the H-/P-/EUH-Statements were taken from. Empty if not from file
        """

        if len(h_match) + len(p_match) + len(euh_match) + len(wgk) == 0:
            print(f"\nFinished extracting. No Statements were found{(' in ' + filename) if filename != '' else ''}.")
            return

        prefix = filename + ": \t" if filename != "" else ""
        print("\nFinished extracting. The following line can be copy + pasted into excel.")
        print(prefix + GMSExtract.OUTPUT_SEP.join([", ".join(h_match), ", ".join(p_match), ", ".join(euh_match), wgk]))

    @staticmethod
    def string_excel(h_match: List[str], p_match: List[str], euh_match: List[str],
                     wgk: str, filename: str) -> Tuple[str, bool]:
        """
        Create string from the H-/P-/EUH-Statements and the WGK (Wassergefährdungsklasse) in a manner that allow the
        returned string to be copy + pasted into excel

        :param h_match: List containing all matches for H-Statements as described in match_h
        :param p_match: List containing all matches for P-Statements as described in match_p
        :param euh_match: List containing all matches for EUH-Statements as described in match_euh
        :param wgk: String of WGK ("Wassergefährdungsklasse") value, empty if non found
        :param filename: Name of the file the H-/P-/EUH-Statements were taken from. Empty if not from file
        :return: formatted string containing the H-/P-/EUH-Statements and the WGK
        """
        prefix = filename + "\t" if filename != "" else ""

        if len(h_match) + len(p_match) + len(euh_match) + len(wgk) == 0:
            return prefix + "No Statements found.", False

        return prefix + GMSExtract.OUTPUT_SEP.join([", ".join(h_match), ", ".join(p_match),
                                                    ", ".join(euh_match), wgk]), True

    @staticmethod
    def string_excel_all(h_matches: List[List[str]], p_matches: List[List[str]], euh_matches: List[List[str]],
                         wgks: List[str], filenames: List[str]) -> str:
        """
        Create string from the H-/P-/EUH-Statements and WGK from each file as described in the string_excel method and
        concatenate them to a table-like output string.

        :param h_matches: List containing all lists of matches for H-Statements for each input file/text
        :param p_matches: List containing all lists of matches for P-Statements for each input file/text
        :param euh_matches: List containing all lists of matches for EUH-Statements for each input file/text
        :param wgks: List containing all WGKs from each input file/text
        :param filenames: List containing all input filenames.
        :return: Concatenated table-like string containing formatted data on all input files/texts
        """
        found_statements: List[str] = []
        not_found_statements: List[str] = []

        for values in zip(h_matches, p_matches, euh_matches, wgks, filenames):
            string, found = GMSExtract.string_excel(*values)

            if found:
                found_statements.append(string)
            else:
                not_found_statements.append(string)

        return "\n".join(found_statements + not_found_statements)


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
            sys.exit(0)

        input_read = input("> ")
        input_buffer += input_read + " "

    input_buffer = input_buffer.strip()

    if input_buffer.split(".")[-1].lower() == "pdf":
        print("\nInterpreting input as path to pdf file(s).")
        try:
            # Get all files matching input with extension '.pdf' or '.PDF' without duplicates
            file_list = glob(input_buffer)
            file_list_upper = glob(".".join(input_buffer.split(".")[:-1]) + ".PDF")
            file_list_upper = list(filter(lambda x: ".".join(x.split(".")[:-1]) + ".pdf" not in file_list,
                                          file_list_upper))

            file_list = list(set(file_list + file_list_upper))

            if len(file_list) == 0:
                raise FileNotFoundError("No files found.")

            return GMSExtract.read_pdf_multiple(file_list), file_list
        except FileNotFoundError:
            print("File could not be found. Interpreting input as plain text.")
    return [input_buffer], [""]


if __name__ == '__main__':
    while True:
        text_inputs, input_files = get_input()

        input_files = list(map(lambda file: file.split("\\")[-1], input_files))

        print("\n" + "#" * 150 + "\n")

        # for name, text in zip(input_files, text_inputs):
        #     GMSExtract.print_excel(*GMSExtract.process(text), name)

        print(GMSExtract.string_excel_all(*GMSExtract.process_all(text_inputs), input_files))

        print("\n" + "#" * 150 + "\n")
