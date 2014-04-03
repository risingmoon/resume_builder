from django import forms
from django.forms import ModelForm
from outline.models import Section, Entry, Data


class ProfileForm(forms.Form):

    first_name = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'class': 'col-sm-4 form-control',
                'placeholder': 'First Name'}))
    middle_name = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'class': 'col-sm-4 form-control',
                'placeholder': 'Middle Name'}))
    last_name = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'class': 'col-sm-4 form-control',
                'placeholder': 'Last Name'}))
    cell = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'class': 'col-sm-4 form-control',
                'placeholder': 'Cell Phone#'}))
    home = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'class': 'col-sm-4 form-control',
                'placeholder': 'Home Phone#'}))
    fax = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'class': 'col-sm-4 form-control',
                'placeholder': 'Fax Phone#'}))
    address1 = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'class': 'col-sm-4 form-control',
                'placeholder': 'Address1'}))
    address2 = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'class': 'col-sm-4 form-control',
                'placeholder': 'Address2'}))
    city = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'class': 'col-sm-4 form-control',
                'placeholder': 'City'}))
    state = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'class': 'col-sm-4 form-control',
                'placeholder': 'State'}))
    zipcode = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'class': 'col-sm-4 form-control',
                'placeholder': 'Zipcode'}))
    email = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'class': 'col-sm-4 form-control',
                'placeholder': 'Email'}))
    region = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'class': 'col-sm-4 form-control',
                'placeholder': 'Region'}))


class WebForm(ModelForm):
    account = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'class': 'col-sm-4 form-control',
                'placeholder': 'Account'}))


class SectionForm(ModelForm):
    class Meta:
        model = Section
        field = [
            'title',
            'description',
        ]


class EntryForm(ModelForm):
    class Meta:
        model = Entry
        fields = [
            'title',
            'subtitle',
            'start_date',
            'end_date',
            'present',
            'city',
            'state',
            'contact',
            'description',
            'display',
        ]


class DataForm(ModelForm):
    class Meta:
        model = Data
        field = [
            'text'
        ]

