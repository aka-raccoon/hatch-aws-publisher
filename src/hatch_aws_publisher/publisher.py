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
        sam_config: dict[str, Any] = self.merge_sam_config(env=env)
        if prefix := project_config.get("stack_name_prefix"):
            sam_config["stack_name"] = f"{prefix}{sam_config['stack_name']}"
        if suffix := project_config.get("stack_name_suffix"):
            sam_config["stack_name"] = f"{sam_config['stack_name']}{suffix}"
        if project_config.get("stack_name_append_env", False) and env:
            sam_config["stack_name"] = f"{sam_config['stack_name']}-{env}"

        if not "s3_prefix" in sam_config:
            sam_config["s3_prefix"] = sam_config["stack_name"]

        tags = [f"{tag}={value}" for tag, value in sam_config.get("tags", {}).items()]
        if tags:
            sam_config["tags"] = tags
        sam_config_file: Path = self.root / "samconfig.toml"
        sam_config = {"version": 0.1, "default": {"deploy": {"parameters": sam_config}}}
        sam_config_file.write_text(tomli_w.dumps(sam_config))
        self.app.display(f'Stack name: {sam_config["stack_name"]}')
        if deploy:
            self.execute(["sam", "deploy"])
