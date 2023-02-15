<!-- markdownlint-disable-file no-inline-html first-line-h1 -->
<div align="center">

# hatch-aws-publisher

[![PyPI - Version](https://img.shields.io/pypi/v/hatch-aws-publisher.svg)](https://pypi.org/project/hatch-aws-publisher) [![PyPI - Python Version](https://img.shields.io/pypi/pyversions/hatch-aws-publisher.svg)](https://pypi.org/project/hatch-aws-publisher) [![Hatch project](https://img.shields.io/badge/%F0%9F%A5%9A-Hatch-4051b5.svg)](https://github.com/pypa/hatch) [![code style - black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black) [![types - mypy](https://img.shields.io/badge/types-Mypy-blue.svg)](https://github.com/python/mypy) [![imports - isort](https://img.shields.io/badge/imports-isort-ef8336.svg)](https://github.com/pycqa/isort)

AWS publisher plugin for **[Hatch 🥚🐍](<https://hatch.pypa.io/latest/>)**. *Hatch is modern, extensible Python project manager.*

</div>

---

## Table of Contents

- [hatch-aws-publisher](#hatch-aws-publisher)
    - [Table of Contents](#table-of-contents)
    - [How to enable](#how-to-enable)
    - [How to use it](#how-to-use-it)
        - [Options](#options)
            - [section `tool.hatch.publish.aws`](#section-toolhatchpublishaws)
            - [section `tool.hatch.publish.aws.sam`](#section-toolhatchpublishawssam)
            - [section `tool.hatch.publish.aws.sam.env.<env-name>`](#section-toolhatchpublishawssamenvenv-name)
    - [License](#license)

## How to enable

Plugin must be installed in the same environment as `Hatch` itself.

```bash
python -m venv .venv
.venv/bin/pip install hatch-aws-publisher
```

## How to use it

The [publisher plugin](https://hatch.pypa.io/latest/plugins/publisher/reference) name is called `aws`.

1. Build you app with [SAM](https://aws.amazon.com/serverless/sam/). You can use my Hatch plugin [hatch-aws](https://github.com/aka-raccoon/hatch-aws).
2. Put your SAM config to `pyproject.toml` (stack name is by default name of your project):

   ```toml
   [project]
   name = "my-app"

   [tool.hatch.publish.aws.sam]
   region = "us-west-1"
   confirm_changeset = false
   fail_on_empty_changeset = false
   force_upload = true
   capabilities = "CAPABILITY_IAM"
   s3_bucket = "my-bucket"
   parameter_overrides = ["stage=dev"]

   [tool.hatch.publish.aws.sam.tags]
   job = "batman"
   name = "bruce"
   ```

3. Publish (deploy) your app.

   ```bash
   hatch publish -p aws
   ```

### Options

#### section `tool.hatch.publish.aws`

This section allows to modify behavior of the plugin. Available options:

```toml
[tool.hatch.publish.aws]
stack_name_append_env = true
stack_name_prefix = "super-"
stack_name_suffix = "-man"
deploy = true
```

All above options can be overwritten using a CLI parameter

```shell
.venv/hatch/bin/hatch publish -p aws -o stack_name_prefix="bat-"
```

- **stack_name_prefix**: adds a prefix to a stack name -> `bat-my-app`
- **stack_name_suffix**: adds a suffix to a stack name -> `bat-my-app-man`
- **stack_name_append_env**: adds a selected environment to a stack name -> `bat-my-app-man-dev`
- **deploy**: if it's `false`, only sam config will be generated, but `sam deploy` will not be executed

#### section `tool.hatch.publish.aws.sam`

Default values for SAM. You can use any key:value pair available in [SAM config](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-config.html).

Only difference is format of tags (they use separate section):

```toml
[tool.hatch.publish.aws.sam.tags]
job = "batman"
name = "bruce"
```

#### section `tool.hatch.publish.aws.sam.env.<env-name>`

You can define specific deployment environments. They inherit values from [tool.hatch.publish.aws.sam](#section-toolhatchpublishawssam).

Environment settings in `pyproject.toml`:

```toml
[tool.hatch.publish.aws.sam]
region = "us-west-1"
confirm_changeset = false
fail_on_empty_changeset = false
force_upload = true
capabilities = "CAPABILITY_IAM"

[tool.hatch.publish.aws.sam.env.dev]
region = "us-west-2"
s3_bucket = "dev-bucket"
parameter_overrides = ["stage=dev"]

[tool.hatch.publish.aws.sam.env.prd]
s3_bucket = "prd-bucket"
parameter_overrides = ["stage=prd"]
fail_on_empty_changeset = true
```

You need to specify an environment using a CLI parameter:

```bash
hatch publish -p aws -o env=dev
```

## License

Plugin `hatch-aws-publisher` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
