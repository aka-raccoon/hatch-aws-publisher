from pathlib import Path
from subprocess import PIPE, Popen  # nosec
from typing import Any, Optional

import tomli_w
from hatch.publish.plugin.interface import PublisherInterface
from hatchling.metadata.core import ProjectMetadata
from hatchling.plugin.manager import PluginManager


class SamPublisher(PublisherInterface):
    PLUGIN_NAME = "aws"

    def execute(self, cmd):
        with Popen(cmd, stdout=PIPE, universal_newlines=True) as popen:  # nosec
            if popen.stdout:
                for line in iter(popen.stdout.readline, ""):
                    self.app.display_info(line)
                popen.stdout.close()
            error = popen.wait()
            if error:
                self.app.display_error("Failure!")
                self.app.abort()

    def merge_sam_config(self, env: Optional[str]):
        metadata = ProjectMetadata(self.root, PluginManager())
        default = {"stack_name": metadata.name}
        basic = self.project_config.get("sam", {})
        env_specific = basic.pop("env", {})
        return default | basic | env_specific.get(env, {})

    def merge_plugin_config(self, options: dict):
        return self.project_config | options

    def publish(self, artifacts: list, options: dict):
        project_config = self.project_config | options
        env = project_config.get("env")
        deploy = project_config.get("deploy", True)
        if isinstance(deploy, str):
            deploy = deploy.lower() == "true"
        deploy_section: dict[str, Any] = self.merge_sam_config(env=env)
        if prefix := project_config.get("stack_name_prefix"):
            deploy_section["stack_name"] = f"{prefix}{deploy_section['stack_name']}"
        if suffix := project_config.get("stack_name_suffix"):
            deploy_section["stack_name"] = f"{deploy_section['stack_name']}{suffix}"
        if project_config.get("stack_name_append_env", False) and env:
            deploy_section["stack_name"] = f"{deploy_section['stack_name']}-{env}"

        if "s3_prefix" not in deploy_section:
            deploy_section["s3_prefix"] = deploy_section["stack_name"]

        tags = [f"{tag}={value}" for tag, value in deploy_section.get("tags", {}).items()]
        if tags:
            deploy_section["tags"] = tags
        sam_config_file: Path = self.root / "samconfig.toml"
        global_section = {}

        if "stack_name" in deploy_section:
            global_section["stack_name"] = deploy_section.pop("stack_name")
        if "region" in deploy_section:
            global_section["region"] = deploy_section.pop("region")

        sam_config = {
            "version": 0.1,
            "default": {
                "global": {"parameters": global_section},
                "deploy": {"parameters": deploy_section},
            },
        }
        sam_config_file.write_text(tomli_w.dumps(sam_config))
        self.app.display_info(f'Stack name: {global_section["stack_name"]}')
        if deploy:
            self.execute(["sam", "deploy"])
