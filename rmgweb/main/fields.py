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

class QuantityField(models.Field):
    """
    A custom model field for representing a physical quantity, with a value
    and units. In Python this is represented as a tuple of the form
    ``(value, units)``, where ``value`` is a float and ``units`` is a string.
    In database tables this data is represented as a text string, with the 
    value and units separated by a space. When creating a :class:`QuantityField`
    object, you must specify the `form_class` to use as a form field; normally
    this will be a class derived from :class:`NumberUnitsField`.
    """
    # A brief description for django.contrib.admindocs
    description = "A physical quantity (value and units)"
    # Setting the metaclass to SubfieldBase causes to_python() to be invoked 
    # when fields of this type are initialized
    __metaclass__ = models.SubfieldBase
    
    def __init__(self, form_class, *args, **kwargs):
        self.form_class = form_class
        super(QuantityField, self).__init__(*args, **kwargs)
        
    def db_type(self, connection):
        return 'char(50)'
    
    def to_python(self, value):
        """
        Convert the given `value` from its representation in the database
        tables to the corresponding Python object.
        """
        if (isinstance(value, tuple) and len(value) == 2 and
            isinstance(value[0], float) and 
            (isinstance(value[1], str) or isinstance(value[1], unicode))):
            # We got a value that is already a 2-tuple in the right format, so
            # simply return it
            pass
        elif value != '':
            # Otherwise assume it is a string and convert it to a 2-tuple
            tokens = value.split()
            if len(tokens) != 2:
                raise ValidationError('Invalid format for quantity.')
            try:
                value = (float(tokens[0]),str(tokens[1]))
            except ValueError:
                raise ValidationError('Invalid format for quantity.')
        return value
    
    def get_prep_value(self, value):
        """
        Convert the given `value` from its representation as a Python object
        to the corresponding representation in the database tables.
        """
        return u'{0} {1}'.format(*value)
    
    def formfield(self, **kwargs):
        """
        Specify the general form field to use to represent this model field
        on a ModelForm.
        """
        defaults = {'form_class': self.form_class}
        defaults.update(kwargs)
        return super(QuantityField, self).formfield(**defaults)

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
