#!/usr/bin/env python3

# Copyright (C) 2025 Dustin Darcy
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.


import argparse
import fnmatch
import os
import platform
import re
import sys
import time
from datetime import datetime
from collections import defaultdict
import pyperclip

VERSION_STRING = "0.0.2.2"

EXTENDED_HELP = {
    "path-style": r"""
Path Style Examples (--path-style, -p)

Assume your project directory is:
D:\Projects\MyApp\
  └─ src\
     ├─ components\
     │  └─ Button.js
     └─ utils\
        └─ helpers.js

If you run this from within D:\Projects\MyApp:
   > cd D:\Projects\MyApp
   > listall.py -d src -p rel

It sees "src" as D:\Projects\MyApp\src. A file in
D:\Projects\MyApp\src\components\Button.js
becomes "components\Button.js" under 'rel' mode.

Output:
components/Button.js
utils/helpers.js

If you use -p rel-base instead:
   > cd D:\Projects\MyApp
   > listall.py -d src -p rel-base

Now each path is prefixed by the basename "src":
Output:
src/components/Button.js
src/utils/helpers.js

-----
If you run from a different folder, e.g. D:\Projects:
   > cd D:\Projects
   > listall.py -d MyApp\src -p rel

The script's 'start path' is D:\Projects\MyApp\src,
so the file paths still become:
components/Button.js
utils/helpers.js

But with -p rel-base, you get:
src/components/Button.js
src/utils/helpers.js

Hence, 'rel-base' always includes the basename (or a custom label) for
the start path, whereas 'rel' does not. This can help keep listings
clear if you're referencing multiple different directories.
""",

    # Extended help for --sort
    "sort": r"""
Sort Options (--sort, -s)

Available choices:
  sequence   => numeric + then text (case-sensitive)
  isequence  => numeric + then text (case-insensitive)
  winsequence => tries to replicate Windows Explorer style by
                 lowercasing all letters but sorting underscores to the top
  name       => plain text (case-sensitive)
  iname      => plain text (case-insensitive)
  date       => sort by file modification time

Tips:
  - 'winsequence' is handy if you want underscore-prefixed files/folders
    at the top, but otherwise a straightforward alphabetical ordering.
  - 'isequence' attempts to do numeric sorting (e.g., file2 < file10),
    but in a case-insensitive way. 
  - If you find that 'winsequence' doesn't match actual Windows Explorer
    in some corner cases (like spaces vs. underscores), consider debugging
    or adjusting the transform logic. 
"""
}

def extended_help_lookup(argv):
    """
    Check if user typed something like:
      listall.py --help path-style
      listall.py -h sort
    If so, print extended help for that param and exit.
    Otherwise, do nothing (return).
    """
    # We look for -h or --help in argv.
    # If found, see if there's a next token that might be 'path-style', 'sort', etc.
    # If so, print from EXTENDED_HELP and exit. Else do normal help.
    if "-h" in argv or "--help" in argv:
        # find index
        idx = argv.index("-h") if "-h" in argv else argv.index("--help")
        if idx + 1 < len(argv):
            topic = argv[idx + 1]
            if topic in EXTENDED_HELP:
                print(EXTENDED_HELP[topic])
                sys.exit(0)
    # If user typed just -h or --help alone or with an unknown topic => normal help.

def numerical_sort(value):
    """
    Extracts the first number from 'value' (string),
    returning (int_number, original_string). Used for 'sequence' or 'isequence' sorting.
    """
    parts = re.findall(r'\d+', value)
    return (int(parts[0]), value) if parts else (0, value)

def windows_explorer_sort(value):
    """
    A custom approach that tries to replicate Windows Explorer ordering:
      - convert everything to lowercase
      - keep underscores at the front (since ASCII '_' < letters)
    For a stronger effect, we could transform '_' into a character that definitely
    sorts to the top or bottom, but since '_' is ASCII 95, it's already before letters.

    If you want underscores sorted after letters, you could do:
      name = name.replace('_','{') 
    but for now we'll keep underscores in the normal ASCII position (which is above letters).
    """
    return os.path.basename(value).lower()

def sort_files(files, sort_mode):
    """
    Sort a list of file or directory paths by 'sort_by'.
    'i' variants are case-insensitive; 
    'sequence' => numeric + text; 
    'winsequence' => attempts Windows-like underscore ordering; 
    'date' => os.path.getmtime(x).
    """
    sort_map = {
        "sequence":   lambda x: numerical_sort(os.path.basename(x)),
        "isequence":  lambda x: numerical_sort(os.path.basename(x).lower()),
        "winsequence": windows_explorer_sort,
        "name":       lambda x: os.path.basename(x),
        "iname":      lambda x: os.path.basename(x).lower(),
        "date":       lambda x: os.path.getmtime(x),
    }
    return sorted(files, key=sort_map[sort_mode])

def apply_decorations(path, decorations):
    """
    Adjusts a path string according to any 'decorators':
      - 'no-leader': remove leading './' or '.\\'
      - 'rel-leader': force a leading './' or '.\\'
      - 'unix': replace backslashes with '/'
      - 'windows': replace '/' with '\\'
    """
    if "no-leader" in decorations:
        path = path.lstrip(".\\").lstrip("./")
    elif "rel-leader" in decorations:
        path = (".\\" if "windows" in decorations else "./") + path.lstrip(".\\").lstrip("./")

    if "unix" in decorations:
        path = path.replace("\\", "/")
    elif "windows" in decorations:
        path = path.replace("/", "\\")
    return path

# Stubs for partial skip
def on_visit_directory(root, dirs, files, depth, max_depth=None, prune_large_dirs=None):
    """
    'descend' => normal
    'skip' => skip subdirs
    'partial' => store only first+last or similar
    """
    if max_depth is not None and depth >= max_depth:
        return "skip"
    if prune_large_dirs is not None and len(files) >= prune_large_dirs:
        return "partial"
    return "descend"

def walk_directories(
    start_path_abs,
    exclude_patterns=None,
    sort_by="iname",
    collect="all",
    collect_limit=None,
    collect_limit_min=None,
    max_depth=None,
    prune_large_dirs=None
):
    """
    Returns { abs_dir: [abs_file,...] }.
    We'll store *all* files in the directory's own entry except
    possibly partial or skipping if on_visit says so.
    """
    exclude_patterns = exclude_patterns or []
    collected = {}

    def is_excluded(p):
        bn = os.path.basename(p)
        return any(fnmatch.fnmatch(bn, pat) for pat in exclude_patterns)

    def recurse_dir(root, depth=0):
        try:
            entries = os.listdir(root)
        except OSError:
            return
        subdirs = []
        files = []
        for e in entries:
            fp = os.path.join(root, e)
            if is_excluded(fp):
                continue
            if os.path.isdir(fp):
                subdirs.append(fp)
            else:
                files.append(fp)
        subdirs = sort_files(subdirs, sort_by)
        files   = sort_files(files, sort_by)

        action = on_visit_directory(
            root,
            [os.path.basename(d) for d in subdirs],
            [os.path.basename(f) for f in files],
            depth,
            max_depth,
            prune_large_dirs
        )
        if collect != "files-only":
            # always store directory for 'dirs-only', 'all', 'dirs-1st-last-file'
            collected.setdefault(root, [])

        if action == "skip":
            pass
        elif action == "partial":
            # store only first+last
            if len(files) > 1:
                files = [files[0], files[-1]]
            # subdirs = [] # skip subdirs or not? Let's skip
            subdirs = []

        # now store files depending on collect:
        if collect == "dirs-only":
            pass
        elif collect == "dirs-1st-last-file":
            if len(files) > 1:
                collected[root] = [files[0], files[-1]]
            else:
                collected[root] = files
        elif collect == "files-only":
            # NEW: for summary mode, we still want each directory to have its file list
            # so we do NOT store in "" but store in the directory key
            collected.setdefault(root, []).extend(files)
        else:  # collect == "all"
            collected[root] = files

        # descend subdirs if not skipped
        if action != "skip":
            for sd in subdirs:
                recurse_dir(sd, depth+1)

    recurse_dir(start_path_abs, 0)
    return collected

def collect_files(
    start_path_abs,
    path_style,
    collect,
    sort_by,
    decorations,
    exclude_patterns=None,
    collect_limit=None,
    collect_limit_min=None,
    strict_rel=False,
    base_label=None,
    max_depth=None,
    prune_large_dirs=None
):
    raw = walk_directories(
        start_path_abs,
        exclude_patterns,
        sort_by,
        collect,
        collect_limit,
        collect_limit_min,
        max_depth,
        prune_large_dirs
    )
    # partial truncation if 'collect == all' and collect_limit
    if collect == "all" and collect_limit:
        for dkey, flist in raw.items():
            if len(flist) > collect_limit:
                half = max((collect_limit_min or 2)//2, 1)
                start_slice = flist[:half]
                end_slice   = flist[-half:]
                raw[dkey] = start_slice + end_slice

    final = adjust_paths(raw, start_path_abs, path_style, decorations, collect,
                         strict_rel, base_label)
    return final

def adjust_paths(
    collected_dict,
    start_path_abs,
    path_style,
    decorations,
    collect,
    strict_rel=False,
    base_label=None
):
    """
    Convert the collected dict of {directory_path: [files]} into a version
    that uses the requested path style. If 'strict_rel' is True, cross-drive references
    cause an exception in rel/rel-base modes. 'base_label' is used in 'rel-base' instead
    of os.path.basename(start_path_abs).
	
    Takes {dir_path: [files]} and applies path transformations 
    (full, rel, rel-base, files-only) plus decorations (unix, windows, etc.).
    If 'strict_rel' is True, crossing drives in 'rel' or 'rel-base' is not allowed.
    """
    adjusted = {}
    for dir_abs, file_list in collected_dict.items():
        dir_abs_norm = os.path.abspath(dir_abs)
        adjusted_files = []
        for f in file_list:
            f_abs = os.path.abspath(f)

            # Cross-drive check if strict
            if strict_rel and path_style in ("rel","rel-base"):
                if os.path.splitdrive(f_abs)[0].lower() != os.path.splitdrive(start_path_abs)[0].lower():
                    raise ValueError(f"Cannot create relative path across drives: {f_abs}")

            # Convert each file path
            if path_style == "files-only":
                adjusted_file = os.path.basename(f_abs)
            elif path_style == "rel":
                same_drive = (
                    os.path.splitdrive(f_abs)[0].lower()
                    == os.path.splitdrive(start_path_abs)[0].lower()
                )
                if same_drive:
                    rel_file = os.path.relpath(f_abs, start_path_abs)
                    adjusted_file = apply_decorations(rel_file, decorations)
                else:
                    # fallback to absolute if not strict
                    adjusted_file = f_abs
            elif path_style == "rel-base":
                label = base_label if base_label else os.path.basename(start_path_abs)
                same_drive = (
                    os.path.splitdrive(f_abs)[0].lower()
                    == os.path.splitdrive(start_path_abs)[0].lower()
                )
                if same_drive:
                    rel_f = os.path.relpath(f_abs, start_path_abs)
                    combo = os.path.join(label, rel_f)
                    adjusted_file = apply_decorations(combo, decorations)
                else:
                    adjusted_file = f_abs
            else:
                # full
                adjusted_file = f_abs
            adjusted_files.append(adjusted_file)

        # now the directory key
        if path_style == "files-only":
            # 'files-only' => just store everything under the same key => '' ?
            # But for summary we want the directory nesting. We'll store them by real dir path
            # Then the summary logic can do braces. So let's keep the directory path but if you want old behavior 
            # of a single list, you'd do inline mode.
            # dir_key = ""
            dir_key = dir_abs_norm  # keep directory path
        else:
            if strict_rel and path_style in ("rel","rel-base"):
                if os.path.splitdrive(dir_abs_norm)[0].lower() != os.path.splitdrive(start_path_abs)[0].lower():
                    raise ValueError(f"Cannot create relative path across drives: {dir_abs_norm}")

            if path_style == "rel":
                same_drive = (
                    os.path.splitdrive(dir_abs_norm)[0].lower()
                    == os.path.splitdrive(start_path_abs)[0].lower()
                )
                if same_drive:
                    rel_dir = os.path.relpath(dir_abs_norm, start_path_abs)
                    dir_key = apply_decorations(rel_dir, decorations)
                else:
                    dir_key = dir_abs_norm
            elif path_style == "rel-base":
                label = base_label if base_label else os.path.basename(start_path_abs)
                same_drive = (
                    os.path.splitdrive(dir_abs_norm)[0].lower()
                    == os.path.splitdrive(start_path_abs)[0].lower()
                )
                if same_drive:
                    rel_dir = os.path.relpath(dir_abs_norm, start_path_abs)
                    if rel_dir == ".":
                        dir_key = apply_decorations(label, decorations)
                    else:
                        combo = os.path.join(label, rel_dir)
                        dir_key = apply_decorations(combo, decorations)
                else:
                    dir_key = dir_abs_norm
            else:
                # full
                dir_key = dir_abs_norm

        adjusted[dir_key] = adjusted_files
    return adjusted

def build_directory_tree(collected):
    """
    Builds a nested dict structure from {dir_key: [file_paths], ...}
    for hierarchical display in summary mode.
    """
    tree = lambda: defaultdict(tree)
    root = tree()
    for dkey, flist in collected.items():
        if dkey:
            parts = dkey.split(os.sep)
            current = root
            for p in parts:
                current = current[p]
    return root

def get_subdir_sort_key(name, sort_by):
    """
    Applies the same 'sort_by' logic for subdirectory names
    that we do for files. We can't do 'date' for pure subdir names
    (no full path), so if 'date' is chosen, we just fallback to 'name'.
    """
    # We'll reuse 'numerical_sort' or 'windows_explorer_sort' 
    # in a way that treats 'name' as the final item.
    if sort_by == "sequence":
        # numeric + then text, case-sensitive
        return numerical_sort(name)
    elif sort_by == "isequence":
        # numeric + text, case-insensitive
        return numerical_sort(name.lower())
    elif sort_by == "winsequence":
        # mimic Windows underscore + case-insensitive
        return name.lower()
    elif sort_by == "name":
        return name
    elif sort_by == "iname":
        return name.lower()
    elif sort_by == "date":
        # We only have the subdir's name here, not a full path,
        # so we can't do a real getmtime. Fallback to 'name'.
        return name
    else:
        # fallback
        return name

def format_collected_items(
    collected_dict,
    format_style,
    collect,
    decorations,
    path_style,
    sort_by,
    indent_size=2,
    compact_braces=False
):
    """
    Takes 'collected_dict' = { <directory_key>: [files], ... }
    and formats it into text for either 'inline' or 'summary' mode.
    
    The 'sort_by' param is used for subdirectory ordering in summary mode,
    so we can replicate 'sequence', 'winsequence', etc.
    """
    lines = []

    directory_tree = build_directory_tree(collected_dict)

    def format_directory(node, full_map, current_path="", level=0):
        indent = " " * (indent_size * level)
        items = list(node.items())
        # Sort subdirs using the new helper:
        items.sort(key=lambda x: get_subdir_sort_key(x[0], sort_by))
        for i, (subdir_name, subsubtree) in enumerate(items):
            is_last = (i == len(items)-1)
            full_path = os.path.join(current_path, subdir_name) if current_path else subdir_name

            # If path_style=rel-base, skip decorations on subdir name:
            dir_display = subdir_name if path_style=="rel-base" else apply_decorations(subdir_name, decorations)

            if collect == "dirs-only":
                # In summary mode, just show subdirectories (with braces if they have children)
                if subsubtree:
                    lines.append(f"{indent}{dir_display}:{{")
                    format_directory(subsubtree, full_map, full_path, level+1)
                    if compact_braces and is_last:
                        lines[-1] += "}"
                    else:
                        lines.append(f"{indent}}}")
                else:
                    lines.append(f"{indent}{dir_display}")

            elif collect == "files-only":
                # Open unlabeled brace:
                lines.append(f"{indent}{{")
                # if we have files in this directory
                if full_path in full_map:
                    for f in full_map[full_path]:
                        findent = indent + " "*indent_size
                        lines.append(f"{findent}{apply_decorations(os.path.basename(f), decorations)}")
                # Recurse sub-subdirs
                format_directory(subsubtree, full_map, full_path, level+1)
                if compact_braces and is_last:
                    lines[-1] += "}"
                else:
                    lines.append(f"{indent}}}")

            elif collect == "dirs-1st-last-file":
                # older logic
                has_sub = bool(subsubtree)
                # If there's a parent or subdirs, we open braces
                if has_sub or current_path:
                    lines.append(f"{indent}{dir_display}:{{")
                else:
                    lines.append(f"{indent}{dir_display}")

                # If this directory has files in 'collected', show first & last
                if full_path in full_map:
                    flist = full_map[full_path]
                    if flist:
                        findent = indent + " "*indent_size
                        lines.append(f"{findent}{apply_decorations(os.path.basename(flist[0]), decorations)}")
                        if len(flist)>1:
                            lines.append(f"{findent}{apply_decorations(os.path.basename(flist[-1]), decorations)}")

                # Recurse subdirectories
                if has_sub:
                    format_directory(subsubtree, full_map, full_path, level+1)
                if has_sub or current_path:
                    if compact_braces and is_last:
                        lines[-1] += "}"
                    else:
                        lines.append(f"{indent}}}")

            else:  # 'all'
                # labeled braces - show all files in this directory + subdirectories
                lines.append(f"{indent}{dir_display}:{{")
                if full_path in full_map:
                    for ff in full_map[full_path]:
                        ffindent = indent + " "*indent_size
                        lines.append(f"{ffindent}{apply_decorations(os.path.basename(ff), decorations)}")
                if subsubtree:
                    format_directory(subsubtree, full_map, full_path, level+1)
                if compact_braces and is_last:
                    lines[-1] += "}"
                else:
                    lines.append(f"{indent}}}")

    if format_style == "inline":
        # Inline mode => just list directories or files
        if collect == "dirs-only":
            for dkey in collected_dict:
                lines.append(apply_decorations(dkey, decorations))
        else:
            for dkey, flist in collected_dict.items():
                for f in flist:
                    lines.append(apply_decorations(f, decorations))
    else:
        # summary => build hierarchical braces (nested tree and print recursively)
        format_directory(directory_tree, collected_dict)

    return "\n".join(lines)

def output_results(content, outputs, filename=None):
    """
    Depending on 'outputs', send 'content' to:
      - a file (with optional custom 'filename')
      - the system clipboard
      - stdout
      - or all
    """
    tzname = time.tzname[time.localtime().tm_isdst]
    def_name = datetime.now().strftime(f"listall_%y.%m.%d_%H-%M_{tzname}.txt")

    if "file" in outputs or "all" in outputs:
        fname = filename or def_name
        with open(fname, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Content written to file: {fname}")
    if "clip" in outputs or "all" in outputs:
        pyperclip.copy(content)
        print("Content copied to clipboard.")
    if "stdout" in outputs or "all" in outputs:
        print(content)

def main():
    # Step A: Intercept `-h param` or `--help param`
    extended_help_lookup(sys.argv[1:])

    # Step B: Normal parser with epilog, rawdesc, etc.
    parser = argparse.ArgumentParser(
        description="List filenames, directories, or specific files with customizable sorting, collection, and output options.",
        epilog="""
Common usage examples:

 listall.py -d . -s sequence  # implies -p rel-base -f inline -o clip -fmt inline -c all
 listall.py -d . -p rel-base -f inline -s sequence -o clip   # same as above

Other examples:
 listall.py -d "path/to/dir1" "path/to/dir2" --path-style files-only --collect dirs-only --format inline --output file --filename listall_jan1st_2024.txt
 listall.py -d . --exclude "*.txt" --exclude ".\\temp"
 listall.py -d . -p rel -c dirs-1st-last-file -s sequence -o clip
 listall.py -d . -c dirs-1st-last-file -s sequence --output file --filename listall_jan1st_2024.txt

Use "-h [param]" for extended help on certain parameters, e.g. "-h path-style" or "--help sort".
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--version","-v", action="version", version=f"%(prog)s {VERSION_STRING}")
    parser.add_argument("--dir","-d", nargs="+", required=True,
                        help="Directories to list from.")
    parser.add_argument("--exclude","-xd", action="append",
                        help="Exclude patterns (e.g. *.txt or dir_name). Repeatable.")
    parser.add_argument("--path-style","-p", choices=["full","rel","rel-base","files-only"],
                        default="rel-base",
                        help="Path style for output (default: rel-base).")
    parser.add_argument("--format","-fmt", choices=["inline","summary"], default="inline",
                        help="Output formatting style (default: inline).")
    parser.add_argument("--collect","-c", choices=["all","dirs-only","dirs-1st-last-file","files-only"],
                        default="all",
                        help="Collection strategy (default: all).")
    parser.add_argument("--sort","-s", choices=["sequence","isequence","winsequence","name","iname","date"],
                        default="iname",
                        help="File/directory sorting strategy (default: iname). See '-h sort' for details.")
    parser.add_argument("--output","-o", action="append",
                        choices=["clip","stdout","file","all"],
                        default=[],
                        help="Output method(s). If none, defaults to stdout.")
    parser.add_argument("--decorator","-dec", action="append",
                        choices=["unix","windows","rel-leader","no-leader"],
                        default=[],
                        help="Decorate path presentation (e.g. 'unix' => forward slashes).")
    parser.add_argument("--filename","-f",
                        help="If '-o file', we write to this filename (or a default).")
    parser.add_argument("--collect-limit","-cl", type=int,
                        help="If '--collect all', truncates if directory has >N files to 1st/Nth subset.")
    parser.add_argument("--collect-limit-min","-clm", type=int,
                        help="Number of total files to show in truncated dirs, half at start/half at end (default:2).")
    parser.add_argument("--strict-rel", action="store_true",
                        help="If set, cross-drive references in rel or rel-base cause error.")
    parser.add_argument("--base-label","-bl", type=str,
                        help="When -p rel-base, override default subfolder name with a custom label.")
    parser.add_argument("--indent","-i", type=int, default=2,
                        help="Spaces per indentation level in summary mode (default:2).")
    parser.add_argument("--compact-braces","-cb", action="store_true",
                        help="Close braces on same line in summary mode")
    parser.add_argument("--max-depth", type=int,
                        help="Skip subdirectories below this depth.")
    parser.add_argument("--prune-large-dirs", type=int,
                        help="If a directory has >=N files, partial approach (like first+last).")

    # Step 3: Parse the user's real arguments
    args = parser.parse_args()

    # Step 4: Validate at least one directory
    if not args.dir:
        parser.print_help()
        print("\nError: Please provide at least one directory with --dir.\n")
        sys.exit(1)

    # Step 5: Determine decorators with system default
    os_type = platform.system()
    sys_def_dec = ["unix"] if os_type in ["Darwin","Linux","Unix","FreeBSD","BSD"] else ["windows"]
    final_decs = set(args.decorator) if args.decorator else set(sys_def_dec)
    
    # If user provided both 'windows' and 'unix', discard system default
    # (like older code logic)
    if {"unix","windows"}.issubset(final_decs):
        final_decs.discard(next(iter(sys_def_dec)))

    # Step 6: Determine output methods
    out_methods = set(args.output) if args.output else {"stdout"}
    if "all" in out_methods:
        out_methods = {"clip","stdout","file"}

    # Step 7: Multidir handling: Collect from each directory separately to avoid collisions
    results_by_dir = {}
    for d in args.dir:
        absd = os.path.abspath(d)
        subcollected = collect_files(
            start_path_abs=absd,
            path_style=args.path_style,
            collect=args.collect,
            sort_by=args.sort,
            decorations=final_decs,
            exclude_patterns=args.exclude,
            collect_limit=args.collect_limit,
            collect_limit_min=args.collect_limit_min,
            strict_rel=args.strict_rel,
            base_label=args.base_label,
            max_depth=args.max_depth,
            prune_large_dirs=args.prune_large_dirs
        )
        results_by_dir[absd] = subcollected

    # If only one directory, we can flatten results
    if len(results_by_dir)==1:
        # Single directory => straightforward
        col = next(iter(results_by_dir.values()))
        final_str = format_collected_items(
            col,
            format_style=args.format,
            collect=args.collect,
            decorations=final_decs,
            path_style=args.path_style,
            sort_by=args.sort,
            indent_size=args.indent,
            compact_braces=args.compact_braces
        )
    else:
        # Multiple directories => label each section
        lumps = []
        for rootd, subdict in results_by_dir.items():
            lumps.append(f"=== Listing for: {rootd} ===")
            block = format_collected_items(
                subdict,
                format_style=args.format,
                collect=args.collect,
                decorations=final_decs,
                path_style=args.path_style,
                sort_by=args.sort,
                indent_size=args.indent,
                compact_braces=args.compact_braces
            )
            lumps.append(block)
            lumps.append("")
        final_str = "\n".join(lumps)

    # Step 8: Output
    output_results(final_str, out_methods, args.filename)

if __name__=="__main__":
    main()
