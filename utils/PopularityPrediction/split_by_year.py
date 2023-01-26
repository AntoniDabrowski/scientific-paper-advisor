import argparse
import logging
import os.path
import sys

import pandas as pd

parser = argparse.ArgumentParser(description="Tool for collecting the further research suggestions "
                                             "from the arxiv articles. ")

parser.add_argument("-od", "--output-dir",
                    default=1000,
                    help="Dictates how many records should the output database contain.",
                    required=True)
parser.add_argument("-f", "--filename",
                    help="Name of the output file. This will be a csv file."
                         "If this files already exist and is of csv format the script will try to append "
                         "the results to it, to allow continuation of interrupted processes.",
                    required=True)
parser.add_argument("-d", "--debug", action="store_true")

args = parser.parse_args()

log = logging.getLogger(__name__)

handler = logging.StreamHandler(sys.stderr)
handler.setLevel(logging.DEBUG if args.debug else logging.WARNING)
log.addHandler(handler)


def split_json_by_year(file_name: str, output_dir: str):
    database = pd.read_json(file_name, lines=True, chunksize=10000)

    database_dframe: pd.DataFrame
    for database_dframe in database:
        for year_group in database_dframe.groupby('year'):
            year, df = year_group
            file_year_name = f"{output_dir}/{year}.csv"
            df.to_csv(file_year_name, mode='a', index=False, header=(not os.path.exists(file_year_name)))


if __name__ == '__main__':
    split_json_by_year(
        file_name=args.filename,
        output_dir=args.output_dir
    )
