import fitz
import os
from utils import Question
from PIL import Image
import io
import json
from bs4 import BeautifulSoup
import base64
from io import BytesIO

def organizeText(text_list):
    text_str = ''
    for t in text_list:
        text_str += t
    text_by_newline = text_str.split('\n')
    new_text = ''
    temp_letter = ''
    add_letter = False

    for elem in text_by_newline:
        elem = elem.strip(" ")
        if elem not in ['A', 'B', 'C', 'D', 'E', 'F', 'G']:
            if add_letter:
                new_text += f'{temp_letter} {elem}\n'
                add_letter = False
            else:
                new_text += f'{elem}\n'
        else:
            temp_letter = elem
            add_letter = True
    #print(new_text)
    return new_text

def pdfExtractorToHTML(file_pdf):
    doc = fitz.open(file_pdf)
    image_num = 0
    file_name = os.path.basename(file_pdf).rsplit(".", 1)[0]

    with open(f'{file_name}.txt', 'w', encoding='utf-8', errors='replace') as text_file:
        for page_num in range(doc.page_count):
            page = doc[page_num]
            page_html = page.get_text('html')
            soup = BeautifulSoup(page_html, 'html.parser')

            n_p = soup.find('div')
            p_children = n_p.findChildren(['p', 'img'], recursive=False)
            for pimg_child in p_children:
                temp_text_line = ''
                temp_answer_line = '$'
                temp_psyko_line = '¤'

                img_64 = None
                try:
                    img_64 = pimg_child['src'].split(',', 1)[-1]
                except:
                    pass

                psyko_list = pimg_child.select('[style="font-family:Arial,serif;font-size:10.0pt;color:#ed1c24"]')
                text_list = pimg_child.select('[style*="font-family:Arial,serif;font-size:10.0pt;color:#363639"]')
                answer_list = pimg_child.select('[style="font-family:Arial,serif;font-size:10.0pt;color:#0071a2"]')
                end_list = pimg_child.select('[style="font-family:Arial,serif;font-size:3.0pt;color:#363639"]')

                temp_text = ''
                for text in text_list:
                    temp_text += text.get_text()
                temp_text_line += temp_text

                for answer in answer_list:
                    temp_answer_line += answer.get_text()

                for psyko in psyko_list:
                    temp_psyko_line += psyko.get_text()

                if img_64 != None:
                    image = Image.open(BytesIO(base64.b64decode(img_64)))
                    image_name = f'{file_name}_image{image_num}.png'
                    temp_text_line += f'[{image_name}]\n'
                    image.save(image_name)
                    image_num += 1

                if temp_text_line != '':
                    if temp_text not in ['A', 'B', 'C', 'D', 'E', 'F', 'G']:
                        text_file.write(f'{temp_text_line}\n')
                    else:
                        text_file.write(f'{temp_text_line} ')

                if temp_answer_line != '$':
                    text_file.write(f'{temp_answer_line}\n')

                if temp_psyko_line != '¤':
                    text_file.write(f'{temp_psyko_line}\n')

                if end_list != []:
                    text_file.write(f'#end#\n')

def pdfExtractorToHTMLprint(file_pdf):
    doc = fitz.open(file_pdf)
    image_num = 0
    file_name = os.path.basename(file_pdf).rsplit(".", 1)[0]

    for page_num in range(doc.page_count):
        page = doc[page_num]
        page_html = page.get_text('html')
        soup = BeautifulSoup(page_html, 'html.parser')

        n_p = soup.find('div')
        p_children = n_p.findChildren(['p', 'img'], recursive=False)
        for pimg_child in p_children:
            temp_text_line = ''
            temp_answer_line = '$'
            temp_psyko_line = '¤'

            img_64 = None
            try:
                img_64 = pimg_child['src'].split(',', 1)[-1]
            except:
                pass

            psyko_list = pimg_child.select('[style="font-family:Arial,serif;font-size:10.0pt;color:#ed1c24"]')
            text_list = pimg_child.select('[style*="font-family:Arial,serif;font-size:10.0pt;color:#363639"]')
            answer_list = pimg_child.select('[style="font-family:Arial,serif;font-size:10.0pt;color:#0071a2"]')
            end_list = pimg_child.select('[style="font-family:Arial,serif;font-size:3.0pt;color:#363639"]')

            temp_text = ''
            for text in text_list:
                temp_text += text.get_text()
            temp_text_line += temp_text

            for answer in answer_list:
                temp_answer_line += answer.get_text()

            for psyko in psyko_list:
                temp_psyko_line += psyko.get_text()

            if img_64 != None:
                #image = Image.open(BytesIO(base64.b64decode(img_64)))
                image_name = f'{file_name}_image{image_num}.png'
                temp_text_line += f'[{image_name}]\n'
                #image.save(image_name)
                image_num += 1

            if temp_text_line != '':
                if temp_text not in ['A', 'B', 'C', 'D', 'E', 'F', 'G']:
                    print(f'{temp_text_line}\n')
                    pass
                else:
                    print(f'{temp_text_line} ')
                    pass

            if temp_answer_line != '$':
                print(f'{temp_answer_line}\n')
                pass

            if temp_psyko_line != '¤':
                print(f'{temp_psyko_line}\n')
                pass

            if end_list != []:
                print(f'#end#\n')
                pass

def textToJsonImproved(text_pth):
    file_name = os.path.basename(text_pth).rsplit(".", 1)[0]
    question_list = []
    count = 1
    choice_list = ['A', 'B', 'C', 'D', 'E', 'F', 'G']

    with io.open(text_pth, 'r', encoding='utf-8', errors='replace') as obj:
        lines = obj.readlines()
        last_line = None
        temp_question = None
        temp_text = ''

        for line in lines:
            no_newline = line.replace('\n', '')
            no_newline_strip = no_newline.strip(' ')
            if no_newline_strip != '':
                if no_newline_strip == f'{count}':
                    temp_question = Question()
                    temp_question.set_question_set(file_name)
                    temp_question.set_question_number(count)
                    #temp_question.print_all_info()
                    count += 1
                    last_line = 'start'

                elif no_newline_strip[0] == '¤':
                    if last_line == 'start':
                        temp_text = no_newline_strip[1:]
                        last_line = 'psyko_text'
                    elif last_line == 'psyko_text':
                        temp_text += f' {no_newline_strip[1:]}'
                        last_line = 'psyko_text'

                    elif last_line == 'choice_text':
                        temp_question.set_answer(choice, temp_text)
                        temp_text = no_newline_strip[1:]
                        last_line = 'psyko_explaination_text'
                    elif last_line == 'psyko_explaination_text':
                        temp_text += f' {no_newline_strip[1:]}'
                        last_line = 'psyko_explaination_text'

                elif no_newline_strip[0] == '[' and no_newline_strip[-1] == ']':
                    if last_line == 'question_text':
                        temp_question.add_image_id(no_newline_strip[1:-1])
                        last_line = 'question_text'

                elif no_newline_strip.split(' ', 1)[0] in choice_list:
                    if last_line == 'question_text':
                        temp_question.set_question_text(temp_text)

                    elif last_line == 'choice_text':
                        temp_question.set_answer(choice, temp_text)

                    elif last_line == 'psyko_explaination_text':
                        temp_question.set_psyko(choice, temp_text)

                    elif last_line == 'explaination_text':
                        temp_question.set_explaination(choice, temp_text)

                    if no_newline_strip.split(' ', 2)[1] == 'X':
                        print(text_pth)
                        print(no_newline_strip)
                        choice, _, choice_text = no_newline_strip.split(' ', 2)
                        temp_question.set_answer_tag(choice)
                    else:
                        choice, choice_text = no_newline_strip.split(' ', 1)
                    temp_text = choice_text.lstrip()
                    last_line = 'choice_text'

                elif no_newline_strip[0] == '$':
                    if last_line == 'choice_text':
                        temp_question.set_answer(choice, temp_text)
                        temp_text = no_newline_strip[1:]

                    elif last_line == 'explaination_text':
                        temp_text += f' {no_newline_strip[1:]}'

                    elif last_line == 'psyko_explaination_text':
                        temp_question.set_psyko(choice, temp_text)
                        temp_text = no_newline_strip[1:]
                    last_line = 'explaination_text'

                elif no_newline_strip[0:5] == '#end#':
                    if last_line == 'choice_text':
                        temp_question.set_answer(choice, temp_text)

                    elif last_line == 'explaination_text':
                        temp_question.set_explaination(choice, temp_text)

                    elif last_line == 'psyko_explaination_text':
                        temp_question.set_psyko(choice, temp_text)
                    question_list.append(temp_question)
                    temp_text = ''
                    last_line = 'end'
                else:
                    if last_line == 'psyko_text':
                        temp_question.set_psyko_text(temp_text)
                        temp_text = no_newline_strip
                        last_line = 'question_text'

                    elif last_line == 'start':
                        temp_text = no_newline_strip
                        last_line = 'question_text'

                    elif last_line == 'question_text':
                        temp_text += f' {no_newline_strip}'
                        last_line = 'question_text'

                    elif last_line == 'choice_text':
                        temp_text += f' {no_newline_strip}'
                        last_line = 'choice_text'

                    elif last_line == 'psyko_explaination_text':
                        temp_question.set_psyko(choice, temp_text)
                        temp_question.set_answer(choice, temp_question.abcd[choice]['answer'] + f' {no_newline_strip}')

    out_dict = dict()
    for question in question_list:
        all_question_info = question.get_all_info_as_dict()
        out_dict[f'{all_question_info["question_set"]}_{all_question_info["question_number"]}'] = all_question_info

    out_json = json.dumps(out_dict)
    # print(out_json)
    with open(f'{file_name}.json', "w", encoding='utf-8', errors='replace') as outfile:
        outfile.write(out_json)



def textToJson(text_pth):
    file_name = os.path.basename(text_pth).rsplit(".", 1)[0]
    question_list = []
    count = 1
    choice_list = ['A', 'B', 'C', 'D', 'E', 'F', 'G']

    with io.open(text_pth, 'r', encoding='utf-8', errors='replace') as obj:
        lines = obj.readlines()
        last_line = None
        temp_question = None
        temp_text = ''

        for line in lines:
            no_newline = line.replace('\n', '')
            # print(last_line)

            if last_line == 'start':
                temp_text = no_newline
                last_line = 'question_text'
            elif last_line == 'question_text' and no_newline.split(' ', 1)[0] not in choice_list:
                try:
                    if no_newline[0] == '[' and no_newline[-1] == ']':
                        temp_question.add_image_id(no_newline[1:-1])
                    else:
                        temp_text += f' {no_newline}'
                        last_line = 'question_text'
                except Exception as e:
                    temp_text += f' {no_newline}'
                    last_line = 'question_text'

            if last_line == 'choice_text' and no_newline[0:5] == '#end#':
                temp_question.set_answer(choice, temp_text)
                temp_text = ''
                question_list.append(temp_question)
                last_line = 'end'

            if last_line == 'explaination_text' and no_newline[0:5] == '#end#':
                temp_question.set_explaination(choice, temp_text)
                temp_text = ''
                question_list.append(temp_question)
                last_line = 'end'

            if last_line == 'question_text' and no_newline.split(' ', 1)[0] in choice_list:
                temp_question.set_question_text(temp_text)

                if no_newline.split(' ', 2)[1] == 'X':
                    choice, _, choice_text = no_newline.split(' ', 2)
                    temp_question.set_answer_tag(choice)
                else:
                    choice, choice_text = no_newline.split(' ', 1)

                choice_text = choice_text.lstrip()
                temp_text = choice_text
                last_line = 'choice_text'

            if last_line == 'explaination_text' and no_newline.split(' ', 1)[0] in choice_list:
                temp_question.set_explaination(choice, temp_text)

                if no_newline.split(' ', 2)[1] == 'X':
                    choice, _, choice_text = no_newline.split(' ', 2)
                    temp_question.set_answer_tag(choice)
                else:
                    choice, choice_text = no_newline.split(' ', 1)

                choice_text = choice_text.lstrip()
                temp_text = choice_text
                last_line = 'choice_text'

            if last_line == 'choice_text' and no_newline.split(' ', 1)[0] in choice_list:
                temp_question.set_answer(choice, temp_text)

                if no_newline.split(' ', 2)[1] == 'X':
                    choice, _, choice_text = no_newline.split(' ', 2)
                    temp_question.set_answer_tag(choice)
                else:
                    choice, choice_text = no_newline.split(' ', 1)

                choice_text = choice_text.lstrip()
                temp_text = choice_text
                last_line = 'choice_text'

            if last_line == 'choice_text' and no_newline[0] == '•':
                temp_question.set_answer(choice, temp_text)
                temp_text = no_newline[1:]
                last_line = 'explaination_text'
            elif last_line == 'explaination_text' and no_newline[0] == '•':
                temp_temp = no_newline[1:]
                temp_text += f' {temp_temp}'
                last_line = 'explaination_text'

            if last_line == 'choice_text' and no_newline.split(' ', 1)[0] not in choice_list:
                temp_text += f' {no_newline}'
                last_line = 'choice_text'

            if no_newline == f'{count}':
                temp_question = Question()
                temp_question.set_question_set(file_name)
                temp_question.set_question_number(count)
                #temp_question.print_all_info()
                count += 1
                last_line = 'start'

    out_dict = dict()
    for question in question_list:
        all_question_info = question.get_all_info_as_dict()
        out_dict[f'{all_question_info["question_set"]}_{all_question_info["question_number"]}'] = all_question_info

    out_json = json.dumps(out_dict)
    #print(out_json)
    with open(f'{file_name}.json', "w", encoding='utf-8', errors='replace') as outfile:
        outfile.write(out_json)

def printJson(json_pth):
    file_json = open(json_pth)
    file_dict = json.load(file_json)

    for q in file_dict:
        print(q)
        print(file_dict[q])

if __name__ == '__main__':
    #pdf = 'Nasjonal felles avsluttende skriftlig deleksamen i medisin høst 2021 - Revidert fasit etter sensur bokmål.pdf'
    #pdfExtractorToHTML(pdf)
    #textToJsonImproved(f'{pdf.rsplit(".")[0]}.txt')

    folder_pth = 'alle_fasiter'
    file_pdfs = []

    for dirName, subdirList, fileList in os.walk(folder_pth):
        for fname in fileList:
            file_pdfs.append(os.path.join(dirName, fname))
            #print(os.path.join(dirName, fname, fname))

    #print(len(file_pdfs))
    for pdf in file_pdfs:
        #pdfExtractorToHTML(pdf) #comment out after fixing txt files because of outliers, makes txt files
        pdf_name = os.path.basename(pdf).rsplit(".", 1)[0] #makes json
        textToJsonImproved(f'{pdf_name}.txt')

        #printJson(f'{pdf.rsplit(".")[0]}.json')


