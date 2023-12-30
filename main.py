# -*- coding:utf-8 -*-
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import json
import random
import os
import sys
import _thread
import time
from math import log, floor

class Gifplay:
    """
    Usage: mygif=gifplay(<<tkinter.label Objec>>,<<GIF path>>,<<frame_rate(in ms)>>)
    example:
    gif=GIF.gifplay(self.model2,'./res/neural.gif',0.1)
    gif.play()
    This will play gif infinitely
    """
    def __init__(self, label, giffile, delay):
        self.frame = []
        i = 0
        while 1:
            try:
                image = tk.PhotoImage(file=giffile, format="gif -index "+str(i))
                self.frame.append(image)
                i += 1
            except:
                break
        #print(i)
        self.totalFrames = i - 1
        self.delay = delay
        self.labelspace = label
        self.labelspace.image = self.frame[0]

    def play(self):
        """
        plays the gif
        """
        _thread.start_new_thread(self.infinite, ())

    def infinite(self):
        try:
            i = 0
            while 1:
                self.labelspace.configure(image=self.frame[i])
                i = (i + 1) % self.totalFrames
                time.sleep(self.delay)
        except:
            pass

class Statistics:
    def __init__(self, json_path, category_list):
        self.json_path = json_path
        self.statistics_dict = dict()
        if os.path.isfile(json_path) == False:
            with open(json_path, "w", encoding="utf8") as outfile:
                normal_mode = {'Total fullføringsgrad': '0.0% (0 av 0 oppgaver)'}
                exam_mode = {'Total fullføringsgrad': '0.0% (0 av 0 eksamensett)'}
                for c in category_list:
                    normal_mode[f'{c} fullføringsgrad'] = '0.0% (0 av 0 oppgaver)'
                    exam_mode[f'{c} fullføringsgrad'] = '0.0% (0 av 0 eksamensett)'

                exam_mode['Beste eksamensett'] = ''
                exam_mode['Beste eksamenscore'] = '0.0% (0 av 0 oppgaver)'
                exam_mode['Leverte eksamensett'] = []

                doctor_mode = {'Beste tittel': 'Medisinstudent',
                               'Max antall riktige': 0,
                               'Beste score (antall riktige)': '0.0% (0 av 0 oppgaver)',
                               'Beste score (antall riktige) innstillinger': [],
                               'Beste score (% riktige)': '0.0% (0 av 0 oppgaver)',
                               'Beste score (% riktige) innstillinger': [],
                               'Lengste streak': '0 oppgaver'}
                statistics = {'QUIZMODUS': normal_mode,
                              'EKSAMENSMODUS': exam_mode,
                              'OVERLEGEMODUS': doctor_mode}
                self.statistics_dict = statistics
                statistics_json = json.dumps(statistics)
                outfile.write(statistics_json)
        else:
            with open(self.json_path, "r", encoding="utf8") as file_json:
                self.statistics_dict = json.load(file_json)

    def edit_single_json_info(self, mode_tag, edit_tag, input_info):
        with open(self.json_path, "r", encoding="utf8") as file_json:
            file_dict_temp = json.load(file_json)

        file_dict_temp[mode_tag][edit_tag] = input_info

        with open(self.json_path, "w", encoding="utf8") as file_json:
            json.dump(file_dict_temp, file_json)

    def read_json_and_return_dict(self):
        return self.statistics_dict

    def write_dict_to_json(self):
        with open(self.json_path, "w", encoding="utf8") as file_json:
            json.dump(self.statistics_dict, file_json)


class MCQ:
    def __init__(self, question_dict):
        self.question_set = question_dict['question_set']
        self.question_number = question_dict['question_number']
        self.question_text = question_dict['question_text']
        self.image_id = question_dict['image_id']
        self.abcd = question_dict['abcd'] # answer, psyko, explaination
        self.answer_tag = question_dict['answer_tag']
        self.completion_status = question_dict['completion_status']
        self.psyko_text = question_dict['psyko_text']

    def modify_json(self):
        file_pth = f'{self.question_set}.json'

        with open(file_pth, "r", encoding="utf8") as file_json:
            file_dict_temp = json.load(file_json)

        file_dict_temp[f'{self.question_set}_{self.question_number}']['completion_status'] = self.completion_status

        with open(file_pth, "w", encoding="utf8") as file_json:
            json.dump(file_dict_temp, file_json)

def calculate_time_from_seconds(seconds_int):
    mins, secs = divmod(seconds_int, 60)
    hours = 0
    if mins > 60:
        hours, mins = divmod(mins, 60)

    return hours, mins, secs

def scale_image(image_pth_list, h=800, w=760):
    imgs_pil_list = []
    for pth in image_pth_list:
        img_pil = Image.open(pth)

        if img_pil.width >= w:
            aspect_ratio = img_pil.height / img_pil.width
            new_width = w
            new_height = int(new_width * aspect_ratio)

        elif img_pil.height >= h:
            aspect_ratio = img_pil.width / img_pil.height
            new_height = h
            new_width = int(new_height * aspect_ratio)

        else:
            new_width = img_pil.width
            new_height = img_pil.height

        img_pil = img_pil.resize((new_width, new_height), Image.Resampling.BILINEAR)
        imgs_pil_list.append(img_pil)

    return imgs_pil_list


def check_tag_in_question(question, comma_sepatered_tags_list):
    question_string = question.question_text
    #print(question.question_set)
    #print(question.question_number)
    for choice_key in question.abcd:
        question_string += ' ' + question.abcd[choice_key]['answer']

    #input_string_lower = question_string.lower()
    #tag_list_lower = [tag.lower() for tag in comma_sepatered_tags_list]

    include = False
    for t in comma_sepatered_tags_list:
        if t in question_string:
            include = True

    return include

def check_tag_in_string(string, comma_sepatered_tags_list):
    include = False
    string_lower = string.lower()
    for t in comma_sepatered_tags_list:
        if t.lower() in string_lower:
            include = True

    return include

def input_tags_to_list(input_tags_string):
    comma_sepatered_tags_list = input_tags_string.split(',')
    #comma_sepatered_tags_list = [i.strip(' ') for i in comma_sepatered_tags_list]

    return comma_sepatered_tags_list

def calculate_heart_string(int_hearts):
    heart_string = ''
    if int_hearts > 5:
        heart_string = str(int_hearts) + '❤'
    else:
        for l in range(int_hearts):
            heart_string += '❤'

    return heart_string

def check_evolution(evolution_img_list, current_correct, log_base=2, evolution_score=10):
    try:
        index_int = floor(log(current_correct / evolution_score, log_base))
        #print(log(current_correct / evolution_score, log_base))
        #print(index_int)
        if index_int >= 0:
            return index_int + 1
        elif index_int + 1 >= len(evolution_img_list):
            return len(evolution_img_list)
        else:
            return 0
    except:
        return 0

class QuizApp(tk.Tk):
    def __init__(self, file_path_list):
        tk.Tk.__init__(self)
        self.file_path_list = file_path_list
        self.statstics_path = 'statistics.json'
        self.name = 'NTNUiO Quiz'
        self.version = '01.01.24'
        self.configs_tk = {'font': 'Helvetica 12',
                           'font_i': 'Helvetica 12 italic',
                           'font_b': 'Helvetica 12 bold',
                           'font_ib': 'Helvetica 12 italic bold',
                           'font_subtitle': 'Helvetica 20 bold italic',
                           'w_length': 765,
                           'w_length_menu': 700,
                           'color_white': '#ffffff',
                           'color_orange': '#fed06a',
                           'color_green': '#88d8b0',
                           'color_grey': '#626262',
                           'color_red': '#f96e5a',
                           'color_blue': '#65cbda'}
        self.normal_order_mode_var = tk.StringVar()
        self.normal_hidden_mode_var = tk.StringVar()
        self.exam_time_mode_var = tk.StringVar()
        self.exam_manual_time_var = tk.StringVar()
        self.doctor_time_mode_var = tk.StringVar()
        self.doctor_life_mode_var = tk.StringVar()
        self.exam_choice = tk.StringVar()
        self.choice_var = tk.StringVar()
        self.category_info_list = ['Nasjonal - Nasjonal delprøve (Avsluttende eksamen for medisin i Norge)',
                          'MFFAGPR - Fagprøven (Tilsvarer Nasjonal delprøve for leger utdannet utenfor EØS og Sveits og har overlappende oppgaver)',
                          'MD4062 - Modul 8 ekvivalent på NTNU (Tidligere avsluttende eksamen for medisinstudiet på NTNU)',
                          'MD4061 - Modul 7 ekvivalent på NTNU (Allmennmedisin, miljø/samfunnsmedisin, arbeidsmedisin, epidemiologi, medisinsk statistikk)',
                          'MD4043 - Modul 6 ekvivalent på NTNU (Gynekologi/obstetrikk, pediatri, endokrinologi, nefrologi, urologi, global helse)',
                          'MD4042 - Modul 5+3 ekvivalent på NTNU (Ortopedi, psykiatri, hud/veneriske sykdommer, plastikk, farmakologi, revmatologi, radiologi)',
                          'MD4030 - Modul 3+4 ekvivalent på NTNU (Indremedisin, kirurgi, radiologi, øye, nevrologi, øre-nese-hals, onkologi, patologi)',
                          'MD4020 - Modul 2 ekvivalent på NTNU (Anatomi, fysiologi, patologi, immunologi, mikrobiologi, farmakologi)',
                          'MD4011 - Modul 1 ekvivalent på NTNU (Cellebiologi, biokjemi, genetikk, histologi, embryologi)']
        self.normal_year_list = [f'{y}' for y in range(2023, 2015, -1)]
        self.normal_category_list = ['Nasjonal', 'MFFAGPR', 'MD4062', 'MD4061', 'MD4043', 'MD4042', 'MD4030', 'MD4020', 'MD4011']
        self.normal_order_mode_list = ['Kronologisk', 'Tilfeldig']
        self.normal_hidden_mode_list = ['Standard', 'Skjult']
        self.normal_filter_tags = []
        self.exam_time_mode_list = ['Ingen', '4 timer (240 min)', 'Egendefinert (0-300 min)']
        self.exam_filter_tags = []
        self.doctor_time_mode_list = ['Post (Ingen)', 'Poliklinikk (100 sek)', 'Vakt (60 sek)']
        self.doctor_life_mode_list = ['Frisk (10 liv)', 'Komorbid (5 liv)', 'Multimorbid (3 liv)']
        self.doctor_evolution_path_list = ['ascii-evolution0.png', 'ascii-evolution1.png', 'ascii-evolution2.png', 'ascii-evolution3.png', 'ascii-evolution4.png', 'ascii-evolution5.png', 'ascii-evolution6.png']
        self.doctor_evolution_path_alias_list = ['Medisinstudent', 'Medisinstudent med lisens', 'LIS1', 'LIS2', 'LIS3', 'Overlege', 'Overlege med UpToDate']
        self.doctor_evolution_locked_path = 'ascii-lock.png'

        self.title(f'{self.name} {self.version}')
        self.state('zoomed')
        self.update_idletasks() #update resolution
        self.max_width = self.winfo_width()
        self.max_height = self.winfo_height()
        self.create_root()
        self.create_scrollbar()

        self.create_intro_frame()
        self.current_mode = ''

        self.statistics_obj = Statistics(self.statstics_path, self.normal_category_list)

    def _on_mousewheel(self, event):
        #print(event.delta)
        # code for free scroll
        self.main_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def create_root(self):
        self.root_frame = tk.Frame(self)
        self.root_frame.pack(fill=tk.BOTH, expand=True)

    def create_scrollbar(self):
        self.main_canvas = tk.Canvas(self.root_frame)
        self.main_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.scrollbar = tk.Scrollbar(self.root_frame, orient=tk.VERTICAL, command=self.main_canvas.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.main_canvas.configure(yscrollcommand=self.scrollbar.set)
        self.main_canvas.bind('<Configure>', lambda e:self.main_canvas.configure(scrollregion=self.main_canvas.bbox("all")))
        self.main_canvas.bind_all("<MouseWheel>", self._on_mousewheel) #code for free scroll

    def create_intro_logo_label(self):
        self.intro_logo_container = tk.Frame(self.intro_frame)
        self.intro_logo_container.pack()

        logo_text = tk.Label(self.intro_logo_container, text=self.name, justify='left', font='Helvetica 50 bold italic', pady=5)
        logo_text.pack()
        version_text = tk.Label(self.intro_logo_container, text=f'Versjon {self.version}', justify='left', font=self.configs_tk['font_i'])
        version_text.pack()

        gif_label = tk.Label(self.intro_logo_container)
        gif_label.pack(padx=140, pady=5)
        mygif = Gifplay(gif_label, 'ascii-boy.gif', 0.1)
        mygif.play()

    def create_intro_buttons_container(self):
        self.intro_buttons_container = tk.Frame(self.intro_frame)
        self.intro_buttons_container.pack(pady=5)

        dummy_label = tk.Label(self.intro_buttons_container, text='', font=self.configs_tk['font_i'], height=2, width=4)
        dummy_label.grid(row=0, column=0, pady=5, padx=5)

        normal_button = tk.Button(self.intro_buttons_container, text="QUIZMODUS", font=self.configs_tk['font_b'],
                                  bg=self.configs_tk['color_green'], height=2, width=30, command=lambda: self.create_normal_menu_from_intro())
        normal_button.grid(row=0, column=1, pady=5, padx=5)
        normal_info_button = tk.Menubutton(self.intro_buttons_container, text="Info", font=self.configs_tk['font_i'],
                                           bg=self.configs_tk['color_grey'], fg=self.configs_tk['color_white'], relief='raised', height=2, width=4)
        normal_info_button.grid(row=0, column=2, pady=5, padx=5)
        normal_info_button.menu = tk.Menu(normal_info_button, tearoff=0)
        normal_info_button["menu"] = normal_info_button.menu
        normal_info_button.menu.add_cascade(
            label="Formål - Læringsbasert quiz med umiddelbare tilbakemeldinger etter eget tempo")
        normal_info_button.menu.add_cascade(
            label="Oppsett - Riktig svar og forklaringer vises etter hver besvarte oppgave")
        normal_info_button.menu.add_cascade(
            label="Valgmuligheter - Spesifikke emner, spesifikke årganger, kombinasjon av eksamensett og skjuling av svaralternativer")

        exam_button = tk.Button(self.intro_buttons_container, text="EKSAMENSMODUS", font=self.configs_tk['font_b'],
                                bg=self.configs_tk['color_green'], height=2, width=30, command=lambda: self.create_exam_menu_from_intro())
        exam_button.grid(row=1, column=1, pady=5, padx=5)
        exam_info_button = tk.Menubutton(self.intro_buttons_container, text="Info", font=self.configs_tk['font_i'],
                                         bg=self.configs_tk['color_grey'], fg=self.configs_tk['color_white'], relief='raised', height=2,
                                         width=4)
        exam_info_button.grid(row=1, column=2, pady=5, padx=5)
        exam_info_button.menu = tk.Menu(exam_info_button, tearoff=0)
        exam_info_button["menu"] = exam_info_button.menu
        exam_info_button.menu.add_cascade(
            label="Formål - Etterligner det digitale oppsettet på Nasjonal delprøve i medisin")
        exam_info_button.menu.add_cascade(
            label="Oppsett - Alle oppgaver må besvares før riktig svar og forklaringer vises")
        exam_info_button.menu.add_cascade(
            label="Valgmuligheter - Spesifikke eksamensett og eksamenstid")

        doctor_button = tk.Button(self.intro_buttons_container, text="OVERLEGEMODUS", font=self.configs_tk['font_b'],
                                bg=self.configs_tk['color_green'], height=2, width=30, command=lambda: self.create_doctor_menu_from_intro())
        doctor_button.grid(row=2, column=1, pady=5, padx=5)
        doctor_info_button = tk.Menubutton(self.intro_buttons_container, text="Info", font=self.configs_tk['font_i'],
                                         bg=self.configs_tk['color_grey'], fg=self.configs_tk['color_white'],
                                         relief='raised', height=2,
                                         width=4)
        doctor_info_button.grid(row=2, column=2, pady=5, padx=5)
        doctor_info_button.menu = tk.Menu(doctor_info_button, tearoff=0)
        doctor_info_button["menu"] = doctor_info_button.menu
        doctor_info_button.menu.add_cascade(
            label="Formål - Spillbasert quiz der du kan vise medstudentene dine hvor smart du er")
        doctor_info_button.menu.add_cascade(
            label="Oppsett - Tilfeldige oppgaver trekkes fra hele oppgavebanken til man går tom for liv")
        doctor_info_button.menu.add_cascade(
            label="Valgmuligheter - Antall liv, oppgavetid og hjelpemidler")

        statistics_button = tk.Button(self.intro_buttons_container, text="STATISTIKK", font=self.configs_tk['font_b'],
                                      bg=self.configs_tk['color_white'], height=2, width=30, command=lambda: self.create_statistics_from_intro())
        statistics_button.grid(row=3, column=1, pady=5, padx=5)
        sources_button = tk.Button(self.intro_buttons_container, text="INFO OG KILDER", font=self.configs_tk['font_b'],
                                   bg=self.configs_tk['color_white'], height=2, width=30, command=lambda: self.create_sources_from_intro())
        sources_button.grid(row=4, column=1, pady=5, padx=5)

    def create_intro_shoutout_container(self):
        self.intro_shoutout_container = tk.Frame(self.intro_frame)
        self.intro_shoutout_container.pack(pady=10)

        shoutout_text = tk.Label(self.intro_shoutout_container,
                                 text='Doner til MedHum ( ´◉◞౪◟◉)୨', font='Helvetica 15 bold italic',
                                 wraplength=self.configs_tk['w_length'])
        shoutout_text.pack(pady=5)
        shoutout_link = tk.Text(self.intro_shoutout_container, font=self.configs_tk['font'], height=1, width=33, borderwidth=0,)
        shoutout_link.insert(1.0, 'https://www.medhum.no/take-action')
        shoutout_link.configure(state='disabled')
        shoutout_link.pack(pady=5)

    def create_intro_frame(self):
        self.intro_frame = tk.Frame(self.main_canvas, pady=10, padx=80)
        self.main_canvas.create_window((self.max_width // 2, 0), window=self.intro_frame, anchor="n")
        self.intro_frame.bind('<Configure>', lambda e: self.main_canvas.configure(scrollregion=self.main_canvas.bbox("all")))

        self.create_intro_logo_label()
        self.create_intro_buttons_container()
        self.create_intro_shoutout_container()

    def create_intro_from_any(self, current_frame):
        current_frame.destroy()
        if self.current_mode == 'QUIZMODUS':
            self.update_statistics_normal()
        elif self.current_mode == 'EKSAMENSMODUS' and self.submit_exam == True:
            self.update_statistics_exam()
        elif self.current_mode == 'OVERLEGEMODUS':
            if self.remaining_lives != 0:
                self.current_largest_question_index += self.remaining_lives
            self.update_statistics_doctor()
        self.current_mode = ''
        self.create_intro_frame()

    def create_normal_filter_container(self):
        normal_tag_filter_container = tk.Frame(self.normal_menu_frame)
        normal_tag_filter_container.pack(pady=10)

        box_label = tk.LabelFrame(normal_tag_filter_container,
                                  text='OPPGAVEFILTER', font=self.configs_tk['font_b'], padx=32, pady=20)
        box_label.pack()

        box_label_info_button = tk.Menubutton(box_label, text="Info", font=self.configs_tk['font_i'],
                                              bg=self.configs_tk['color_grey'], fg=self.configs_tk['color_white'], relief='raised', height=1,
                                              width=10)
        box_label_info_button.pack(anchor='w')
        box_label_info_button.menu = tk.Menu(box_label_info_button, tearoff=0)
        box_label_info_button["menu"] = box_label_info_button.menu
        box_label_info_button.menu.add_cascade(
            label='Skriv inn ønskede stikkord for å filtrere oppgavene i det underliggende eksamensutvalget')
        box_label_info_button.menu.add_cascade(
            label='Angitte stikkord søkes for i oppgaveteksten og svaralternativene. Tomt filter inkluderer alle oppgaver for det underliggende eksamensutvalget')
        box_label_info_button.menu.add_cascade(
            label='Dersom flere stikkord er ønskelig, brukes "," for å skille stikkordene (dvs komma uten hermetegnene)')
        box_label_info_button.menu.add_cascade(
            label='Filteret skiller mellom store/små bokstaver, samt bruk av mellomrom. Det vil være forskjell på "slag" vs "slag " og "CT" vs "ct"')
        box_label_info_button.menu.add_cascade(
            label='Stikkordet "slag" vil inkludere oppgaver med ordene "hjerneslag", "slag" og "slagsmål". Derimot vil "slag " ekskludere "slagsmål" pga mellomrommet')
        box_label_info_button.menu.add_cascade(
            label='Et filter for slag-oppgaver kan feks være: Slag,slag ,Trombektomi,trombektomi,Trombolyse,trombolyse')

        self.normal_text_input = tk.Text(box_label, font=self.configs_tk['font'], height=1)
        self.normal_text_input.pack()

    def create_normal_year_box_container(self):
        normal_year_box_container = tk.Frame(self.normal_menu_checkbox_container)
        normal_year_box_container.grid(row=1, column=0, sticky='n')

        box_label = tk.LabelFrame(normal_year_box_container, text='ÅRGANG', font=self.configs_tk['font_b'], padx=30, pady=20, height=419, width=198)
        box_label.pack()
        self.normal_check_label_year = []
        self.normal_check_label_year_vars = []

        box_label_info_button = tk.Menubutton(box_label, text="Info", font=self.configs_tk['font_i'],
                                              bg=self.configs_tk['color_grey'], fg=self.configs_tk['color_white'], relief='raised', height=1,
                                              width=10)
        box_label_info_button.pack(anchor='w')
        box_label_info_button.menu = tk.Menu(box_label_info_button, tearoff=0)
        box_label_info_button["menu"] = box_label_info_button.menu
        box_label_info_button.menu.add_cascade(
            label='Valg av årganger for eksamensutvalget')
        box_label_info_button.menu.add_cascade(
            label='Nasjonal og MFFAGPR har høst- og våreksamen, mens NTNU-settene har ordinær- og konteeksamen')
        box_label_info_button.menu.add_cascade(
            label='Vanligvis vil det være 0-2 eksamensett for hver årgang, men dette kan være varierende')

        for y in self.normal_year_list:
            self.normal_check_label_year_vars.append(tk.IntVar())
            check_label = tk.Checkbutton(box_label, text=y, variable=self.normal_check_label_year_vars[-1],
                                         font=self.configs_tk['font'])
            self.normal_check_label_year.append(check_label)
            check_label.pack(anchor='w')
        box_label.pack_propagate(False)  # makes height and width in labelframe active

        select_all_button = tk.Button(box_label, text='Velg alle', command=lambda:self.on_selectall_normal(self.normal_check_label_year),
                                      bg=self.configs_tk['color_white'], font=self.configs_tk['font_i'],
                                      height=1, width=10)
        select_all_button.pack(anchor='w')
        remove_all_button = tk.Button(box_label, text='Fjern alle', command=lambda:self.on_deselectall_normal(self.normal_check_label_year),
                                      bg=self.configs_tk['color_white'], font=self.configs_tk['font_i'],
                                      height=1, width=10)
        remove_all_button.pack(anchor='w')

    def create_normal_category_box_container(self):
        normal_category_box_container = tk.Frame(self.normal_menu_checkbox_container)
        normal_category_box_container.grid(row=1, column=1, sticky='n')

        box_label = tk.LabelFrame(normal_category_box_container, text='EKSAMENSETT', font=self.configs_tk['font_b'], padx=30, pady=20, height=419, width=198)
        box_label.pack()
        self.normal_category_check_label = []
        self.normal_category_check_label_vars = []

        box_label_info_button = tk.Menubutton(box_label, text="Info", font=self.configs_tk['font_i'],
                                                bg=self.configs_tk['color_grey'], fg=self.configs_tk['color_white'], relief='raised', height=1,
                                                width=10)
        box_label_info_button.pack(anchor='w')
        box_label_info_button.menu = tk.Menu(box_label_info_button, tearoff=0)
        box_label_info_button["menu"] = box_label_info_button.menu
        box_label_info_button.menu.add_cascade(label='Valg av moduler/emner for eksamensutvalget')
        for i in self.category_info_list:
            box_label_info_button.menu.add_cascade(label=i)

        for e in self.normal_category_list:
            self.normal_category_check_label_vars.append(tk.IntVar())
            check_label = tk.Checkbutton(box_label, text=e, variable=self.normal_category_check_label_vars[-1], font=self.configs_tk['font'])
            self.normal_category_check_label.append(check_label)
            check_label.pack(anchor='w')
        box_label.pack_propagate(False)  # makes height and width in labelframe active

        select_all_button = tk.Button(box_label, text='Velg alle',
                                      command=lambda: self.on_selectall_normal(self.normal_category_check_label),
                                      bg=self.configs_tk['color_white'], font=self.configs_tk['font_i'],
                                      height=1, width=10)
        select_all_button.pack(anchor='w')
        remove_all_button = tk.Button(box_label, text='Fjern alle',
                                      command=lambda: self.on_deselectall_normal(self.normal_category_check_label),
                                      bg=self.configs_tk['color_white'], font=self.configs_tk['font_i'],
                                      height=1, width=10)
        remove_all_button.pack(anchor='w')

    def create_normal_order_box_container(self):
        normal_order_box_container = tk.Frame(self.normal_menu_checkbox_container)
        normal_order_box_container.grid(row=1, column=2, sticky='n')

        box_label = tk.LabelFrame(normal_order_box_container, text='REKKEFØLGE', font=self.configs_tk['font_b'], padx=30, pady=20, height=419, width=198)
        box_label.pack()

        box_label_info_button = tk.Menubutton(box_label, text="Info", font=self.configs_tk['font_i'],
                                                bg=self.configs_tk['color_grey'], fg=self.configs_tk['color_white'], relief='raised', height=1,
                                                width=10)
        box_label_info_button.pack(anchor='w')
        box_label_info_button.menu = tk.Menu(box_label_info_button, tearoff=0)
        box_label_info_button["menu"] = box_label_info_button.menu
        box_label_info_button.menu.add_cascade(
            label='Valg av oppgaverekkefølge for eksamensutvalget')
        box_label_info_button.menu.add_cascade(label='Kronologisk - Oppgavene kommer i rekkefølgen til de originale eksamensettene')
        box_label_info_button.menu.add_cascade(label='Tilfeldig - Oppgavene i de ulike eksamensettene blandes og kommer i tilfeldig rekkefølge')

        self.normal_order_mode_var.set('0')
        for r in self.normal_order_mode_list:
            button = tk.Radiobutton(box_label, text=r, variable=self.normal_order_mode_var, value=r, font=self.configs_tk['font'])
            button.pack(anchor='w')
        box_label.pack_propagate(False) # makes height and width in labelframe active

    def create_normal_hidden_mode_container(self):
        hidden_mode_container = tk.Frame(self.normal_menu_checkbox_container)
        hidden_mode_container.grid(row=1, column=3, sticky='n')

        box_label = tk.LabelFrame(hidden_mode_container, text='ALTERNATIVER', font=self.configs_tk['font_b'], padx=30, pady=20, height=419, width=198)
        box_label.pack()

        box_label_info_button = tk.Menubutton(box_label, text="Info", font=self.configs_tk['font_i'],
                                              bg=self.configs_tk['color_grey'], fg=self.configs_tk['color_white'], relief='raised', height=1,
                                              width=10)
        box_label_info_button.pack(anchor='w')
        box_label_info_button.menu = tk.Menu(box_label_info_button, tearoff=0)
        box_label_info_button["menu"] = box_label_info_button.menu
        box_label_info_button.menu.add_cascade(
            label='Valg for av skjuling av svaralternativer for eksamensutvalget')
        box_label_info_button.menu.add_cascade(
            label='Standard - Oppgaveteksten gis sammen med svaralternativer som ved vanlig multiple choice')
        box_label_info_button.menu.add_cascade(
            label='Skjult - Oppgaveteksen gis først uten svaralternativer og vises når man selv bestemmer det')

        self.normal_hidden_mode_var.set('0')
        for r in self.normal_hidden_mode_list:
            button = tk.Radiobutton(box_label, text=r, variable=self.normal_hidden_mode_var, value=r, font=self.configs_tk['font'])
            button.pack(anchor='w')
        box_label.pack_propagate(False)  # makes height and width in labelframe active

    def create_normal_menu_checkbox_container(self):
        self.normal_menu_checkbox_container = tk.Frame(self.normal_menu_frame)
        self.normal_menu_checkbox_container.pack(pady=10)

        self.create_normal_year_box_container()
        self.create_normal_category_box_container()
        self.create_normal_order_box_container()
        self.create_normal_hidden_mode_container()

    def create_normal_overview_container(self):
        normal_overview_container = tk.Frame(self.normal_menu_frame)
        normal_overview_container.pack(pady=10)

        box_label = tk.LabelFrame(normal_overview_container, text='OPPGAVEOVERSIKT', font=self.configs_tk['font_b'],
                                  padx=32, pady=20, height=268, width=792)
        box_label.pack()
        box_label_info_button = tk.Menubutton(box_label, text="Info", font=self.configs_tk['font_i'],
                                              bg=self.configs_tk['color_grey'], fg=self.configs_tk['color_white'], relief='raised', height=1,
                                              width=10)
        box_label_info_button.pack(anchor='w')
        box_label_info_button.menu = tk.Menu(box_label_info_button, tearoff=0)
        box_label_info_button["menu"] = box_label_info_button.menu
        box_label_info_button.menu.add_cascade(label='Oversikt over oppgaveutvalget (for angitt filter og eksamensutvalg), samt andre innstillinger før "Start"')
        box_label_info_button.menu.add_cascade(label='Dersom det står "Fullføringsgrad 0% (0 av 0 oppgaver)" betyr det at det ikke finnes noen oppgaver for angitt filter og eksamensutvalg')
        box_label_info_button.menu.add_cascade(label='Riktig besvarte oppgaver i denne modusen markeres som "fullført", og vil ikke vises på nytt med mindre oppgaven tilbakestilles')
        box_label_info_button.menu.add_cascade(label='Oppgaveutvalget (for angitt filter og eksamensutvalg), kan tilbakestilles med "Tilbakestill" dersom dette er ønskelig')
        box_label_info_button.menu.add_cascade(label='Statistikk lagres når man trykker "Hjem"')

        self.normal_questions_number_label = tk.Label(box_label, text=f'Fullføringsgrad: ?% (? av ? oppgaver)',
                                                      font=self.configs_tk['font'], anchor='w', justify='left',
                                                      wraplength=self.configs_tk['w_length_menu'])
        self.normal_questions_number_label.pack(anchor='w')
        self.normal_filter_label = tk.Label(box_label, text=f'Filter: Ingen',
                                            font=self.configs_tk['font'], anchor='w', justify='left',
                                            wraplength=self.configs_tk['w_length_menu'])
        self.normal_filter_label.pack(anchor='w')
        self.normal_category_label = tk.Label(box_label, text=f'Eksamensutvalg: ?',
                                              font=self.configs_tk['font'], anchor='w', justify='left',
                                              wraplength=self.configs_tk['w_length_menu'])
        self.normal_category_label.pack(anchor='w')
        self.normal_order_label = tk.Label(box_label, text=f'Rekkefølge: ?',
                                                    font=self.configs_tk['font'], anchor='w', justify='left',
                                                    wraplength=self.configs_tk['w_length_menu'])
        self.normal_order_label.pack(anchor='w')
        self.normal_hidden_label = tk.Label(box_label, text=f'Alternativer: ?',
                                            font=self.configs_tk['font'], anchor='w', justify='left',
                                            wraplength=self.configs_tk['w_length_menu'])
        self.normal_hidden_label.pack(anchor='w')
        update_button = tk.Button(box_label, text='Oppdater',
                                 bg=self.configs_tk['color_white'], font=self.configs_tk['font_i'],
                                 height=1, width=10, command=lambda: self.on_check_normal())
        update_button.pack(anchor='w')
        box_label.pack_propagate(False)  # makes height and width in labelframe active

    def create_normal_start_container(self):
        normal_start_container = tk.Frame(self.normal_menu_frame)
        normal_start_container.pack(pady=10)

        check_button = tk.Button(normal_start_container, text='TILBAKESTILL',
                                  bg=self.configs_tk['color_orange'], font=self.configs_tk['font_b'],
                                  height=2, width=30, command=lambda: self.on_reset_normal())
        check_button.grid(row=0, column=0, padx=5)
        start_button = tk.Button(normal_start_container, text='START', command=lambda: self.on_start_normal(),
                                 bg=self.configs_tk['color_green'], height=2, width=30, font=self.configs_tk['font_b'])
        start_button.grid(row=0, column=1, padx=5)

    def create_normal_menu_frame(self):
        self.questions = []
        self.current_question_index = 0
        self.current_largest_question_index = 0
        self.correct_questions = 0
        self.normal_filter_tags = []
        self.submit_normal = False

        self.normal_menu_frame = tk.Frame(self.main_canvas, pady=10, padx=80)
        self.main_canvas.create_window((self.max_width // 2, 0), window=self.normal_menu_frame, anchor="n")
        self.normal_menu_frame.bind('<Configure>', lambda e: self.main_canvas.configure(scrollregion=self.main_canvas.bbox("all")))

        self.create_subtitle_info_container(self.normal_menu_frame, 'QUIZMODUS')
        self.create_normal_filter_container()
        self.create_normal_menu_checkbox_container()
        self.create_normal_overview_container()
        self.create_normal_start_container()

    def on_reset_normal(self):
        if sum([yv.get() for yv in self.normal_check_label_year_vars]) > 0 and sum([cv.get() for cv in self.normal_category_check_label_vars]) > 0:
            included_year_tags = []
            for y in zip(self.normal_year_list, self.normal_check_label_year_vars):
                if y[1].get() == 1:
                    included_year_tags.append(y[0])

            included_category_tags = []
            for c in zip(self.normal_category_list, self.normal_category_check_label_vars):
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

            self.on_check_normal()
            self.update_statistics_normal()

    def on_check_normal(self):
        included_year_tags = []
        for y in zip(self.normal_year_list, self.normal_check_label_year_vars):
            if y[1].get() == 1:
                included_year_tags.append(y[0])

        included_category_tags = []
        for c in zip(self.normal_category_list, self.normal_category_check_label_vars):
            if c[1].get() == 1:
                included_category_tags.append(c[0])

        self.normal_filter_tags = input_tags_to_list(self.normal_text_input.get("1.0", 'end-1c'))
        if len(self.normal_filter_tags) > 0:
            if self.normal_filter_tags[0] != '':
                self.normal_filter_label.configure(text=f'Filter: {self.normal_filter_tags}')
            else:
                self.normal_filter_label.configure(text=f'Filter: Ingen')
        else:
            self.normal_filter_label.configure(text=f'Filter: Ingen')

        if len(included_year_tags) > 0 and len(included_category_tags) > 0:
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

                    if check_tag_in_question(question, self.normal_filter_tags):
                        if question.completion_status == 0:
                            included_questions += 1
                        else:
                            completed_questions += 1

            all_tags = included_year_tags + included_category_tags

            self.normal_category_label.configure(text=f'Eksamensutvalg: {all_tags}')
            if included_questions > 0:
                self.normal_questions_number_label.configure(text=f'Fullføringsgrad: {round((completed_questions * 100 / (completed_questions + included_questions)), 1)}% ({completed_questions} av {completed_questions + included_questions} oppgaver)')
            else:
                self.normal_questions_number_label.configure(text=f'Fullføringsgrad: 0.0% (0 av 0 oppgaver)')
        else:
            self.normal_category_label.configure(text=f'Eksamensutvalg: ?')
            self.normal_questions_number_label.configure(text=f'Fullføringsgrad: ?% (? av ? oppgaver)')
        if self.normal_order_mode_var.get() != '0':
            self.normal_order_label.configure(text=f'Rekkefølge: {self.normal_order_mode_var.get()}')
        else:
            self.normal_order_label.configure(text=f'Rekkefølge: ?')

        if self.normal_hidden_mode_var.get() != '0':
            self.normal_hidden_label.configure(text=f'Alternativer: {self.normal_hidden_mode_var.get()}')
        else:
            self.normal_hidden_label.configure(text=f'Alternativer: ?')

    def on_start_normal(self):
        if self.normal_order_mode_var.get() != '0' and self.normal_hidden_mode_var.get() != '0' and sum([yv.get() for yv in self.normal_check_label_year_vars]) > 0 and sum([cv.get() for cv in self.normal_category_check_label_vars]) > 0:

            included_year_tags = []
            for y in zip(self.normal_year_list, self.normal_check_label_year_vars):
                if y[1].get() == 1:
                    included_year_tags.append(y[0])

            included_category_tags = []
            for c in zip(self.normal_category_list, self.normal_category_check_label_vars):
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
            self.normal_filter_tags = input_tags_to_list(self.normal_text_input.get("1.0", 'end-1c'))

            for pth in included_paths:
                file_json = open(pth)
                try:
                    file_dict = json.load(file_json)
                    for q in range(1, len(file_dict) + 1):
                        question = MCQ(file_dict[f'{pth.rsplit(".", 1)[0]}_{q}'])
                        if check_tag_in_question(question, self.normal_filter_tags):
                            if question.completion_status == 0:
                                included_questions.append(question)
                except:
                    print(file_json)

            if self.normal_order_mode_var.get() == 'Tilfeldig':
                random.shuffle(included_questions)

            self.questions = included_questions
            if len(included_questions) > 0:
                self.create_normal_quiz_frame_from_menu()
                self.current_mode = 'QUIZMODUS'

    def create_normal_question_dock_info_container(self):
        dock_info_container = tk.Frame(self.normal_quiz_frame, height=40, width=790)
        dock_info_container.pack(anchor='w')

        self.progress_count = tk.StringVar()
        self.progress_count.set(f'Progresjon: {self.current_question_index + 1} av {len(self.questions)}')
        progress_number = tk.Label(dock_info_container, textvariable=self.progress_count,
                                   font=self.configs_tk['font_ib'])
        progress_number.pack(side=tk.LEFT)

        self.correct_count = tk.StringVar()
        self.correct_count.set(f'Riktige: 0.0% ({self.correct_questions} av {self.current_largest_question_index})')
        correct_percent = tk.Label(dock_info_container, textvariable=self.correct_count, font=self.configs_tk['font_ib'])
        correct_percent.pack(side=tk.RIGHT)

        dock_info_container.pack_propagate(False)

    def create_normal_question_dock_button_container(self):
        button_container = tk.Frame(self.normal_quiz_frame)
        button_container.pack(anchor='center')

        previous_button = tk.Button(button_container, text='<', command=lambda: self.on_previous_normal(),
                                    bg=self.configs_tk['color_white'], height=1, width=7, font=self.configs_tk['font_b'])
        previous_button.grid(row=0, column=0, padx=5)
        self.normal_submit_button = tk.Button(button_container, text='SVAR', command=lambda: self.on_submit_normal(), bg=self.configs_tk['color_green'], height=1, width=14, font=self.configs_tk['font_b'])
        self.normal_submit_button.grid(row=0, column=1, padx=5)
        next_button = tk.Button(button_container, text='>', command=lambda: self.on_next_normal(), bg=self.configs_tk['color_white'], height=1, width=7, font=self.configs_tk['font_b'])
        next_button.grid(row=0, column=2, padx=5)

        self.feedback_label = tk.Label(button_container, text='', font=self.configs_tk['font_b'])
        self.feedback_label.grid(row=1, column=1, padx=5)

    def create_text_container(self, frame):
        self.text_container = tk.Frame(frame)
        self.text_container.pack(anchor='w')

        title = f'Eksamensett: {self.questions[self.current_question_index].question_set}\nOppgave: {self.questions[self.current_question_index].question_number}'
        question_id = tk.Label(self.text_container, text=title, font=self.configs_tk['font_i'], justify='left', wraplength=self.configs_tk['w_length'], pady=10)
        question_id.pack(anchor='w')

        self.psyko_text_label = tk.Label(self.text_container, text='',
                                         font=self.configs_tk['font_b'], justify='left', wraplength=self.configs_tk['w_length'])
        self.psyko_text_label.pack(anchor='w')

        text = self.questions[self.current_question_index].question_text
        question_text = tk.Label(self.text_container, text=text,
                                 font=self.configs_tk['font'], justify='left', wraplength=self.configs_tk['w_length'])
        question_text.pack(anchor='w')

    def create_image_container(self, frame):
        self.image_container = tk.Frame(frame)
        self.image_container.pack(anchor='center')

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

                image_container_buttons = tk.Frame(self.image_container)
                image_container_buttons.pack()
                self.left_scroll_button = tk.Button(image_container_buttons, text='<', command=lambda: self.on_leftscroll_normal(),
                                                    bg=self.configs_tk['color_white'], font=self.configs_tk['font_b'],
                                                    height=1, width=7, state='disabled')
                self.right_scroll_button = tk.Button(image_container_buttons, text='>',
                                                     command=lambda: self.on_rightscroll_normal(), bg=self.configs_tk['color_white'], font=self.configs_tk['font_b'],
                                                     height=1, width=7)

                self.img_count = tk.StringVar()
                self.img_count.set(f'Bilde: {self.img_index + 1} av {len(self.list_pil)}')
                img_count_label = tk.Label(image_container_buttons, textvariable=self.img_count,
                                                font=self.configs_tk['font_i'])

                img_count_label.grid(row=0, column=1, padx=5)
                self.left_scroll_button.grid(row=0, column=0, padx=5)
                self.right_scroll_button.grid(row=0, column=2, padx=5)

    def create_normal_choice_container(self, frame):
        self.choice_container = tk.Frame(frame)
        self.choice_container.pack(anchor='w')

        self.choice_explainations = []
        self.choice_explaination_contents = []
        self.psyko_explainations = []
        self.psyko_explaination_contents = []

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

            try:
                psyko = f'{choice}: {self.questions[self.current_question_index].abcd[choice]["psyko"]}'
            except:
                psyko = f''

            choice_explanation = tk.Label(self.choice_container, text='', font=self.configs_tk['font'], justify='left', wraplength=self.configs_tk['w_length'])
            choice_explanation.pack(anchor='w')
            self.choice_explaination_contents.append(explaination)
            self.choice_explainations.append(choice_explanation)

            psyko_explanation = tk.Label(self.choice_container, text='', font=self.configs_tk['font_b'], justify='left', wraplength=self.configs_tk['w_length'])
            psyko_explanation.pack(anchor='w')
            self.psyko_explaination_contents.append(psyko)
            self.psyko_explainations.append(psyko_explanation)

    def create_normal_quiz_frame(self):
        self.normal_quiz_frame = tk.Frame(self.main_canvas, pady=10, padx=80)
        self.normal_quiz_frame.pack(anchor='w')
        self.main_canvas.create_window((self.max_width // 2, 0), window=self.normal_quiz_frame, anchor="n")
        self.normal_quiz_frame.bind('<Configure>', lambda e: self.main_canvas.configure(scrollregion=self.main_canvas.bbox("all")))

        self.create_subtitle_info_container(self.normal_quiz_frame, 'QUIZMODUS')
        self.create_normal_question_dock_info_container()
        self.create_normal_question_dock_button_container()
        self.create_text_container(self.normal_quiz_frame)
        self.create_image_container(self.normal_quiz_frame)
        if self.normal_hidden_mode_var.get() == 'Skjult':
            self.normal_submit_button.configure(text='VIS', command=lambda: self.on_show_normal())
        else:
            self.create_normal_choice_container(self.normal_quiz_frame)

    def create_normal_menu_from_intro(self):
        self.intro_frame.destroy()
        self.create_normal_menu_frame()

    def create_normal_quiz_frame_from_menu(self):
        self.normal_menu_frame.destroy()
        self.create_normal_quiz_frame()

    def on_show_normal(self):
        self.normal_submit_button.configure(text='SVAR', command=lambda: self.on_submit_normal())
        self.create_normal_choice_container(self.normal_quiz_frame)

    def on_selectall_normal(self, check_box_list):
        for i in check_box_list:
            i.select()

    def on_deselectall_normal(self, check_box_list):
        for i in check_box_list:
            i.deselect()

    def on_leftscroll_normal(self):
        self.img_index -= 1
        image_tk = ImageTk.PhotoImage(self.list_pil[self.img_index])
        self.image_label.configure(image=image_tk)
        self.image_label.image = image_tk

        if self.img_index == 0:
            self.left_scroll_button.configure(state='disabled')

        self.right_scroll_button.configure(state='normal')
        self.img_count.set(f'Bilde: {self.img_index + 1} av {len(self.list_pil)}')

    def on_rightscroll_normal(self):
        self.img_index += 1
        image_tk = ImageTk.PhotoImage(self.list_pil[self.img_index])
        self.image_label.configure(image=image_tk)
        self.image_label.image = image_tk

        if self.img_index == len(self.list_pil) - 1:
            self.right_scroll_button.configure(state='disabled')

        self.left_scroll_button.configure(state='normal')
        self.img_count.set(f'Bilde: {self.img_index + 1} av {len(self.list_pil)}')

    def on_next_normal(self):
        self.current_question_index += 1
        if self.current_question_index >= len(self.questions):
            self.normal_quiz_frame.destroy()
            self.create_normal_menu_frame()
        else:
            if self.current_question_index > self.current_largest_question_index:

                if self.submit_normal == True:
                    self.submit_normal = False

                self.correct_count.set(
                    f'Riktige: {round((self.correct_questions * 100 / (self.current_largest_question_index + 1)), 1)}% ({self.correct_questions} av {self.current_largest_question_index + 1})')
                self.current_largest_question_index += 1

                if self.normal_submit_button['state'] == 'disabled':
                    self.normal_submit_button.configure(state='active')

                # Update the widgets with the new question
                self.normal_submit_button.configure(text='SVAR', command=lambda: self.on_submit_normal(), bg=self.configs_tk['color_green'])
                self.feedback_label.configure(text='')
                self.text_container.destroy()
                self.image_container.destroy()
                self.choice_container.destroy()

                self.create_text_container(self.normal_quiz_frame)
                self.create_image_container(self.normal_quiz_frame)
                if self.normal_hidden_mode_var.get() == 'Skjult':
                    self.normal_submit_button.configure(text='VIS', command=lambda: self.on_show_normal())
                else:
                    self.create_normal_choice_container(self.normal_quiz_frame)
            elif self.current_question_index == self.current_largest_question_index and self.submit_normal == False:
                    if self.normal_submit_button['state'] == 'disabled':
                        self.normal_submit_button.configure(state='active')

                    # Update the widgets with the new question
                    self.normal_submit_button.configure(text='SVAR', command=lambda: self.on_submit_normal(),
                                                        bg=self.configs_tk['color_green'])
                    self.feedback_label.configure(text='')
                    self.text_container.destroy()
                    self.image_container.destroy()
                    self.choice_container.destroy()

                    self.create_text_container(self.normal_quiz_frame)
                    self.create_image_container(self.normal_quiz_frame)
                    if self.normal_hidden_mode_var.get() == 'Skjult':
                        self.normal_submit_button.configure(text='VIS', command=lambda: self.on_show_normal())
                    else:
                        self.create_normal_choice_container(self.normal_quiz_frame)
            else:
                self.text_container.destroy()
                self.image_container.destroy()
                self.choice_container.destroy()

                self.create_text_container(self.normal_quiz_frame)
                self.create_image_container(self.normal_quiz_frame)
                self.create_normal_choice_container(self.normal_quiz_frame)

                if self.questions[self.current_question_index].psyko_text != '':
                    self.psyko_text_label.configure(text=self.questions[self.current_question_index].psyko_text,
                                                    fg=self.configs_tk['color_red'])

                for ce in zip(self.choice_explainations, self.choice_explaination_contents, self.psyko_explainations,
                              self.psyko_explaination_contents):
                    ce[0].configure(text=ce[1])
                    ce[2].configure(text=ce[3])
                    if ce[1].strip(' ')[0] == self.questions[self.current_question_index].answer_tag:
                        ce[0].configure(bg=self.configs_tk['color_green'])
                    else:
                        ce[0].configure(bg=self.configs_tk['color_orange'])
                    ce[2].configure(fg=self.configs_tk['color_red'])

            self.progress_count.set(f'Progresjon: {self.current_question_index + 1} av {len(self.questions)}')

    def on_previous_normal(self):
        self.current_question_index -= 1
        if self.current_question_index >= 0:

            # Update the widgets with the new question
            self.normal_submit_button.configure(text='REVISJON', state='disabled', bg=self.configs_tk['color_white'])
            self.feedback_label.configure(text='')
            self.text_container.destroy()
            self.image_container.destroy()
            self.choice_container.destroy()

            self.create_text_container(self.normal_quiz_frame)
            self.create_image_container(self.normal_quiz_frame)
            self.create_normal_choice_container(self.normal_quiz_frame)

            if self.questions[self.current_question_index].psyko_text != '':
                self.psyko_text_label.configure(text=self.questions[self.current_question_index].psyko_text, fg=self.configs_tk['color_red'])

            for ce in zip(self.choice_explainations, self.choice_explaination_contents, self.psyko_explainations, self.psyko_explaination_contents):
                ce[0].configure(text=ce[1])
                ce[2].configure(text=ce[3])
                if ce[1].strip(' ')[0] == self.questions[self.current_question_index].answer_tag:
                    ce[0].configure(bg=self.configs_tk['color_green'])
                else:
                    ce[0].configure(bg=self.configs_tk['color_orange'])
                ce[2].configure(fg=self.configs_tk['color_red'])

            self.progress_count.set(f'Progresjon: {self.current_question_index + 1} av {len(self.questions)}')

        else:
            self.normal_quiz_frame.destroy()
            self.create_normal_menu_frame()

    def on_submit_normal(self):
        if self.choice_var.get() != '0':
            self.submit_normal = True
            if self.questions[self.current_question_index].psyko_text != '':
                self.psyko_text_label.configure(text=self.questions[self.current_question_index].psyko_text, fg=self.configs_tk['color_red'])
                self.feedback_label.configure(text='PSYKOMETRI')

                if self.questions[self.current_question_index].abcd[self.choice_var.get()]["psyko"].lstrip(' ')[0] == '1':
                    self.correct_questions += 1
                    self.questions[self.current_question_index].completion_status = 1
                    self.questions[self.current_question_index].modify_json()
                else:
                    no_correct = True
                    for p in self.questions[self.current_question_index].abcd:
                        if self.questions[self.current_question_index].abcd[p]["psyko"].lstrip(' ')[0] == '1':
                            no_correct = False
                    if no_correct == True:
                        self.questions[self.current_question_index].completion_status = 1
                        self.questions[self.current_question_index].modify_json()

            else:
                if self.choice_var.get() == self.questions[self.current_question_index].answer_tag:
                    self.feedback_label.configure(text='RIKTIG')
                    self.correct_questions += 1
                    self.questions[self.current_question_index].completion_status = 1
                    self.questions[self.current_question_index].modify_json()
                else:
                    self.feedback_label.configure(text='FEIL')

            for ce in zip(self.choice_explainations, self.choice_explaination_contents, self.psyko_explainations, self.psyko_explaination_contents):
                ce[0].configure(text=ce[1])
                ce[2].configure(text=ce[3])
                if ce[1].strip(' ')[0] == self.questions[self.current_question_index].answer_tag:
                    ce[0].configure(bg=self.configs_tk['color_green'])
                else:
                    ce[0].configure(bg=self.configs_tk['color_orange'])
                ce[2].configure(fg=self.configs_tk['color_red'])

            self.correct_count.set(
                f'Riktige: {round((self.correct_questions * 100 / (self.current_largest_question_index + 1)), 1)}% ({self.correct_questions} av {self.current_largest_question_index + 1})')
            self.normal_submit_button.configure(text='NESTE', command=lambda: self.on_submit_next_normal(), bg=self.configs_tk['color_green'])

    def update_statistics_normal(self):
        total_questions = 0
        total_completed_questions = 0
        for c in self.normal_category_list:
            category_total_questions = 0
            category_completed_questions = 0

            for pth in self.file_path_list:
                if c in pth:
                    file_json = open(pth)
                    try:
                        file_dict = json.load(file_json)
                    except:
                        print(file_json)

                    for q in range(1, len(file_dict) + 1):
                        question = MCQ(file_dict[f'{pth.rsplit(".", 1)[0]}_{q}'])
                        category_total_questions += 1
                        if question.completion_status != 0:
                            category_completed_questions += 1
            self.statistics_obj.statistics_dict["QUIZMODUS"][f'{c} fullføringsgrad'] = f'{round((category_completed_questions * 100 / category_total_questions), 1)}% ({category_completed_questions} av {category_total_questions} oppgaver)'
            total_questions += category_total_questions
            total_completed_questions += category_completed_questions
        self.statistics_obj.statistics_dict["QUIZMODUS"]['Total fullføringsgrad'] = f'{round((total_completed_questions * 100 / total_questions), 1)}% ({total_completed_questions} av {total_questions} oppgaver)'
        self.statistics_obj.write_dict_to_json()

    def on_submit_next_normal(self):
        # Move to the next question
        self.current_question_index += 1
        self.current_largest_question_index += 1
        self.submit_normal = False
        if self.current_question_index >= len(self.questions):
            self.normal_quiz_frame.destroy()
            self.create_normal_menu_frame()
        else:
            # Update the widgets with the new question
            self.progress_count.set(f'Progresjon: {self.current_question_index + 1} av {len(self.questions)}')

            self.normal_submit_button.configure(text='SVAR', command=lambda: self.on_submit_normal(), bg=self.configs_tk['color_green'])
            self.feedback_label.configure(text='')
            self.text_container.destroy()
            self.image_container.destroy()
            self.choice_container.destroy()

            self.create_text_container(self.normal_quiz_frame)
            self.create_image_container(self.normal_quiz_frame)
            if self.normal_hidden_mode_var.get() == 'Skjult':
                self.normal_submit_button.configure(text='VIS', command=lambda: self.on_show_normal())
            else:
                self.create_normal_choice_container(self.normal_quiz_frame)

    def create_exam_tag_filter_container(self):
        exam_tag_filter_container = tk.Frame(self.exam_menu_frame)
        exam_tag_filter_container.pack(pady=10)

        box_label = tk.LabelFrame(exam_tag_filter_container,
                             text='EKSAMENSFILTER', font=self.configs_tk['font_b'], padx=30, pady=20)
        box_label.pack()

        box_label_info_button = tk.Menubutton(box_label, text="Info", font=self.configs_tk['font_i'],
                                              bg=self.configs_tk['color_grey'], fg=self.configs_tk['color_white'], relief='raised', height=1,
                                              width=10)
        box_label_info_button.pack(anchor='w')
        box_label_info_button.menu = tk.Menu(box_label_info_button, tearoff=0)
        box_label_info_button["menu"] = box_label_info_button.menu
        box_label_info_button.menu.add_cascade(
            label='Skriv inn ønskede stikkord for å filtrere de underliggende eksamensettene')
        box_label_info_button.menu.add_cascade(
            label='Angitte stikkord søkes for i tittelen på eksamensettene. Ved tomt filter viser underliggende liste alle eksamensett')
        box_label_info_button.menu.add_cascade(
            label='Dersom flere stikkord er ønskelig, brukes "," for å skille stikkordene (dvs komma uten hermetegnene)')
        box_label_info_button.menu.add_cascade(
            label='Filteret skiller kun på mellomrom. Det vil være forskjell på "nasjonal" vs "nasjonal ", men ikke "VÅR" vs "vår"')
        box_label_info_button.menu.add_cascade(
            label='Et filter for Nasjonal delprøve kan feks være: nasjonal')

        self.exam_text_input = tk.Text(box_label, font=self.configs_tk['font'], height=1)
        self.exam_text_input.pack()

    def create_exam_list_container(self):
        exam_list_container = tk.Frame(self.exam_menu_frame)
        exam_list_container.pack(pady=10)

        box_label = tk.LabelFrame(exam_list_container,
                                  text='ALLE EKSAMENER', font=self.configs_tk['font_b'], padx=32, pady=20)
        box_label.pack()
        box_label_info_button = tk.Menubutton(box_label, text="Info", font=self.configs_tk['font_i'],
                                              bg=self.configs_tk['color_grey'], fg=self.configs_tk['color_white'], relief='raised', height=1,
                                              width=10)
        box_label_info_button.pack(anchor='w')
        box_label_info_button.menu = tk.Menu(box_label_info_button, tearoff=0)
        box_label_info_button["menu"] = box_label_info_button.menu
        box_label_info_button.menu.add_cascade(
            label='Valg av spesifikke eksamensett. Kun 1 eksamensett kan velges om gangen. Fullførte eksamensett markeres i grønt')
        for i in self.category_info_list:
            box_label_info_button.menu.add_cascade(label=i)

        listbox_subcontainer = tk.Frame(box_label)
        listbox_subcontainer.pack()

        self.exam_listbox = tk.Listbox(listbox_subcontainer, font=self.configs_tk['font'], width=78, height=7, selectmode='SINGLE')
        for i, r in enumerate(self.file_path_list):
            self.exam_listbox.insert(i + 1, r.rsplit('.', 1)[0])
            if r.rsplit('.', 1)[0] in self.statistics_obj.statistics_dict['EKSAMENSMODUS']['Leverte eksamensett']:
                self.exam_listbox.itemconfig(i, {'bg': self.configs_tk['color_green']})
        self.exam_listbox.pack(anchor='w', side='left', fill='both')

        scrollbar = tk.Scrollbar(listbox_subcontainer)
        scrollbar.pack(anchor='w', side='right', fill='both')
        self.exam_listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.exam_listbox.yview)

        filter_button = tk.Button(box_label, text='Filtrer', command=lambda: self.on_filter_exam(),
                                  bg=self.configs_tk['color_white'], font=self.configs_tk['font_i'],
                                  height=1, width=10)
        filter_button.pack(anchor='w')

    def create_exam_time_container(self):
        exam_time_container = tk.Frame(self.exam_menu_frame)
        exam_time_container.pack(pady=10)

        box_label = tk.LabelFrame(exam_time_container, text='EKSAMENSTID', font=self.configs_tk['font_b'], padx=32, pady=20, height=180, width=792)
        box_label.pack()
        box_label_info_button = tk.Menubutton(box_label, text="Info", font=self.configs_tk['font_i'],
                                              bg=self.configs_tk['color_grey'], fg=self.configs_tk['color_white'], relief='raised', height=1,
                                              width=10)
        box_label_info_button.grid(row=0, column=0, sticky='w')
        box_label_info_button.menu = tk.Menu(box_label_info_button, tearoff=0)
        box_label_info_button["menu"] = box_label_info_button.menu
        box_label_info_button.menu.add_cascade(
            label='Valg av eksamenstid for eksamensettet. Ordinær tid for Nasjonal deleksamen er 4 timer')
        box_label_info_button.menu.add_cascade(label='Dersom egendefinert eksamenstid velges, må dette ligge mellom 0-300 min (0-5 timer)')

        self.exam_time_mode_var.set('0')
        for i, r in enumerate(self.exam_time_mode_list):
            button = tk.Radiobutton(box_label, text=r, variable=self.exam_time_mode_var, value=r,
                                    font=self.configs_tk['font'], command=lambda: self.on_manual_time())
            button.grid(row=i + 1, column=0, sticky='w')
            if r == 'Egendefinert (0-300 min)':
                self.manual_time_input = tk.Spinbox(box_label, from_=0, to=300, font=self.configs_tk['font'], state='disabled', textvariable=self.exam_manual_time_var)
                self.manual_time_input.grid(row=i+1, column=1, sticky='w')

        box_label.grid_propagate(False)  # makes height and width in labelframe active

    def create_exam_overview_container(self):
        exam_overview_container = tk.Frame(self.exam_menu_frame)
        exam_overview_container.pack(pady=10)

        box_label = tk.LabelFrame(exam_overview_container, text='EKSAMENSOVERSIKT', font=self.configs_tk['font_b'],
                                  padx=32, pady=20, height=220, width=792)
        box_label.pack()
        box_label_info_button = tk.Menubutton(box_label, text="Info", font=self.configs_tk['font_i'],
                                              bg=self.configs_tk['color_grey'], fg=self.configs_tk['color_white'], relief='raised', height=1,
                                              width=10)
        box_label_info_button.pack(anchor='w')
        box_label_info_button.menu = tk.Menu(box_label_info_button, tearoff=0)
        box_label_info_button["menu"] = box_label_info_button.menu
        box_label_info_button.menu.add_cascade(label='Oversikt over valg av eksamensett og eksamenstid før "Start"')
        box_label_info_button.menu.add_cascade(label='Oppgaver man er usikre på i eksamensettet kan flagges som på Nasjonal deleksamen')
        box_label_info_button.menu.add_cascade(label='Alle oppgaver bør besvares før man trykker på "Lever eksamen". Dersom tiden går ut, leveres eksamen automatisk')
        box_label_info_button.menu.add_cascade(label='Beregnet eksamenscore er justert i henhold til psykometrien. Oppgaver fargekodes etter riktig/galt/psykometri/ubesvart')
        box_label_info_button.menu.add_cascade(label='Statistikk lagres når man trykker "Hjem" etter levert eksamensett')

        self.exam_id_label = tk.Label(box_label, text=f'Eksamensett: ?',
                                              font=self.configs_tk['font'], anchor='w', justify='left',
                                              wraplength=self.configs_tk['w_length_menu'])
        self.exam_id_label.pack(anchor='w')
        self.exam_questions_number_label = tk.Label(box_label, text=f'Antall oppgaver: ?',
                                                    font=self.configs_tk['font'], anchor='w', justify='left',
                                                    wraplength=self.configs_tk['w_length_menu'])
        self.exam_questions_number_label.pack(anchor='w')
        self.exam_time_label = tk.Label(box_label, text=f'Eksamenstid: ?',
                                                    font=self.configs_tk['font'], anchor='w', justify='left',
                                                    wraplength=self.configs_tk['w_length_menu'])
        self.exam_time_label.pack(anchor='w')

        update_button = tk.Button(box_label, text='Oppdater',
                                  bg=self.configs_tk['color_white'], font=self.configs_tk['font_i'],
                                  height=1, width=10, command=lambda: self.on_check_exam())
        update_button.pack(anchor='w')

        box_label.pack_propagate(False)  # makes height and width in labelframe active

    def create_exam_start_container(self):
        exam_start_container = tk.Frame(self.exam_menu_frame)
        exam_start_container.pack(pady=10)

        start_button = tk.Button(exam_start_container, text='START', command=lambda: self.on_start_exam(),
                                 bg=self.configs_tk['color_green'], height=2, width=30, font=self.configs_tk['font_b'])
        start_button.grid(row=0, column=1, padx=5)

    def create_exam_menu_frame(self):
        self.questions = []
        self.current_question_index = 0
        self.correct_questions = 0
        self.exam_filter_tags = []
        self.horizontal_button_list = []
        self.question_answer_choice_list = []
        self.flagged_question_list = []
        self.submit_exam = False
        self.hour = '00'
        self.minute = '00'
        self.second = '00'
        self.total_exam_time_sec = 0
        self.remaining_exam_time_sec = 0

        self.exam_menu_frame = tk.Frame(self.main_canvas, pady=10, padx=80)
        self.main_canvas.create_window((self.max_width // 2, 0), window=self.exam_menu_frame, anchor="n")
        self.exam_menu_frame.bind('<Configure>',
                                  lambda e: self.main_canvas.configure(scrollregion=self.main_canvas.bbox("all")))

        self.create_subtitle_info_container(self.exam_menu_frame, 'EKSAMENSMODUS')
        self.create_exam_tag_filter_container()
        self.create_exam_list_container()
        self.create_exam_time_container()
        self.create_exam_overview_container()
        self.create_exam_start_container()

    def create_exam_question_dock_info_container(self):
        dock_info_container = tk.Frame(self.exam_quiz_frame, height=40, width=790)
        dock_info_container.pack(anchor='w')

        self.progress_count = tk.StringVar()
        self.progress_count.set(f'Progresjon: {self.current_question_index + 1} av {len(self.questions)}')
        progress_number = tk.Label(dock_info_container, textvariable=self.progress_count,
                                   font=self.configs_tk['font_ib'])
        progress_number.pack(side=tk.LEFT)

        if self.exam_time_mode_var.get() != 'Ingen':
            self.time_count = tk.StringVar()
            self.time_count.set(f'Eksamenstid: {self.hour}:{self.minute}:{self.second}')
            time_count_label = tk.Label(dock_info_container, textvariable=self.time_count,
                                        font=self.configs_tk['font_ib'])
            time_count_label.pack(side=tk.RIGHT)
        else:
            time_count_label = tk.Label(dock_info_container, text='Eksamenstid: Ingen', font=self.configs_tk['font_ib'])
            time_count_label.pack(side=tk.RIGHT)

        dock_info_container.pack_propagate(False)

    def create_exam_question_dock_horizontal_button_container(self):
        dummy_container = tk.Frame(self.exam_quiz_frame, width=780, height=50, highlightbackground='black', highlightthickness=1)#, bg='blue')
        dummy_container.pack(anchor='center', pady=10)

        button_canvas = tk.Canvas(dummy_container, height=30)#, bg='green') #canvas reduces height(padding) from the top, button has to be sw
        button_canvas.pack(anchor='nw', expand=True, fill=tk.X)

        scrollbar = tk.Scrollbar(dummy_container, orient=tk.HORIZONTAL, command=button_canvas.xview)
        scrollbar.pack(fill=tk.X, side=tk.BOTTOM, anchor='nw')
        button_canvas.config(xscrollcommand=scrollbar.set)
        scrollbar.config(command=button_canvas.xview)
        dummy_container.bind('<Configure>',
                             lambda e: button_canvas.configure(scrollregion=button_canvas.bbox("all")))

        button_subcontainer = tk.Frame(button_canvas)#, bg='red') #canvas reduces height(padding) from the top, button has to be sw
        button_subcontainer.pack(anchor='nw')

        for q in range(len(self.questions)):
            q_button = tk.Button(button_subcontainer, text=f'{q + 1}',
                                 command=lambda q=q: self.on_specific_question_exam(q),
                                 bg=self.configs_tk['color_white'], height=1, width=3,
                                 font=self.configs_tk['font_i'])
            self.horizontal_button_list.append(q_button)
            self.flagged_question_list.append(0)
            self.question_answer_choice_list.append('0')
            q_button.pack(side=tk.LEFT, anchor='sw')

        button_canvas.create_window((0, 0), window=button_subcontainer, anchor='sw', height=60)
        dummy_container.pack_propagate(False)

    def create_exam_question_dock_button_container(self):
        button_container = tk.Frame(self.exam_quiz_frame)
        button_container.pack(anchor='center')

        previous_button = tk.Button(button_container, text='<', command=lambda: self.on_previous_exam(),
                                    bg=self.configs_tk['color_white'], height=1, width=7, font=self.configs_tk['font_b'])
        previous_button.grid(row=0, column=0, padx=5)
        self.flag_button = tk.Button(button_container, text='Flagg', command=lambda: self.on_flag_question_exam(), fg=self.configs_tk['color_white'], bg=self.configs_tk['color_grey'], height=1, width=14, font=self.configs_tk['font_i'])
        self.flag_button.grid(row=0, column=1, padx=5)
        next_button = tk.Button(button_container, text='>', command=lambda: self.on_next_exam(), bg=self.configs_tk['color_white'], height=1, width=7, font=self.configs_tk['font_b'])
        next_button.grid(row=0, column=2, padx=5)

        self.flag_label = tk.Label(button_container, text='', font=self.configs_tk['font_b'])
        self.flag_label.grid(row=1, column=1, padx=5)

    def create_exam_submit_container(self):
        self.exam_submit_container = tk.Frame(self.exam_quiz_frame)
        self.exam_submit_container.pack(anchor='center', pady=10)

        self.exam_submit_button = tk.Button(self.exam_submit_container, text='LEVER EKSAMEN', command=lambda: self.on_submit_exam(),
                                    bg=self.configs_tk['color_green'], height=2, width=30, font=self.configs_tk['font_b'])
        self.exam_submit_button.pack()

    def create_exam_results_info_container(self, n_total, n_correct, n_unanswered, n_psyko, n_pskyo_zero):
        results_info_container = tk.Frame(self.exam_quiz_frame, height=80, width=790)
        results_info_container.pack(anchor='w')

        self.exam_results_correct = n_correct #temp fix
        self.exam_results_total_after_psyko = n_total - n_pskyo_zero # temp fix

        left_subcontainer = tk.Frame(results_info_container)
        left_subcontainer.pack(side=tk.LEFT)

        correct_n_label = tk.Label(left_subcontainer, text=f'Eksamenscore: {round((n_correct * 100 / (n_total - n_pskyo_zero)), 1)}% ({n_correct} av {n_total - n_pskyo_zero} riktige)', font=self.configs_tk['font_ib'])
        correct_n_label.pack(anchor='w')
        unanswered_n_label = tk.Label(left_subcontainer,
                                   text=f'Besvarte oppgaver: {n_total - n_unanswered} av {n_total}',
                                   font=self.configs_tk['font_ib'])
        unanswered_n_label.pack(anchor='w')
        psyko_n_label = tk.Label(left_subcontainer,
                                   text=f'Psykometri-oppgaver: {n_psyko} ({n_pskyo_zero} av {n_psyko} fjernet)',
                                   font=self.configs_tk['font_ib'])
        psyko_n_label.pack(anchor='w')

        right_subcontainer = tk.Frame(results_info_container)
        right_subcontainer.pack(side=tk.RIGHT)

        hours, mins, secs = calculate_time_from_seconds(self.total_exam_time_sec - self.remaining_exam_time_sec)
        if self.exam_time_mode_var.get() != 'Ingen':
            time_usage_label = tk.Label(right_subcontainer,
                                       text=f'Tidsforbruk: {"{:0>2d}".format(hours)}:{"{:0>2d}".format(mins)}:{"{:0>2d}".format(secs)}',
                                       font=self.configs_tk['font_ib'])
            time_usage_label.pack(anchor='ne')
        else:
            time_usage_label = tk.Label(right_subcontainer,
                                        text=f'Tidsforbruk: ?',
                                        font=self.configs_tk['font_ib'])
            time_usage_label.pack(anchor='ne')

        if n_total > n_unanswered:
            mean_time_label = tk.Label(right_subcontainer,
                                          text=f'Gjennomsnittstid per svar: {round((self.total_exam_time_sec - self.remaining_exam_time_sec) / (n_total - n_unanswered), 1)} sek',
                                          font=self.configs_tk['font_ib'])
            mean_time_label.pack(anchor='ne')
        else:
            mean_time_label = tk.Label(right_subcontainer,
                                       text=f'Gjennomsnittstid per svar: ? sek',
                                       font=self.configs_tk['font_ib'])
            mean_time_label.pack(anchor='ne')
        allocated_time_label = tk.Label(right_subcontainer,
                                   text=f'Avsatt tid per svar: {round((self.total_exam_time_sec) / (n_total), 1)} sek',
                                   font=self.configs_tk['font_ib'])
        allocated_time_label.pack(anchor='ne')

        results_info_container.pack_propagate(False)

    def exam_timer_tick(self):
        hours, mins, secs = calculate_time_from_seconds(self.remaining_exam_time_sec)

        self.time_count.set(f'Eksamenstid: {"{:0>2d}".format(hours)}:{"{:0>2d}".format(mins)}:{"{:0>2d}".format(secs)}')

        if self.submit_exam != True:
            if self.remaining_exam_time_sec > 0:
                self.remaining_exam_time_sec -= 1
                self.exam_quiz_frame.after(1000, self.exam_timer_tick)
            else:
                self.on_submit_exam()

    def create_exam_choice_container(self, frame):
        self.choice_container = tk.Frame(frame)
        self.choice_container.pack(anchor='w')

        self.choice_explainations = []
        self.choice_explaination_contents = []
        self.psyko_explainations = []
        self.psyko_explaination_contents = []

        if self.question_answer_choice_list[self.current_question_index] != '0':
            self.choice_var.set(self.question_answer_choice_list[self.current_question_index])
        else:
            self.choice_var.set('0')

        for choice in self.questions[self.current_question_index].abcd:
            choice_text = f'{choice}: {self.questions[self.current_question_index].abcd[choice]["answer"]}'
            button = tk.Radiobutton(self.choice_container, text=choice_text, variable=self.choice_var, value=choice,
                                    font=self.configs_tk['font_b'], justify='left', wraplength=self.configs_tk['w_length'], command=lambda: self.on_choice_exam())
            button.pack(anchor='w')

            if self.choice_var.get() == choice:
                button.select()

            try:
                explaination = f'{choice}: {self.questions[self.current_question_index].abcd[choice]["explaination"]}'
            except:
                explaination = f'{choice}: Ingen forklaring'

            try:
                psyko = f'{choice}: {self.questions[self.current_question_index].abcd[choice]["psyko"]}'
            except:
                psyko = f''

            choice_explanation = tk.Label(self.choice_container, text='', font=self.configs_tk['font'], justify='left', wraplength=self.configs_tk['w_length'])
            choice_explanation.pack(anchor='w')
            self.choice_explaination_contents.append(explaination)
            self.choice_explainations.append(choice_explanation)

            psyko_explanation = tk.Label(self.choice_container, text='', font=self.configs_tk['font_b'], justify='left', wraplength=self.configs_tk['w_length'])
            psyko_explanation.pack(anchor='w')
            self.psyko_explaination_contents.append(psyko)
            self.psyko_explainations.append(psyko_explanation)

            if self.submit_exam == True:
                button.configure(state='disabled')

        if self.submit_exam == True:
            if self.questions[self.current_question_index].psyko_text != '':
                self.psyko_text_label.configure(text=self.questions[self.current_question_index].psyko_text,
                                                fg=self.configs_tk['color_red'])

            for ce in zip(self.choice_explainations, self.choice_explaination_contents, self.psyko_explainations,
                          self.psyko_explaination_contents):
                ce[0].configure(text=ce[1])
                ce[2].configure(text=ce[3])
                if ce[1].strip(' ')[0] == self.questions[self.current_question_index].answer_tag:
                    ce[0].configure(bg=self.configs_tk['color_green'])
                else:
                    ce[0].configure(bg=self.configs_tk['color_orange'])
                ce[2].configure(fg=self.configs_tk['color_red'])

    def create_exam_quiz_frame(self):
        self.exam_quiz_frame = tk.Frame(self.main_canvas, pady=10, padx=80)
        self.main_canvas.create_window((self.max_width // 2, 0), window=self.exam_quiz_frame, anchor="n")
        self.exam_quiz_frame.bind('<Configure>', lambda e: self.main_canvas.configure(scrollregion=self.main_canvas.bbox("all")))

        self.create_subtitle_info_container(self.exam_quiz_frame, 'EKSAMENSMODUS')
        self.create_exam_question_dock_info_container()
        self.create_exam_question_dock_horizontal_button_container()
        self.create_exam_question_dock_button_container()
        self.create_text_container(self.exam_quiz_frame)
        self.create_image_container(self.exam_quiz_frame)
        self.create_exam_choice_container(self.exam_quiz_frame)
        self.horizontal_button_list[self.current_question_index].configure(font=self.configs_tk['font_ib'])
        self.create_exam_submit_container()
        if self.exam_time_mode_var.get() != 'Ingen':
            self.exam_timer_tick()

    def create_exam_quiz_frame_from_menu(self):
        self.exam_menu_frame.destroy()
        self.create_exam_quiz_frame()

    def create_exam_menu_from_intro(self):
        self.intro_frame.destroy()
        self.create_exam_menu_frame()

    def on_manual_time(self):
        if self.exam_time_mode_var.get() == 'Egendefinert (0-300 min)':
            self.manual_time_input.configure(state='normal')
        else:
            self.manual_time_input.configure(state='disabled')

    def on_filter_exam(self):
        self.exam_filter_tags = input_tags_to_list(self.exam_text_input.get("1.0", 'end-1c'))

        self.exam_listbox.delete(0, self.exam_listbox.size())
        filtered_listbox_file = []

        for j in self.file_path_list:
            if check_tag_in_string(j, self.exam_filter_tags):
                filtered_listbox_file.append(j)

        for i, r in enumerate(filtered_listbox_file):
            self.exam_listbox.insert(i + 1, r.rsplit('.', 1)[0])
            if r.rsplit('.', 1)[0] in self.statistics_obj.statistics_dict['EKSAMENSMODUS']['Leverte eksamensett']:
                self.exam_listbox.itemconfig(i, {'bg': self.configs_tk['color_green']})

    def on_start_exam(self):
        if self.exam_listbox.curselection() != () and self.exam_time_mode_var.get() != '0':
            #print(self.exam_listbox.curselection())
            value = self.exam_listbox.get(self.exam_listbox.curselection())
            self.exam_choice.set(value)
            file_json_pth = self.exam_choice.get() + '.json'

            included_questions = []
            file_json = open(file_json_pth)
            try:
                file_dict = json.load(file_json)
                for q in range(1, len(file_dict) + 1):
                    question = MCQ(file_dict[f'{self.exam_choice.get()}_{q}'])
                    included_questions.append(question)
            except:
                print(file_json_pth)

            if self.exam_time_mode_var.get() == 'Egendefinert (0-300 min)':
                if self.exam_manual_time_var.get().isdigit() and int(self.exam_manual_time_var.get()) in range(1, 301):
                    self.total_exam_time_sec = int(self.exam_manual_time_var.get()) * 60
                    self.remaining_exam_time_sec = self.total_exam_time_sec
                else:
                    self.exam_time_label.configure(text=f'Eksamenstid: ?')
            elif self.exam_time_mode_var.get() == '4 timer (240 min)':
                self.total_exam_time_sec = 240 * 60
                self.remaining_exam_time_sec = self.total_exam_time_sec

            self.questions = included_questions
            if len(included_questions) > 0:
                self.create_exam_quiz_frame_from_menu()
                self.current_mode = 'EKSAMENSMODUS'

    def on_check_exam(self):
        if self.exam_listbox.curselection() != ():
            #print(self.exam_listbox.curselection())
            value = self.exam_listbox.get(self.exam_listbox.curselection())
            self.exam_choice.set(value)
            file_json_pth = self.exam_choice.get() + '.json'

            included_questions = []
            file_json = open(file_json_pth)
            try:
                file_dict = json.load(file_json)
                for q in range(1, len(file_dict) + 1):
                    question = MCQ(file_dict[f'{self.exam_choice.get()}_{q}'])
                    included_questions.append(question)
            except:
                print(file_json_pth)

            self.questions = included_questions
            self.exam_id_label.configure(text=f'Eksamensett: {self.exam_choice.get()}')
            self.exam_questions_number_label.configure(text=f'Antall oppgaver: {len(self.questions)}')
        else:
            self.exam_id_label.configure(text=f'Eksamensett: ?')
            self.exam_questions_number_label.configure(text=f'Antall oppgaver: ?')

        if self.exam_time_mode_var.get() != '0':
            if self.exam_time_mode_var.get() == 'Egendefinert (0-300 min)':
                if self.exam_manual_time_var.get().isdigit() and int(self.exam_manual_time_var.get()) in range(1, 301):
                    self.exam_time_label.configure(text=f'Eksamenstid: {self.exam_manual_time_var.get()} min')
                else:
                    self.exam_time_label.configure(text=f'Eksamenstid: ?')
            elif self.exam_time_mode_var.get() == '4 timer (240 min)':
                self.exam_time_label.configure(text='Eksamenstid: 4 timer (240 min)')
            else:
                self.exam_time_label.configure(text='Eksamenstid: Ingen')
        else:
            self.exam_time_label.configure(text='Eksamenstid: ?')

    def on_choice_exam(self):
        if self.choice_var.get() != '0':
            self.question_answer_choice_list[self.current_question_index] = self.choice_var.get()
        #print(self.question_answer_choice_list)

    def on_flag_question_exam(self):
        if self.flagged_question_list[self.current_question_index] == 0:
            self.flagged_question_list[self.current_question_index] = 1
            self.horizontal_button_list[self.current_question_index].configure(fg=self.configs_tk['color_white'], bg=self.configs_tk['color_grey'])
            self.flag_label.configure(text='⚑')
        else:
            self.flagged_question_list[self.current_question_index] = 0
            self.horizontal_button_list[self.current_question_index].configure(bg=self.configs_tk['color_white'], fg='black')
            self.flag_label.configure(text='')

    def on_specific_question_exam(self, question_index):
        self.horizontal_button_list[self.current_question_index].configure(font=self.configs_tk['font_i'])
        self.current_question_index = question_index
        self.horizontal_button_list[self.current_question_index].configure(font=self.configs_tk['font_ib'])

        # Update the widgets with the new question
        self.text_container.destroy()
        self.image_container.destroy()
        self.choice_container.destroy()
        self.exam_submit_container.destroy()

        self.create_text_container(self.exam_quiz_frame)
        self.create_image_container(self.exam_quiz_frame)
        self.create_exam_choice_container(self.exam_quiz_frame)
        self.create_exam_submit_container()
        if self.submit_exam == True:
            self.exam_submit_button.configure(state='disabled')

        if self.flagged_question_list[self.current_question_index] == 1:
            self.flag_label.configure(text='⚑')
        else:
            self.flag_label.configure(text='')
        self.progress_count.set(f'Progresjon: {self.current_question_index + 1} av {len(self.questions)}')

    def on_next_exam(self):
        if self.current_question_index < len(self.questions) - 1:
            self.current_question_index += 1
            self.horizontal_button_list[self.current_question_index].configure(font=self.configs_tk['font_ib'])
            self.horizontal_button_list[self.current_question_index - 1].configure(font=self.configs_tk['font_i'])

            # Update the widgets with the new question
            self.text_container.destroy()
            self.image_container.destroy()
            self.choice_container.destroy()
            self.exam_submit_container.destroy()

            self.create_text_container(self.exam_quiz_frame)
            self.create_image_container(self.exam_quiz_frame)
            self.create_exam_choice_container(self.exam_quiz_frame)
            self.create_exam_submit_container()
            if self.submit_exam == True:
                self.exam_submit_button.configure(state='disabled')

            if self.flagged_question_list[self.current_question_index] == 1:
                self.flag_label.configure(text='⚑')
            else:
                self.flag_label.configure(text='')
            self.progress_count.set(f'Progresjon: {self.current_question_index + 1} av {len(self.questions)}')

    def on_previous_exam(self):
        if self.current_question_index > 0:
            self.current_question_index -= 1
            self.horizontal_button_list[self.current_question_index].configure(font=self.configs_tk['font_ib'])
            self.horizontal_button_list[self.current_question_index + 1].configure(font=self.configs_tk['font_i'])

            if self.flagged_question_list[self.current_question_index] == 1:
                self.flag_label.configure(text='⚑')
            else:
                self.flag_label.configure(text='')
            self.progress_count.set(f'Progresjon: {self.current_question_index + 1} av {len(self.questions)}')

            # Update the widgets with the new question
            self.text_container.destroy()
            self.image_container.destroy()
            self.choice_container.destroy()
            self.exam_submit_container.destroy()

            self.create_text_container(self.exam_quiz_frame)
            self.create_image_container(self.exam_quiz_frame)
            self.create_exam_choice_container(self.exam_quiz_frame)
            self.create_exam_submit_container()
            if self.submit_exam == True:
                self.exam_submit_button.configure(state='disabled')

    def update_statistics_exam(self):
        if self.exam_choice.get() not in self.statistics_obj.statistics_dict["EKSAMENSMODUS"]["Leverte eksamensett"]:
            self.statistics_obj.statistics_dict["EKSAMENSMODUS"]["Leverte eksamensett"].append(self.exam_choice.get())
        self.statistics_obj.statistics_dict['EKSAMENSMODUS']['Total fullføringsgrad'] = f'{round(len(self.statistics_obj.statistics_dict["EKSAMENSMODUS"]["Leverte eksamensett"]) * 100 / len(self.file_path_list), 1)}% ({len(self.statistics_obj.statistics_dict["EKSAMENSMODUS"]["Leverte eksamensett"])} av {len(self.file_path_list)} eksamensett)'

        for c in self.normal_category_list:
            category_total_exams = 0
            category_completed_exams = 0

            for pth in self.file_path_list:
                if c in pth:
                    file_json = open(pth)
                    try:
                        file_dict = json.load(file_json)
                        category_total_exams += 1
                        if pth.rsplit('.', 1)[0] in self.statistics_obj.statistics_dict["EKSAMENSMODUS"]["Leverte eksamensett"]:
                            category_completed_exams += 1
                    except:
                        print(file_json)

            self.statistics_obj.statistics_dict['EKSAMENSMODUS'][f'{c} fullføringsgrad'] = f'{round(category_completed_exams * 100 / category_total_exams, 1)}% ({category_completed_exams} av {category_total_exams} eksamensett)'

        if float(self.statistics_obj.statistics_dict['EKSAMENSMODUS']['Beste eksamenscore'].split('%', 1)[0]) < (self.exam_results_correct * 100 / self.exam_results_total_after_psyko):
            self.statistics_obj.statistics_dict['EKSAMENSMODUS']['Beste eksamensett'] = self.exam_choice.get()
            self.statistics_obj.statistics_dict['EKSAMENSMODUS']['Beste eksamenscore'] = f'{round((self.exam_results_correct * 100 / self.exam_results_total_after_psyko), 1)}% ({self.exam_results_correct} av {self.exam_results_total_after_psyko} oppgaver)'
        elif self.statistics_obj.statistics_dict['EKSAMENSMODUS']['Beste eksamensett'] == '':
            self.statistics_obj.statistics_dict['EKSAMENSMODUS']['Beste eksamensett'] = self.exam_choice.get()
            self.statistics_obj.statistics_dict['EKSAMENSMODUS']['Beste eksamenscore'] = f'{round((self.exam_results_correct * 100 / self.exam_results_total_after_psyko), 1)}% ({self.exam_results_correct} av {self.exam_results_total_after_psyko} oppgaver)'

        self.statistics_obj.write_dict_to_json()

    def on_submit_exam(self):
        n_total = 0
        n_correct = 0
        n_unanswered = 0
        n_psykometri = 0
        n_psykometri_zero = 0
        for i, q in enumerate(zip(self.question_answer_choice_list, self.horizontal_button_list)):
            n_total += 1
            self.horizontal_button_list[i].configure(fg='black', bg=self.configs_tk['color_white'])
            if self.questions[i].psyko_text != '':
                n_psykometri += 1
                self.horizontal_button_list[i].configure(bg=self.configs_tk['color_red'])
                no_correct = True
                for p in self.questions[i].abcd:
                    if self.questions[i].abcd[p]["psyko"].lstrip(' ')[0] == '1':
                        no_correct = False
                if no_correct == True:
                    n_psykometri_zero += 1
            if q[0] == '0':
                n_unanswered += 1
            else:
                if self.questions[i].psyko_text != '':
                    if self.questions[i].abcd[q[0]]["psyko"].lstrip(' ')[0] == '1':
                        n_correct += 1
                elif self.questions[i].answer_tag == q[0]:
                    n_correct += 1
                    self.horizontal_button_list[i].configure(bg=self.configs_tk['color_green'])
                else:
                    self.horizontal_button_list[i].configure(bg=self.configs_tk['color_orange'])

        self.submit_exam = True
        self.flag_button.configure(state='disabled')
        self.create_exam_results_info_container(n_total, n_correct, n_unanswered, n_psykometri, n_psykometri_zero)
        self.on_specific_question_exam(0)

    def create_doctor_level_container(self):
        normal_level_container = tk.Frame(self.doctor_menu_frame)
        normal_level_container.pack(pady=10)

        box_label = tk.LabelFrame(normal_level_container, text='TITLER', font=self.configs_tk['font_b'],
                                  padx=32, pady=20, height=410, width=792)
        box_label.pack()
        box_label_info_button = tk.Menubutton(box_label, text="Info", font=self.configs_tk['font_i'],
                                              bg=self.configs_tk['color_grey'], fg=self.configs_tk['color_white'], relief='raised', height=1,
                                              width=10)
        box_label_info_button.pack(anchor='w')
        box_label_info_button.menu = tk.Menu(box_label_info_button, tearoff=0)
        box_label_info_button["menu"] = box_label_info_button.menu
        box_label_info_button.menu.add_cascade(label='Oversikt over titler som kan oppnås basert på antall riktige oppgaver som besvares')
        box_label_info_button.menu.add_cascade(label='Medisinstudent - Tildeles ved 0 riktige oppgaver')
        for j in range(1, len(self.doctor_evolution_path_list)):
            if j > self.doctor_evolution_path_alias_list.index(self.statistics_obj.statistics_dict['OVERLEGEMODUS']['Beste tittel']):
                box_label_info_button.menu.add_cascade(label=f'(Låst tittel) - Tildeles ved {10 * 2 ** (j - 1)} riktige oppgaver')
            else:
                box_label_info_button.menu.add_cascade(label=f'{self.doctor_evolution_path_alias_list[j]} - Tildeles ved {10 * 2**(j - 1)} riktige oppgaver')

        self.img_level_count = tk.StringVar()
        self.img_level_count.set(f'{self.doctor_evolution_path_alias_list[0]} - 0 riktige oppgaver')
        img_count_level_label = tk.Label(box_label, textvariable=self.img_level_count,
                                         font=self.configs_tk['font_ib'])

        img_count_level_label.pack()

        image_container_buttons = tk.Frame(box_label)
        image_container_buttons.pack()

        # create evolution img
        self.evolution_img_index = 0
        self.evolution_img_list_pil = scale_image(self.doctor_evolution_path_list)

        image_tk = ImageTk.PhotoImage(self.evolution_img_list_pil[self.evolution_img_index])
        self.evolution_image_label = tk.Label(image_container_buttons, image=image_tk)
        self.evolution_image_label.image = image_tk
        self.evolution_image_label.grid(row=0, column=1)

        self.left_scroll_level_button = tk.Button(image_container_buttons, text='<',
                                            command=lambda: self.on_leftscroll_doctor(),
                                            bg=self.configs_tk['color_white'], font=self.configs_tk['font_b'],
                                            height=1, width=7, state='disabled')
        self.right_scroll_level_button = tk.Button(image_container_buttons, text='>',
                                             command=lambda: self.on_rightscroll_doctor(),
                                             bg=self.configs_tk['color_white'], font=self.configs_tk['font_b'],
                                             height=1, width=7)
        self.left_scroll_level_button.grid(row=0, column=0, padx=5)
        self.right_scroll_level_button.grid(row=0, column=2, padx=5)

        box_label.pack_propagate(False)  # makes height and width in labelframe active

    def create_doctor_powerup_container(self):
        normal_powerup_container = tk.Frame(self.doctor_menu_mode_container)
        normal_powerup_container.pack(side=tk.LEFT)

        box_label = tk.LabelFrame(normal_powerup_container, text='HJELPEMIDLER', font=self.configs_tk['font_b'],
                                  padx=32, pady=20, height=180, width=264)
        box_label.pack()
        box_label_info_button = tk.Menubutton(box_label, text="Info", font=self.configs_tk['font_i'],
                                              bg=self.configs_tk['color_grey'], fg=self.configs_tk['color_white'], relief='raised', height=1,
                                              width=10)
        box_label_info_button.pack(anchor='w')
        box_label_info_button.menu = tk.Menu(box_label_info_button, tearoff=0)
        box_label_info_button["menu"] = box_label_info_button.menu
        box_label_info_button.menu.add_cascade(label='Oversikt over spesielle hjelpemidler for denne modusen. Hvert hjelpemiddel kan brukes inntil 3 ganger')
        box_label_info_button.menu.add_cascade(
            label='📞 (Ringe en venn) - Du konfererer med en smartere kollega som utelukker halvparten av svaralternativene')
        box_label_info_button.menu.add_cascade(
            label='🕒 (Jobbe overtid) - Du jobber overtid og får dobbelt så lang tid på nåværende oppgave')

        call_label = tk.Label(box_label, text=f'📞 (Ringe en venn)',
                                          font=self.configs_tk['font'], anchor='w', justify='left',
                                          wraplength=self.configs_tk['w_length_menu'])
        call_label.pack(anchor='w', pady=2)
        overtime_label = tk.Label(box_label, text=f'🕒 (Jobbe overtid)',
                                               font=self.configs_tk['font'], anchor='w', justify='left',
                                               wraplength=self.configs_tk['w_length_menu'])
        overtime_label.pack(anchor='w', pady=2)

        box_label.pack_propagate(False)  # makes height and width in labelframe active

    def create_doctor_time_mode_container(self):
        doctor_time_mode_container = tk.Frame(self.doctor_menu_mode_container)
        doctor_time_mode_container.pack(side=tk.LEFT)

        box_label = tk.LabelFrame(doctor_time_mode_container, text='TIDSPRESS', font=self.configs_tk['font_b'], padx=32, pady=20, height=180, width=264)
        box_label.pack()
        box_label_info_button = tk.Menubutton(box_label, text="Info", font=self.configs_tk['font_i'],
                                              bg=self.configs_tk['color_grey'], fg=self.configs_tk['color_white'], relief='raised', height=1,
                                              width=10)
        box_label_info_button.pack(anchor='w')
        box_label_info_button.menu = tk.Menu(box_label_info_button, tearoff=0)
        box_label_info_button["menu"] = box_label_info_button.menu
        box_label_info_button.menu.add_cascade(label='Tiden du har til å svare og lese fasit på hver oppgave. Overflødig tid overføres ikke til neste oppgave')
        box_label_info_button.menu.add_cascade(label='På post har du tid til å drikke kaffe. På poliklinikk må du gjennom listen. På vakt brenner det rundt deg')

        self.doctor_time_mode_var.set('0')
        for r in self.doctor_time_mode_list:
            button = tk.Radiobutton(box_label, text=r, variable=self.doctor_time_mode_var, value=r, font=self.configs_tk['font'])
            button.pack(anchor='w')

        box_label.pack_propagate(False)  # makes height and width in labelframe active

    def create_doctor_life_mode_container(self):
        doctor_life_mode_container = tk.Frame(self.doctor_menu_mode_container)
        doctor_life_mode_container.pack(side=tk.LEFT)

        box_label = tk.LabelFrame(doctor_life_mode_container, text='PASIENTSTATUS', font=self.configs_tk['font_b'], padx=32,
                                       pady=20, height=180, width=264)
        box_label.pack()
        box_label_info_button = tk.Menubutton(box_label, text="Info", font=self.configs_tk['font_i'],
                                              bg=self.configs_tk['color_grey'], fg=self.configs_tk['color_white'],
                                              relief='raised', height=1,
                                              width=10)
        box_label_info_button.pack(anchor='w')
        box_label_info_button.menu = tk.Menu(box_label_info_button, tearoff=0)
        box_label_info_button["menu"] = box_label_info_button.menu
        box_label_info_button.menu.add_cascade(
            label='Antall feil man kan gjøre før man taper')
        box_label_info_button.menu.add_cascade(
            label='Dårlige pasienter har mindre marginer for feil')

        self.doctor_life_mode_var.set('0')
        for r in self.doctor_life_mode_list:
            button = tk.Radiobutton(box_label, text=r, variable=self.doctor_life_mode_var, value=r,
                                    font=self.configs_tk['font'])
            button.pack(anchor='w')

        box_label.pack_propagate(False)

    def create_doctor_menu_mode_container(self):
        self.doctor_menu_mode_container = tk.Frame(self.doctor_menu_frame)
        self.doctor_menu_mode_container.pack(pady=10)

        self.create_doctor_powerup_container()
        self.create_doctor_time_mode_container()
        self.create_doctor_life_mode_container()

    def create_doctor_overview_container(self):
        normal_overview_container = tk.Frame(self.doctor_menu_frame)
        normal_overview_container.pack(pady=10)

        box_label = tk.LabelFrame(normal_overview_container, text='OVERSIKT', font=self.configs_tk['font_b'],
                                  padx=32, pady=20, height=210, width=792)
        box_label.pack()
        box_label_info_button = tk.Menubutton(box_label, text="Info", font=self.configs_tk['font_i'],
                                              bg=self.configs_tk['color_grey'], fg=self.configs_tk['color_white'], relief='raised', height=1,
                                              width=10)
        box_label_info_button.pack(anchor='w')
        box_label_info_button.menu = tk.Menu(box_label_info_button, tearoff=0)
        box_label_info_button["menu"] = box_label_info_button.menu
        box_label_info_button.menu.add_cascade(label='Oversikt over oppgavebanken og andre innstillinger før "Start"')
        box_label_info_button.menu.add_cascade(label='Oppgavene trekkes tilfeldig fra hele oppgavebanken uavhengig av tidligere besvarelser i andre moduser')
        box_label_info_button.menu.add_cascade(label='Statistikk lagres når man trykker "Hjem". Ved prematur avslutning blir gjenværende liv regnet som oppgavefeil')

        self.doctor_questions_number_label = tk.Label(box_label, text=f'Antall oppgaver: ?',
                                          font=self.configs_tk['font'], anchor='w', justify='left',
                                          wraplength=self.configs_tk['w_length_menu'])
        self.doctor_questions_number_label.pack(anchor='w')
        self.doctor_time_mode_label = tk.Label(box_label, text=f'Oppgavetid: ?',
                                               font=self.configs_tk['font'], anchor='w', justify='left',
                                               wraplength=self.configs_tk['w_length_menu'])
        self.doctor_time_mode_label.pack(anchor='w')
        self.doctor_life_mode_label = tk.Label(box_label, text=f'Antall liv: ?',
                                               font=self.configs_tk['font'], anchor='w', justify='left',
                                               wraplength=self.configs_tk['w_length_menu'])
        self.doctor_life_mode_label.pack(anchor='w')
        update_button = tk.Button(box_label, text='Oppdater',
                                 bg=self.configs_tk['color_white'], font=self.configs_tk['font_i'],
                                 height=1, width=10, command=lambda: self.on_check_doctor())
        update_button.pack(anchor='w')
        box_label.pack_propagate(False)  # makes height and width in labelframe active

    def create_doctor_start_container(self):
        normal_start_container = tk.Frame(self.doctor_menu_frame)
        normal_start_container.pack(pady=10)

        start_button = tk.Button(normal_start_container, text='START', command=lambda: self.on_start_doctor(),
                                 bg=self.configs_tk['color_green'], height=2, width=30, font=self.configs_tk['font_b'])
        start_button.pack()

    def create_doctor_menu_frame(self):
        self.questions = []
        self.current_question_index = 0
        self.current_largest_question_index = 0
        self.correct_questions = 0
        self.hour = '00'
        self.minute = '00'
        self.second = '00'
        self.remaining_doctor_time_sec = 0
        self.remaining_lives = 0
        self.submit_doctor = False
        self.current_streak = 0
        self.longest_streak = 0
        self.remaining_call = 3
        self.remaining_overtime = 3

        self.doctor_menu_frame = tk.Frame(self.main_canvas, pady=10, padx=80)
        self.main_canvas.create_window((self.max_width // 2, 0), window=self.doctor_menu_frame, anchor="n")
        self.doctor_menu_frame.bind('<Configure>', lambda e: self.main_canvas.configure(scrollregion=self.main_canvas.bbox("all")))

        self.create_subtitle_info_container(self.doctor_menu_frame, 'OVERLEGEMODUS')
        self.create_doctor_level_container()
        self.create_doctor_menu_mode_container()
        self.create_doctor_overview_container()
        self.create_doctor_start_container()

    def create_doctor_question_dock_info_container(self):
        dock_info_container = tk.Frame(self.doctor_quiz_frame, height=300, width=790)
        dock_info_container.pack(anchor='w')

        left_subcontainer = tk.Frame(dock_info_container)
        left_subcontainer.pack(side=tk.LEFT, anchor='nw')

        self.progress_count = tk.StringVar()
        self.progress_count.set(f'Progresjon: {self.current_question_index + 1} av {len(self.questions)}')
        progress_count_label = tk.Label(left_subcontainer, textvariable=self.progress_count, font=self.configs_tk['font_ib'])
        progress_count_label.pack(anchor='w')

        self.life_count = tk.StringVar()
        self.life_count.set(f'Liv: {calculate_heart_string(self.remaining_lives)}')

        life_count_label = tk.Label(left_subcontainer, textvariable=self.life_count,
                                    font=self.configs_tk['font_ib'])
        life_count_label.pack(anchor='w')

        self.current_streak_count = tk.StringVar()
        self.current_streak_count.set(f'Nåværende streak: 0')
        time_count_label = tk.Label(left_subcontainer, textvariable=self.current_streak_count,
                                    font=self.configs_tk['font_ib'])
        time_count_label.pack(anchor='w')

        right_subcontainer = tk.Frame(dock_info_container)
        right_subcontainer.pack(side=tk.RIGHT, anchor='ne')

        self.correct_count = tk.StringVar()
        self.correct_count.set(
                f'Riktige: 0.0% (0 av 0)')
        correct_count_label = tk.Label(right_subcontainer, textvariable=self.correct_count,
                                      font=self.configs_tk['font_ib'])
        correct_count_label.pack(anchor='e')

        if self.doctor_time_mode_var.get() != 'Post (Ingen)':
            self.time_count = tk.StringVar()
            self.time_count.set(f'Oppgavetid: {self.hour}:{self.minute}:{self.second}')
            time_count_label = tk.Label(right_subcontainer, textvariable=self.time_count,
                                        font=self.configs_tk['font_ib'])
            time_count_label.pack(anchor='e')
        else:
            time_count_label = tk.Label(right_subcontainer, text='Oppgavetid: Ingen', font=self.configs_tk['font_ib'])
            time_count_label.pack(anchor='e')

        self.streak_count = tk.StringVar()
        self.streak_count.set(f'Lengste streak: 0')
        streak_count_label = tk.Label(right_subcontainer, textvariable=self.streak_count,
                                    font=self.configs_tk['font_ib'])
        streak_count_label.pack(anchor='e')

        # create evolution image
        self.create_doctor_question_evolution_img_container(dock_info_container)

        dock_info_container.pack_propagate(False)

    def create_doctor_question_evolution_img_container(self, frame):
        image_container = tk.Frame(frame)
        image_container.pack(anchor='center')

        self.evolution_name_var = tk.StringVar()
        self.evolution_name_var.set(f'{self.doctor_evolution_path_alias_list[0]}')
        self.evolution_name_label = tk.Label(image_container, textvariable=self.evolution_name_var,
                                             font=self.configs_tk['font_ib'])
        self.evolution_name_label.pack()

        self.evolution_img_index = 0
        self.evolution_img_list_pil = scale_image(self.doctor_evolution_path_list)

        image_tk = ImageTk.PhotoImage(self.evolution_img_list_pil[self.evolution_img_index])
        self.evolution_image_label = tk.Label(image_container, image=image_tk)
        self.evolution_image_label.image = image_tk
        self.evolution_image_label.pack()

    def create_doctor_question_dock_button_container(self):
        button_container = tk.Frame(self.doctor_quiz_frame)
        button_container.pack(anchor='center')

        self.call_button = tk.Button(button_container, text='📞', command=lambda: self.on_call_doctor(),
                                    bg=self.configs_tk['color_grey'], fg=self.configs_tk['color_white'], height=1, width=7,
                                    font=self.configs_tk['font_b'])
        self.call_button.grid(row=0, column=0, padx=5)
        self.doctor_submit_button = tk.Button(button_container, text='SVAR', command=lambda: self.on_submit_doctor(),
                                              bg=self.configs_tk['color_green'], height=1, width=14,
                                              font=self.configs_tk['font_b'])
        self.doctor_submit_button.grid(row=0, column=1, padx=5)
        self.overtime_button = tk.Button(button_container, text='🕒', command=lambda: self.on_overtime_doctor(),
                                    bg=self.configs_tk['color_grey'], fg=self.configs_tk['color_white'], height=1, width=7,
                                    font=self.configs_tk['font_b'])
        self.overtime_button.grid(row=0, column=2, padx=5)
        if self.doctor_time_mode_var.get() == 'Post (Ingen)':
            self.overtime_button.configure(state='disabled')

        self.feedback_label = tk.Label(button_container, text='', font=self.configs_tk['font_b'])
        self.feedback_label.grid(row=1, column=1, padx=5)

        self.call_count = tk.StringVar()
        self.call_count.set('3')
        self.call_label = tk.Label(button_container, textvariable=self.call_count, font=self.configs_tk['font_b'])
        self.call_label.grid(row=1, column=0, padx=5)
        self.overtime_count = tk.StringVar()
        self.overtime_count.set('3')
        self.overtime_label = tk.Label(button_container, textvariable=self.overtime_count, font=self.configs_tk['font_b'])
        self.overtime_label.grid(row=1, column=2, padx=5)

    def on_leftscroll_doctor(self):
        self.evolution_img_index -= 1

        if self.evolution_img_index > self.doctor_evolution_path_alias_list.index(self.statistics_obj.statistics_dict['OVERLEGEMODUS']['Beste tittel']):
            image_tk = ImageTk.PhotoImage(scale_image([self.doctor_evolution_locked_path])[0])
        else:
            image_tk = ImageTk.PhotoImage(self.evolution_img_list_pil[self.evolution_img_index])

        self.evolution_image_label.configure(image=image_tk)
        self.evolution_image_label.image = image_tk

        if self.evolution_img_index == 0:
            self.left_scroll_level_button.configure(state='disabled')

        self.right_scroll_level_button.configure(state='normal')
        if self.evolution_img_index > 0:
            if self.evolution_img_index > self.doctor_evolution_path_alias_list.index(
                    self.statistics_obj.statistics_dict['OVERLEGEMODUS']['Beste tittel']):
                self.img_level_count.set(f'(Låst tittel) - {10 * 2 ** (self.evolution_img_index - 1)} riktige oppgaver')
            else:
                self.img_level_count.set(
                    f'{self.doctor_evolution_path_alias_list[self.evolution_img_index]} - {10 * 2 ** (self.evolution_img_index - 1)} riktige oppgaver')
        else:
            self.img_level_count.set(f'{self.doctor_evolution_path_alias_list[self.evolution_img_index]} - 0 riktige oppgaver')

    def on_rightscroll_doctor(self):
        self.evolution_img_index += 1

        if self.evolution_img_index > self.doctor_evolution_path_alias_list.index(self.statistics_obj.statistics_dict['OVERLEGEMODUS']['Beste tittel']):
            image_tk = ImageTk.PhotoImage(scale_image([self.doctor_evolution_locked_path])[0])
        else:
            image_tk = ImageTk.PhotoImage(self.evolution_img_list_pil[self.evolution_img_index])

        self.evolution_image_label.configure(image=image_tk)
        self.evolution_image_label.image = image_tk

        if self.evolution_img_index == len(self.doctor_evolution_path_list) - 1:
            self.right_scroll_level_button.configure(state='disabled')

        self.left_scroll_level_button.configure(state='normal')
        self.img_level_count.set(f'{self.doctor_evolution_path_alias_list[self.evolution_img_index]}')
        if self.evolution_img_index > 0:
            if self.evolution_img_index > self.doctor_evolution_path_alias_list.index(self.statistics_obj.statistics_dict['OVERLEGEMODUS']['Beste tittel']):
                self.img_level_count.set(f'(Låst tittel) - {10 * 2 ** (self.evolution_img_index - 1)} riktige oppgaver')
            else:
                self.img_level_count.set(f'{self.doctor_evolution_path_alias_list[self.evolution_img_index]} - {10 * 2 ** (self.evolution_img_index - 1)} riktige oppgaver')
        else:
            self.img_level_count.set(
                f'{self.doctor_evolution_path_alias_list[self.evolution_img_index]} - 0 riktige oppgaver')

    def on_check_doctor(self):
        included_questions = []

        for pth in self.file_path_list:
            file_json = open(pth)
            try:
                file_dict = json.load(file_json)
                for q in range(1, len(file_dict) + 1):
                    question = MCQ(file_dict[f'{pth.rsplit(".", 1)[0]}_{q}'])
                    included_questions.append(question)
            except:
                print(file_json)

        self.questions = included_questions
        self.doctor_questions_number_label.configure(text=f'Antall oppgaver: {len(self.questions)}')

        if self.doctor_time_mode_var.get() != '0':
            if self.doctor_time_mode_var.get() == 'Vakt (60 sek)':
                self.doctor_time_mode_label.configure(text=f'Oppgavetid: 60 sek')
            elif self.doctor_time_mode_var.get() == 'Poliklinikk (100 sek)':
                self.doctor_time_mode_label.configure(text=f'Oppgavetid: 100 sek')
            else:
                self.doctor_time_mode_label.configure(text=f'Oppgavetid: Ingen')
        else:
            self.doctor_time_mode_label.configure(text=f'Oppgavetid: ?')

        if self.doctor_life_mode_var.get() != '0':
            if self.doctor_life_mode_var.get() == 'Multimorbid (3 liv)':
                self.doctor_life_mode_label.configure(text=f'Antall liv: 3')
            elif self.doctor_life_mode_var.get() == 'Komorbid (5 liv)':
                self.doctor_life_mode_label.configure(text=f'Antall liv: 5')
            else:
                self.doctor_life_mode_label.configure(text=f'Antall liv: 10')
        else:
            self.doctor_life_mode_label.configure(text=f'Antall liv: ?')

    def on_start_doctor(self):
        if self.doctor_time_mode_var.get() != '0' and self.doctor_life_mode_var.get() != '0':
            included_questions = []

            for pth in self.file_path_list:
                file_json = open(pth)
                try:
                    file_dict = json.load(file_json)
                    for q in range(1, len(file_dict) + 1):
                        question = MCQ(file_dict[f'{pth.rsplit(".", 1)[0]}_{q}'])
                        included_questions.append(question)
                except:
                    print(file_json)

            random.shuffle(included_questions)
            self.questions = included_questions
            if len(self.questions) > 0:

                if self.doctor_time_mode_var.get() == 'Vakt (60 sek)':
                    self.remaining_doctor_time_sec = 60
                elif self.doctor_time_mode_var.get() == 'Poliklinikk (100 sek)':
                    self.remaining_doctor_time_sec = 100
                else:
                    pass

                if self.doctor_life_mode_var.get() == 'Multimorbid (3 liv)':
                    self.remaining_lives = 3
                elif self.doctor_life_mode_var.get() == 'Komorbid (5 liv)':
                    self.remaining_lives = 5
                else:
                    self.remaining_lives = 10

                self.create_doctor_quiz_frame_from_menu()
                self.current_mode = 'OVERLEGEMODUS'

    def create_doctor_choice_container(self, frame):
        self.choice_container = tk.Frame(frame)
        self.choice_container.pack(anchor='w')

        self.choice_explainations = []
        self.choice_explaination_contents = []
        self.psyko_explainations = []
        self.psyko_explaination_contents = []
        self.doctor_choice_buttons_dict = {}

        self.choice_var.set('0')
        for choice in self.questions[self.current_question_index].abcd:
            choice_text = f'{choice}: {self.questions[self.current_question_index].abcd[choice]["answer"]}'
            button = tk.Radiobutton(self.choice_container, text=choice_text, variable=self.choice_var, value=choice,
                                    font=self.configs_tk['font_b'], justify='left', wraplength=self.configs_tk['w_length'])
            button.pack(anchor='w')
            self.doctor_choice_buttons_dict[choice] = button

            try:
                explaination = f'{choice}: {self.questions[self.current_question_index].abcd[choice]["explaination"]}'
            except:
                explaination = f'{choice}: Ingen forklaring'

            try:
                psyko = f'{choice}: {self.questions[self.current_question_index].abcd[choice]["psyko"]}'
            except:
                psyko = f''

            choice_explanation = tk.Label(self.choice_container, text='', font=self.configs_tk['font'], justify='left', wraplength=self.configs_tk['w_length'])
            choice_explanation.pack(anchor='w')
            self.choice_explaination_contents.append(explaination)
            self.choice_explainations.append(choice_explanation)

            psyko_explanation = tk.Label(self.choice_container, text='', font=self.configs_tk['font_b'], justify='left', wraplength=self.configs_tk['w_length'])
            psyko_explanation.pack(anchor='w')
            self.psyko_explaination_contents.append(psyko)
            self.psyko_explainations.append(psyko_explanation)

    def create_doctor_quiz_frame(self):
        self.doctor_quiz_frame = tk.Frame(self.main_canvas, pady=10, padx=80)
        self.main_canvas.create_window((self.max_width // 2, 0), window=self.doctor_quiz_frame, anchor="n")
        self.doctor_quiz_frame.bind('<Configure>', lambda e: self.main_canvas.configure(scrollregion=self.main_canvas.bbox("all")))

        self.create_subtitle_info_container(self.doctor_quiz_frame, 'OVERLEGEMODUS')
        self.create_doctor_question_dock_info_container()
        self.create_doctor_question_dock_button_container()
        self.create_text_container(self.doctor_quiz_frame)
        self.create_image_container(self.doctor_quiz_frame)
        self.create_doctor_choice_container(self.doctor_quiz_frame)
        if self.doctor_time_mode_var.get() != 'Post (Ingen)':
            self.doctor_timer_tick()

    def create_doctor_quiz_frame_from_menu(self):
        self.doctor_menu_frame.destroy()
        self.create_doctor_quiz_frame()

    def create_doctor_menu_from_intro(self):
        self.intro_frame.destroy()
        self.create_doctor_menu_frame()

    def doctor_timer_tick(self):
        hours, mins, secs = calculate_time_from_seconds(self.remaining_doctor_time_sec)

        self.time_count.set(f'Oppgavetid: {"{:0>2d}".format(hours)}:{"{:0>2d}".format(mins)}:{"{:0>2d}".format(secs)}')

        if self.remaining_lives > 0:

            if self.remaining_doctor_time_sec > 0:
                self.remaining_doctor_time_sec -= 1
            elif self.remaining_doctor_time_sec == 0 and self.submit_doctor == True:
                self.on_submit_next_doctor()
            else:
                if self.choice_var.get() != '0':
                    self.on_submit_doctor()
                else:
                    self.current_streak = 0
                    self.current_streak_count.set(f'Nåværende streak: {self.current_streak}')

                    self.remaining_lives -= 1
                    self.life_count.set(f'Liv: {calculate_heart_string(self.remaining_lives)}')

                    self.correct_count.set(
                        f'Riktige: {round((self.correct_questions * 100 / (self.current_largest_question_index + 1)), 1)}% ({self.correct_questions} av {self.current_largest_question_index + 1})')

                self.on_submit_next_doctor()
            self.doctor_quiz_frame.after(1000, self.doctor_timer_tick)

    def on_call_doctor(self):
        if self.submit_doctor != True:
            reveal_n_false_answers = len(self.questions[self.current_question_index].abcd) // 2
            false_answers_index_list = [f for f in self.questions[self.current_question_index].abcd]
            false_answers_index_list.remove(self.questions[self.current_question_index].answer_tag)

            for r in range(reveal_n_false_answers):
                random_false_key = random.choice(false_answers_index_list)
                self.doctor_choice_buttons_dict[random_false_key].configure(state='disabled')
                false_answers_index_list.remove(random_false_key)

            self.remaining_call -= 1
            if self.remaining_call > 0:
                self.call_count.set(f'{self.remaining_call}')
            else:
                self.call_count.set('')
                self.call_button.configure(state='disabled')

    def on_overtime_doctor(self):
        if self.doctor_time_mode_var.get() == 'Vakt (60 sek)':
            self.remaining_doctor_time_sec += 60
        elif self.doctor_time_mode_var.get() == 'Poliklinikk (100 sek)':
            self.remaining_doctor_time_sec += 100
        else:
            pass

        self.remaining_overtime -= 1
        if self.remaining_overtime > 0:
            self.overtime_count.set(f'{self.remaining_overtime}')
        else:
            self.overtime_count.set('')
            self.overtime_button.configure(state='disabled')

    def on_submit_doctor(self):
        if self.choice_var.get() != '0':
            self.submit_doctor = True

            if self.questions[self.current_question_index].psyko_text != '':
                self.psyko_text_label.configure(text=self.questions[self.current_question_index].psyko_text, fg=self.configs_tk['color_red'])
                self.feedback_label.configure(text='PSYKOMETRI')

                if self.questions[self.current_question_index].abcd[self.choice_var.get()]["psyko"].lstrip(' ')[0] == '1':
                    self.correct_questions += 1
                    self.current_streak += 1
                    if self.current_streak > self.longest_streak:
                        self.longest_streak = self.current_streak
                        self.streak_count.set(f'Lengste streak: {self.longest_streak}')
                else:
                    no_correct = True
                    for p in self.questions[self.current_question_index].abcd:
                        if self.questions[self.current_question_index].abcd[p]["psyko"].lstrip(' ')[0] == '1':
                            no_correct = False
                            self.current_streak = 0

                            self.remaining_lives -= 1
                            self.life_count.set(f'Liv: {calculate_heart_string(self.remaining_lives)}')

                    if no_correct == True:
                        pass

            else:
                if self.choice_var.get() == self.questions[self.current_question_index].answer_tag:
                    self.feedback_label.configure(text='RIKTIG')
                    self.correct_questions += 1
                    self.current_streak += 1
                    if self.current_streak > self.longest_streak:
                        self.longest_streak = self.current_streak
                        self.streak_count.set(f'Lengste streak: {self.longest_streak}')
                else:
                    self.feedback_label.configure(text='FEIL')
                    self.current_streak = 0

                    self.remaining_lives -= 1
                    self.life_count.set(f'Liv: {calculate_heart_string(self.remaining_lives)}')

            for ce in zip(self.choice_explainations, self.choice_explaination_contents, self.psyko_explainations, self.psyko_explaination_contents):
                ce[0].configure(text=ce[1])
                ce[2].configure(text=ce[3])
                if ce[1].strip(' ')[0] == self.questions[self.current_question_index].answer_tag:
                    ce[0].configure(bg=self.configs_tk['color_green'])
                else:
                    ce[0].configure(bg=self.configs_tk['color_orange'])
                ce[2].configure(fg=self.configs_tk['color_red'])

            self.current_streak_count.set(f'Nåværende streak: {self.current_streak}')
            self.correct_count.set(
                f'Riktige: {round((self.correct_questions * 100 / (self.current_largest_question_index + 1)), 1)}% ({self.correct_questions} av {self.current_largest_question_index + 1})')
            self.doctor_submit_button.configure(text='NESTE', command=lambda: self.on_submit_next_doctor(), bg=self.configs_tk['color_green'])

            self.evolution_img_index = check_evolution(self.doctor_evolution_path_list, self.correct_questions, log_base=2, evolution_score=10)
            image_tk = ImageTk.PhotoImage(self.evolution_img_list_pil[self.evolution_img_index])
            self.evolution_image_label.configure(image=image_tk)
            self.evolution_image_label.image = image_tk
            self.evolution_name_var.set(f'{self.doctor_evolution_path_alias_list[self.evolution_img_index]}') #(Utvikling etter {10 * 2**(self.evolution_img_index)} riktige)')

    def update_statistics_doctor(self):
        if self.doctor_evolution_path_alias_list.index(self.statistics_obj.statistics_dict['OVERLEGEMODUS']['Beste tittel']) < self.evolution_img_index:
            self.statistics_obj.statistics_dict['OVERLEGEMODUS']['Beste tittel'] = self.doctor_evolution_path_alias_list[self.evolution_img_index]

        if self.statistics_obj.statistics_dict['OVERLEGEMODUS']['Max antall riktige'] < self.correct_questions:
            self.statistics_obj.statistics_dict['OVERLEGEMODUS']['Max antall riktige'] = self.correct_questions
            self.statistics_obj.statistics_dict['OVERLEGEMODUS']['Beste score (antall riktige)'] = f'{round((self.correct_questions * 100 / (self.current_largest_question_index + 1)), 1)}% ({self.correct_questions} av {self.current_largest_question_index + 1} oppgaver)'
            self.statistics_obj.statistics_dict['OVERLEGEMODUS']['Beste score (antall riktige) innstillinger'] = [self.doctor_time_mode_var.get(), self.doctor_life_mode_var.get()]

        if float(self.statistics_obj.statistics_dict['OVERLEGEMODUS']['Beste score (% riktige)'].split('%', 1)[0]) < self.current_largest_question_index + 1:
            self.statistics_obj.statistics_dict['OVERLEGEMODUS']['Beste score (% riktige)'] = f'{round((self.correct_questions * 100 / (self.current_largest_question_index + 1)), 1)}% ({self.correct_questions} av {self.current_largest_question_index + 1} oppgaver)'
            self.statistics_obj.statistics_dict['OVERLEGEMODUS']['Beste score (% riktige) innstillinger'] = [self.doctor_time_mode_var.get(), self.doctor_life_mode_var.get()]

        if int(self.statistics_obj.statistics_dict['OVERLEGEMODUS']['Lengste streak'].split(' ', 1)[0]) < self.longest_streak:
            self.statistics_obj.statistics_dict['OVERLEGEMODUS']['Lengste streak'] = f'{self.longest_streak} oppgaver'

        self.statistics_obj.write_dict_to_json()

    def on_submit_next_doctor(self):
        # Move to the next question
        self.current_question_index += 1
        self.current_largest_question_index += 1

        if self.current_question_index >= len(self.questions) or self.remaining_lives == 0:
            self.doctor_submit_button.configure(state='disabled', text='GAME OVER')
            self.call_button.configure(state='disabled')
            self.overtime_button.configure(state='disabled')
            #self.doctor_quiz_frame.destroy()
            #self.create_doctor_menu_frame()
        else:
            # Update the widgets with the new question
            self.progress_count.set(f'Progresjon: {self.current_question_index + 1} av {len(self.questions)}')

            if self.doctor_time_mode_var.get() == 'Vakt (60 sek)':
                self.remaining_doctor_time_sec = 60
            elif self.doctor_time_mode_var.get() == 'Poliklinikk (100 sek)':
                self.remaining_doctor_time_sec = 100
            self.submit_doctor = False

            self.doctor_submit_button.configure(text='SVAR', command=lambda: self.on_submit_doctor(), bg=self.configs_tk['color_green'])
            self.feedback_label.configure(text='')
            self.text_container.destroy()
            self.image_container.destroy()
            self.choice_container.destroy()

            self.create_text_container(self.doctor_quiz_frame)
            self.create_image_container(self.doctor_quiz_frame)
            self.create_doctor_choice_container(self.doctor_quiz_frame)

    def create_statistics_container(self):
        statistics_info_container = tk.Frame(self.statistics_frame)
        statistics_info_container.pack(pady=10, fill=tk.X)

        normal_statistics_container = tk.Frame(statistics_info_container)
        normal_statistics_container.pack(pady=10, anchor='w')

        normal_title_label = tk.Label(normal_statistics_container,
                                      text='QUIZMODUS', font=self.configs_tk['font_b'], justify='left',
                                      wraplength=self.configs_tk['w_length'])
        normal_title_label.pack(anchor='w')
        for n in self.statistics_obj.statistics_dict['QUIZMODUS']:
            normal_text_label = tk.Label(normal_statistics_container,
                                         text=f'{n}: {self.statistics_obj.statistics_dict["QUIZMODUS"][n]}',
                                         font=self.configs_tk['font'], justify='left',
                                         wraplength=self.configs_tk['w_length'])
            normal_text_label.pack(anchor='w')

        exam_statistics_container = tk.Frame(statistics_info_container)
        exam_statistics_container.pack(pady=10, anchor='w')

        exam_title_label = tk.Label(exam_statistics_container,
                                    text='EKSAMENSMODUS', font=self.configs_tk['font_b'], justify='left',
                                    wraplength=self.configs_tk['w_length'])
        exam_title_label.pack(anchor='w')
        for q in self.statistics_obj.statistics_dict['EKSAMENSMODUS']:
            if q == 'Leverte eksamensett':
                pass
            else:
                exam_text_label = tk.Label(exam_statistics_container,
                                           text=f'{q}: {self.statistics_obj.statistics_dict["EKSAMENSMODUS"][q]}',
                                           font=self.configs_tk['font'], justify='left',
                                           wraplength=self.configs_tk['w_length'])
                exam_text_label.pack(anchor='w')

        doctor_statistics_container = tk.Frame(statistics_info_container)
        doctor_statistics_container.pack(pady=10, anchor='w')

        doctor_title_label = tk.Label(doctor_statistics_container,
                                      text='OVERLEGEMODUS', font=self.configs_tk['font_b'], justify='left',
                                      wraplength=self.configs_tk['w_length'])
        doctor_title_label.pack(anchor='w')
        for d in self.statistics_obj.statistics_dict['OVERLEGEMODUS']:
            if d == 'Max antall riktige':
                pass
            else:
                doctor_text_label = tk.Label(doctor_statistics_container,
                                             text=f'{d}: {self.statistics_obj.statistics_dict["OVERLEGEMODUS"][d]}',
                                             font=self.configs_tk['font'], justify='left',
                                             wraplength=self.configs_tk['w_length'])
                doctor_text_label.pack(anchor='w')

    def create_statistics_frame(self):
        self.statistics_frame = tk.Frame(self.main_canvas, pady=10, padx=80)
        self.main_canvas.create_window((self.max_width // 2, 0), window=self.statistics_frame, anchor="n")
        self.statistics_frame.bind('<Configure>',
                                   lambda e: self.main_canvas.configure(scrollregion=self.main_canvas.bbox("all")))

        self.create_subtitle_info_container(self.statistics_frame, 'STATISTIKK')
        self.create_statistics_container()

    def create_statistics_from_intro(self):
        self.intro_frame.destroy()
        self.create_statistics_frame()

    def create_subtitle_info_container(self, frame, title):
        menu_info_container = tk.Frame(frame, height=40, width=790)
        menu_info_container.pack(pady=10)

        subtitle_text = tk.Label(menu_info_container,
                                 text=title, font=self.configs_tk['font_subtitle'], justify='left',
                                 wraplength=self.configs_tk['w_length'])
        subtitle_text.pack(side=tk.LEFT)
        home_button = tk.Button(menu_info_container, text='Hjem',
                                command=lambda: self.create_intro_from_any(frame),
                                bg=self.configs_tk['color_white'], font=self.configs_tk['font_i'],
                                height=1, width=10)
        home_button.pack(side=tk.RIGHT)
        menu_info_container.pack_propagate(False)

    def create_about_info_container(self, frame, title, text):
        about_info_container = tk.Frame(frame)
        about_info_container.pack(anchor='w', pady=10)

        about_title_label = tk.Label(about_info_container,
                                     text=title, font=self.configs_tk['font_b'], justify='left',
                                     wraplength=self.configs_tk['w_length'])
        about_title_label.pack(anchor='w')
        about_text_label = tk.Label(about_info_container, text=text, font=self.configs_tk['font'], justify='left',
                                    wraplength=self.configs_tk['w_length'])
        about_text_label.pack(anchor='w')

    def create_link_info_container(self, frame, title, link_list):
        link_info_container = tk.Frame(frame)
        link_info_container.pack(anchor='w', pady=10)
        sources_text = tk.Label(link_info_container,
                                text=title, font=self.configs_tk['font_b'], justify='left',
                                wraplength=self.configs_tk['w_length'])
        sources_text.pack(anchor='w')
        sources_link = tk.Text(link_info_container, font=self.configs_tk['font'], height=len(link_list), borderwidth=0,
                               width=88)
        for l in link_list:
            sources_link.insert(1.0, f'{l}\n')
        sources_link.configure(state='disabled')
        sources_link.pack(anchor='w')

    def create_sources_frame(self):
        self.sources_frame = tk.Frame(self.main_canvas, pady=10, padx=80)
        self.main_canvas.create_window((self.max_width // 2, 0), window=self.sources_frame, anchor="n")
        self.sources_frame.bind('<Configure>',
                                lambda e: self.main_canvas.configure(scrollregion=self.main_canvas.bbox("all")))

        self.create_subtitle_info_container(self.sources_frame, 'INFO OG KILDER')

        self.create_about_info_container(self.sources_frame, 'OM PROGRAMMET',
                                         '''Programmet har enkelte begrensninger man bør være klar over.\n• Enkelte oppgaver har feil i fasit/endringer etter psykometrimøtet. I programmet gis det poeng for riktig(e) svaralternativ etter psykometrimøtet. Les psykometrinotat for begrunnelsen bak fasitendring da dette ikke vises i programmet.\n• Enkelte oppgaver vil inneholde tabeller. I programmet fremvises tabeller som tekst. Feks vil følgende tabell: \n-------------------------------------------------------------\n|    A (prøve)    |    B (verdi)    |  C (referanse)  |\n-------------------------------------------------------------\n|           D          |          1           |            2            |\n-------------------------------------------------------------\n|           E          |          3           |            4            |\n-------------------------------------------------------------\nvises som "A B C D 1 2 E 3 4" i oppgaveteksten.\n• Enkelte oppgaver inneholder små tall som feks "10 opphøyd i 5" i kontekst av bakterievekst. Små tall vil vises som normale tall i programmet (forrige eksempel vil da vises som "105").\n• Programmet er ikke tilkoblet internett så programmet må lastes ned på nytt for oppdateringer. Merk at tidligere progresjon og statistikk vil forsvinne ved bruk av ny versjon. Sjekk datering på versjon og dato på zip-filen for å se om du har siste versjon.\n• Bugs vil forekomme for enkelte oppgaver grunnet uforutsette variasjoner i oppgaveformat. Dette skjer sjeldent, men eksamensett og oppgavenummer er oppgitt for hver oppgave slik at fasiten kan sjekkes manuelt ved usikkerhet.''')
        self.create_about_info_container(self.sources_frame, 'OM MEG',
                                         'Hei, jeg heter Sigurd Z. Zha og har vært medisin- og forskerlinjestudent ved UiO 2017-2024. Programmet ble laget fordi det var kjipt å gjøre eksamensett manuelt. Synes det var kult at mange på kull V18 fikk nytte av programmet, så har nå laget en oppdatert versjon med forbedringer. Er nå ferdig lege, men vedlikeholder programmet på fritiden. Disclaimer: Det er UiO, NTNU og eksamenskommisjonen som eier rettighetene til eksamensettene. Donasjoner kan gå til MedHum.\n\nTa gjerne kontakt med meg på Facebook eller på mail (sigzha@gmail.com) dersom det er noe du lurer på')
        self.create_link_info_container(self.sources_frame, 'EKSAMENSETT', [
            'https://www.uio.no/studier/program/medisin/tidligere-eksamensoppgaver/felles-avsluttende-deleksamen/',
            'https://www.uio.no/studier/program/medisin/tidligere-eksamensoppgaver/fagproven/',
            'https://i.ntnu.no/wiki/-/wiki/Norsk/Eksamensoppgaver+-+Medisin+-+MH'])
        self.create_link_info_container(self.sources_frame, 'PSYKOMETRINOTAT', [
            'https://www.uio.no/studier/program/medisin/tidligere-eksamensoppgaver/felles-avsluttende-deleksamen/index.html'])
        self.create_link_info_container(self.sources_frame, 'KILDEKODE', ['https://github.com/shigurd/NTNUiO.git'])

    def create_sources_from_intro(self):
        self.intro_frame.destroy()
        self.create_sources_frame()

if __name__ == '__main__':
    #pyinstaller main.spec
    os.chdir(os.path.join(os.path.dirname(sys.argv[0]), 'lib'))

    question_set_json_pths = ['2016 - IIAB - MD4030 - eksamen 2-2016-01-04.json', '2016 - IIID - MD4062 - eksamen 1-2016-05-23.json', '2016 - IIID - MD4062 - eksamen 2-2016-10-19 fasit FVO.json', '2017 - IID - MD4043 - eksamen 1-2017-05-16.json', '2018 - IAB - MD4011 - FVO med fasit eksamen 1-2018-05-16.json', '2018 - IAB kont - MD4011 - FVO med fasit -2018-08-14.json', '2018 - ICD - MD4020 - FVo med fasit eksamen 2-2018-06-01.json', '2018 - ICD kont - MD4020 - FVO med fasit -2018-08-14.json', '2018 - IIAB forskerlinje - MD4030- korrigert FVO med fasit - ny.json', '2018 - IIAB kont - MD4030 - FVO med fasit -2018-08-14.json', '2018 - IIC - MD4042 - FVO med fasit - eksamen 2-2018-12-13.json', '2018 - IIC - MD4042 -FVO med fasit, eksamen 1-2018-05-29.json', '2018 - IID - MD4043 - FVO med fasit - Eksamen 3.-2018-12-13.json', '2018 - IID - MD4043 -FVO med fasit 1-2018-05-28.json', '2018 - IID kont - MD4043 - FVO med fasit.json', '2018 - IIIC - MD4061 - FVO med fasit - eksamen 1-2018-12-13.json', '2018 - IIIC kont - MD4061 - FVO med fasit.json', '2018 - IIID -Kont - MD4062 - FVO med fasit.json', '2018 - IIID ordinær - MD4062 - FVO med fasit.json', '2018 ordinær - IIAB - MD4030 -FVO med fasit eksamen 1-2018-05-24.json', '2019 - IAB kont - MD4011 - FVO med fasit.json', '2019 - IAB Ordinær- MD4011 - FVO med fasit.json', '2019 - ICD kont ny - MD4020 - Fvo med fasit.json', '2019 - ICD ordinær - MD4020 - FVO med fasit.json', '2019 - IIAB Forskerlinje - MD4030 - FVO med fasit - eksamen 3-2019-04-30.json', '2019 - IIAB kont - MD4030 - FVO med fasit.json', '2019 - IIAB ordinær - MD4030 - FVO med fasit.json', '2019 - IIC kont - MD4042 - Fvo med fasit.json', '2019 - IIC Ordinær - MD4042 - FVO med fasit.json', '2019 - IIC ordinær desember- MD4042 - FVO med fasit.json', '2019 - IID desember norsk- MD4043 - FVO med fasit.json', '2019 - IID kont - MD4043 - FVO med fasit.json', '2019 - IID ordinær - MD4043 - FVO med fasit.json', '2019 - IIIC ordinær - MD4061 -FVO med fasit.json', '2019 - IIIC utsatt februar - MD4061 - FVO med fasit.json', '2019 - IIID - ordinær - MD4062 - FVO med fasit.json', '2020 - IAB -ordinær - MD4011 - FVO med fasit.json', '2020 - IAB utsatt - MD4011 - FVO med fasit.json', '2020 - ICD ordinær - MD4020 - FVO med fasit.json', '2020 - ICD utsatt - MD4020 - FVO med fasit.json', '2020 - IIAB ordinær - MD4030 - FVO med fasit.json', '2020 - IIAB utsatt - MD4030 - FVO med fasit.json', '2020 - IIC - ordinær - MD4042 - FVO med fasit.json', '2020 - IIC ordinær desember - MD4042 - FVO med fasit.json', '2020 - IID - ordinær - MD4043 - FVO med fasit.json', '2020 - IID ordinær desember - MD4043 - FVO med fasit.json', '2020 - IIIC ordinær - MD4061 - FVO med fasit.json', '2020 - IIID -ordinær MD4062 - FVO med fasit.json', '2020 - IIID kont - MD4062 - FVO med begrunnelse.json', '2020 januar - IIAB forskerlinje- MD4030 - FVO med fasit.json', '2021 - IAB kont - MD4011 - FVO med fasit.json', '2021 - IAB ordinær - MD4011 - FVO med fasit.json', '2021 - ICD kont - MD4020 - FVO med fasit.json', '2021 - ICD ordinær - MD4020 - FVO med fasit.json', '2021 - IIAB forskerlinje ordinær - MD4030 - FVO med fasit.json', '2021 - IIAB kont - MD4030 - FVO med fasit.json', '2021 - IIAB ordinær - MD4030 - FVO med fasit.json', '2021 - IIC ordinær desember - MD4042 - FVO med fasit.json', '2021 - IIC ordinær vår - MD4042 - FVO med fasit.json', '2021 - IID kont vår - MD4043 - FVO med fasit.json', '2021 - IID ordinær desember - MD4043 -FVO med fasit.json', '2021 - IID ordinær vår - MD4043 - FVO med fasit.json', '2021 - IIIC ordinær - MD4061 - FVO med fasit.json', '2022 - IAB kont - MD4011 - FVO med fasit.json', '2022 - IAB ordinær - MD4011 - FVO med fasit.json', '2022 - ICD kont - MD4020 - FVO med fasit.json', '2022 - ICD ordinær - MD4020 - FVO med fasit.json', '2022 - IIAB kont - MD4030 - FVO med fasit.json', '2022 - IIAB ordinær - MD4030 - FVO med fasit.json', '2022 - IIAB ordinær forskerlinje - MD4030 - FVO med fasit.json', '2022 - IIC kont vår - MD4042 - FVO med fasit.json', '2022 - IIC ordinær høst - MD4042 - FVO med fasit.json', '2022 - IIC ordinær vår - MD4042 - FVO med fasit.json', '2022 - IID - MD4043 Ordinær høst - Norsk.json', '2022 - IID kont vår - MD4043 - FVO med fasit.json', '2022 - IID ordinær vår - MD4043 - FVO med fasit.json', '2022 - IIIC - MD4061 KONT FVO med fasit.json', '2022 - IIIC - MD4061 ORDINÆR FVO med fasit.json', '2023 - IAB - MD4012 (MD4011) - FVO m fasit.json', '2023 - IAB - MD4012 (MD4011) - ORDINÆR m fasit.json', '2023 - ICD - MD4020 - FVO m fasit.json', '2023 - ICD - MD4020 - ORDINÆR m fasit.json', '2023 - IIAB - MD4030 - FVO m fasit.json', '2023 - IIAB - MD4030 - ORDINÆR m fasit.json', '2023 - IIC - MD4042 - høst FVO Fasit.json', '2023 - IIC - MD4042 - ORDINÆR m fasit.json', '2023 - IID - MD4043 - FVO m fasit kont.json', '2023 - IID - MD4043 - ORDINÆR m fasit.json', 'Fasit 2017 - IIC - MD4042 - eksamen 1-2017-05-16.json', 'Fasit FVO IIC MD4042 2017 konte 08.json', 'Fasit FVO MD4043 IID 2017 konte 08.json', 'Fasit IAB MD4011 2017 konte08.json', 'Fasit IAB MD4011 vår 2017.json', 'Fasit ICD MD4020 vår 2017.json', 'Fasit IIAB MD4030 vår 2017.json', 'Fasit MCQ ICD MD4020 2017 konte 08.json', 'Fasit MD4062-2017-05-15.json', 'HØST 2017 - IIC med fasit - MD4042 - eksamen 1-2017-12-11.json', 'HØST 2017 - IID med fasit- MD4043 - eksamen 1-2017-12-14.json', 'HØST 2017 - IIIC med fasit - MD4061 - eksamen 1-2017-12-18.json', 'MFFAGPR - Fagprøven for leger utdannet utenfor EU EØS og Sveits høst 2022 - Revidert fasit (bokmål).json', 'MFFAGPR - Fagprøven for leger utdannet utenfor EU EØS og Sveits Vår 2023 revidert fasit.json', 'MFFAGPR - Fagprøven for leger utdannet utenfor EU_EØS og Sveits Høst 2021 fasit - bokmål.json', 'MFFAGPR - Fagprøven for leger utdannet utenfor EU_EØS og Sveits Vår 2021-2021-fasit-bokmål.json', 'MFFAGPR Fagproven for leger utdannet utenfor EU EØS og Sveits vår 2022 - revidert fasit (bokmål).json', 'MFFAGPR Høst 2020 Ordinær fasit (bokmal).json', 'MFFAGPR Vår 2019 Ordinær Revidert fasit.json', 'Nasjonal delprøve i medisin høst 2020 - Revidert oppgavesett med fasitsvar bokmål.json', 'Nasjonal delprøve i medisin vår 2017 - Revidert fasit etter sensur.json', 'Nasjonal delprøve i medisin vår 2018 - Revidert fasit etter sensur.json', 'Nasjonal delprøve i medisin vår 2019 - Revidert fasit etter sensur.json', 'Nasjonal delprøve i medisin vår 2020 - Revidert fasit etter sensur.json', 'Nasjonal felles avsluttende skriftlig deleksamen i medisin høst 2021 - Revidert fasit etter sensur bokmål.json', 'Nasjonal felles avsluttende skriftlig deleksamen i medisin vår 2021 - Revidert fasit etter sensur bokmål.json', 'Revidert fasit - MFFAGPR - Fagprøven for leger utdannet utenfor EU EØS og Sveits - Høst 2023 (bokmål).json', 'Revidert fasit - Nasjonal felles avsluttende skriftlig deleksamen i medisin - Høst 2023 (bokmål).json', 'Revidert fasit - Nasjonal felles avsluttende skriftlig deleksamen i medisin - Vår 2023 bokmål.json', 'Revidert fasit - Nasjonal felles avsluttende skriftlig deleksamen i medisin høst 2022 bokmål.json', 'Revidert-fasit - Nasjonal felles avsluttende skriftlig deleksamen i medisin vår 2022 - Bokmål.json']
    app = QuizApp(question_set_json_pths)
    app.tkraise()
    app.mainloop()


