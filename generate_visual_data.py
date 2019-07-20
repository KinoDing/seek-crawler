import os

from PIL import Image
import numpy as np
import matplotlib.pyplot as plt

from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator


class GenerateVisualData:

    def __init__(self, text_value, bg_color, max_font_size, image_background, bg_image_name, stopwords):
        bg_image_color = None
        if image_background and (bg_image_name is not None):
            bg_image_color = self.__read_resource_file(bg_image_name)

        wc = WordCloud(background_color=bg_color,
                       # width=1159, height=1017,
                       max_words=5000000,
                       mask=bg_image_color,
                       max_font_size=max_font_size,
                       random_state=42,
                       relative_scaling=1,
                       # scale=15,
                       stopwords=stopwords)

        # wc = WordCloud(background_color=bg_color,
        #                width=1159, height=1017,
        #                max_words=5000000,
        #                # mask=bg_image_color,
        #                max_font_size=max_font_size,
        #                min_font_size=13,
        #                relative_scaling=0.7,
        #                random_state=4,
        #                stopwords=stopwords)
        print('开始加载文本')
        wc.generate(text_value)
        image_colors = ImageColorGenerator(bg_image_color)
        print('加载图片成功！')
        # # 在只设置mask的情况下,你将会得到一个拥有图片形状的词云
        # plt.imshow(wc, interpolation="bilinear")
        # plt.axis("off")
        # plt.figure()

        plt.imshow(wc.recolor(color_func=image_colors), interpolation="bilinear")
        plt.axis("off")
        plt.figure()
        # plt.show()
        self.save_image(wc, 'cloud_image.png')
        print('生成词云成功!')
        # plt.imshow(image_colors, cmap=plt.cm.grey, interpolation="bilinear")
        # plt.axis("off")
        # plt.show()

    # load image from resources folder
    def __read_resource_file(self, file_name):
        __name__ = 'resources'
        __location__ = os.path.join(os.path.dirname(__file__), __name__ + os.path.sep + file_name)
        try:
            return np.array(Image.open(__location__))
        except FileNotFoundError as error:
            print('can\' find file:' + file_name, error)

    def save_image(self, wc, file_name):
        __name__ = 'resources'
        __location__ = os.path.join(os.path.dirname(__file__), __name__ + os.path.sep + file_name)
        wc.to_file(__location__)
        pass
