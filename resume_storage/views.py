from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required, permission_required
from outline.models import Section, Entry, Data, Profile, Web
from resume_storage.models import Resume, Resume_Web
from resume_storage.models import Saved_Entry, Saved_Section
from resume_storage.forms import ResumeForm, SectionForm, EntryForm, DataForm
from django.forms import model_to_dict
from convertToPDF import writeResumePDF
from django.core.exceptions import PermissionDenied


def front_view(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse('home'))
    return render(request, 'resume_storage/front.html', {})


@login_required
def home_view(request):
    if not request.user.is_authenticated():
        return HttpResponseRedirect(reverse('front'))
    all_resumes = Resume.objects.all().prefetch_related()
    resumes = all_resumes.filter(user=request.user)
    context = {'resumes': resumes, }
    return render(request, 'resume_storage/home.html', context)


@permission_required('resume_storage.add_resume')
def create_resume(request):
    prof = Profile.objects.get(user=request.user)
    webs = Web.objects.filter(profile=prof)
    kwargs = model_to_dict(prof, exclude=['user', 'id'])
    res = Resume.objects.create(
        user=request.user,
        title='New Resume',
        **kwargs
    )
    for item in webs:
        Resume_Web.objects.create(resume=res, account=item.account)
    return HttpResponseRedirect(reverse('resume_view', args=(res.pk,)))


@permission_required('resume_storage.change_resume')
def resume_view(request, resume_no):
    try:
        resume = Resume.objects.get(pk=resume_no)
    except Resume.DoesNotExist:
        raise Http404
    if resume.user != request.user:
        raise PermissionDenied
    data = model_to_dict(resume)
    data.pop('title')
    accts = Resume_Web.objects.filter(resume=resume)
    websites = {}
    for i in range(len(accts)):
        websites.update({'account%d' % i: accts[i].account})
    sections = Section.objects.filter(user=request.user).prefetch_related()
    if request.method == 'POST':
        _save_resume(request, resume, data, websites)
        return HttpResponseRedirect(reverse('resume_view', args=(resume_no,)))
    form = ResumeForm(data=data)
    saved = _build_saved(resume)
    return render(
        request,
        'resume_storage/resume.html',
        {
            'form': form,
            'websites': websites,
            'resume': resume,
            'sections': sections,
            'saved': saved,
        }
    )


def _save_resume(request, resume, data, websites):
    data.update(request.POST)
    form = ResumeForm(data)
    form.data['title'] = form.data['title'][0]
    if form.is_valid():
        _edit_resume_profile(resume, form)
        _edit_resume_webs(resume, form, websites)
        _build_resume_fields(
            resume,
            request.user,
            request.POST.getlist('sections'),
            request.POST.getlist('entries'),
            request.POST.getlist('datas')
        )


def _edit_resume_profile(resume, form):
    resume.title = form.cleaned_data['title']
    if not form.data.get('Middle name', False):
        resume.middle_name = ''
    if not form.data.get('Cell', False):
        resume.cell = ''
    if not form.data.get('Home', False):
        resume.home = ''
    if not form.data.get('Fax', False):
        resume.fax = ''
    if not form.data.get('Address1', False):
        resume.address1 = ''
    if not form.data.get('Address2', False):
        resume.address2 = ''
    if not form.data.get('City', False):
        resume.city = ''
    if not form.data.get('State', False):
        resume.state = ''
    if not form.data.get('Zipcode', False):
        resume.zipcode = ''
    if not form.data.get('Email', False):
        resume.email = ''
    if not form.data.get('Region', False):
        resume.region = ''
    resume.save()


def _edit_resume_webs(resume, form, websites):
    for i in range(len(websites)):
        if not form.data.get('account%d' % i, False):
            Resume_Web.objects.filter(
                resume=resume,
                account=websites['account%d' % i]
            ).delete()


def _build_resume_fields(resume, usr, sect_list, ent_list, dat_list):
    sect_dict = {}
    for title in sect_list:
        try:
            sect = Section.objects.get(user=usr, title=title)
            ent_dict = {}
            for ent_title in ent_list:
                try:
                    ent = Entry.objects.get(section=sect, title=ent_title)
                    dat_rtn_list = []
                    for text in dat_list:
                        try:
                            dat_rtn_list.append(Data.objects.get(entry=ent, text=text))
                        except Data.DoesNotExist:
                            pass
                    ent_dict[ent] = dat_rtn_list
                except Entry.DoesNotExist:
                    pass
            sect_dict[sect] = ent_dict
        except Section.DoesNotExist:
            pass
    resume.setResumeFields(sect_dict)


def _build_saved(resume):
    saved_dict, saved = resume.getResumeFields(), []
    for key, val in saved_dict.iteritems():
        saved.append(key.section)
        for k, v in val.iteritems():
            saved.append(k.entry)
            saved.extend(v)
    return saved


@login_required
def print_resume(request, resume_no):
    try:
        resume = Resume.objects.get(pk=resume_no)
    except Resume.DoesNotExist:
        raise Http404
    if resume.user != request.user:
        raise PermissionDenied
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="somefilename.pdf"'
    writeResumePDF(resume, response)
    return response


@permission_required('resume_storage.delete_resume')
def delete_resume(request, resume_no):
    try:
        resume = Resume.objects.get(pk=resume_no)
    except Resume.DoesNotExist:
        raise Http404
    if resume.user != request.user:
        raise PermissionDenied
    return render(request, 'resume_storage/delete.html', {'resume': resume})


@permission_required('resume_storage.delete_resume')
def real_delete(request, resume_no):
    try:
        resume = Resume.objects.get(pk=resume_no)
    except Resume.DoesNotExist:
        raise Http404
    if resume.user != request.user:
        raise PermissionDenied
    resume.delete()
    return HttpResponseRedirect(reverse('home'))
