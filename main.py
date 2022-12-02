from utils.FileLoader import FileLoader
from utils.driver import run
import argparse
import sys
import os


def run_file(input_file, output_file):
    with open(output_file, "w") as file:
        sys.stdout = file
        loader = FileLoader(input_file)
        case_id = 1
        while loader.has_next() is not None:
            print("Test" + str(case_id) + "Result")
            run(loader.next_case())
            case_id = case_id + 1

def runf(input, output):
    run_file(input, output)


def rund(input, output):
    files = os.listdir(input)

    try:
        os.mkdir(output)
    except Exception as e:
        print("Directory has existed, ignore")

    for file in files:
        if file.endswith(".txt") == True:
            input_file = os.path.join(input, file)
            output_file = os.path.join(output, file)
            run_file(input_file, output_file)


if __name__ == "__main__":
    parser = argparse.ArgumentParser("RepCRec")
    parser.add_argument("mode", type=str, help="program mode (f/d)")
    parser.add_argument("-input", type=str, help="input source")
    parser.add_argument("-output", type=str, help="output source")
    args = parser.parse_args()

    mode = args.mode
    input_src = args.input
    output_src = args.output
    rundict = {
        "f": runf(input_src, output_src),
        "d": rund(input_src, output_src)
    }

    fun = rundict.get(mode)
    fun()


