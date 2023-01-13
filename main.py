# -*- coding:utf-8 -*-
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import json
import random

class MCQ:
    def __init__(self, question_dict):
        self.question_set = question_dict['question_set']
        self.question_number = question_dict['question_number']
        self.question_text = question_dict['question_text']
        self.image_id = question_dict['image_id']
        self.abcd = question_dict['abcd']
        self.answer_tag = question_dict['answer_tag']
        self.completion_status = question_dict['completion_status']

    def modify_json(self):
        file_pth = f'{self.question_set}.json'

        with open(file_pth, "r") as file_json:
            file_dict_temp = json.load(file_json)

        file_dict_temp[f'{self.question_set}_{self.question_number}']['completion_status'] = self.completion_status

        with open(file_pth, "w") as file_json:
            json.dump(file_dict_temp, file_json)


def scale_image(image_pth_list, h=384, w=768):
    imgs_pil_list = []
    for pth in image_pth_list:
        img_pil = Image.open(pth)

        if img_pil.height >= h:
            aspect_ratio = img_pil.width / img_pil.height
            new_height = h
            new_width = int(new_height * aspect_ratio)

        elif img_pil.width >= w:
            aspect_ratio = img_pil.height / img_pil.width
            new_width = w
            new_height = int(new_width * aspect_ratio)
        else:
            new_width = img_pil.width
            new_height = img_pil.height

        img_pil = img_pil.resize((new_width, new_height), Image.BILINEAR)
        imgs_pil_list.append(img_pil)

    return imgs_pil_list


class QuizApp(tk.Tk):
    def __init__(self, file_path_list):
        tk.Tk.__init__(self)
        self.file_path_list = file_path_list
        self.configs_tk = {'font': 'Helvetica 12',
                           'font_i': 'Helvetica 12 italic',
                           'font_b': 'Helvetica 12 bold',
                           'w_length': 770,
                           'color_orange': '#fed06a',
                           'color_green': '#88d8b0',
                           'color_grey': '#626262',
                           'color_red': '#f96e5a',
                           'color_blue': '#65cbda'}
        self.order_var = tk.StringVar()
        self.hidden_var = tk.StringVar()
        self.year_list = [f'{y}' for y in range(2022, 2015, -1)]
        self.category_list = ['Nasjonal', 'MD4062', 'MD4061', 'MD4043', 'MD4042', 'MD4030', 'MD4020', 'MD4011']
        self.order_mode = ['Kronologisk', 'Tilfeldig']
        self.hidden_mode = ['Standard MCQ', 'Skjult MCQ']
        self.title('NTNUiO')
        self.frame_main = tk.Frame(self)
        self.frame_main.pack(padx=20, pady=20)

        self.create_frame_menu()
        self.count_relative = tk.IntVar()
        self.choice_var = tk.StringVar()

    def create_question_dock_container(self):
        self.dock_container = tk.Frame(self.frame_quiz)
        self.dock_container.grid(row=0, column=0, sticky='w')

        # Create progress bar
        self.progress_container = tk.Frame(self.dock_container)
        self.progress_container.pack()

        self.count_relative.set(int(self.current_question_index + 1) * 100 / len(self.questions))
        self.progress_count = tk.StringVar()
        self.progress_count.set(f'Progresjon: {self.current_question_index + 1} / {len(self.questions)}')
        self.correct_count = tk.StringVar()
        self.correct_count.set(f'Riktige: {0}% ({self.correct_questions} / {self.current_question_index})')
        progress_number = tk.Label(self.progress_container, textvariable=self.progress_count, font=self.configs_tk['font_i'])
        correct_percent = tk.Label(self.progress_container, textvariable=self.correct_count, font=self.configs_tk['font_i'])
        progress_number.grid(row=0, column=0)
        correct_percent.grid(row=0, column=2)

        progress_bar = ttk.Progressbar(self.progress_container, variable=self.count_relative, orient='horizontal', length=550,
                                            mode='determinate')
        progress_bar.grid(row=1, column=1)

        # Create button bar
        self.button_container = tk.Frame(self.dock_container)
        self.button_container.pack()

        menu_button = tk.Button(self.button_container, text='MENY', command=self.on_menu, bg=self.configs_tk['color_grey'], fg='white', height=1, width=13, font=self.configs_tk['font'])
        self.submit_button = tk.Button(self.button_container, text='SVAR', command=self.on_submit, bg='white', height=1, width=13, font=self.configs_tk['font'])
        skip_button = tk.Button(self.button_container, text='SKIP', command=self.on_skip, bg=self.configs_tk['color_orange'], height=1, width=13, font=self.configs_tk['font'])
        menu_button.grid(row=0, column=0)
        self.submit_button.grid(row=0, column=1)
        skip_button.grid(row=0, column=2)

        self.feedback_text = tk.Label(self.button_container, text='', font=self.configs_tk['font_b'])
        self.feedback_text.grid(row=1, column=1)

    def create_text_container(self):
        self.text_container = tk.Frame(self.frame_quiz)
        self.text_container.grid(row=1, column=0, sticky='w')

        title = f'Eksamensett: {self.questions[self.current_question_index].question_set}\nOppgave: {self.questions[self.current_question_index].question_number}'
        question_id = tk.Label(self.text_container, text=title, font=self.configs_tk['font_i'], justify='left', wraplength=self.configs_tk['w_length'], pady=10)
        question_id.pack(anchor='w')

        text = self.questions[self.current_question_index].question_text
        question_text = tk.Label(self.text_container, text=text,
                                      font=self.configs_tk['font'], justify='left', wraplength=self.configs_tk['w_length'])
        question_text.pack(anchor='w')

    def create_image_container(self):
        self.image_container = tk.Frame(self.frame_quiz)
        self.image_container.grid(row=2, column=0, sticky='')

        if len(self.questions[self.current_question_index].image_id) != 0:

            if len(self.questions[self.current_question_index].image_id) == 1:
                image_pil = scale_image(self.questions[self.current_question_index].image_id)[0]
                image_tk = ImageTk.PhotoImage(image_pil)
                self.image_label = tk.Label(self.image_container, image=image_tk)
                self.image_label.image = image_tk
                self.image_label.pack()
            else:
                self.img_index = 0

                self.list_pil = scale_image(self.questions[self.current_question_index].image_id)
                image_tk = ImageTk.PhotoImage(self.list_pil[self.img_index])
                self.image_label = tk.Label(self.image_container, image=image_tk)
                self.image_label.image = image_tk
                self.image_label.pack()

                self.image_container_buttons = tk.Frame(self.image_container)
                self.image_container_buttons.pack()
                self.left_scroll_button = tk.Button(self.image_container_buttons, text='<', command=self.on_leftscroll,
                                                    bg='white', font=self.configs_tk['font_b'],
                                                    height=1, width=2, state='disabled')
                self.right_scroll_button = tk.Button(self.image_container_buttons, text='>',
                                                     command=self.on_rightscroll, bg='white', font=self.configs_tk['font_b'],
                                                     height=1, width=2)

                self.img_count = tk.StringVar()
                self.img_count.set(f'Bilde: {self.img_index + 1} / {len(self.list_pil)}')
                self.img_counter = tk.Label(self.image_container_buttons, textvariable=self.img_count,
                                      font=self.configs_tk['font_i'])

                self.img_counter.grid(row=0, column=1)
                self.left_scroll_button.grid(row=0, column=0)
                self.right_scroll_button.grid(row=0, column=2)

    def create_choice_container(self):
        self.choice_container = tk.Frame(self.frame_quiz)
        self.choice_container.grid(row=3, column=0, sticky='w')

        self.choice_explainations = []
        self.choice_explaination_contents = []

        self.choice_var.set('0')
        for choice in self.questions[self.current_question_index].abcd:
            choice_text = f'{choice}: {self.questions[self.current_question_index].abcd[choice]["answer"]}'
            button = tk.Radiobutton(self.choice_container, text=choice_text, variable=self.choice_var, value=choice,
                                    font=self.configs_tk['font_b'], justify='left', wraplength=self.configs_tk['w_length'])
            button.pack(anchor='w')
            try:
                explaination = f'{choice}: {self.questions[self.current_question_index].abcd[choice]["explaination"]}'
            except:
                explaination = f'{choice}: Ingen forklaring'

            choice_explanation = tk.Label(self.choice_container, text='', font=self.configs_tk['font'], justify='left', wraplength=self.configs_tk['w_length'])
            choice_explanation.pack(anchor='w')
            self.choice_explaination_contents.append(explaination)
            self.choice_explainations.append(choice_explanation)


    def create_frame_quiz(self):
        self.frame_quiz = tk.Frame(self.frame_main)
        self.frame_quiz.pack()

        self.create_question_dock_container()
        self.create_text_container()
        self.create_image_container()
        if self.hidden_var.get() == 'Skjult MCQ':
            self.submit_button.configure(text='VIS', command=self.on_show)
        else:
            self.create_choice_container()

    def create_year_box_container(self):
        self.year_box_container = tk.Frame(self.lower_menu_container)
        self.year_box_container.grid(row=1, column=0, sticky='nw')

        box_label = tk.LabelFrame(self.year_box_container, text='ÅRGANG', font=self.configs_tk['font_b'], padx=40, pady=20)
        box_label.pack()
        self.check_label_year = []
        self.check_label_year_vars = []

        for y in self.year_list:
            self.check_label_year_vars.append(tk.IntVar())
            check_label = tk.Checkbutton(box_label, text=y, variable=self.check_label_year_vars[-1],
                                         font=self.configs_tk['font'])
            self.check_label_year.append(check_label)
            check_label.pack(anchor='w')

        select_all_button = tk.Button(box_label, text='Velg alle', command=lambda:self.on_selectall(self.check_label_year),
                                      bg='white', font=self.configs_tk['font'],
                                      height=1, width=7)
        remove_all_button = tk.Button(box_label, text='Fjern alle', command=lambda:self.on_deselectall(self.check_label_year),
                                      bg='white', font=self.configs_tk['font'],
                                      height=1, width=7)
        select_all_button.pack()
        remove_all_button.pack()


    def create_category_box_container(self):
        self.category_box_container = tk.Frame(self.lower_menu_container)
        self.category_box_container.grid(row=1, column=1, sticky='nw')

        box_label = tk.LabelFrame(self.category_box_container, text='EKSAMENSETT', font=self.configs_tk['font_b'], padx=40, pady=20)
        box_label.pack()
        self.check_label_category = []
        self.check_label_category_vars = []

        for e in self.category_list:
            self.check_label_category_vars.append(tk.IntVar())
            check_label = tk.Checkbutton(box_label, text=e, variable=self.check_label_category_vars[-1], font=self.configs_tk['font'])
            self.check_label_category.append(check_label)
            check_label.pack(anchor='w')

        select_all_button = tk.Button(box_label, text='Velg alle', command=lambda:self.on_selectall(self.check_label_category),
                                      bg='white', font=self.configs_tk['font'],
                                      height=1, width=7)
        remove_all_button = tk.Button(box_label, text='Fjern alle', command=lambda:self.on_deselectall(self.check_label_category),
                                      bg='white', font=self.configs_tk['font'],
                                      height=1, width=7)
        select_all_button.pack()
        remove_all_button.pack()


    def create_order_box_container(self):
        self.order_box_container = tk.Frame(self.lower_menu_container)
        self.order_box_container.grid(row=1, column=2, sticky='nw')

        box_label = tk.LabelFrame(self.order_box_container, text='REKKEFØLGE', font=self.configs_tk['font_b'], padx=40, pady=20)
        box_label.pack()

        self.order_var.set('0')
        for r in self.order_mode:
            button = tk.Radiobutton(box_label, text=r, variable=self.order_var, value=r, font=self.configs_tk['font'])
            button.pack(anchor='w')

    def create_hidden_mode_container(self):
        self.hidden_mode_container = tk.Frame(self.lower_menu_container)
        self.hidden_mode_container.grid(row=1, column=3, sticky='nw')

        box_label = tk.LabelFrame(self.hidden_mode_container, text='MODUS', font=self.configs_tk['font_b'], padx=40, pady=20)
        box_label.pack()

        self.hidden_var.set('0')
        for r in self.hidden_mode:
            button = tk.Radiobutton(box_label, text=r, variable=self.hidden_var, value=r, font=self.configs_tk['font'])
            button.pack(anchor='w')


    def create_menu_dock_container(self):
        self.start_container = tk.Frame(self.upper_menu_container)
        self.start_container.pack()

        start_button = tk.Button(self.start_container, text='START', command=self.on_start, bg=self.configs_tk['color_green'], height=1,
                                       width=13, font=self.configs_tk['font'])
        start_button.grid(row=1, column=2)

        stats_button = tk.Button(self.start_container, text='VIS UTVALG', command=self.on_check,
                                 bg='white', height=1, width=13, font=self.configs_tk['font'])
        stats_button.grid(row=1, column=3)

        reset_button = tk.Button(self.start_container, text='RESET', command=self.on_reset,
                                 bg=self.configs_tk['color_grey'], fg='white', height=1, width=13, font=self.configs_tk['font'])
        reset_button.grid(row=1, column=1)

        self.remaining_questions_number = tk.Label(self.start_container, text='Fullført: 0% (0 / 0)',
                                                   font=self.configs_tk['font'], justify='left',
                                                   wraplength=self.configs_tk['w_length'])
        self.remaining_questions_number.grid(row=0, column=4, sticky='nw')
        white_space = tk.Label(self.start_container, text='୧ ( ´ ◉ ◞౪◟ ◉ ) ୨',
                                                   font=self.configs_tk['font'], justify='left',
                                                   wraplength=self.configs_tk['w_length'])
        white_space.grid(row=0, column=0, sticky='nw')


    def create_menu_info_container(self):
        self.menu_info_container = tk.Frame(self.frame_menu)
        self.menu_info_container.pack(pady=20)

        info_text = tk.Label(self.menu_info_container, text='RESET: Tilbakestiller oppgaver som er fullført for utvalget.\nSTART: Starter quiz for utvalget. Fullførte ekskluderes med mindre de tilbakestilles.\nVIS UTVALG: Viser antall oppgaver og fullføringsgrad for utvalget.', font=self.configs_tk['font_i'], justify='left',
                               wraplength=self.configs_tk['w_length'], pady=10)
        info_text.pack(anchor='w')

        text = tk.Label(self.menu_info_container, text='Kilder:\nhttps://www.uio.no/studier/program/medisin/tidligere-eksamensoppgaver/felles-avsluttende-deleksamen/\nhttps://i.ntnu.no/wiki/-/wiki/Norsk/Eksamensoppgaver+-+Medisin+-+MH',
                                 font=self.configs_tk['font'], justify='left', wraplength=self.configs_tk['w_length'])
        text.pack(anchor='w')

    def create_frame_menu(self):
        self.questions = []
        self.questions_completed = []
        self.current_question_index = 0
        self.correct_questions = 0

        self.frame_menu = tk.Frame(self.frame_main)
        self.frame_menu.pack()

        self.upper_menu_container = tk.Frame(self.frame_menu)
        self.upper_menu_container.pack()
        self.create_menu_dock_container()

        self.create_menu_info_container()

        self.lower_menu_container = tk.Frame(self.frame_menu)
        self.lower_menu_container.pack()
        self.create_year_box_container()
        self.create_category_box_container()
        self.create_order_box_container()
        self.create_hidden_mode_container()


    def create_quiz_page(self):
        self.frame_menu.destroy()
        self.create_frame_quiz()

    def on_show(self):
        self.submit_button.configure(text='SVAR', command=self.on_submit)
        self.create_choice_container()

    def on_reset(self):
        if sum([yv.get() for yv in self.check_label_year_vars]) > 0 and sum([cv.get() for cv in self.check_label_category_vars]) > 0:
            included_year_tags = []
            for y in zip(self.year_list, self.check_label_year_vars):
                if y[1].get() == 1:
                    included_year_tags.append(y[0])

            included_category_tags = []
            for c in zip(self.category_list, self.check_label_category_vars):
                if c[1].get() == 1:
                    included_category_tags.append(c[0])

            included_paths = []
            for pth in self.file_path_list:
                no_ext = pth.rsplit('.', 1)[0].lower()
                for yt in included_year_tags:
                    for ct in included_category_tags:
                        if yt.lower() in no_ext and ct.lower() in no_ext:
                            included_paths.append(pth)

            completed_questions = []
            for pth in included_paths:
                file_json = open(pth)
                try:
                    file_dict = json.load(file_json)
                except:
                    print(file_json)

                for q in range(1, len(file_dict) + 1):
                    question = MCQ(file_dict[f'{pth.rsplit(".", 1)[0]}_{q}'])
                    if question.completion_status == 1:
                        completed_questions.append(question)

            for r in completed_questions:
                r.completion_status = 0
                r.modify_json()

    def on_check(self):
        included_year_tags = []
        for y in zip(self.year_list, self.check_label_year_vars):
            if y[1].get() == 1:
                included_year_tags.append(y[0])

        included_category_tags = []
        for c in zip(self.category_list, self.check_label_category_vars):
            if c[1].get() == 1:
                included_category_tags.append(c[0])

        included_paths = []
        for pth in self.file_path_list:
            no_ext = pth.rsplit('.', 1)[0].lower()
            for yt in included_year_tags:
                for ct in included_category_tags:
                    if yt.lower() in no_ext and ct.lower() in no_ext:
                        included_paths.append(pth)

        included_questions = 0
        completed_questions = 0

        for pth in included_paths:
            file_json = open(pth)
            try:
                file_dict = json.load(file_json)
            except:
                print(file_json)

            for q in range(1, len(file_dict) + 1):
                question = MCQ(file_dict[f'{pth.rsplit(".", 1)[0]}_{q}'])
                if question.completion_status == 0:
                    included_questions += 1
                else:
                    completed_questions += 1

        if included_questions + completed_questions > 0:
            self.remaining_questions_number.configure(text=f'Fullført: {int(completed_questions * 100 / (completed_questions + included_questions))}% ({completed_questions} / {completed_questions + included_questions})')
        else:
            self.remaining_questions_number.configure(text=f'Fullført: 0% (0 / 0)')


    def on_start(self):
        if self.order_var.get() != '0' and self.hidden_var.get() != '0' and sum([yv.get() for yv in self.check_label_year_vars]) > 0 and sum([cv.get() for cv in self.check_label_category_vars]) > 0:

            included_year_tags = []
            for y in zip(self.year_list, self.check_label_year_vars):
                if y[1].get() == 1:
                    included_year_tags.append(y[0])

            included_category_tags = []
            for c in zip(self.category_list, self.check_label_category_vars):
                if c[1].get() == 1:
                    included_category_tags.append(c[0])

            included_paths = []
            for pth in self.file_path_list:
                no_ext = pth.rsplit('.', 1)[0].lower()
                for yt in included_year_tags:
                    for ct in included_category_tags:
                        if yt.lower() in no_ext and ct.lower() in no_ext:
                            included_paths.append(pth)

            included_questions = []
            for pth in included_paths:
                file_json = open(pth)
                try:
                    file_dict = json.load(file_json)
                except:
                    print(file_json)

                for q in range(1, len(file_dict) + 1):
                    question = MCQ(file_dict[f'{pth.rsplit(".", 1)[0]}_{q}'])
                    if question.completion_status == 0:
                        included_questions.append(question)

            if self.order_var.get() == 'Tilfeldig':
                random.shuffle(included_questions)

            self.questions = included_questions

            if len(included_questions) > 0:
                self.create_quiz_page()


    def on_selectall(self, check_box_list):
        for i in check_box_list:
            i.select()

    def on_deselectall(self, check_box_list):
        for i in check_box_list:
            i.deselect()

    def on_leftscroll(self):
        self.img_index -= 1
        image_tk = ImageTk.PhotoImage(self.list_pil[self.img_index])
        self.image_label.configure(image=image_tk)
        self.image_label.image = image_tk

        if self.img_index == 0:
            self.left_scroll_button.configure(state='disabled')

        self.right_scroll_button.configure(state='normal')
        self.img_count.set(f'Bilde: {self.img_index + 1} / {len(self.list_pil)}')

    def on_rightscroll(self):
        self.img_index += 1
        image_tk = ImageTk.PhotoImage(self.list_pil[self.img_index])
        self.image_label.configure(image=image_tk)
        self.image_label.image = image_tk

        if self.img_index == len(self.list_pil) - 1:
            self.right_scroll_button.configure(state='disabled')

        self.left_scroll_button.configure(state='normal')
        self.img_count.set(f'Bilde: {self.img_index + 1} / {len(self.list_pil)}')

    def on_skip(self):
        self.current_question_index += 1
        if self.current_question_index >= len(self.questions):
            self.destroy()
        else:
            # Update the widgets with the new question
            self.count_relative.set(int(self.current_question_index + 1) * 100 / len(self.questions))
            self.progress_count.set(f'Progresjon: {self.current_question_index + 1} / {len(self.questions)}')
            self.correct_count.set(f'Riktige: {int(self.correct_questions * 100 / (self.current_question_index))}% ({self.correct_questions} / {self.current_question_index})')

            self.submit_button.configure(text='SVAR', command=self.on_submit, bg='white', fg='black')
            self.feedback_text.configure(text='')
            self.text_container.destroy()
            self.image_container.destroy()
            self.choice_container.destroy()

            self.create_text_container()
            self.create_image_container()
            if self.hidden_var.get() == 'Skjult MCQ':
                self.submit_button.configure(text='VIS', command=self.on_show)
            else:
                self.create_choice_container()

    def on_menu(self):
        self.frame_quiz.destroy()
        self.create_frame_menu()

    def on_submit(self):
        if self.choice_var.get() != '0':

            if self.choice_var.get() == self.questions[self.current_question_index].answer_tag:
                self.feedback_text.configure(text='RIKTIG')
                self.correct_questions += 1

                self.questions[self.current_question_index].completion_status = 1
                self.questions[self.current_question_index].modify_json()

            else:
                self.feedback_text.configure(text='FEIL')

            for ce in zip(self.choice_explainations, self.choice_explaination_contents):
                ce[0].configure(text=ce[1])
                if ce[1].strip(' ')[0] == self.questions[self.current_question_index].answer_tag:
                    ce[0].configure(bg=self.configs_tk['color_green'])
                else:
                    ce[0].configure(bg=self.configs_tk['color_orange'])

            self.submit_button.configure(text='NESTE', command=self.on_next, bg=self.configs_tk['color_green'])


    def on_next(self):
        # Move to the next question
        self.current_question_index += 1
        if self.current_question_index >= len(self.questions):
            self.destroy()
        else:
            # Update the widgets with the new question
            self.count_relative.set(int(self.current_question_index + 1) * 100 / len(self.questions))
            self.progress_count.set(f'Progresjon: {self.current_question_index + 1} / {len(self.questions)}')
            self.correct_count.set(f'Riktige: {int(self.correct_questions * 100 / (self.current_question_index))}% ({self.correct_questions} / {self.current_question_index})')

            self.submit_button.configure(text='SVAR', command=self.on_submit, bg='white', fg='black')
            self.feedback_text.configure(text='')
            self.text_container.destroy()
            self.image_container.destroy()
            self.choice_container.destroy()

            self.create_text_container()
            self.create_image_container()
            if self.hidden_var.get() == 'Skjult MCQ':
                self.submit_button.configure(text='VIS', command=self.on_show)
            else:
                self.create_choice_container()


if __name__ == '__main__':
    question_set_json_pths = ['2016 - IIAB - MD4030 - eksamen 2-2018-01-04.json', '2016 - IIID - MD4062 - eksamen 1-2016-05-23.json', '2016 - IIID - MD4062 - eksamen 2-2016-10-19 fasit FVO.json', '2017 - IID - MD4043 - eksamen 1-2017-05-16.json', '2018 - IAB - MD4011 - FVO med fasit eksamen 1-2018-05-16.json', '2018 - IAB kont - MD4011 - FVO med fasit -2018-08-14.json', '2018 - ICD - MD4020 - FVo med fasit eksamen 2-2018-06-01.json', '2018 - ICD kont - MD4020 - FVO med fasit -2018-08-14.json', '2018 - IIAB forskerlinje - MD4030- korrigert FVO med fasit - ny.json', '2018 - IIAB kont - MD4030 - FVO med fasit -2018-08-14.json', '2018 - IIC - MD4042 - FVO med fasit - eksamen 2-2018-12-13.json', '2018 - IIC - MD4042 -FVO med fasit, eksamen 1-2018-05-29.json', '2018 - IID - MD4043 - FVO med fasit - Eksamen 3.-2018-12-13.json', '2018 - IID - MD4043 -FVO med fasit 1-2018-05-28.json', '2018 - IID kont - MD4043 - FVO med fasit.json', '2018 - IIIC - MD4061 - FVO med fasit - eksamen 1-2018-12-13.json', '2018 - IIIC kont - MD4061 - FVO med fasit.json', '2018 - IIID -Kont - MD4062 - FVO med fasit.json', '2018 - IIID ordinær - MD4062 - FVO med fasit.json', '2018 ordinær - IIAB - MD4030 -FVO med fasit eksamen 1-2018-05-24.json', '2019 - IAB kont - MD4011 - FVO med fasit.json', '2019 - IAB Ordinær- MD4011 - FVO med fasit.json', '2019 - ICD kont ny - MD4020 - Fvo med fasit.json', '2019 - ICD ordinær - MD4020 - FVO med fasit.json', '2019 - IIAB Forskerlinje - MD4030 - FVO med fasit - eksamen 3-2019-04-30.json', '2019 - IIAB kont - MD4030 - FVO med fasit.json', '2019 - IIAB ordinær - MD4030 - FVO med fasit.json', '2019 - IIC kont - MD4042 - Fvo med fasit.json', '2019 - IIC Ordinær - MD4042 - FVO med fasit.json', '2019 - IIC ordinær desember- MD4042 - FVO med fasit.json', '2019 - IID desember norsk- MD4043 - FVO med fasit.json', '2019 - IID kont - MD4043 - FVO med fasit.json', '2019 - IID ordinær - MD4043 - FVO med fasit.json', '2019 - IIIC ordinær - MD4061 -FVO med fasit.json', '2019 - IIIC utsatt februar - MD4061 - FVO med fasit.json', '2019 - IIID - ordinær - MD4062 - FVO med fasit.json', '2020 - IAB -ordinær - MD4011 - FVO med fasit.json', '2020 - IAB utsatt - MD4011 - FVO med fasit.json', '2020 - ICD ordinær - MD4020 - FVO med fasit.json', '2020 - ICD utsatt - MD4020 - FVO med fasit.json', '2020 - IIAB ordinær - MD4030 - FVO med fasit.json', '2020 - IIAB utsatt - MD4030 - FVO med fasit.json', '2020 - IIC - ordinær - MD4042 - FVO med fasit.json', '2020 - IIC ordinær desember - MD4042 - FVO med fasit.json', '2020 - IID - ordinær - MD4043 - FVO med fasit.json', '2020 - IID ordinær desember - MD4043 - FVO med fasit.json', '2020 - IIIC ordinær - MD4061 - FVO med fasit.json', '2020 - IIID -ordinær MD4062 - FVO med fasit.json', '2020 - IIID kont - MD4062 - FVO med begrunnelse.json', '2020 januar - IIAB forskerlinje- MD4030 - FVO med fasit.json', '2021 - IAB kont - MD4011 - FVO med fasit.json', '2021 - IAB ordinær - MD4011 - FVO med fasit.json', '2021 - ICD kont - MD4020 - FVO med fasit.json', '2021 - ICD ordinær - MD4020 - FVO med fasit.json', '2021 - IIAB forskerlinje ordinær - MD4030 - FVO med fasit.json', '2021 - IIAB kont - MD4030 - FVO med fasit.json', '2021 - IIAB ordinær - MD4030 - FVO med fasit.json', '2021 - IIC ordinær desember - MD4042 - FVO med fasit.json', '2021 - IIC ordinær vår - MD4042 - FVO med fasit.json', '2021 - IID kont vår - MD4043 - FVO med fasit.json', '2021 - IID ordinær desember - MD4043 -FVO med fasit.json', '2021 - IID ordinær vår - MD4043 - FVO med fasit.json', '2021 - IIIC ordinær - MD4061 - FVO med fasit.json', '2022 - IAB ordinær - MD4011 - FVO med fasit.json', '2022 - ICD ordinær - MD4020 - FVO med fasit.json', '2022 - IIAB ordinær forskerlinje - MD4030 - FVO med fasit.json', 'Fasit 2017 - IIC - MD4042 - eksamen 1-2017-05-16.json', 'Fasit FVO IIC MD4042 2017 konte 08.json', 'Fasit FVO MD4043 IID 2017 konte 08.json', 'Fasit IAB MD4011 2017 konte08.json', 'Fasit IAB MD4011 vår 2017.json', 'Fasit ICD MD4020 vår 2017.json', 'Fasit IIAB MD4030 vår 2017.json', 'Fasit MCQ ICD MD4020 2017 konte 08.json', 'Fasit MD4062-2017-05-15.json', 'HØST 2017 - IIC med fasit - MD4042 - eksamen 1-2017-12-11.json', 'HØST 2017 - IID med fasit- MD4043 - eksamen 1-2017-12-14.json', 'HØST 2017 - IIIC med fasit - MD4061 - eksamen 1-2017-12-18.json', 'Nasjonal delprøve i medisin høst 2020 - Revidert oppgavesett med fasitsvar bokmål.json', 'Nasjonal delprøve i medisin vår 2017 - Revidert fasit etter sensur.json', 'Nasjonal delprøve i medisin vår 2018 - Revidert fasit etter sensur.json', 'Nasjonal delprøve i medisin vår 2019 - Revidert fasit etter sensur.json', 'Nasjonal delprøve i medisin vår 2020 - Revidert fasit etter sensur.json', 'Nasjonal felles avsluttende skriftlig deleksamen i medisin høst 2021 - Revidert fasit etter sensur bokmål.json', 'Nasjonal felles avsluttende skriftlig deleksamen i medisin vår 2021 - Revidert fasit etter sensur bokmål.json', 'Revidert fasit - Nasjonal felles avsluttende skriftlig deleksamen i medisin høst 2022 bokmål.json', 'Revidert-fasit - Nasjonal felles avsluttende skriftlig deleksamen i medisin vår 2022 - Bokmål.json', 'Nasjonal fasit v22.json']
    app = QuizApp(question_set_json_pths)
    app.tkraise()
    app.mainloop()

    #hurtigtaster
    #skjerme alternativer


