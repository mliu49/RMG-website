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

import math
import numpy
import re
import urllib

from django.core.urlresolvers import reverse

import rmgpy.constants as constants
from rmgpy.molecule.molecule import Molecule
from rmgpy.molecule.group import Group

################################################################################

def moleculeToURL(molecule):
    """
    Convert a given :class:`Molecule` object `molecule` to a string 
    representation of its structure suitable for a URL.
    """
    mol = molecule.copy(deep=True)
    mol.clearLabeledAtoms()
    adjlist = mol.toAdjacencyList(removeH=False)
    #url = urllib.quote(adjlist)
    return adjlist

def moleculeToInfo(molecule):
    """
    Creates an html rendering which includes molecule structure image but
    also allows you to click on it to enter a molecule info page.
    """

    from rmgweb.database.views import moleculeEntry
    href = reverse(moleculeEntry, kwargs={'adjlist': molecule.toAdjacencyList()})
    structureMarkup = getStructureMarkup(molecule)
    markup = '<a href="'+ href + '">' + structureMarkup + '</a>'
    return markup

def moleculeFromURL(adjlist):
    """
    Convert a given adjacency list `adjlist` from a URL to the corresponding
    :class:`Molecule` object.
    """
    adjlist = str(urllib.unquote(adjlist))
    molecule = Molecule().fromAdjacencyList(adjlist)
    return molecule

################################################################################

def groupToURL(group):
    """
    Convert a given :class:`Group` object `group` to a string 
    representation of its structure suitable for a URL.
    """
    gro = group.copy(deep=True)
    gro.clearLabeledAtoms()
    adjlist = gro.toAdjacencyList(removeH=False)
    url = urllib.quote(adjlist)
    return url

def groupToInfo(group):
    """
    Creates an html rendering which includes group structure image but
    also allows you to click on it to enter a group info page.
    """

    from rmgweb.database.views import groupEntry
    href = reverse(groupEntry, kwargs={'adjlist': group.toAdjacencyList()})
    structureMarkup = getStructureMarkup(group)
    markup = '<a href="'+ href + '">' + structureMarkup + '</a>'
    return markup

def groupFromURL(adjlist):
    """
    Convert a given adjacency list `adjlist` from a URL to the corresponding
    :class:`Group` object.
    """   
    adjlist = str(urllib.unquote(adjlist))
    group = Group().fromAdjacencyList(adjlist)
    return group

################################################################################

def getStructureInfo(object):
    """ 
    Convert either a Entry, Molecule, Species, or Group object to its html 
    markup containing a clickable image of the group or molecule that contains 
    a link to its information page.
    """
    from rmgpy.data.base import Entry
    from rmgpy.species import Species
    
    if isinstance(object, Entry):
        object = object.item
        
    if isinstance(object, Molecule):
        return moleculeToInfo(object)
    elif isinstance(object, Species):
        return moleculeToInfo(object.molecule[0])
    elif isinstance(object, Group):
        return groupToInfo(object)
    else:
        return ''
################################################################################

def getLaTeXScientificNotation(value):
    """
    Return a LaTeX-formatted string containing the provided `value` in
    scientific notation.
    """
    if value == 0: return '0'
    negative = value < 0
    value = abs(value)
    exp = int(math.log10(abs(value)))
    mant = value / 10**exp
    if abs(mant) < 1:
        mant *= 10; exp -= 1
    return '{0}{1:g} \\times 10^{{{2:d}}}'.format('-' if negative else '', mant, exp)

################################################################################

def getStructureMarkup(item):
    """
    Return the HTML used to markup structure information for the given `item`.
    For a :class:`Molecule`, the markup is an ``<img>`` tag so that we can
    draw the molecule. For a :class:`Group`, the markup is the
    adjacency list, wrapped in ``<pre>`` tags.
    """
    from rmgpy.molecule.molecule import Molecule
    from rmgpy.molecule.group import Group
    from rmgpy.species import Species
    import urllib
    
    if isinstance(item, Molecule):
        # We can draw Molecule objects, so use that instead of an adjacency list
        adjlist = item.toAdjacencyList(removeH=False)
        url = urllib.quote(adjlist)
        structure = '<img src="{0}" alt="{1}" title="{1}"/>'.format(reverse('rmgweb.main.views.drawMolecule', kwargs={'adjlist': url}), adjlist)
    elif isinstance(item, Species) and len(item.molecule) > 0:
        # We can draw Species objects, so use that instead of an adjacency list
        adjlist = item.molecule[0].toAdjacencyList(removeH=False)
        url = urllib.quote(adjlist)
        structure = '<img src="{0}" alt="{1}" title="{1}"/>'.format(reverse('rmgweb.main.views.drawMolecule', kwargs={'adjlist': url}), item.label)
    elif isinstance(item, Species) and len(item.molecule) == 0:
        # We can draw Species objects, so use that instead of an adjacency list
        structure = item.label
    elif isinstance(item, Group):
        # We can draw Group objects, so use that instead of an adjacency list
        adjlist = item.toAdjacencyList()
        url = urllib.quote(adjlist)
        structure = '<img src="{0}" alt="{1}" title="{1}" />'.format(reverse('rmgweb.main.views.drawGroup', kwargs={'adjlist': url}), adjlist)
        #structure += '<pre style="font-size:small;" class="adjacancy_list">{0}</pre>'.format(adjlist)
    elif isinstance(item, str) or isinstance(item, unicode):
        structure = item
    else:
        structure = ''
    return structure
