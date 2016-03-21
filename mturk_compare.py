# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import os
import sys
import time
import csv
import string
import argparse
from copy import deepcopy

# -----------------
# Helper Functions
# -----------------


def col_to_num(col):
    """ Converts spreadsheet column letter to number """
    num = 0
    for c in col:
        if c in string.ascii_letters:
            num = num * 26 + (ord(c.upper()) - ord('A')) + 1
    return num


def _get_headers(csv_reader):
    """ Returns the header of a parsed CSV"""
    return list(csv_reader)[0]


def _header_is_repeated(csv_reader):
    """ Verifies if a CSV header title is repeated """
    return len(list(csv_reader)[0]) != len(set(list(csv_reader)[0]))
# End


# Stats
errors = []


def compare(csv_file, grouping_column='A', answer_column='B',
            generated_file_folder=''):
    uid_col = col_to_num(grouping_column)  # TODO: col_to_num(grouping_column)-1

    reader = csv.reader(
        csv_file, delimiter=str(','), dialect='excel', quotechar=str('"'))

    # Set Off-Set assuming the first row both files is a header
    rows_offset = 1

    # Normalize Content
    parsed_content = list(reader)
    csv_content = deepcopy(parsed_content)

    # ----------------
    # Test CSV Format
    # ----------------
    # Checks if headers titles are unique
    if _header_is_repeated(csv_content):
        errors.append("%s: Repeated headers." %
                      (file1_name))
    # End

    if not len(errors):
        # -------------------------------------------
        # Search and Compare CSV by Grouping Columnn
        # -------------------------------------------

        # Extracts Grouping IDs in CSV and it's answers values
        if type(uid_col) == int:  # TODO: Verify if this checking is required
            csv_ids = {}

            # Iterate over rows, excluding header
            for index, row in enumerate(csv_content[rows_offset:]):
                key = str(row[uid_col-1]).strip()
                answer = row[col_to_num(answer_column)-1].lower().strip()
                if csv_ids.get(key):
                    csv_ids.get(key)
                    csv_ids[key].append((index, answer))
                else:
                    csv_ids[key] = [(index, answer)]

        # Filter matching IDs
        csv_match = {}
        csv_no_match = {}
        csv_skipped = {}

        for _id in csv_ids:
            if csv_ids.get(_id):
                # Picks answers for current ID
                answers = [answer[1].lower().strip()
                           for answer in csv_ids.get(_id)]
                answer_set = list(set(answers))

                # Verify if there are 2 or more answers for current ID
                if len(answers) and len(answers) >= 2:
                    # Verify if answers are the same for current ID
                    if len(answer_set) == 1:
                        csv_match[_id] = answer_set
                    else:
                        csv_no_match[_id] = answer_set
                else:
                    csv_skipped[_id] = answer_set

        # ------------
        # Output File
        # ------------
        if len(csv_match):
            selected_rows = []

            # Set output filename
            output_file_name = 'mturk-compared-{timestamp}.csv'\
                                          .format(timestamp = int(time.time()))

            # Adds headers to output file
            selected_rows.append(_get_headers(csv_content))

            # TODO: insert "MATCH" column providing column letter
            selected_rows[0].extend(["", "MATCH"])

            # get header columns count
            col_count = len(selected_rows[0])

            # Picks matching IDs rows and add it to output file
            for row in deepcopy(parsed_content[rows_offset:]):
                # If row latests columns are empty are not included in
                # the array, this piece of code adds those trailing
                # empty columns
                empty_cols_count = col_count-len(row)
                empty_cols = ["" for x in range(0, empty_cols_count)]
                row.extend(empty_cols)
                _id = row[col_to_num(grouping_column)-1]
                # End

                if csv_match.get(_id):
                    row[-1] = "True"
                elif csv_no_match.get(_id):
                    row[-1] = "False"
                else:
                    row[-1] = "*Skipped"
                selected_rows.append(row)

            # Write file
            with open(os.path.join(generated_file_folder,
                                   output_file_name), 'wb') as f:

                writer = csv.writer(f,
                                    delimiter=str(','),
                                    quotechar=str('"'),
                                    quoting=csv.QUOTE_MINIMAL)

                writer.writerows(selected_rows)
                print "Ouput File: ", output_file_name
    else:
        print errors


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Compares CSV file fields.')
    parser.add_argument('infile', nargs='?', type=argparse.FileType('rU'),
                        default=sys.stdin)
    parser.add_argument('--grouping-column', type=str,
                        default="A")
    parser.add_argument('--answer-column', type=str,
                        default="B")
    args = parser.parse_args()

    print "Comparing: ", (args.infile).name

    compare(args.infile, grouping_column=args.grouping_column,
            answer_column=args.answer_column)
