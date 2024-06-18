import os
import fnmatch

def read_gitignore(base_dir):
    gitignore_path = os.path.join(base_dir, '.gitignore')
    if not os.path.exists(gitignore_path):
        return []

    with open(gitignore_path, 'r') as f:
        lines = f.readlines()

    ignore_patterns = []
    for line in lines:
        line = line.strip()
        if line and not line.startswith('#'):
            ignore_patterns.append(line)
    return ignore_patterns

def is_ignored(file_path, ignore_patterns, additional_ignores):
    for pattern in ignore_patterns + additional_ignores:
        if pattern.startswith('/'):
            if fnmatch.fnmatch(file_path, pattern[1:]) or fnmatch.fnmatch(os.path.dirname(file_path), pattern[1:]):
                return True
        if fnmatch.fnmatch(file_path, pattern) or fnmatch.fnmatch(os.path.dirname(file_path), pattern):
            return True
    return False

def read_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except UnicodeDecodeError:
        try:
            with open(file_path, 'r', encoding='latin-1') as f:
                return f.read()
        except Exception as e:
            return f"Error reading file {file_path}: {e}"

def gather_project_files(base_dir, output_file):
    ignore_patterns = read_gitignore(base_dir)
    additional_ignores = [
        'package-lock.json', 
        '.gitignore', 
        os.path.basename(__file__),
        output_file,
    ]

    with open(output_file, 'w', encoding='utf-8') as outfile:
        for root, dirs, files in os.walk(base_dir):
            # Filter out ignored directories
            rel_root = os.path.relpath(root, base_dir)
            dirs[:] = [d for d in dirs if not is_ignored(os.path.relpath(os.path.join(root, d), base_dir), ignore_patterns, additional_ignores)]
            if is_ignored(rel_root, ignore_patterns, additional_ignores):
                continue
            for file in files:
                file_path = os.path.relpath(os.path.join(root, file), base_dir)
                if not is_ignored(file_path, ignore_patterns, additional_ignores):
                    content = read_file(os.path.join(root, file))
                    outfile.write(f"\n# Begin {file_path}\n")
                    outfile.write(content)
                    outfile.write(f"\n# End {file_path}\n")
                    outfile.write(f"\n-------------------------------\n")
    
    # Write the directory structure at the end of the file
    with open(output_file, 'a', encoding='utf-8') as outfile:
        outfile.write("\n# Directory Structure\n")
        for root, dirs, files in os.walk(base_dir):
            level = root.replace(base_dir, '').count(os.sep)
            indent = ' ' * 4 * level
            outfile.write(f"{indent}{os.path.basename(root)}/\n")
            subindent = ' ' * 4 * (level + 1)

            rel_root = os.path.relpath(root, base_dir)
            dirs[:] = [d for d in dirs if not is_ignored(os.path.relpath(os.path.join(root, d), base_dir), ignore_patterns, additional_ignores)]
            if is_ignored(rel_root, ignore_patterns, additional_ignores):
                continue

            for f in files:
                file_path = os.path.relpath(os.path.join(root, f), base_dir)
                if not is_ignored(file_path, ignore_patterns, additional_ignores):
                    outfile.write(f"{subindent}{f}\n")

    print(f"Project files and structure have been gathered into {output_file}")

# Usage
project_directory = os.path.abspath('./')
output_filename = 'consolidated_project.txt'
gather_project_files(project_directory, output_filename)
