import os
import re
import logging
import subprocess
import pty
import sys
import difflib
from pathlib import Path


logger = logging.getLogger()


class Colors:
    WHITE = '\033[1;37m'
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    LIGHT_GREEN = '\033[1;32m'
    LIGHT_BLUE = '\033[1;36m'
    PURPLE = '\033[0;35m'
    LIGHT_PURPLE = '\033[1;35m'
    YELLOW = '\033[0;33m'
    LIGHT_RED = '\033[1;31m'
    NC = '\033[0m'  # No Color



DEFAULT_COMPILE_FLAGS = ["-Wall", "-Wextra", "-Werror"]
IGNORED_EXERCISE_HEADER = f"{Colors.YELLOW}" \
        "═════════════════════════════════ Ex## Ignored ═════════════════════════════════" \
        f"{Colors.NC}"

EXERCISE_HEADER= f"{Colors.LIGHT_BLUE}" \
        "═════════════════════════════════ Testing Ex## ═════════════════════════════════" \
        f"{Colors.NC}"


TEST_PASSED = f"\n{Colors.LIGHT_GREEN}" \
        "══════════════════════════════    #### passed!    ══════════════════════════════" \
        f"{Colors.NC}"


TEST_FAILED = f"\n{Colors.LIGHT_RED}" \
        "══════════════════════════════    #### failed!    ══════════════════════════════" \
        f"{Colors.NC}"

def show_banner():
    message = f"Welcome to {Colors.LIGHT_PURPLE}Francinette{Colors.LIGHT_BLUE}, a 42 tester framework!"
    print(f"{Colors.LIGHT_BLUE}")
    print(f"╔══════════════════════════════════════════════════════════════════════════════╗")
    print(f"║                {message}                ║")
    print(f"╚══════════════════════════════════════════════════════════════════════════════╝")
    print(f"{Colors.NC}")


class CommonTester:

    def __init__(self, options):
        self.compile = []
        self.norm_ignore = []
        self.compile_flags = []
        self.base = options["base"]
        self.project = options["project"]
        self.selected_test = options["exercise"]

        self.available_tests = [test for test in dir(self) if re.match(r"ex\d{2}", test)]
        logger.info("tests found: %s", self.available_tests)

        show_banner()

        test_status = {}
        for test in self.available_tests:
            test_ok = self.execute_test(test)
            test_status[test] = test_ok
            if test_ok:
                print(TEST_PASSED.replace("####", test.title()))
            else:
                print(TEST_FAILED.replace("####", test.title()))

            print("\n")
            self.clean_up(test)

        self.print_summary(test_status)


    def print_summary(self, test_status):
        ok_tests = [test for test, st in test_status.items() if st is True]

        print(f"{Colors.LIGHT_GREEN}Passed tests: {' '.join(ok_tests)}{Colors.NC}")
        failed_tests = [test for test, st in test_status.items() if st is False]
        if failed_tests:
            print(f"{Colors.LIGHT_RED}Failed tests: {' '.join(failed_tests)}{Colors.NC}")


    def pass_norminette(self, test):
        norm_files = [file for file in self.compile if file not in self.norm_ignore]

        os.chdir(os.path.join(self.base, "temp", self.project, test))
        logger.info(f"On directory { os.getcwd() }")
        logger.info(f"Executing norminette on files: {norm_files}")
        norm_exec = ["norminette", "-R", "CheckForbiddenSourceHeader"] + norm_files

        result = subprocess.run(norm_exec, capture_output=True, text=True)

        print(f"Executing: {Colors.WHITE}{' '.join(norm_exec)}{Colors.NC}:")
        if result.returncode == 0:
            print(f"{Colors.GREEN}{result.stdout}{Colors.NC}")
        else:
            print(f"{Colors.YELLOW}{result.stdout}{Colors.NC}")

        return result.returncode == 0


    def compile_files(self):
        files = self.compile
        flags = self.compile_flags if self.compile_flags else DEFAULT_COMPILE_FLAGS

        logger.info(f"compiling files: {self.compile} with flags: {flags}")
        #result = os.system(f"gcc { " ".join(flags) } { " ".join(files) }")
        gcc_exec = ["gcc"] + flags + self.compile

        print(f"Executing: {Colors.WHITE}{' '.join(gcc_exec)}{Colors.NC}:")
        p = subprocess.Popen(gcc_exec);
        p.wait()

        if p.returncode == 0:
            print(f"{Colors.GREEN}gcc: OK!{Colors.NC}")
        else:
            print(f"{Colors.LIGHT_RED}Problem compiling files{Colors.NC}")

        return p.returncode


    def execute_program(self):
        logger.info(f"Running the output of the compilation: ")
        #result = os.system(f"gcc { " ".join(flags) } { " ".join(files) }")
        logger.info(f"On directory { os.getcwd() }")
        main_exec = ["./a.out"]

        print(f"\nExecuting: {Colors.WHITE}{' '.join(main_exec)}{Colors.NC}:")
        result = subprocess.run(main_exec, capture_output=True, text=True)

        if result.returncode == 0:
            logger.info("Executed program successfully main")
            print(result.stdout)
        else:
            print(f"{Colors.LIGHT_RED}{result.stderr}{Colors.NC}")

        return result.stdout


    def compare_with_expected(self, output):
        expected_file = os.path.join(os.getcwd(), 'expected')

        if not os.path.exists(expected_file):
            return True

        out_file_path = os.path.join(os.getcwd(), 'out')

        logger.info(f"Creating out file: {out_file_path} with content {output}")
        with open(out_file_path, 'w') as out_file:
            out_file.write(output)
            out_file.close();

            diff_exec = ["diff", "expected", "out"]
            print(f"\nExecuting: {Colors.WHITE}{' '.join(diff_exec)}{Colors.NC}:")

            result = subprocess.run(diff_exec, capture_output=True, text=True)
            if result.returncode == 0:
                print(f"{Colors.GREEN}diff: No differences{Colors.NC}")
            else:
                print(f"{Colors.LIGHT_PURPLE}< expected, > your result{Colors.NC}")
                print(f"{Colors.RED}{result.stdout}{Colors.NC}")

            return result.returncode == 0


    def execute_test(self, test_to_execute):
        logger.info(f"starting execution of {test_to_execute}")
        ex_number = test_to_execute[-2:]
        if self.selected_test and selected_test != ex_number:
            # If a test is specified, then it only executes the matching test
            print(IGNORED_EXERCISE_HEADER.replace("##", ex_number))
            return

        print(EXERCISE_HEADER.replace("##", ex_number))
        test_fn = getattr(self, test_to_execute)()

        norm_passed = self.pass_norminette(test_to_execute)
        status = self.compile_files()
        if status != 0:
            return False
         
        output = self.execute_program()
        return self.compare_with_expected(output) and norm_passed


    def clean_up(self, test):
        self.compile_flags = []
        self.compile = []
        self.norm_ignore = []