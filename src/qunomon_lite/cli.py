import argparse
from qunomon_lite import ait


class keyvalue(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, dict())

        for value in values:
            key, value = value.split("=")
            getattr(namespace, self.dest)[key] = value


def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    parser_run = subparsers.add_parser("run", help="see `run -h`")
    parser_run.add_argument("ait")
    parser_run.add_argument("--inventories", nargs="*", action=keyvalue)
    parser_run.add_argument("--params", nargs="*", action=keyvalue)
    parser_run.set_defaults(handler=run)

    parser_result_show = subparsers.add_parser("result-show", help="see `run -h`")
    parser_result_show.add_argument("run_id")
    parser_result_show.set_defaults(handler=result_show)

    args = parser.parse_args()

    if hasattr(args, "handler"):
        args.handler(args)
    else:
        parser.print_help()


def run(args):
    ait.run(args.ait, inventories=args.inventories, params=args.params)


def result_show(args):
    ait.result(args.run_id).show()


if __name__ == "__main__":
    main()
