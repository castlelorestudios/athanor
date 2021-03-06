
import re, hashlib
from django.db import models
from django.db.models import Q
from athanor.utils.text import partial_match

# Create your models here.


class MushObject(models.Model):
    obj = models.OneToOneField('objects.ObjectDB', related_name='mush', null=True)
    account = models.OneToOneField('accounts.AccountDB', related_name='mush', null=True)
    group = models.OneToOneField('athanor-groups.Group', related_name='mush', null=True)
    board = models.OneToOneField('athanor-bbs.Board', related_name='mush', null=True)
    fclist = models.OneToOneField('fclist.FCList', related_name='mush', null=True)
    dbref = models.CharField(max_length=15, db_index=True)
    objid = models.CharField(max_length=30, unique=True, db_index=True)
    type = models.PositiveSmallIntegerField(db_index=True)
    name = models.CharField(max_length=80)
    created = models.DateTimeField()
    location = models.ForeignKey('MushObject', related_name='contents', null=True)
    destination = models.ForeignKey('MushObject', related_name='exits_to', null=True)
    parent = models.ForeignKey('MushObject', related_name='children', null=True)
    owner = models.ForeignKey('MushObject', related_name='owned', null=True)
    flags = models.TextField(blank=True)
    powers = models.TextField(blank=True)
    recreated = models.BooleanField(default=False)

    def __unicode__(self):
        return self.name

    def __repr__(self):
        return '<PennObj %s: %s>' % (self.dbref, self.name)

    def mushget(self, attrname):
        if not attrname:
            return False
        attr = self.attrs.filter(attr__key__iexact=attrname).first()
        if attr:
            return attr.value.replace('%r', '%R').replace('%t', '%T')
        if self.parent:
            return self.parent.mushget(attrname)
        else:
            return ""

    def hasattr(self, attrname):
        if not attrname:
            return False
        attr = self.attrs.filter(attr__key__iexact=attrname).first()
        return bool(attr)

    def lattr(self, attrpattern):
        if not attrpattern:
            return list()
        attrpattern = attrpattern.replace('`**','`\S+')
        attrpattern = r'^%s$' % attrpattern.replace('*','\w+')
        check = [attr.attr.key for attr in self.attrs.filter(attr__key__iregex=attrpattern)]
        if not check:
            return list()
        return check

    def lattrp(self, attrpattern):
        attrset = list()
        attrset += self.lattr(attrpattern)
        if self.parent:
            attrset += self.parent.lattrp(attrpattern)
        return list(set(attrset))

    def lattrp2(self, attrpattern):
        attrset = list()
        attrset += self.lattr(attrpattern)
        if self.parent:
            attrset += self.parent.lattrp2(attrpattern)
        return attrset

    def getstat(self, attrname, stat):
        attr = self.mushget(attrname)
        if not attr:
            return
        attr_dict = dict()
        for element in attr.split('|'):
            name, value = element.split('~', 1)
            attr_dict[name] = value
        find_stat = partial_match(stat, attr_dict)
        if not find_stat:
            return
        return attr_dict[find_stat]

    @property
    def exits(self):
        return self.contents.filter(type=4)

    def check_password(self, password):
        old_hash = self.mushget('XYXXY')
        if not old_hash:
            return False
        if old_hash.startswith('1:'):
            hash_against = old_hash.split(':')[2]
            check = hashlib.new('sha1')
            check.update(password)
            return check.hexdigest() == hash_against
        elif old_hash.startswith('2:'):
            hash_against = old_hash.split(':')[2]
            salt = hash_against[0:2]
            hash_against = hash_against[2:]
            check = hashlib.new('sha1')
            check.update('%s%s' % (salt, password))
            return check.hexdigest() == hash_against



def cobj(abbr=None):
    if not abbr:
        raise ValueError("No abbreviation entered!")
    code_object = MushObject.objects.filter(name='Master Code Object <MCO>').first()
    if not code_object:
        raise ValueError("Master Code Object <MCO> not found!")
    search_name = 'COBJ`%s' % abbr.upper()
    found_attr = code_object.attrs.filter(attr__key=search_name).first()
    if not found_attr:
        raise ValueError("COBJ`%s not found!" % abbr.upper())
    dbref = found_attr.value
    if not dbref:
        raise ValueError("Cannot find DBREF of %s" % abbr.upper())
    return objmatch(dbref)


def pmatch(dbref=None):
    if not dbref:
        return False
    find = MushObject.objects.filter(Q(dbref=dbref) | Q(objid=dbref)).exclude(obj=None).first()
    if find:
        return find.obj
    return False


def objmatch(dbref=None):
    if not dbref:
        return False
    find = MushObject.objects.filter(Q(dbref=dbref) | Q(objid=dbref)).first()
    if find:
        return find
    return False


class MushAttributeName(models.Model):
    key = models.CharField(max_length=200, unique=True, db_index=True)


class MushAttribute(models.Model):
    dbref = models.ForeignKey(MushObject, related_name='attrs')
    attr = models.ForeignKey('mushimport.MushAttributeName', related_name='characters')
    value = models.TextField(blank=True)


    class Meta:
        unique_together = (("dbref", "attr"),)

