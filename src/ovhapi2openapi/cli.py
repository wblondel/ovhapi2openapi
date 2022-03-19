import importlib.resources as pkg_resources
from typing import Any, Tuple, Optional

import click
import yaml
from requests_cache import CachedSession

from ovhapi2openapi import data

OVH_SERVERS = yaml.safe_load(pkg_resources.read_text(data, "servers.yaml"))


def _arg_process_apis(ctx: click.Context, param: click.Parameter, value: str) -> Any:
    assert type(value) == str

    return _arg_split(ctx, param, value)


def _arg_split(ctx: click.Context, param: click.Parameter, value: str) -> list:
    assert type(value) == str
    return [v.strip() for v in value.split(",")]


def _check_requested_apis(
    available_apis_paths: list[str], requested_apis: list[str]
) -> Tuple[bool, Optional[str]]:
    for requested_api in requested_apis:
        if requested_api not in available_apis_paths:
            return False, requested_api

    return True, None


@click.command()
@click.option(
    "-s",
    "--server",
    "req_server",
    required=True,
    type=click.Choice(OVH_SERVERS, case_sensitive=False),
    help="The server from which to get the APIs",
)
@click.option(
    "-a",
    "--apis",
    "req_apis",
    default="*",
    show_default=True,
    required=True,
    type=click.STRING,
    help="The APIs that you want the specification to be converted.",
    callback=_arg_process_apis,
)
@click.option(
    "-o",
    "--output-file",
    required=True,
    type=click.Path(
        exists=False,
        file_okay=True,
        dir_okay=False,
        writable=True,
        resolve_path=True,
        path_type=None,
    ),
    help="The file to which the converted API specification should be saved",
)
@click.option(
    "-f",
    "--output-format",
    required=True,
    type=click.Choice(["swagger2", "openapi3"], case_sensitive=False),
    default="openapi3",
    show_default=True,
    help=(
        "The API description format to which the OVH API description should be"
        " converted."
    ),
)
@click.version_option(prog_name="ovhapi2openapi")
def main(
    req_server: str, req_apis: list[str], output_format: str, output_file: str
) -> None:
    server: dict = OVH_SERVERS[req_server]

    print("[DEBUG] Initializing requests cache...")
    s = CachedSession(cache_name="ovh-cache", backend="sqlite", use_cache_dir=True)
    print(f"[DEBUG] Cache created in {s.cache.db_path}")  # type: ignore[attr-defined]

    server_url = f"{server['url']}/1.0/"
    print(f"Getting available APIs from server {server['name']} ({server_url})")
    tmp_available_apis = s.get(server_url)
    tmp_available_apis = tmp_available_apis.json()["apis"]

    # convert list into dict
    available_apis = {}
    for item in tmp_available_apis:
        available_apis[item["path"][1:]] = {
            "schema": item["schema"],
            "format": item["format"],
            "description": item["description"],
        }

    available_apis_paths = list(available_apis)

    # If the wildcard is used, replace it with all available API paths
    if "*" in req_apis:
        req_apis = available_apis_paths
    else:
        r, e = _check_requested_apis(available_apis_paths, req_apis)
        if not r:
            raise click.BadOptionUsage(
                "apis",
                f"{e} is not a valid API on server {server_url}.\n"
                f"Available APIs: {', '.join(available_apis_paths)}",
            )
    print(f"{', '.join(req_apis)} is/are valid API.")

    for requested_api in req_apis:
        requested_api_url = f"{server_url}{requested_api}"

        requested_api_schema_url = available_apis[requested_api]["schema"].format(
            path=requested_api_url, format="json"
        )
        print(f"[DEBUG] Getting routes from API {requested_api} ({requested_api_url})")

        resp = s.get(requested_api_schema_url)
        resp.raise_for_status()
        requested_api_schema = resp.json()
        print(requested_api_schema)

    print(f"Converting to {output_format} (type {type(output_format)})")
    print(f"Saving to {output_file} (type {type(output_file)})")
