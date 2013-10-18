# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Person'
        db.create_table(u'main_person', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('first_name', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('last_name', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('deleted', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'main', ['Person'])

        # Adding model 'Capability'
        db.create_table(u'main_capability', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=30)),
        ))
        db.send_create_signal(u'main', ['Capability'])

        # Adding model 'PersonCapability'
        db.create_table('person_capability', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('person', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main.Person'])),
            ('capability', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main.Capability'], on_delete=models.PROTECT)),
        ))
        db.send_create_signal(u'main', ['PersonCapability'])

        # Adding unique constraint on 'PersonCapability', fields ['person', 'capability']
        db.create_unique('person_capability', ['person_id', 'capability_id'])

        # Adding model 'OfftimeType'
        db.create_table('offtime_type', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('color', self.gf('main.models.ColorField')(default='#66B0FF', max_length=7)),
            ('type_choice', self.gf('django.db.models.fields.CharField')(default='untracked', max_length=20)),
        ))
        db.send_create_signal(u'main', ['OfftimeType'])

        # Adding model 'Offtime'
        db.create_table(u'main_offtime', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('person', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main.Person'])),
            ('type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main.OfftimeType'], on_delete=models.PROTECT)),
            ('start_date', self.gf('django.db.models.fields.DateTimeField')()),
            ('end_date', self.gf('django.db.models.fields.DateTimeField')()),
            ('approved', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('comment', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('deleted', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('added_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal(u'main', ['Offtime'])


    def backwards(self, orm):
        # Removing unique constraint on 'PersonCapability', fields ['person', 'capability']
        db.delete_unique('person_capability', ['person_id', 'capability_id'])

        # Deleting model 'Person'
        db.delete_table(u'main_person')

        # Deleting model 'Capability'
        db.delete_table(u'main_capability')

        # Deleting model 'PersonCapability'
        db.delete_table('person_capability')

        # Deleting model 'OfftimeType'
        db.delete_table('offtime_type')

        # Deleting model 'Offtime'
        db.delete_table(u'main_offtime')


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
