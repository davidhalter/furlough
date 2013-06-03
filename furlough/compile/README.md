# Customize Your Bootstrap
Any bootstrap customizations go in this directory, as described below.
Feel free to add additional less files, but make sure to include them 
at the bottom of bootstrap.less. Running `make` will generate bootstrap.css
and copy it into `assets/css/bootstrap.css`.

An added bonus of using this method is that you don't need to wait for the
entire bootstrap build process every time you make a small change to the less.

You need `npm` and `recess` installed for the Makefile to work. See the
official boostrap developer documentation for more information.

If you have watchr installed, you can just run `make watch` and make will
run automatically whenever any .less files are modified.

## Files => bootstrap.css
* bootstrap.less - the main less file that should include the others
* variables.less - for overriding bootstrap-defined variables or defining new ones
* font-awesome.less - styles for font-awesome icons
* custom.less - other site-wide styles

## Other files
* sticky-footer.less - optional sticky footer code. Not compiled into
bootstrap.css by default. See the comment at the top of the file.

