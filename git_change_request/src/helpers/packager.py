
from typing import ValuesView, TYPE_CHECKING, Any
import pkg_resources
import logging
import os
logger = logging.getLogger(__name__)
if TYPE_CHECKING:
    from ..apis import BaseRequest


def get_change_request_plugin_classes() -> ValuesView['BaseRequest']:
    """Return all plugin classes discovered
    :return: The list of change request plugin classes
    """
    change_request_plugin_dict = {}
    for entry_point in pkg_resources.iter_entry_points('git_cr_plugins'):
        change_request_plugin_dict[entry_point.name] = entry_point.load()
    return change_request_plugin_dict.values()


def get_change_request_plugin_class(name_or_url: str) -> 'BaseRequest':
    """
    Return the change request class based on the class name.
    :param name_or_url: the name of the change request class
    :return: the change request class
    """
    name = os.getenv('GIT_CR_PLUGIN_NAME', None)
    if not name:
        name = name_or_url

    for cr in get_change_request_plugin_classes():
        logger.debug(cr)
        prefix = get_plugin_prefix(cr.__name__)
        if prefix == name or \
                name.find(prefix) != -1:
            return cr


def get_plugin_prefix(plugin_name: str) -> str:
    """
    Return the change request class name string without the 'Request' portion.
    :param plugin_name: the name of the change request class
    :return: the string containing change request class implementation
    """
    for i in range(1, len(plugin_name)):
        if plugin_name[i].istitle():
            return plugin_name[:i].lower()
    return plugin_name.lower()
