django-yubin
============

In our projects we use always two django packages for dealing with emails:
django-mailer2 (our own fork in APSL) and django-mailviews to compose the
emails.

django-mailer-2 by is a Chris Beaven fork from a fork of
James Tauber's django-mailer and is a reusable Django app for queuing the sending of email.

django-mailviews from Disqus, allows you to compose e-mails using templates in
the same way you compose your html templates, and allows you to preview the
e-mails.

As we use both packages our choice has been  create a new one which could deal
with both task: sending and composing e-mails instead of mantaining two diferent
branches. As you can see it seems django-mailer2 is not accepting patches, so in
order to put a new version on pypi a new name was mandatory.

So django-yubin is born (yubin is postal mail in japanese). The name attribution is for @morenosan.

If you want to run the test you'll need a test smtpd server, you can find one in

    ./bin/fake-server

run it in a different console and execute `runtests.py`

You can read the package documentation at http://django-yubin.readthedocs.org/en/latest/

History
-------

* 0.1.1       Updated documentation and unit tests.
* 0.1.2       Fixed Templates
* 0.1.3       Fixed Python3 compatibility, thanks Marc
* 0.1.4       Uptated README 

