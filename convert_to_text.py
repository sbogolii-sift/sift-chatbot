import os

from bs4 import BeautifulSoup

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
file_path = 'api-reference.html'
page_dir = os.path.join(ROOT_DIR, 'api-reference')

if not os.path.exists(page_dir):
    os.makedirs(page_dir)


def li_to_text(li, level_separator=''):
    text = ''
    for element in li.children:
        if element.name == 'ul':
            text += '\n' + ul_to_text(element, level_separator + '-')
        else:
            text += ' ' + element.get_text(strip=True, separator=' ')
    return text


def ul_to_text(ul, level_separator):
    list_if_items = []
    for element in ul.children:
        if element.name == 'ul':
            list_if_items.append(ul_to_text(element, level_separator + '-'))
        elif element.name == 'li':
            list_if_items.append(level_separator + li_to_text(element, level_separator))
        else:
            list_if_items.append(element.get_text())
    return '\n'.join(list_if_items)


def ul_table_to_text(ul, prefix=''):
    rows = []
    headers = []
    rowIndex = 0
    inner_lists = {}
    previous_element_name = ''
    for element in ul.children:
        if element.name == 'ul':
            inner_lists[previous_element_name] = element
            continue
        if 'class' in element.attrs and element['class'] == ['header']:
            for headerDiv in element.children:
                headers.append(headerDiv.get_text())
        else:
            if len(headers) > 0:
                cellIndex = 0
                key = ''
                for cell in element.children:
                    if cellIndex == 0:
                        key = cell.get_text(strip=True, separator=' ')
                    else:
                        if cellIndex >= len(headers):
                            continue
                        previous_element_name = f'{prefix} {headers[cellIndex]}'
                        rows.append(
                            f'---\nKEY\n{prefix} {headers[cellIndex]} for {headers[0]} {key}\n'
                            f'VALUE\n{li_to_text(cell)}\n---')
                    cellIndex += 1
            else:
                cellIndex = 0
                key = ''
                for cell in element.children:
                    if cellIndex == 0:
                        key = cell.get_text(strip=True, separator=' ')
                    else:
                        previous_element_name = f'{prefix} {key}'
                        rows.append(f'---\nKEY\n{prefix} {key}\n' +
                                    f'VALUE\n{li_to_text(cell)}\n---')
                    cellIndex += 1

        rowIndex += 1

    list_text = ''.join(rows)

    for inner_list_key in inner_lists.keys():
        list_text += '\n\n' + ul_table_to_text(inner_lists[inner_list_key], inner_list_key)

    return list_text


def code_to_text(div):
    list_of_code_snippets = []
    for element in div.find_all('pre'):
        text = '---\nCODE\n'
        if 'curl' in element.attrs['class']:
            text += 'Curl'
        elif 'java' in element.attrs['class']:
            text += 'Java'
        elif 'ruby' in element.attrs['class']:
            text += 'Ruby'
        elif 'python' in element.attrs['class']:
            text += 'Python'
        elif 'php' in element.attrs['class']:
            text += 'PHP'
        else:
            text += 'Unrecognized Language'
        text += f'\nVALUE\n{element.get_text()}\n---'
        list_of_code_snippets.append(text)
    return '\n\n'.join(list_of_code_snippets)


def div_to_text(div):
    text = ''
    for element in div.children:
        if element.name == 'h1':
            text += '\n\n\n' + element.get_text() + '\n'
        if element.name == 'h2' or element.name == 'h3' or element.name == 'h4':
            text += '\n' + element.get_text() + '\n'
        if element.name == 'div' and 'class' in element.attrs \
                and element['class'] == ['code-container']:
            text += '\n\n' + code_to_text(element) + '\n'
        elif element.name == 'div':
            text += '\n' + div_to_text(element) + '\n'
        if element.name == 'p':
            text += '\n' + element.get_text(strip=True, separator=' ')
        if element.name == 'ul' and 'class' in element.attrs and element['class'] == ['api-fields']:
            text += '\n' + ul_table_to_text(element)
        elif element.name == 'ul':
            text += '\n' + ul_to_text(element, '-')
    return text


with open(file_path, 'r') as f:
    contents = f.read()
    html_parse = BeautifulSoup(contents, 'html.parser')
    single_file_path = "api-reference.txt"
    with open(single_file_path, "a", encoding="utf-8") as single_file:
        for div in html_parse.find_all("div"):
            try:
                firstElement = next(div.children)
                if firstElement.name == 'h1' or firstElement.name == 'h2' \
                        or firstElement.name == 'h3':
                    single_file.write(div_to_text(div).replace(" ", " "))
            except StopIteration:
                continue
