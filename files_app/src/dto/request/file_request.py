class FileRequest:
    def __init__(self, request):
        self.filename = request.json["filename"]
        self.path_to_file = request.json["path_to_file"]
        self.date = request.json["date"]

    def __str__(self):
        return "filename: {0}, path_to_file: {1}, date: {2}".format(self.filename, self.path_to_file, self.date)
