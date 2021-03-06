from source.instance import get_json_from_path
from source.instance import Instance


class Module:
    def __init__(self, wd=None, state=None, parent=None):
        self.parent = parent
        try:
            self.properties = get_json_from_path(wd / "settings.json")
        except FileNotFoundError:
            self.properties = {}
        self.instance = Instance.state
        if state:
            # merges static settings and dynamically passed state. States override settings.
            self.properties.update(state)
