# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Offtime.parent_offtime'
        db.add_column(u'main_offtime', 'parent_offtime',
                      self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main.Offtime'], null=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Offtime.parent_offtime'
        db.delete_column(u'main_offtime', 'parent_offtime_id')


    models = {
        u'main.capability': {
            'Meta': {'object_name': 'Capability'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '30'})
        },
        u'main.offtime': {
            'Meta': {'object_name': 'Offtime'},
            'added_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'approved': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'comment': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'end_date': ('django.db.models.fields.DateTimeField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'parent_offtime': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['main.Offtime']", 'null': 'True', 'blank': 'True'}),
            'person': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['main.Person']"}),
            'start_date': ('django.db.models.fields.DateTimeField', [], {}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['main.OfftimeType']", 'on_delete': 'models.PROTECT'})
        },
        u'main.offtimetype': {
            'Meta': {'object_name': 'OfftimeType', 'db_table': "'offtime_type'"},
            'color': ('main.models.ColorField', [], {'default': "'#66B0FF'", 'max_length': '7'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'type_choice': ('django.db.models.fields.CharField', [], {'default': "'untracked'", 'max_length': '20'})
        },
        u'main.person': {
            'Meta': {'object_name': 'Person'},
            'deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30'})
        },
        u'main.personcapability': {
            'Meta': {'unique_together': "(('person', 'capability'),)", 'object_name': 'PersonCapability', 'db_table': "'person_capability'"},
            'capability': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['main.Capability']", 'on_delete': 'models.PROTECT'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'person': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['main.Person']"})
        }
    }

    complete_apps = ['main']
