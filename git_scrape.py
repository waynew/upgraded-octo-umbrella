import argparse
import json
import pathlib
from datetime import datetime, timedelta

import quiz
import quiz.build

__version__ = "2020.01.31.1"


quiz.build.argument_as_gql.register(
    list,
    lambda x: "[{}]".format(",".join(quiz.build.argument_as_gql(thing) for thing in x)),
)


def make_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("--owner", default="waynew", help="Repo owner")
    parser.add_argument("--repo", default="upgraded-octo-umbrella", help="Repo name")

    subparsers = parser.add_subparsers()

    cache_parser = subparsers.add_parser(
        "cache",
        help="Cache issues from GitHub. Will refresh whatever issues may be around.",
    )
    cache_parser.set_defaults(action="cache")

    report_parser = subparsers.add_parser(
        "report", help="Report on issues cached from GitHub."
    )
    report_parser.set_defaults(action="report")
    report_parser.add_argument(
        "--refresh",
        action="store_true",
        default=False,
        help="Refresh the cache before running the report.",
    )

    return parser


def convert_node_to_dict(node):
    data = {
        "title": node.title,
        "number": node.number,
        "state": node.state.value,
        "is_closed": node.closed,
        "closed_timestamp": node.closed_at,
        "created_timestamp": node.created_at,
        "labels": [l.node.name for l in node.labels.edges],
    }
    return data


def cache_issues(*, owner, reponame, issues):
    cache_path = pathlib.Path(".cache", owner, reponame, "issues.json")
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    cache_path.write_text(json.dumps(issues))


def load_issues(owner, reponame):
    cache_path = pathlib.Path(".cache", owner, reponame, "issues.json")
    return json.loads(cache_path.read_text())


def get_em_all(*, owner, reponame, auth):
    """
    Get an owner like "waynew" and a reponame like 'upgraded-octo-umbrella',
    scrape all the issues, dumping them into `.cache`.
    """
    schema_path = pathlib.Path(".cache", owner, reponame, "schema.json")
    schema_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        print("Loading schema from disk...")
        schema = quiz.Schema.from_path(schema_path)
        print("Done!")
    except FileNotFoundError:
        print("Failed!")
        print("Loading schema from GitHub...")
        schema = quiz.Schema.from_url("https://api.github.com/graphql", auth=auth,)
        schema.to_path(schema_path)
        print("Done!")

    _ = quiz.SELECTOR
    end_cursor = ""
    issues = []
    while end_cursor is not None:
        issue_filters = {
            "first": 100,
            "states": [schema.IssueState.OPEN, schema.IssueState.CLOSED],
        }
        if end_cursor:
            print("Loading after", end_cursor)
            issue_filters["after"] = end_cursor

        # fmt: off
        query = schema.query[
            _
            .repository(owner=owner, name=reponame)[
                _
                .issues(**issue_filters)[
                    _
                    ('page_info').pageInfo [
                        _
                        ('end_cursor').endCursor
                    ]
                    .nodes[
                        _
                        .title
                        .number
                        .state
                        .closed
                        ('closed_at').closedAt
                        ('created_at').createdAt
                        .labels(first=100) [
                            _
                            .edges [
                                _
                                .node [
                                    _
                                    .name
                                ]
                            ]
                        ]
                    ]
                ]
            ]
        ]
        # fmt: on
        result = quiz.execute(query, "https://api.github.com/graphql", auth=auth,)
        end_cursor = result.repository.issues.page_info.end_cursor
        issues.extend(
            convert_node_to_dict(node) for node in result.repository.issues.nodes
        )
    return issues


def show_report(*, issues):
    total_issues = len(issues)
    min_lead_time = datetime.max - datetime.min
    max_lead_time = timedelta(hours=0)
    total_lead_time = timedelta(hours=0)
    for issue in issues:
        if issue["is_closed"]:
            create_timestamp = datetime.strptime(
                issue["created_timestamp"], "%Y-%m-%dT%H:%M:%SZ",
            )
            close_timestamp = datetime.strptime(
                issue["closed_timestamp"], "%Y-%m-%dT%H:%M:%SZ",
            )
            lead_time = close_timestamp - create_timestamp
            total_lead_time += lead_time
            max_lead_time = max((max_lead_time, lead_time))
            min_lead_time = min((min_lead_time, lead_time))
    print("Average lead time:", total_lead_time / len(issues))
    print("Max Lead Time:", max_lead_time)
    print("Min Lead Time:", min_lead_time)


def load_auth():
    token_path = pathlib.Path("~/.gittoken").expanduser()
    name, token = token_path.read_text().strip().split()
    return (name, token)


def do_it():  # Shia LeBeouf!
    parser = make_parser()
    args = parser.parse_args()
    auth = load_auth()
    if args.action == "cache" or (args.action == "report" and args.refresh):
        issues = get_em_all(owner=args.owner, reponame=args.repo, auth=auth)
        cache_issues(owner=args.owner, reponame=args.repo, issues=issues)
    else:
        try:
            issues = load_issues(owner=args.owner, reponame=args.repo)
        except FileNotFoundError:
            exit("ERROR: Failed to find cached issues.json. Run `cache` first.")

    if args.action == "report":
        show_report(issues=issues)


if __name__ == "__main__":
    do_it()
