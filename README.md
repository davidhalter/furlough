django-skel
===========

A modern Django (1.4) project skeleton. (Now with Bootstrap 2.2.2)

![A fancy Django project skeleton](https://github.com/rdegges/django-skel/raw/master/docs/source/_static/skel.jpg)


Meta
====

* author: Randall Degges
* email:  rdegges@gmail.com
* status: maintained, in development
* notes:  Have feedback? Please send me an email. This project is still in its
          infancy, and will be changing rapidly.
* random guy who added teh bootstraps: Justin McManus


Purpose
=======

For background, see: http://rdegges.com/deploying-django

Essentially--deploying Django projects is hard. There are lots of things you
need to take into consideration. Being a Django user for years, I believe I've
found some extremely useful patterns to help manage all sorts of Django sites
(from the very smallest apps, to the largest).

This project is meant to be a boilerplate project for starting development. It
is heavily opinionated in terms of services and tools--but I think the tradeoff
is worthwhile.


Docs
====

The full project documentation is hosted at RTFD: http://django-skel.rtfd.org/.
They are continuously updated to reflect changes and information about the
project, so be sure to read them before using this boilerplate.


Install
=======

django-skel currently supports Django 1.4. To create a new django-skel base
project, run the following command (this assumes you have Django 1.4 installed
already):

    $ django-admin.py startproject --template=https://github.com/rdegges/django-skel/zipball/master woot
    $ heroku config:add DJANGO_SETTINGS_MODULE=myproject.settings.prod


Where ``woot`` is the name of the project you'd like to create.

This is possible because Django 1.4's ``startproject`` command allows you to
fetch a project template over HTTP (which is what we're doing here).

While not strictly required, it is also recommended to do

     $ heroku config:add SECRET_KEY=putsomethingfairlycomplexhere

The production settings pull SECRET_KEY from environment but fallbacks
to a value which is generated mainly for development environment.

This setup allows you to easily keep your site in a public repo if you so 
wish without causing opening a route to attack your Django passwords.


Bootstrap
=========

The bootstrap sources are included in the `compile` directory. The 
README in that directory contains additional information on how to 
customize bootstrap to suit your needs. If you want to develop using less,
its a good idea to organize your files there, add a rule to the Makefile
to build and copy them to the `assets` directory, and run `make watch` to
recompile them automatically when modified.

If you'd rather just use the unmodified bootstrap css, a pre-built version
is included at `assets/css/boostrap.css`. An example bootstrap template is
included in `templates/base.html`. The bootstrap javascript sources are
in `assets/js/boostrap/`.

[django-crispy-forms](http://django-crispy-forms.readthedocs.org/en/latest/)
is included to help you add Bootstrap styling to your forms in a very DRY
manner.


Additional Tips for New Django Users
====================================

The [django-extensions](http://packages.python.org/django-extensions/) libarary
is also included in the dev requirements. Particularly useful is the runserver_plus
command extension. Run `python manage.py runserver_plus` instead of the usual
`runserver`, and upon hitting an exception you'll get the Werkzeug traceback
page instead of Django's default error page. This gives you the option to, for
any point in the stack trace, access an interactive debugging console, with
the ability to execute arbitrary code, inspect variables in the current scope, etc.
It's not a full debugger -- you can't step through code -- but sometimes it's
all you need.

Need a debugger? Try `ipdb`. It's like the stock `pdb` module, but includes the
IPython shell and all of the [magic](http://ipython.org/ipython-doc/dev/interactive/tutorial.html)
that entails. Just `pip install ipdb` to install it. Usage is the same as with pdb --
just place the following code wherever you want your breakpoint:

    import ipdb
    ipdb.set_trace()


