import sys

from main import build_app, architecture_map, parse_arguments


# todo: There's got to be a less repetitive way to do this.


# Intended for use with gunicorn. You can start Hay Say on a gunicorn server with:
# gunicorn --workers 1 --bind 0.0.0.0:6573 'wsgi:get_server()'
# and pass various arguments directly to the method, like this:
# gunicorn --workers 1 --bind 0.0.0.0:6573 'wsgi:get_server(enable_model_management=True)'
# See the parse_arguments method.
def get_server(update_model_lists_on_startup=False, enable_model_management=False, enable_session_caches=False,
               cache_implementation='file', migrate_models=False, architectures=architecture_map.keys()):
    app = build_app(update_model_lists_on_startup, enable_model_management, enable_session_caches,
                    cache_implementation, migrate_models, architectures)
    return app.server


# Intended for use in a development environment only. You can start Hay Say with:
# python wsgi.py
# and pass various arguments via the command line, like this:
# python wsgi.py --enable_model_management.
# See the parse_arguments method.
if __name__ == '__main__':
    args = parse_arguments(sys.argv[1:])
    app = build_app(args.update_model_lists_on_startup, args.enable_model_management, args.enable_session_caches,
                    args.cache_implementation, args.migrate_models, args.architectures)
    app.run(host='0.0.0.0', port=6573, debug=True)
