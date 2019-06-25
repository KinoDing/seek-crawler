import re

from wordcloud import STOPWORDS

from database_config import Database
from generate_visual_data import GenerateVisualData
from io import StringIO


class Start:

    def __init__(self):
        pass

    def process_job_content(self, results):
        if len(results) <= 0:
            raise IndexError('invalid number of results')
        lines = ''
        for row in results:
            # line = ''.join(row).rstrip()
            # word_list = line.split(' ')

            # word_list.remove()
            # no_word_pattern = re.compile('[^((?!hede).)*$]')
            # line = re.findall(no_word_pattern, line)
            lines += row[1]
        return lines

    def begin(self) -> object:
        db = Database('db_config', 'dev', 'postgres')
        results = db.get_all_job_content()
        text = self.process_job_content(results)

        green = '#4DD443'
        bg = '#35263B'
        # self, text_value, bg_color, max_font_size, image_background, bg_image_name
        stopwords = set(STOPWORDS)
        stopwords.update(['etc', 'you', 'a', 'this', 'in', 'is', 'an', 'and', 'or','with','will','be'])

        GenerateVisualData(text, bg_color=bg, max_font_size=40, image_background=True, bg_image_name='bg.jpg',
                           stopwords=stopwords)

    def temp_clean_data(self):
        db = Database('db_config', 'dev', 'postgres')
        results = db.get_all_job_content()
        results = self.clean_results(results)
        results = tuple(results)
        db.update_job_content(results)

    def clean_results(self, results):
        # email_pattern = re.(r"\w{4,20}@(\w+)(\.[a-zA-Z0-9_-]+)+")
        data = []
        for row in results:
            line = ''.join(row[1])
            line = line.replace('\\xa0', ' ')
            email = re.search(r'\w+[\w\.-]*\w+@\w+(-\w+)*[\.\w]+', line)
            row_list = list(row)
            if email is not None:
                ee = email.group(0)
                line = line.replace(ee, '')
                line = line.replace('\'\'\'\'', ' ')
            row_value = {'job_id': row_list[0], 'content': line}
            data.append(row_value)
        return data


start = Start()
start.begin()
