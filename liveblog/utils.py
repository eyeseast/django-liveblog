from django.template import Context
from django.template.loader import get_template

def can_tweet():
    from django.conf import settings
    try:
        getattr(settings, 'TWITTER_USERNAME')
        getattr(settings, 'TWITTER_PASSWORD')
        getattr(settings, 'BITLY_API_KEY')
        getattr(settings, 'BITLY_LOGIN')):
    except AttributeError:
        return False
    
    try:
        import twitter as twitter_api
        import bitly as bitly_api
        twitter = twitter_api.Api(username=settings.TWITTER_USERNAME, password=settings.TWITTER_PASSWORD)
        bitly = bitly_api.Api(login=settings.BITLY_LOGIN, apikey=settings.BITLY_API_KEY)
    except:
        return False
        
    return True



def dump_updates(qs, outfile_name, template='liveblog/updates_dump.html'):
    """
    Dump updates out into some kind of file,
    either plain text or HTML. It's up to you
    to decide that in the template. This just
    gives you context and puts things in order.
    Everything gets dumpted out into a file you 
    name in the 'template' argument.
    
    Default ordering is chronological, by entry
    and then timestamp.
    """
    
    # first, let's put things in order
    # We assume here that your blog order defaults to
    # reverse chronological, so we reverse that
    
    updates = qs.order_by('-blog_entry', 'timestamp')
    outfile = open(outfile_name, 'wb')
    
    t = get_template(template)
    c = Context({'updates': updates})
    
    outfile.write(t.render(c).encode('utf-8'))
    outfile.close()