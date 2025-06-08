import os
import sys
import subprocess
import traceback
import shutil
from pathlib import Path
from datetime import datetime

import pandas as pd
from openai import OpenAIError
from scenariogeneration import xosc

from GD import esmini
from GD import config as cf
from GD.controller import GPTController, GeminiController
from GD.preprocessing import preprocessing

if __name__ == "__main__":
# experiment settings
    success_count = 0
    fail_count = 0
    success_flag = True
    err_msg = ""
    start_time = 0
    end_time = 0
    elapsed_time = 0
    video_path = ""
    rows = []
    columns = ["experiment count", "level", "index", "model", "prompting", "scenario file path", "log file path", "success", "generating time", "video path"]

    input_file = "your scenario file path"
    mode = "gemini"
    input_file = r"D:\TUK\25-1\BusinessAnalatics\InsertDisturbance_RB\src\esmini\straight_500m.xosc"
    mode = "gpt"
    model = "o4-mini"

    result_path = cf.LOG_DIR / "result.csv"
    ex_prompts = [("fs", ), ("cot", ), ("ltm", ), ("fs", "cot"), ("fs", "ltm")]
    ex_prompts = [("fs", "ltm")]
    ex_dir = cf.BASE_PATH / "experiment"
    ex_result_dir = ex_dir / "results"
    
# model setting start
    cf.INPUT_PATH = Path(input_file).resolve()
    cf.INPUT_DIR = cf.INPUT_PATH.parent

    disturbance_list = []
    test_path = ex_dir / "test"
    test_file_list = os.listdir(test_path)

    for file in test_file_list:
        with open(test_path / file, "r", encoding='utf-8') as f:
            sentences = f.readlines()
            disturbance_list.append(sentences)

    preprocessing()
    if mode == "gpt":
        controller = GPTController()
    elif mode == "gemini":
        controller = GeminiController()
    else:
        raise ValueError("mode is supported only \"gemini\" or \"gpt\"")
    
# model setting end

# experiment start
    for promptings in ex_prompts:
        log_dir_name = f"{cf.DATE}_{mode}_{"_".join(promptings)}"
        log_dir = cf.LOG_BASE / log_dir_name
        os.mkdir(log_dir)
        result_path = log_dir / "result.csv"
        rows = []

        for i in range(1, 4):
            for ii, file in enumerate(test_file_list, start=1):
                with open(test_path / file, "r", encoding='utf-8') as f:
                    sentences = f.readlines()
                for iii, sentence in enumerate(sentences, start=1):
                    row = {}
                    video_path = ""
                    log_path = ""

                    input_text = sentence
                    output_file = f"gen_{cf.DATE}_{model}_{"_".join(promptings)}_{i:02}_{ii:02}_{iii:02}.xosc"
                    cf.OUTPUT_PATH = cf.INPUT_DIR / output_file
                    controller.output_path = cf.OUTPUT_PATH
                    print(output_file, sentence)

                    try:
                        start_time = datetime.now()
                        controller.gen_disturbance(input_text, model, *promptings)
                        sce = xosc.ParseOpenScenario(controller.output_path)

                    except OpenAIError:
                        print(traceback.format_exc())
                        sys.exit()
                    except Exception as e:
                        end_time = datetime.now()
                        elapsed_time = end_time - start_time
                        elapsed_time = elapsed_time.total_seconds()
                        success_flag = False
                        err_msg = traceback.format_exc()
                    else:
                        end_time = datetime.now()
                        elapsed_time = end_time - start_time
                        elapsed_time = elapsed_time.total_seconds()
                        success_flag = True

                    if success_flag:
                        log_file = f"log_{cf.DATE}_{model}_{"_".join(promptings)}_{i:02}_{ii:02}_{iii:02}_{"success" if success_flag else "fail"}.txt"
                        log_path = log_dir / log_file
                        args = []
                        args += ["--logfile_path", str(log_path)]
                        args += ["--disable_stdout"]
                        args += ["--capture_screen"]
                        
                        try:
                            esmini(sce, cf.ESMINI_PATH, generation_path=cf.GENERATION_DIR, timestep=0.033, args=args)
                            print(f"Log file written to {log_path}")
                        except Exception as e:
                            success_flag = False
                            err_msg = traceback.format_exc()
                        else:
                            endline = ""
                            with open(log_path, "r", encoding="utf-8") as f:
                                endline = f.readlines()[-1]
                            if endline.__contains__("[error]"):
                                success_flag = False
                                log_file = f"log_{cf.DATE}_{model}_{"_".join(promptings)}_{i:02}_{ii:02}_{iii:02}_{"success" if success_flag else "fail"}.txt"
                                dst_log_path = log_dir / log_file
                                os.rename(log_path, dst_log_path)

                    if success_flag:
                        video_name = "".join(input_text.split()) + f"_{i:02}_{ii:02}_{iii:02}.mp4"
                        video_path = log_dir / video_name
                        cmd = f"ffmpeg -f image2 -framerate 120 -i screen_shot_%5d.tga -c:v libx264 -vf format=yuv420p -crf 20 {video_path}"
                        result = subprocess.run(cmd)

                        if result.returncode != 0:
                            print("An error occurred while trying to save the video")
                        for f in Path(".").glob("screen_shot_*.tga"):
                            f.unlink()

                    if not success_flag:
                        log_file = f"log_{cf.DATE}_{model}_{"_".join(promptings)}_{i:02}_{ii:02}_{iii:02}_{"success" if success_flag else "fail"}.txt"
                        log_path = log_dir / log_file
                        with open(log_path, "w", encoding='utf-8') as f:
                            f.write(err_msg)
                            print(f"Log file written to {log_path}")

                    sv_scenario_file_path = str(cf.OUTPUT_PATH.relative_to(cf.BASE_PATH))
                    sv_log_file_path = str(log_path.relative_to(cf.BASE_PATH)) if isinstance(log_path, Path) else ""
                    sv_video_path = str(video_path.relative_to(cf.BASE_PATH)) if isinstance(video_path, Path) else ""

                    row = {
                        "experiment count": i,
                        "level": ii,
                        "index": iii,
                        "model": model,
                        "prompting": "_".join(promptings),
                        "scenario file path": sv_scenario_file_path,
                        "log file path": sv_log_file_path,
                        "success": success_flag,
                        "generating time": elapsed_time,
                        "video path": sv_video_path
                    }
                    rows.append(row)
                    df = pd.DataFrame(rows, columns=columns)
                    df.to_csv(result_path, encoding="utf-8")
        print(f"Result file written to {result_path}")
        shutil.copy(result_path, ex_result_dir / f"{log_dir_name}.csv")