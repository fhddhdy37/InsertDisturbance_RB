"""
  from scenariogeneration

  scenariogeneration
  https://github.com/pyoscx/scenariogeneration

  This Source Code Form is subject to the terms of the Mozilla Public
  License, v. 2.0. If a copy of the MPL was not distributed with this
  file, You can obtain one at https://mozilla.org/MPL/2.0/.

  Copyright (c) 2022 The scenariogeneration Authors.

"""

import os
import subprocess

from scenariogeneration.xosc import Scenario

def esmini(
    generator,
    esminipath="esmini",
    window_size="60 60 800 400",
    save_osi=False,
    record=False,
    disable_controllers=False,
    args=[],
    generation_path="generated",
    resource_path=None,
    timestep=0.01,
    headless=False
):
    """write a scenario and runs it in esminis OpenDriveViewer with some random traffic

    Parameters
    ----------
        generator (OpenDrive, Scenario, or ScenarioGenerator): the xodr road to run

        esminipath (str): the path to esmini
            Default: esmini

        window_size (str): sets the window size of the esmini viewer
            Default: 60 60 800 400

        save_osi (str): name of the wanted osi file (None will not create a osi file)
            Default: None

        record (str): name of a esmini .dat file should be saved
            Default: '' (no recording)

        disable_controllers (bool): let esmini disable all controllers in the scenario and run with default behaviour
            Default: False

        args (list): additional options to esmini

        generation_path (str): path to where the files should be generated
            Default: generated

        resource_path (str): path to the catalogs/xodrs that you want to add (relative path in scenario should be relative to this one)
            Default: esminipath/resources/xosc

        timestep (float): fixed timestep to use in combination with replayer

        headless (boolean): run esmini in headless mode (no viewer)
    """
    additional_args = []
    # resource_path = os.path.join(esminipath,'resources')
    if not resource_path:
        resource_path = os.path.join(esminipath, "resources", "xosc")

    # genereate file for running in esmini, and set some esmini replated parameters
    if isinstance(generator, Scenario):
        if not os.path.exists(generation_path):
            os.mkdir(generation_path)
        if not os.path.exists(os.path.join(generation_path, "xosc")):
            os.mkdir(os.path.join(generation_path, "xosc"))
        if not os.path.exists(os.path.join(generation_path, "xodr")):
            os.mkdir(os.path.join(generation_path, "xodr"))
        executable = "esmini"
        filetype = "--osc"
        if not headless:
            additional_args += ["--window"] + window_size.split()

        filename = os.path.join(generation_path, "xosc", "python_scenario.xosc")
        generator.write_xml(filename)
    else:
        raise TypeError(
            "generator is not of type Scenario"
        )

    # create the additional_args for the esmini execusion
    if save_osi:
        additional_args += ["--osi_file", save_osi]

    if record:
        additional_args += ["--record", record]

    if disable_controllers:
        additional_args += ["--disable_controllers"]

    if timestep != None:
        additional_args += ["--fixed_timestep", str(timestep)]

    additional_args += args

    additional_args += ["--path", resource_path]

    # find executable based on OS
    if os.name == "posix":
        executable_path = os.path.join(".", esminipath, "bin", executable)
        replay_executable = os.path.join(".", esminipath, "bin", "replayer")
    elif os.name == "nt":
        executable_path = os.path.join(
            os.path.realpath(esminipath), "bin", executable + ".exe"
        )

    cmd_and_args = [executable_path] + [filetype] + [filename] + additional_args
    print("Executing: ", " ".join(cmd_and_args))
    result = subprocess.run(cmd_and_args)
    if result.returncode != 0:
        print("An error occurred while trying to execute the scenario")
        return