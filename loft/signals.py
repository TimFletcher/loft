from django.contrib.sites.models import Site
from django.template.loader import render_to_string
from django.core.mail import mail_managers
from django.conf import settings
from akismet import Akismet

def comment_spam_check(sender, comment, request, **kwargs):
    
    """
    Check a comment to see if Akismet flags it as spam
    """
    
    ak = Akismet(
        key=settings.AKISMET_API_KEY,
        blog_url='http://%s/' % Site.objects.get(pk=settings.SITE_ID).domain
    )
    if ak.verify_key():
        data = {
        'user_ip': request.META.get('REMOTE_ADDR', '127.0.0.1'),
        'user_agent': request.META.get('HTTP_USER_AGENT', ''),
        'referrer': request.META.get('HTTP_REFERER', ''),
        'comment_type': 'comment',
        'comment_author': comment.user_name.encode('utf-8'),
        }
        if ak.comment_check(comment.comment.encode('utf-8'), data=data, build_data=True):
            comment.delete()


def comment_notifier(sender, comment, **kwargs):
    
    """
    Email admins when a new comment is posted
    """
    
    if comment.is_public:
        subject = "New comment by %s on %s" % (comment.user_name, Site.objects.get_current().domain)
        body = render_to_string(
            "comments/notification_email.txt", {
                'comment': comment
            }
        )
        mail_managers(subject, body, fail_silently=False, connection=None)