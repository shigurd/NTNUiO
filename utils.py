
class Question:
    def __init__(self):
        self.question_set = None
        self.question_number = None
        self.question_text = None
        self.image_id = []
        self.abcd = dict()
        self.answer_tag = None
        self.completion_status = 0

    def set_question_set(self, string):
        self.question_set = string

    def set_question_number(self, string):
        self.question_number = string

    def set_question_text(self, string):
        self.question_text = string

    def add_image_id(self, string):
        self.image_id.append(string)

    def set_answer(self, tag, answer_string):
        try:
            self.abcd[tag]['answer'] = answer_string
        except:
            self.abcd[tag] = dict()
            self.abcd[tag]['answer'] = answer_string

    def set_explaination(self, tag, explaination_string):
        try:
            self.abcd[tag]['explaination'] = explaination_string
        except:
            self.abcd[tag] = dict()
            self.abcd[tag]['explaination'] = explaination_string

    def set_answer_tag(self, string):
        self.answer_tag = string

    def get_all_info_as_dict(self):
        out_dict = {}
        out_dict['question_set'] = self.question_set
        out_dict['question_number'] = self.question_number
        out_dict['question_text'] = self.question_text
        out_dict['image_id'] = self.image_id
        out_dict['abcd'] = self.abcd
        out_dict['answer_tag'] = self.answer_tag
        out_dict['completion_status'] = self.completion_status

        return out_dict

    def print_all_info(self):
        print(self.question_set, '\n')
        print(self.question_number, '\n')
        print(self.question_text, '\n')
        print(self.image_id, '\n')
        for key in self.abcd:
            print(key)
            print(self.abcd[key]['answer'])
            try:
                print(self.abcd[key]['explaination'])
            except:
                print('No explaination')
        print('Correct answer:', self.answer_tag, '\n')