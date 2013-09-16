Furlough - a Furlough Tracker for NGOs
======================================

Developed originally for an NGO, this furlough tracker allows you to easily
overview your employees with their different capabilities. The problem for NGOs
is that they have furloughs every few years and that vacation resets at that
point (and starts fresh when the furlough is finished). This is much more
complicated than in a normal company.

This tools goal is mainly a good visual overview with an easy-to-use GUI.

.. image:: https://github.com/davidhalter/jedi/raw/master/example.png


Install
=======

To be discussed... (probably use gunicorn)

Caveats
=======

Knowing that the year doesn't have 365 days always, vacation days are still
calculated with that idea in mind. Calculating vacation without fixed ending
years is quite complicated, so it might happen that the vacation year has a 
different start due to leap years (which probably won't be a problem, since
furloughs are typically being used every 2-4 years).
