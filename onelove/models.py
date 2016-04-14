from flask_mongoengine import Document
from mongoengine.fields import (
    BaseField,
    BooleanField,
    DateTimeField,
    EmailField,
    EmbeddedDocument,
    EmbeddedDocumentField,
    ListField,
    ReferenceField,
    StringField,
    UUIDField,
)
from flask_security import UserMixin, RoleMixin


field_types = {
    'BooleanField': 'boolean',
    'DateTimeField': 'date_time',
    'EmailField': 'email',
    'EmbeddedDocument': 'embedded',
    'EmbeddedDocumentField': 'embedded_document',
    'EmbeddedDocumentListField': 'embedded_document_list',
    'ListField': 'list',
    'ReferenceField': 'reference',
    'StringField': 'string',
    'UUIDField': 'uuid',
}


class Application(EmbeddedDocument):
    name = StringField(max_length=512)
    galaxy_role = StringField(max_length=1024)

    def __repr__(self):
        return '<Application %r>' % self.name

    # Required for administrative interface
    def __unicode__(self):
        return self.__repr__()


class Provider(EmbeddedDocument):
    name = StringField(max_length=512)
    username = StringField(max_length=64)
    type = 'BASE'
    meta = {'allow_inheritance': True}

    def list(self):
        return []

    def update(self, **kwargs):
        pass

    def create(self, **kwargs):
        pass

    def destroy(self, id):
        pass

    @classmethod
    def fields(cls):
        result = []
        for property in dir(cls):
            if property[0] != '_':
                property_type = getattr(cls, property)
                if isinstance(property_type, BaseField):
                    type_name = type(property_type).__name__
                    result.append(
                        {
                            'name': property_type.name,
                            'type': field_types[type_name]
                        }
                    )
        return result

    def _setup(self):
        pass

    def __init__(self, *args, **kwargs):
        super(Provider, self).__init__(*args, **kwargs)
        self._setup()

    def __repr__(self):
        return '<Provider %r>' % self.name

    # Required for administrative interface
    def __unicode__(self):
        return self.__repr__()


class Role(Document, RoleMixin):
    """
    Role
    """
    name = StringField(max_length=255)
    admin = BooleanField()
    description = StringField(max_length=255)

    # Required for administrative interface
    def __unicode__(self):
        return self.name


class User(Document, UserMixin):
    """
    User
    """
    active = BooleanField(default=False)
    email = EmailField(unique=True)
    first_name = StringField(max_length=255)
    last_name = StringField(max_length=255)
    password = StringField(max_length=255)
    roles = ListField(ReferenceField(Role), default=[])
    register_uuid = UUIDField(binary=False)
    username = StringField(max_length=255, unique=True)

    def __repr__(self):
        return '<User %r>' % self.email


class Service(Document):
    user = ReferenceField(User)
    name = StringField(max_length=512, unique_with='user')
    applications = ListField(EmbeddedDocumentField(Application))

    def __repr__(self):
        return '<Service %s/%s>' % (self.user.username, self.name)


class Cluster(Document):
    name = StringField(max_length=512)
    applications = ListField(EmbeddedDocumentField(Application))
    providers = ListField(EmbeddedDocumentField(Provider))
    roles = ListField(ReferenceField(Role), default=[])
    services = ListField(ReferenceField(Service), default=[])

    def __repr__(self):
        return '<Cluster %r>' % self.name


class Task(Document):
    id = UUIDField(primary_key=True, binary=False)
    meta = {'collection': 'celery_taskmeta'}
    status = StringField(max_length=63, default='PENDING')
    date_done = DateTimeField()
    traceback = StringField()
    children = StringField()
    result = StringField()
