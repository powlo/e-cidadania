# -*- coding: utf-8 -*-
#
# Copyright (c) 2010 Cidadanía Coop.
# Written by: Oscar Carballal Prego <info@oscarcp.com>
#
# This file is part of e-cidadania.
#
# e-cidadania is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# e-cidadania is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with e-cidadania. If not, see <http://www.gnu.org/licenses/>.

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.template import RequestContext

from django.views.generic.list_detail import object_list
from django.views.generic.list_detail import object_detail
from django.views.generic.create_update import create_object
from django.views.generic.create_update import update_object
from django.views.generic.create_update import delete_object

from e_cidadania.apps.proposals.models import Proposal
from e_cidadania.apps.proposals.forms import ProposalForm
from e_cidadania.apps.spaces.models import Space

@permission_required('proposals.add_proposal')
def add_proposal(request, space_name):

    """
    Create a new proposal.
    """
    prop_space = get_object_or_404(Space, url=space_name)
    
    proposal = Proposal()
    form = ProposalForm(request.POST or None, request.FILES or None, instance=proposal)

    if request.POST:
        form_uncommited = form.save(commit=False)
        form_uncommited.space = prop_space
        form_uncommited.support_votes = 0
        form_uncommited.author = request.user
        if form.is_valid():
            form_uncommited.save()
            return redirect('/spaces/' + space_name)

    return render_to_response('proposal/proposal_add.html',
                              {'form': form, 'get_place': prop_space},
                              context_instance = RequestContext(request))

def list_proposals(request, space_name):

    """
    List all the proposals.
    """
    current_space = get_object_or_404(Space, url=space_name)
    
    return object_list(request,
                       queryset = Proposal.objects.all().filter(space=current_space.id),
                       paginate_by = 50,
                       template_name = 'proposal/proposal_list.html',
                       template_object_name = 'proposal',
                       extra_context = {'get_place': current_space})

@permission_required('proposals.delete_proposal')
def delete_proposal(request, space_name, prop_id):

    """
    Delete a proposal.
    """
    current_space = get_object_or_404(Space, url=space_name)

    return delete_object(request,
                         model = Proposal,
                         object_id = prop_id,
                         login_required = True,
                         template_name = 'proposal/proposal_delete.html',
                         template_object_name = 'proposal',
                         post_delete_redirect = '/',
                         extra_context = {'get_place': current_space})

@permission_required('proposals.edit_proposal')
def edit_proposal(request, space_name, prop_id):

    """
    The proposal can be edited by space and global admins, but also by their
    creator.
    """
    current_space = get_object_or_404(Space, url=space_name)
    current_proposal = get_object_or_404(Proposal, id=prop_id)
    current_user = request.user.username
    
    can_edit = request.user.has_perm('Proposal.edit_proposal')
    
    allow_edit = 0
    
    if can_edit or current_user == current_proposal.author:
        return update_object(request,
                             model = Proposal,
                             object_id = prop_id,
                             login_required = True,
                             template_name = 'proposal/proposal_edit.html',
                             post_save_redirect = '../',
                             extra_context = {'get_place': current_space})
    
    pass

def view_proposal(request, space_name, prop_id):

    """
    View a proposal.
    """
    current_space = get_object_or_404(Space, url=space_name)
    
    return object_detail(request,
                         queryset = Proposal.objects.all().filter(space=current_space.id),
                         object_id = prop_id,
                         template_name = 'proposal/proposal_detail.html',
                         template_object_name = 'proposal',
                         extra_context = {'get_place': current_space})

