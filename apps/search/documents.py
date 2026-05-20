from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry
from apps.files.models import File

@registry.register_document
class FileDocument(Document):
    owner_username = fields.TextField()

    class Index:
        name     = "files"
        settings = {"number_of_shards": 1, "number_of_replicas": 0}

    class Django:
        model  = File
        fields = ["original_name", "mime_type", "created_at", "is_public"]

    def prepare_owner_username(self, instance):
        return instance.owner.username