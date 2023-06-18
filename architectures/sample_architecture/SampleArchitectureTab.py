from architectures.AbstractTab import AbstractTab


class SampleTab(AbstractTab):
    """Just a sample tab that uses the default implementations in AbstractTab"""
    @property
    def id(self):
        return super().id

    @property
    def port(self):
        return super().port

    @property
    def label(self):
        return super().label

    @property
    def description(self):
        return super().description

    @property
    def requirements(self):
        return super().requirements

    def meets_requirements(self, user_text, user_audio):
        return super().meets_requirements(user_text, user_audio)

    @property
    def options(self):
        return super().options

    @property
    def input_ids(self):
        return super().input_ids

    def construct_input_dict(self, *args):
        return super().construct_input_dict
