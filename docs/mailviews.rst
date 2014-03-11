MailViews
=========

Introduction
------------

Rendering and sending emails in Django can quickly become repetitive and
error-prone. By encapsulating message rendering within view classes, you can
easily compose messages in a structured and clear manner.

The idea behind the method is identhical to the template class based view: you can select the template to use, in our
case one for the subject and one for the body (and one extra for the html), you can pass the data you need overriding
the `get_context_data` method and the message rendering is made in `render_to_message` where you can also customize
the parameters as sender, cc, cco, etc. or delay the decision to the `send` method.

Managing mails could become a crazy thing quite fast, so the idea is to be able to organize the mail templates in folders
and use the mailview classes to provide them with the data you need.

Using inheritance in templates, mixins and inheritance will give you again the control.


Sending your first e-mail
--------------------------

Let's suppose we want to send notificantion message to a mailing list. We don't have a customized email, but we want
to be able to render the e-mail

.. code:: python

    from django_yubin.messages import TemplatedEmailMessageView
    import datetime

    class NewsletterView(EmailMessageView):
        subject_template_name = 'emails/newsletter/subject.txt'
        body_template_name = 'emails/newsletter/body.txt'

        def get_context_data(self, **kwargs):
            """
            here we can get the addtional data we want
            """
            context = super(NewsletterView, self).get_context_data(**kwargs)
            context['day'] = datetime.date.today()
            return context

    # Instantiate and send a message.

    NewsletterView().send(to=('mynewsletter@example.com',) )

This would render and send a message to the newsletter with the DEFAULT_FROM_EMAIL` emails settings. Sometimes we'd like
to send it with different e-mail, so we can customize it as

.. code:: python

    NewsletterView().send(from_email='no-reply@example.com',
                          to=('mynewsletter@exemple.com', ))


Any keywords you pass in send will be forwarded to the django mail calss, so you can use the same parameters you have
in the Django `EmailMessage` class documentation:

* **from_email**: The sender’s address. Both fred@example.com and Fred <fred@example.com> forms are legal. If omitted, the DEFAULT_FROM_EMAIL setting is used.
* **to**: A list or tuple of recipient addresses.
* **bcc**: A list or tuple of addresses used in the “Bcc” header when sending the email.
* **cc**: A list or tuple of recipient addresses used in the “Cc” header when sending the email.

Instead of using `send` you can use `render_to_message` method. It's parameters are the same as the `send` method, but
instead of sending the e-mail it will return you an instance of `EmailMessage` that you can use to customize the
e-mail before sending it.

In our example, we could write:


.. code:: python

    from django_yubin.messages import TemplatedEmailMessageView
    import datetime

    class NewsletterView(EmailMessageView):
        subject_template_name = 'emails/newsletter/subject.txt'
        body_template_name = 'emails/newsletter/body.txt'

        def render_to_message(self, extra_context=None, **kwargs):
            kwargs['to'] = ('mynewsletter@example.com',)
            kwargs['from_email'] = 'no-reply@example.com'
            return super(NewsletterView, self).render_to_message(extra_context=None, **kwargs)

        def get_context_data(self, **kwargs):
            """
            here we can get the addtional data we want
            """
            context = super(NewsletterView, self).get_context_data(**kwargs)
            context['day'] = datetime.date.today()
            return context

    # Instantiate and send a message.

    NewsletterView().send()

Supose now that we wan't to send a second newsletter, the monthly one for exaple, then we could just write

.. code:: python

    from django_yubin.messages import TemplatedEmailMessageView
    import datetime

    class MonthlyNewsletterView(NewsletterView):
        subject_template_name = 'emails/newsletter/monthly_subject.txt'
        body_template_name = 'emails/newsletter/monthly_body.txt'

    MonthlyNewsletterView().send()

Sending HTML Emails
-------------------

In the previous example we have sent just text emails. If we want to send HTML email we need also an additional template
to render the HTML content. You just have to inherit your class from `TemplatedHTMLEmailMessageView` and write the
template you're going to use in `html_body_template_name`, so usually we'll have somethins



Sending mail to a user
----------------------

.. code:: python

    from django_yubin.messages import TemplatedEmailMessageView

    # Subclass the `TemplatedEmailMessageView`, adding the templates you want to render.
    class WelcomeMessageView(EmailMessageView):
        subject_template_name = 'emails/welcome/subject.txt'
        body_template_name = 'emails/welcome/body.txt'

    # Instantiate and send a message.
    message = WelcomeMessageView().send(extra_context={
        'user': user,
    }, to=(user.email,))

This isn't actually the best pattern for sending customized messages to a user

Try and avoid using the ``extra_context`` argument when sending emails.
Instead, create an ``TemplatedEmailMessageView`` subclass whose constructor accepts
as arguments all of the objects that you require to generate the context and
send the message. For example, the code shown in "Basic Usage" could written
instead as the following:

.. code:: python

    from django_yubin.messages import TemplatedEmailMessageView

    class WelcomeMessageView(EmailMessageView):
        subject_template_name = 'emails/welcome/subject.txt'
        body_template_name = 'emails/welcome/body.txt'

        def __init__(self, user, *args, **kwargs):
            super(WelcomeMessageView, self).__init__(*args, **kwargs)
            self.user = user

        def get_context_data(self, **kwargs):
            context = super(WelcomeMessageView, self).get_context_data(**kwargs)
            context['user'] = self.user
            return context

        def render_to_message(self, *args, **kwargs):
            assert 'to' not in kwargs  # this should only be sent to the user
            kwargs['to'] = (self.user.email,)
            return super(WelcomeMessageView, self).render_to_message(*args, **kwargs)

    # Instantiate and send a message.
    WelcomeMessageView(user).send()

In fact, you might find it helpful to encapsulate the above "message for a user"
pattern into a mixin or subclass that provides a standard abstraction for all
user-related emails.