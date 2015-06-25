from __future__ import unicode_literals

from django.template import Context, Template

from mailer import send_html_mail

import config


class EmailTemplateSender:
    default_language_code = config.EMAIL_DEFAULT_LANGUAGE_CODE
    default_context_data = {}
    default_from_email = config.EMAIL_DEFAULT_FROM_EMAIL
    default_priority = config.EMAIL_DEFAULT_PRIORITY
    default_auth_user = None
    default_auth_password = None
    default_headers = {}
    default_fail_silently = False
    default_message = ' '

    @classmethod
    def send_html_mail_from_email_template(cls, template_name, recipient_list, attachments=None,
                                           cached_template_obj=None, base_email_template=None, **kwargs):

        for attr_name in ('language_code', 'context_data', 'from_email', 'priority', 'fail_silently', 'auth_user',
                          'auth_password', 'headers', 'message'):
            kwargs[attr_name] = kwargs.get(attr_name, getattr(cls, 'default_%s' % attr_name))

        context = Context(kwargs['context_data'])
        email_template = cls.get_email_template_object(template_name, cached_template_obj)

        html_template = cls.before_render(email_template, kwargs['language_code'],
                                          base_email_template=base_email_template)
        html_message = Template(html_template).render(context).encode('utf-8')
        html_message = cls.after_render(html_message)

        kwargs['subject'] = getattr(email_template, 'subject_%s' % kwargs['language_code'])
        kwargs['message_html'] = html_message
        kwargs['recipient_list'] = recipient_list
        kwargs['attachments'] = attachments

        del kwargs['context_data']
        del kwargs['language_code']

        send_html_mail(**kwargs)
        return True

    @classmethod
    def before_render(cls, email_template, language_code, base_email_template=None):
        return getattr(email_template, 'html_body_%s' % language_code)

    @classmethod
    def after_render(cls, html):
        return html

    @classmethod
    def get_rendered_email_template(cls, language_code, template_name=None, template_obj=None, context_data={}):
        context = Context(context_data)
        email_template = cls.get_email_template_object(template_name, template_obj)
        html_template = getattr(email_template, 'html_body_%s' % language_code)
        return cls.after_render(Template(html_template).render(context).encode('utf-8'))

    @classmethod
    def get_email_template_object(cls, template_name=None, template_obj=None):
        model = config.get_email_template_model()
        if isinstance(template_obj, model):
            return template_obj
        else:
            return model.objects.get(slug=template_name)
