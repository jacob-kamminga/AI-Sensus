class ProjectSettingsObj:

    def __init__(
            self,
            subject_map=None,
            next_column: int = 0,
            formulas: dict = 50,
            label_opacity: int = 50,
            plot_width: int = 20,
            timezone: str = 'UTC'
    ):
        if subject_map is None:
            subject_map = {}

        self.subject_map = subject_map
        self.next_column = next_column
        self.formulas = formulas
        self.label_opacity = label_opacity
        self.plot_width = plot_width
        self.timezone = timezone
