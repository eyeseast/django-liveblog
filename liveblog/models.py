import datetime

from django.db import models
from django.conf import settings
from django.contrib.sites.models import Site
from django.template import loader, Context
from django.template.defaultfilters import striptags, urlize
from markdown import markdown

Entry = models.get_model(*settings.BLOG_ENTRY_MODEL.split('.'))

site = Site.objects.get_current()

def default_entry():
    if Entry._default_manager.count():
        default_blog_entry = Entry._default_manager.all()[0].pk
    else:
        default_blog_entry = None
    return default_blog_entry


if (hasattr(settings, 'TWITTER_USERNAME') 
    and hasattr(settings, 'TWITTER_PASSWORD')
    and hasattr(settings, 'BITLY_API_KEY')
    and hasattr(settings, 'BITLY_LOGIN')):
    
    try:
        import twitter as twitter_api
        import bitly as bitly_api
        twitter = twitter_api.Api(username=settings.TWITTER_USERNAME, password=settings.TWITTER_PASSWORD)
        bitly = bitly_api.Api(login=settings.BITLY_LOGIN, apikey=settings.BITLY_API_KEY)
        CAN_TWEET = True
    except:
        CAN_TWEET = False
else:
    CAN_TWEET = False


class LiveBlogEntry(models.Model):
    timestamp = models.DateTimeField(default=datetime.datetime.now)
    tweet = models.BooleanField(default=CAN_TWEET, editable=CAN_TWEET)
    body = models.TextField()
    body_html = models.TextField(editable=False, blank=True)
    blog_entry = models.ForeignKey(Entry, related_name="updates", default=default_entry)


    class Meta:
        verbose_name_plural = "Live Blog Entries"
        ordering = ['-timestamp']


    def __unicode__(self):
        self.sample_size = 100 # Used only in admin.
        return '%s: %s %s' % (self.blog_entry.title, 
                              self.body[:self.sample_size],
                              '...' if len(self.body) > self.sample_size else '')


    def save(self, *args, **kwargs):
        self.body_html = markdown(urlize(self.body.strip()))
        if self.tweet:
            try:
                self.send_tweet()
                self.tweet = False
            except: # sometimes, twitter just doesn't work
                pass
        super(LiveBlogEntry, self).save()


    def get_absolute_url(self):
        return "%s#update%s" % (self.blog_entry.get_absolute_url(), self.id)
    
    
    def get_short_url(self):
        try:
            url = bitly.shorten("http://%s%s" % (site.domain, self.get_absolute_url()))
        except:
            url = None
        return url


    def send_tweet(self):
        url = self.get_short_url()
        if url:
            max_length = 139 - len(url) # leaving a space here
        else:
            max_length = 140
        
        text = striptags(self.body_html)[:max_length]
        if url:
            text = ' '.join([text, url])
        
        twitter.PostUpdate(text)