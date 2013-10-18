from south.v2 import SchemaMigration
from django.core.management import call_command

class Migration(SchemaMigration):
    def forwards(self, orm):
        call_command("loaddata", "capabilities_initial.yaml")

    def backwards(self, orm):
        pass
