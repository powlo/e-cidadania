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

from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django.contrib.auth.decorators import login_required, permission_required
from django.views.generic.create_update import update_object
from django.views.generic.create_update import delete_object
from django.views.generic.list_detail import object_detail
from django.contrib.syndication.views import Feed
from django.utils.translation import ugettext_lazy as _
from django.views.generic.list import ListView
from django.contrib import messages

from e_cidadania.apps.news.models import Post
from e_cidadania.apps.news.forms import NewsForm
from e_cidadania.apps.spaces.models import Space
from e_cidadania.apps.staticpages.models import StaticPage
from e_cidadania import settings

def index_view(request):

    """
    Main view for the index page. It's separated from the urls.py file
    because using directo_to_template in urls.py doesn't refresh the content
    (it's loaded only once).
    """
    pub = Post.objects.filter(pub_index=True).order_by('-pub_date')
    space_list = Space.objects.all()
    recent_spaces = Space.objects.all().order_by('-date')[:5]
    page_list = StaticPage.objects.filter(show_footer=True).order_by('-order')

    extra_context = {
        'publication': pub,
        'spaces': space_list,
        'recent_spaces': recent_spaces,
        'page': page_list,
        'version': settings.__version__,
        'status': settings.__status__,
        'debug_mode': settings.DEBUG,
    }

    if request.user.is_anonymous():
        messages.info(request, _("Hi! It seems that it's your first time here. \
                                 Maybe you want to <a href=\"/accounts/register\">register</a> \
                                 or <a href=\"/accounts/login\">login</a> if you have an account."))
    return render_to_response('site_index.html',
                              extra_context,
                              context_instance=RequestContext(request))

class IndexEntriesFeed(Feed):

    """
    Creates an RSS feed out of the news posts in the index page.

    :rtype: RSS Feed
    :context: None

    .. versionadded:: 0.1b
    """
    title = _('e-cidadania news')
    link = '/news/'
    description = _('Updates on the main e-cidadania site.')

    def items(self):
        return Post.objects.all().order_by('-pub_date')[:10]

    def item_title(self, item):
        return item.post_title

    def item_description(self, item):
        return item.post_message

###############
# BIG WARNING #
###############

# The following code violates the DRY principle. Repeating exactly the same
# code as in apps/news/views.py

@permission_required('news.add_post')
def add_news(request):

    """
    This is a DRY violation. This is a reimplementation of the news view
    located at apps.news.views
    """
    form = NewsForm(request.POST or None)

    if request.method == 'POST':
        form_uncommited = form.save(commit=False)
        form_uncommited.author = request.user
        form_uncommited.pub_index = True

        if form.is_valid():
            form_uncommited.save()
            messages.success(request, _('Post added successfully.'))
            return redirect('/')

    return render_to_response('news/post_add.html',
                              {'form': form},
                              context_instance=RequestContext(request))

@permission_required('news.delete_post')
def delete_post(request, post_id):

    """
    Delete an existent post. Post deletion is only reserved to spaces
    administrators or site admins.
    """

    return delete_object(request,
                         model = Post,
                         object_id = post_id,
                         login_required=True,
                         template_name = 'news/post_confirm_delete.html',
                         post_delete_redirect = '/',
                         extra_context = {'messages': messages.success(request, _('Post deleted successfully.'))})

@permission_required('news.edit_post')
def edit_post(request, post_id):

    """
    Edit an existent post.
    """

    return update_object(request,
                         model = Post,
                         object_id = post_id,
                         login_required = True,
                         post_save_redirect = '/',
                         template_name = 'news/post_edit.html',
                         extra_context = {'messages': messages.success(request, _('Post edited successfully.'))})

def view_post(request, post_id):

    """
    View a post with comments.
    """

    return object_detail(request,
                         queryset = Post.objects.all(),
                         object_id = post_id,
                         template_name = 'news/post_detail.html',
                         template_object_name = 'news')

class ListNews(ListView):

    """
    List all the news within a space.
    """
    paginate_by = 10
    template_name = 'news/news_list.html'

    def get_queryset(self):
        news = Post.objects.all().filter(pub_index = True)

        return news

