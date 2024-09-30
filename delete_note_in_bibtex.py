import re


def remove_note_from_bibtex(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as file:
        bibtex_content = file.read()

    # Regular expression to find the note field
    note_pattern = re.compile(r'\s*note\s*=\s*\{[^}]*\},?\n', re.IGNORECASE)

    # Remove all note fields
    modified_content = re.sub(note_pattern, '', bibtex_content)

    with open(output_file, 'w', encoding='utf-8') as file:
        file.write(modified_content)


# 使用示例
input_file = 'input.bib'
output_file = 'output.bib'
remove_note_from_bibtex(input_file, output_file)
