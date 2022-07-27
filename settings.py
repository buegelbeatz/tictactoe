import json

SETTINGS_FILENAME_TMPLATE = "tictactoe_recommended_mapping_{}.json"

class Settings:
    def __init__(self, size=3, filename_template=SETTINGS_FILENAME_TMPLATE):
        self.size = size
        self.file_name = filename_template.format(size)

    def load(self):
        try:
            with open(self.file_name, 'r') as scoring_file:
                return json.load(scoring_file)
        except:
            return None

    def save(self, data):
        with open(self.file_name, 'w') as scoring_file:
            json.dump(data, scoring_file, ensure_ascii=False, indent=4)
