# =================================================================
#
# Authors: Tom Kralidis <tomkralidis@gmail.com>
#
# Copyright (c) 2021 Tom Kralidis
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation
# files (the "Software"), to deal in the Software without
# restriction, including without limitation the rights to use,
# copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following
# conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
#
# =================================================================

import logging
import sys

import click


def cli_option_verbosity(f):
    logging_options = ['ERROR', 'WARNING', 'INFO', 'DEBUG']

    def callback(ctx, param, value):
        if value is not None:
            logging.basicConfig(stream=sys.stdout,
                                level=getattr(logging, value))
        return True

    return click.option('--verbosity', '-v',
                        type=click.Choice(logging_options),
                        help='Verbosity',
                        callback=callback)(f)


cli_option_directory = click.option(
    '--directory', '-d', required=True,
    help='Directory  metadata records',
    type=click.Path(resolve_path=True, file_okay=False))


def cli_callbacks(f):
    f = cli_option_verbosity(f)
    return f
