#!/usr/bin/env python

'''
Formats source code with clang-format or checks if the code is properly formatted.
'''

# TODO: Code in JsMaterialX sub-directory is not formatted properly. for now it is excluded


import argparse, os, re, subprocess, shutil


def find_clang_format_cmd():
    names = ['clang-format-13', 'clang-format']
    for name in names:
        if shutil.which(name) is not None:
            return name
    print("clang-format is missing")
    exit(1)


def verify_clang_format(cmd):
    result = subprocess.run([cmd, '--version'], stdout=subprocess.PIPE)
    tokens = result.stdout.decode("utf-8").split()
    while len(tokens) > 0 and tokens[0] != 'clang-format':
        tokens.pop(0)
    if (
        result.returncode != 0
        or len(tokens) < 3
        or tokens[0] != 'clang-format'
        or tokens[1] != 'version'
    ):
        print('error while checking clang-format version')
        print("version string: " + str(tokens))
        exit(1)
    version = tokens[2].split('.', 2)
    print(f"clang-format version: {version[0]}.{version[1]}.{version[2]}")

    if int(version[0]) < 13:
        print("clang-format is too old; At least version 13 is required")
        exit(1)

def find_source_files():
    '''Finds all source code files which should be formatted. Groups files by directory, so that
       generated commands won't be too long (under Windows there is a limit of 8K characters).'''

    out = []
    regex = re.compile('(.*\.h$)|(.*\.cpp$)|(.*\.mm$)')
    exclude_dir_regex = re.compile('.*[\\\\\\/](External|NanoGUI|JsMaterialX)')
    for root_dir in ['source']:
        for root, dirs, files in os.walk(root_dir):
            if not exclude_dir_regex.match(root):
                group = []
                for file in files:
                    if regex.match(file):
                        group.append(os.path.join(root, file))
                if len(group) > 0:
                    out.append(group)
    return out


def format_source(cf_cmd, check: bool):
    print("Checking C++ code formatting..." if check else "Formatting C++ code...")
    command_prefix = [cf_cmd, '-i']
    if check:
        command_prefix += ['--dry-run', '-Werror']
        
    for source_files in find_source_files():
        full_command = command_prefix + source_files
        result = subprocess.run(full_command)
        if check and result.returncode != 0:
            exit(1)

    print("All OK")


def main():
    parser = argparse.ArgumentParser(
        prog='format',
        description='Tool for code formatting and format verification',
    )
    parser.add_argument('-c', '--check', action='store_true')
    args = parser.parse_args()

    libfwk_path = os.path.join(__file__, '..')

    clang_format_cmd = find_clang_format_cmd()
    verify_clang_format(clang_format_cmd)

    format_source(clang_format_cmd, args.check)


if __name__ == "__main__":
    main()
