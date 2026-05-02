# Funkworks Vellum Attr Stream — File > Run Script entry point.
#
# Houdini's File > Run Script only accepts .cmd files. This .cmd is a
# one-line HScript dispatcher: it resolves its own folder via $arg0,
# then exec's the sibling vellum_attr_stream_setup.py with __file__
# set so that .py can resolve vellum_attr_stream.hda next to itself.
#
# Place this .cmd, vellum_attr_stream_setup.py, and
# vellum_attr_stream.hda in the same folder.

python -c "import os; p=os.path.join(os.path.dirname(os.path.abspath(r'$arg0')),'vellum_attr_stream_setup.py'); exec(compile(open(p).read(),p,'exec'),{'__name__':'__main__','__file__':p})"
