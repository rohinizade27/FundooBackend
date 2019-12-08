from django_elasticsearch_dsl import Document,fields
from django_elasticsearch_dsl.registries import registry
from .models import Notes
from elasticsearch_dsl import analyzer, tokenizer

my_analyzer = analyzer('my_analyzer',
                       tokenizer=tokenizer('trigram', 'nGram', min_gram=1, max_gram=2),
                       filter=['lowercase']
                       )


@registry.register_document
class NoteDocument(Document):
    """
    The fields of the model you want to be indexed in Elasticsearch
    """
    title = fields.TextField(
        analyzer=my_analyzer,
        fields={'raw': fields.KeywordField()}
    )
    description = fields.TextField(
        analyzer=my_analyzer,
        fields={'raw': fields.KeywordField()}
    )

    class Index:
        """
         Name of the Elasticsearch index
        """
        name = 'notess'
        settings = {'number_of_shards': 1,
                    'number_of_replicas': 0}

    class Django:
        """
        The model associated with this Document
        """
        model = Notes
