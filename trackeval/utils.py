
import os
import argparse
from pandas import DataFrame


def init_config(config, default_config, name=None):
    """Initialise non-given config values with defaults"""
    if config is None:
        config = default_config
    else:
        for k in default_config.keys():
            if k not in config.keys():
                config[k] = default_config[k]
    if name and config['PRINT_CONFIG']:
        print('\n%s Config:' % name)
        for c in config.keys():
            print('%-20s : %-30s' % (c, config[c]))
    return config


def update_config(config):
    """
    Parse the arguments of a script and updates the config values for a given value if specified in the arguments.
    :param config: the config to update
    :return: the updated config
    """
    parser = argparse.ArgumentParser()
    for setting in config.keys():
        if type(config[setting]) == list or type(config[setting]) == type(None):
            parser.add_argument("--" + setting, nargs='+')
        else:
            parser.add_argument("--" + setting)
    args = parser.parse_args().__dict__
    for setting in args.keys():
        if args[setting] is not None:
            if type(config[setting]) == type(True):
                if args[setting] == 'True':
                    x = True
                elif args[setting] == 'False':
                    x = False
                else:
                    raise Exception('Command line parameter ' + setting + 'must be True or False')
            elif type(config[setting]) == type(1):
                x = int(args[setting])
            elif type(args[setting]) == type(None):
                x = None
            else:
                x = args[setting]
            config[setting] = x
    return config


def get_code_path():
    """Get base path where code is"""
    return os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))


def validate_metrics_list(metrics_list):
    """Get names of metric class and ensures they are unique, further checks that the fields within each metric class
    do not have overlapping names.
    """
    metric_names = [metric.get_name() for metric in metrics_list]
    # check metric names are unique
    if len(metric_names) != len(set(metric_names)):
        raise TrackEvalException('Code being run with multiple metrics of the same name')
    fields = []
    for m in metrics_list:
        fields += m.fields
    # check metric fields are unique
    if len(fields) != len(set(fields)):
        raise TrackEvalException('Code being run with multiple metrics with fields of the same name')
    return metric_names


def write_summary_results(summaries, cls, output_folder):
    """Write summary results to file"""
    out_file = os.path.join(output_folder, cls + '_summary.csv')
    if os.path.exists(out_file):
        os.remove(out_file)
    os.makedirs(os.path.dirname(out_file), exist_ok=True)
    for sums in summaries:
        x = DataFrame(sums)
        x = DataFrame(x.values.T, index=x.columns, columns=x.index)
        with open(out_file, 'a', newline='') as f:
            x.to_csv(f, mode="a", index=True)
            f.write("\n")


def write_detailed_results(details, cls, output_folder):
    """Write detailed results to file"""
    out_file = os.path.join(output_folder, cls + '_detailed.csv')
    if os.path.exists(out_file):
        os.remove(out_file)
    os.makedirs(os.path.dirname(out_file), exist_ok=True)
    for detail in details:
        x = DataFrame(detail)
        x = DataFrame(x.values.T, index=x.columns, columns=x.index)
        col_classes = {"ori": []}
        for col in x.columns.tolist():
            if "___" in col:
                the_class = col.split("___", 1)[0]
                if the_class not in col_classes.keys():
                    col_classes[the_class] = [col]
                else:
                    col_classes[the_class].append(col)
            else:
                col_classes["ori"].append(col)
        for v in col_classes.values():
            tmp_df = x[v]
            with open(out_file, 'a', newline='') as f:
                tmp_df.to_csv(f, mode="a", index=True)
                f.write("\n")


def load_detail(file):
    """Loads detailed data for a tracker."""
    data = {}
    with open(file) as f:
        for i, row_text in enumerate(f):
            row = row_text.replace('\r', '').replace('\n', '').split(',')
            if i == 0:
                keys = row[1:]
                continue
            current_values = row[1:]
            seq = row[0]
            if seq == 'COMBINED':
                seq = 'COMBINED_SEQ'
            if (len(current_values) == len(keys)) and seq != '':
                data[seq] = {}
                for key, value in zip(keys, current_values):
                    data[seq][key] = float(value)
    return data


class TrackEvalException(Exception):
    """Custom exception for catching expected errors."""
    ...
