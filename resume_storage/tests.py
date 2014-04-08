from django.test import TestCase
from outline.models import Section, Entry, Data
from models import Resume, Resume_Web, Saved_Section, Saved_Entry
from django.contrib.auth.models import User
from django.test import Client
from django.core.urlresolvers import reverse


class ResumeStorageTestCase(TestCase):

    def setUp(self):
        self.testUser = User.objects.create_user('testperson',
                                                 'fake@email.ro',
                                                 'badpass',)
        Resume.objects.create(first_name='test',
                              last_name='user',
                              user=self.testUser)
        for atitle in ('one title', 'two title', 'red title', 'blue title'):
            asection = Section.objects.create(title=atitle, user=self.testUser)
            for anothertitle in ('big title', 'small title', 'sub title'):
                anentry = Entry.objects.create(title=anothertitle,
                                               section=asection,)
                for atext in ('almost', 'done'):
                    Data.objects.create(text=atext, entry=anentry)

    def testGetResume(self):
        newResume = Resume.objects.create(first_name='jack',
                                          last_name='markley',
                                          user=self.testUser)
        self.assertEqual(newResume.getResumeFields(), {})

        newResume = Resume.objects.create(first_name='mark',
                                          last_name='charyk',
                                          user=self.testUser)
        sectdict = {}
        for atitle in ('a', 'no', 'the', 'why'):
            asection = Section.objects.create(title=atitle, user=self.testUser)
            sectdict[asection] = {}
            for anothertitle in ('top', 'bot', 'mid'):
                anentry = Entry.objects.create(title=anothertitle,
                                               section=asection,)
                sectdict[asection][anentry] = []
                for atext in ('makeit', 'end'):
                    newdata = Data.objects.create(text=atext, entry=anentry)
                    sectdict[asection][anentry].append(newdata)
        result = newResume.getResumeFields()
        for savesect in result.keys():
            assert savesect.section in sectdict.keys()

    def testSetResume(self):
        newResume = Resume.objects.create(first_name='jack',
                                          last_name='markley',
                                          user=self.testUser)
        Section.objects.create(user=self.testUser, title='invissection')
        mysection = Section.objects.create(user=self.testUser,
                                           title='vissection')
        Entry.objects.create(section=mysection, title='invisentry')
        myentry = Entry.objects.create(section=mysection,
                                       title='visentry')
        Data.objects.create(entry=myentry, text='invisdata')
        mydata = Data.objects.create(entry=myentry,
                                     text='visdata')
        fieldDict = {mysection: {myentry: [mydata]}}

        newResume.setResumeFields(fieldDict)
        for eachSection in Saved_Section.objects.filter(resume=newResume):
            assert eachSection.section in fieldDict.keys()
            for eachEntry in Saved_Entry.objects.filter(section=eachSection):
                assert eachEntry.entry in fieldDict[eachSection.section].keys()


class TestViews(TestCase):
    fixtures = ['test_fixture.json', ]

    def setUp(self):
        self.client = Client()
        self.client.login(username='admin', password='admin')

    def tearDown(self):
        self.client.logout()

    def test_front_logged_out(self):
        self.client.logout()
        resp = self.client.get(reverse('index'))
        self.assertContains(resp, 'Resume Storage Front page')

    def test_front_logged_in(self):
        resp = self.client.get(reverse('index'), follow=True)
        print str(resp)
        self.assertContains(resp, 'Print this resume')
