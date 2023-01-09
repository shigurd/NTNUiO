import os

def move_files(input_dir, out_text):
    file_list = []
    with open(out_text, 'w', encoding='utf-8', errors='replace') as text_file:
        for dirName, subdirList, fileList in os.walk(input_dir):
            for fname in fileList:
                if fname.rsplit('.', 1)[-1] == 'json':
                    file_list.append(fname)
        text_file.write(f'{file_list}')


if __name__ =='__main__':
    input_dir = '.'
    move_files(input_dir, 'file_list.txt')