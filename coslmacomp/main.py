import click
import json
import logging

#import model_detect
import rules as prom_parser
#import nagios_parser
#import rule_compare
#import summary


@click.command()
@click.option('--prometheus-url', default=None, help='Instead of auto-detecting the location of prometheus, use a given URL')
@click.option('--format', "output_format", default='plain', help='Format for the output')
@click.option('-v', '--verbose', is_flag=True, default=False, help='Enable verbose output')
def compare_nrpe(prometheus_url, output_format, verbose):
    '''
    The main entrypoint of the program
    '''

    if verbose:
        # There is likely a Canonical standard here - what is it?
        logging.getLogger().setLevel(logging.DEBUG)

    # Get the list of rules from prometheus
    prom_rules = handle_prometheus(prometheus_url)

    # Get the list of rules from nagios
    nagios_rules = handle_nagios()

    # TODO: Pass both sets to comparer
    comments = rule_compare.compare_all(rules_prom, rules_nagios)

    # TODO: Output nice summary
    if output_format == "plain":
        raw_output = summary.summarize_plain(comments)
    elif output_format == "json":
        #raw_output = summary.summarize_json(comments)
        raw_output = json.dumps(comments)
    else:
        raise Exception("Output format unknown '{}'".format(output_format))

    print(raw_output)


def handle_prometheus(prometheus_url):
    '''
    Get the NRPE rules from prometheus.
    '''

    if prometheus_url is None:
        logging.debug("Searching for default prometheus_url")
        prometheus_url = model_detect.find_prometheus_url()

    logging.debug("Fetching rules from prometheus endpoint")
    prom_raw = prom_parser.fetch_rules_raw(prometheus_url)
    logging.debug("Parsing prometheus rules")
    rules_prom = prom_parser.parse(prom_raw)

    logging.debug("Discovered {} prometheus rules".format(len(rules_prom)))

    return rules_prom


def handle_nagios():
    rules_nagios = nagios_parser.get_rules()
    return rules_nagios



if __name__ == "__main__":
    compare_nrpe()
