#!/usr/bin/env python
# -*- coding: utf-8 -*-

################################################################################
#
#    RMG Website - A Django-powered website for Reaction Mechanism Generator
#
#    Copyright (c) 2011 Prof. William H. Green (whgreen@mit.edu) and the
#    RMG Team (rmg_dev@mit.edu)
#
#    Permission is hereby granted, free of charge, to any person obtaining a
#    copy of this software and associated documentation files (the 'Software'),
#    to deal in the Software without restriction, including without limitation
#    the rights to use, copy, modify, merge, publish, distribute, sublicense,
#    and/or sell copies of the Software, and to permit persons to whom the
#    Software is furnished to do so, subject to the following conditions:
#
#    The above copyright notice and this permission notice shall be included in
#    all copies or substantial portions of the Software.
#
#    THE SOFTWARE IS PROVIDED 'AS IS', WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#    FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
#    DEALINGS IN THE SOFTWARE.
#
################################################################################

from django.db import models
from django import forms

from widgets import *

################################################################################

class NumberUnitsField(forms.MultiValueField):
    """
    A field for specifying a numeric value with corresponding units. Use the
    `choices` parameter in the constructor to specify the allowed units.
    """
    
    def __init__(self, choices, *args, **kwargs):
        fields = (
            forms.FloatField(),
            forms.ChoiceField(choices=choices),
        )
        # Don't forget to set the initial values, or form.has_changed() won't work properly!
        kwargs['initial'] = ['', choices[0][0]]
        kwargs['widget'] = InputAndChoiceWidget(choices)
        super(NumberUnitsField, self).__init__(fields, **kwargs)
        
    def compress(self, data_list):
        if data_list:
            try:
                value = float(data_list[0])
                units = str(data_list[1])
            except ValueError:
                raise forms.ValidationError('A numeric value is required.')
            return (value, units)
        return None
