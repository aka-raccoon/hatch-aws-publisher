from hatchling.plugin import hookimpl

from hatch_aws_publisher.publisher import SamPublisher


@hookimpl
def hatch_register_publisher():
    return SamPublisher
