import dataclasses
import json
import logging
import os
import subprocess
from multiprocessing import Pool, cpu_count
from pathlib import Path
from typing import Any, Dict, List, cast

from uron._source import get_basic_logging_info
from uron.config import UronConfig

logger = logging.getLogger(__name__)


@dataclasses.dataclass
class UronInput:
    name: str
    version: str
    script_path: Path


class Uron(object):

    interpreter: str = "python"
    requirements_file: Path
    target_pkg: str
    pkg_versions: List[str]
    output: str = "./result.json"

    config: UronConfig = UronConfig()

    def __init__(
        self,
        interpreter: str,
        requirements_file: str,
        target_pkg: str,
        pkg_versions: List[str],
        output: str = "result.json",
    ):
        self.interpreter = interpreter
        requirements_file_path = Path(requirements_file).absolute()
        self.requirements_file = requirements_file_path
        self.target_pkg = target_pkg
        self.pkg_versions = pkg_versions
        self.output = output

    def execute(self, script_path: str | Path) -> List[Dict[Any, Any]]:
        script_path = (
            Path(script_path) if isinstance(script_path, str) else script_path
        )
        results = []
        with Pool(cpu_count()) as p:
            r = p.map(
                self._run,
                [
                    UronInput(
                        name=self.target_pkg, version=v, script_path=script_path
                    )
                    for v in self.pkg_versions
                ],
            )
            results.append(cast(Dict[Any, Any], r))

        return results

    def _run(self, uron_input: UronInput) -> Dict[Any, Any]:

        pkg_root_folder = (
            Path(self.config.default_cache_folder) / uron_input.name
        )
        os.makedirs(pkg_root_folder, exist_ok=True)
        logger.debug(
            f"Created folder {pkg_root_folder.absolute()}",
            extra=get_basic_logging_info("DEBUG"),
        )

        pkg_versioned_folder = pkg_root_folder / uron_input.version
        os.makedirs(pkg_versioned_folder, exist_ok=True)
        logger.debug(
            f"Created folder {pkg_versioned_folder.absolute()}",
            extra=get_basic_logging_info("DEBUG"),
        )

        with open(pkg_versioned_folder / "script.sh", "+w") as f:
            f.write(
                f"""#!/bin/bash

echo $PKG_NAME
echo $PKG_VERSION

{self.interpreter} -m venv {pkg_versioned_folder} && \
chmod u+x {pkg_versioned_folder}/bin/activate && \
{pkg_versioned_folder}/bin/activate && \
{pkg_versioned_folder}/bin/python -m pip install --upgrade pip && \
{pkg_versioned_folder}/bin/python -m pip install -r {self.requirements_file} && \
{pkg_versioned_folder}/bin/python -m pip install {uron_input.name}=={uron_input.version} && \
{pkg_versioned_folder}/bin/python {uron_input.script_path.absolute()}
                """
            )
        logger.debug(
            f"Generated bash script {pkg_versioned_folder.absolute()}/script.sh",
            extra=get_basic_logging_info("DEBUG"),
        )

        subprocess.run(
            ["chmod u+x ./script.sh && /bin/bash -c ./script.sh"],
            cwd=pkg_versioned_folder.absolute(),
            text=True,
            stdout=subprocess.PIPE,
            shell=True,
        )

        result_path = Path(pkg_versioned_folder / self.output).absolute()

        logger.debug(
            f"Cached result to {result_path.absolute()}",
            extra=get_basic_logging_info("DEBUG"),
        )

        result = json.load(open(result_path))
        return cast(Dict[Any, Any], result)
