from django.shortcuts import render_to_response
from django.template import RequestContext

def index(request):
    """
    The RMG database homepage.
    """
    return render_to_response('database.html', context_instance=RequestContext(request))

