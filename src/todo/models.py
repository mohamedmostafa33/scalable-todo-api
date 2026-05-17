from mongoengine import Document, StringField, BooleanField

class Todo(Document):
    title = StringField(required=True, max_length=255)
    description = StringField()
    completed = BooleanField(default=False)

    meta = {
        'collection': 'todos'
    }

    def __str__(self):
        return self.title