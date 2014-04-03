from django.db import models
from outline.models import Section, Entry, Data
from django.contrib.auth.models import User


class Resume(models.Model):
    #metadatas
    title = models.CharField(max_length=64)
    user = models.ForeignKey(User)

    #header fields
    first_name = models.CharField(max_length=50)
    middle_name = models.CharField(max_length=50, blank=True)
    last_name = models.CharField(max_length=50)
    cell = models.CharField(max_length=15, blank=True)
    home = models.CharField(max_length=15, blank=True)
    fax = models.CharField(max_length=15, blank=True)
    address1 = models.CharField(max_length=50, blank=True)
    address2 = models.CharField(max_length=50, blank=True)
    city = models.CharField(max_length=50, blank=True)
    state = models.CharField(max_length=50, blank=True)
    zipcode = models.CharField(max_length=50, blank=True)
    email = models.CharField(max_length=50, blank=True)
    region = models.CharField(max_length=50, blank=True)

    def middle_initial(self):
        "Returns full name with middle initial"
        if self.middle_name:
             # pdb.set_trace()
            return unicode(' '.join([
                self.first_name,
                self.middle_name[0] + '.',
                self.last_name]))
        else:
            return unicode(' '.join([
                self.first_name,
                self.last_name]))

    def setResumeFields(self, sectionDict):
        #first need to delete all the entries associated with this resume
        Saved_Section.objects.filter(resume=self).delete()
        #then create the new entries
        for eachSection in sectionDict.keys():
            newSection = Saved_Section.objects.create(resume=self,
                                                      section=eachSection)
            for eachEntry in sectionDict[eachSection].keys():
                newEntry = Saved_Entry.objects.create(section=newSection,
                                                      entry=eachEntry)
                newEntry.dataset.add(*sectionDict[eachSection][eachEntry])

    def getResumeFields(self):
        secEntDats = {}
        for eachSection in Saved_Section.objects.filter(resume=self):
            EntDats = {}
            for eachEntry in Saved_Entry.objects.filter(section=eachSection):
                Dats = []
                for eachData in Data.objects.filter(entry=eachEntry):
                    Dats.append(eachData)
                EntDats[eachEntry] = Dats
            secEntDats[eachSection] = EntDats
        return secEntDats


class Resume_Web(models.Model):
    account = models.CharField(max_length=50)
    resume = models.ForeignKey(Resume)


class Saved_Section(models.Model):
    resume = models.ForeignKey(Resume)
    section = models.ForeignKey(Section)


class Saved_Entry(models.Model):
    section = models.ForeignKey(Saved_Section)
    entry = models.ForeignKey(Entry)
    dataset = models.ManyToManyField(Data)
