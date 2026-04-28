import argparse

from workers.log_worker import run_pipeline


def main():
    parser = argparse.ArgumentParser(prog="oaas", description="OAAS CLI")

    subparsers = parser.add_subparsers(dest="command")

    analyze_parser = subparsers.add_parser("analyze", help="Analyze logs")

    analyze_parser.add_argument("--source", choices=["sample", "cloudwatch"], default="sample")
    analyze_parser.add_argument("--log-group", help="CloudWatch log group name")
    analyze_parser.add_argument("--minutes", type=int, help="Lookback window in minutes")
    analyze_parser.add_argument("--limit", type=int, help="Max number of logs")
    analyze_parser.add_argument("--filter", help="CloudWatch filter pattern")
    analyze_parser.add_argument("--service", help="Override service name")
    analyze_parser.add_argument("--region", help="AWS region")
    analyze_parser.add_argument("--use-llm", action="store_true", help="Enable LLM summarization")

    args = parser.parse_args()

    if args.command == "analyze":
        run_pipeline(
            source=args.source,
            use_llm=args.use_llm,
            log_group_name=args.log_group,
            minutes=args.minutes,
            limit=args.limit,
            filter_pattern=args.filter,
            service_name=args.service,
            aws_region=args.region,
        )
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
