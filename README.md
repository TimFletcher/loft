## Installation

Loft is a well featured single app Django blog designed to be quickly added into any Django project. http://timothyfletcher.com is running on Loft

To install, do the following:

* Add `loft` to your `INSTALLED_APPS`
* Add `(r'^loft/', include('loft.urls'))` to your `urlpatterns`
* Run `./manage.py syncdb` to create the database tables

You'll also need to create the following templates:

* loft/entry_archive_month.html
* loft/entry_archive_year.html
* loft/entry_archive.html
* loft/entry_detail.html
* loft/entry_list.html
* comments/notification_email.txt

## Features

Loft is under active development. All bugs and feature requests are managed through Github's issue tracker. The addition of feature requests is encouraged.

* Actions for bulk publishing and comment enabling/disabling
* Choices of markup (Textile/Markdown)
* Yearly and monthly archives
* RSS and Atom feeds
* Uses standard Django commenting with signals for email notifications and comment spam filtering via Akismet
* SEO features
    * Customisable slugs
    * Customisable title tags
    * Meta keywords
    * Meta description
    * Generic meta tags