#!/usr/bin/env python
# -*- coding: utf-8 -*-

################################################################################
#
#	RMG Website - A Django-powered website for Reaction Mechanism Generator
#
#	Copyright (c) 2011 Prof. William H. Green (whgreen@mit.edu) and the
#	RMG Team (rmg_dev@mit.edu)
#
#	Permission is hereby granted, free of charge, to any person obtaining a
#	copy of this software and associated documentation files (the 'Software'),
#	to deal in the Software without restriction, including without limitation
#	the rights to use, copy, modify, merge, publish, distribute, sublicense,
#	and/or sell copies of the Software, and to permit persons to whom the
#	Software is furnished to do so, subject to the following conditions:
#
#	The above copyright notice and this permission notice shall be included in
#	all copies or substantial portions of the Software.
#
#	THE SOFTWARE IS PROVIDED 'AS IS', WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#	IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#	FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#	AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#	LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#	FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
#	DEALINGS IN THE SOFTWARE.
#
################################################################################

"""
This module defines the Django forms used by the pdep app.
"""

from django import forms
from django.forms.formsets import formset_factory

from models import *
from rmgweb.main.fields import *

################################################################################

class EditNetworkForm(forms.ModelForm):
    """
    A Django form for editing a MEASURE input file.
    """
    class Meta:
        model = Network
        fields = ('inputText',)

################################################################################

class UploadNetworkForm(forms.ModelForm):
    """
    A Django form for uploading a MEASURE input file.
    """
    class Meta:
        model = Network
        fields = ('inputFile',)

################################################################################

class PlotKineticsForm(forms.Form):
    """
    A Django form for choosing parameters for generating k(T,P) vs. T and P
    plots.
    """
    reactant = forms.ChoiceField(choices=[], label='Reactant configuration')
    T = forms.FloatField(initial=1000, label='Temperature of k(T,P) vs. P plot (K)')
    P = forms.FloatField(initial=1, label='Pressure of k(T,P) vs. T plot (bar)')

    def __init__(self, configurations, *args, **kwargs):
        super(PlotKineticsForm, self).__init__(*args, **kwargs)
        choices = [(config, config) for config in configurations]
        self.fields['reactant'].choices = choices

################################################################################

class AddSpeciesForm(forms.Form):
    """
    A Django form for adding a species to a Network.
    """
    label = forms.CharField(widget=forms.TextInput(attrs={'class':'speciesLabel'}))
    structure = forms.CharField(widget=forms.TextInput(attrs={'class':'speciesStructure'}))
    E0 = EnergyField()
    
    def __init__(self, *args, **kwargs):
        super(AddSpeciesForm, self).__init__(*args, **kwargs)
        self.network = None
        
    def clean_label(self):
        """
        Provides custom validation for the label field. In particular, we
        want to check that the label is not already in use.
        """
        label = self.cleaned_data['label']
        for species in self.network.getAllSpecies():
            if species.label == label:
                raise forms.ValidationError('Label already in use.')
        return label
    
AddSpeciesFormSet = formset_factory(AddSpeciesForm, extra=5)

################################################################################

class AddPathReactionsForm(forms.Form):
    """
    A Django form for adding a species to a Network.
    """
    reactant1 = forms.ChoiceField(required=True, choices=[])
    reactant2 = forms.ChoiceField(required=False, choices=[])
    product1 = forms.ChoiceField(required=True, choices=[])
    product2 = forms.ChoiceField(required=False, choices=[])
    E0 = EnergyField()
    
    def __init__(self, *args, **kwargs):
        super(AddPathReactionsForm, self).__init__(*args, **kwargs)
        self.network = None
    
    def setSpeciesChoices(self, choices):
        self.fields['reactant1'].choices = choices
        self.fields['reactant2'].choices = choices
        self.fields['product1'].choices = choices
        self.fields['product2'].choices = choices
    
    def clean(self):
        """
        Provides custom validation for the label field. In particular, we
        want to check that the reaction does not already exist.
        """
        from rmgpy.reaction import Reaction
        
        reactants = []; products = []
        for species in self.network.getAllSpecies():
            if self.cleaned_data['reactant1'] == species.label:
                reactants.append(species)
            if self.cleaned_data['reactant2'] == species.label:
                reactants.append(species)
            if self.cleaned_data['product1'] == species.label:
                products.append(species)
            if self.cleaned_data['product2'] == species.label:
                products.append(species)
        
        if len(reactants) == len(products) and all([reactant in products for reactant in reactants]) and all([product in reactants for product in products]):
            raise forms.ValidationError('Reaction has same reactants and products.')
        
        reaction = Reaction(reactants=reactants, products=products)
        if not reaction.isBalanced():
            raise forms.ValidationError('Reaction is not balanced.')
        
        if len(reactants) == len(products) == 2:
            raise forms.ValidationError('Bimolecular reactions (A + B -> C + D) not allowed.')
        
        for rxn in self.network.pathReactions:
            if rxn.isIsomorphic(reaction):
                raise forms.ValidationError('Reaction already present in network.')
        
        self.cleaned_data['reaction'] = reaction
        
        return self.cleaned_data
    
AddPathReactionsFormSet = formset_factory(AddPathReactionsForm, extra=5)
