import asyncio
import json

import click

from nats.aio.errors import NatsError
from stan.aio.errors import StanError

from . import documentation, helpers, nats


@click.group()
def cli():
    """CLI command group."""
    pass


@cli.command()
@click.argument('subject', envvar='CLI_SUBJECT')
@click.argument('data', type=click.File())
@click.option('--timeout', envvar='CLI_REQUEST_TIMEOUT', type=int, default=5,
              show_default=True, help=documentation.TIMEOUT)
@click.option('--raw', type=bool, default=False, is_flag=True,
              help=documentation.RAW)
@click.option('--user', envvar='NATS_USER', help=documentation.NATS_USER)
@click.option('--password', envvar='NATS_PASSWORD',
              help=documentation.NATS_PASSWORD)
@click.option('--host', envvar='NATS_HOST', help=documentation.NATS_HOST)
@click.option('--servlist', envvar='NATS_SERVLIST', help=documentation.NATS_SERVLIST) #sg
@click.option('--port', envvar='NATS_PORT', type=int,
              default=4222, show_default=True, help=documentation.NATS_PORT)
@click.option('--verbose', type=bool, default=False, is_flag=True,
              show_default=True, help=documentation.VERBOSE)
def request(subject: str, data, timeout: int, raw: bool, **kwargs):
    """Send NATS request command."""
    helpers.is_verbose.set(kwargs.pop('verbose'))

    try:
        data = json.dumps(json.load(data))
    except json.JSONDecodeError:
        click.echo('Only JSON files are supported', err=True)
        return 1

    response = asyncio.run(nats.request(subject, data, timeout,
                                        options=kwargs))
    if not response:
        return 1

    if not raw:
        click.echo(helpers.colorize_json(response))
    else:
        click.echo(response)

    return 0


@cli.command()
@click.argument('subject', envvar='CLI_SUBJECT')
@click.option('--cluster', envvar='STAN_CLUSTER',
              help=documentation.STAN_CLUSTER)
@click.option('--pretty-json', envvar='CLI_ENABLE_JSON', type=bool,
              default=False, is_flag=True)
@click.option('--user', envvar='NATS_USER', help=documentation.NATS_USER)
@click.option('--password', envvar='NATS_PASSWORD',
              help=documentation.NATS_PASSWORD)
@click.option('--servlist', envvar='NATS_SERVLIST', help=documentation.NATS_SERVLIST) #sg
@click.option('--host', envvar='NATS_HOST', help=documentation.NATS_HOST)
@click.option('--port', envvar='NATS_PORT', type=int,
              default=4222, show_default=True, help=documentation.NATS_PORT)
@click.option('--append', type=bool, default=False, is_flag=True,
              help=documentation.APPEND)
@click.option('--verbose', type=bool, default=False, is_flag=True,
              show_default=True, help=documentation.VERBOSE)

def subscribe(subject: str, cluster: str, pretty_json: bool, **kwargs):
    """Subscribe to the specified STAN command."""
    helpers.is_verbose.set(kwargs.pop('verbose'))
    click.clear()

    state = False
    try:
        state = asyncio.run(nats.subscribe(subject,
                                           pretty_json,
                                           cluster=cluster,
                                           options=kwargs))
    except (asyncio.CancelledError, click.Abort, NatsError, StanError):
        state = True
    except Exception:
        state = False
    finally:
        return 0 if state else 1


@cli.command()
@click.argument('subject', envvar='CLI_SUBJECT')
@click.argument('data', type=click.File())
@click.option('--cluster', envvar='STAN_CLUSTER',
              help=documentation.STAN_CLUSTER)
@click.option('--user', envvar='NATS_USER', help=documentation.NATS_USER)
@click.option('--password', envvar='NATS_PASSWORD',
              help=documentation.NATS_PASSWORD)
@click.option('--servlist', envvar='NATS_SERVLIST', help=documentation.NATS_SERVLIST) #sg
@click.option('--host', envvar='NATS_HOST', help=documentation.NATS_HOST)
@click.option('--port', envvar='NATS_PORT', type=int,
              default=4222, show_default=True, help=documentation.NATS_PORT)
@click.option('--verbose', type=bool, default=False, is_flag=True,
              show_default=True, help=documentation.VERBOSE)
def publish(subject: str, cluster: str, data, **kwargs):
    """Publish the data to the subject in STAN."""
    helpers.is_verbose.set(kwargs.pop('verbose'))

    try:
        data = json.dumps(json.load(data))
    except json.JSONDecodeError:
        click.echo('Only JSON files are supported', err=True)
        return 1

    status = asyncio.run(nats.publish(subject, data,
                                      cluster=cluster,
                                      options=kwargs))

    if status:
        return 0
    else:
        return 1
