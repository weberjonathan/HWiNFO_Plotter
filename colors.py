class ColorFactory(object):
    colors = ['red', 'blue', 'green', 'purple', 'orange', 'brown', 'cyan', 'magenta', 'gray']
    curr_clr_index = 0

    @classmethod
    def reset(self):
        self.curr_clr_index = 0

    @classmethod
    def next(cls):
        rtn = cls.colors[cls.curr_clr_index % len(cls.colors)]
        cls.curr_clr_index += 1
        return rtn
