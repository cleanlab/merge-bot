import os
from typing import Any, Dict, List

import requests


REVIEW_APPROVED: str = "APPROVED"
GITHUB_TOKEN: str = os.getenv("GITHUB_TOKEN")


def get_requested_reviewers(repository: str, pull_request_number: str) -> List[str]:
    """Gets requested reviewers for PR.

    :param repository: repository to get PR from
    :param pull_request_number: PR to get requested reviewers for
    :return: list of logins of requested reviewers
    """
    gh_api_response: requests.Response = requests.get(
        f"https://api.github.com/repos/{repository}/pulls/{pull_request_number}/requested_reviewers",
        headers={
            "Authorization": f"Bearer {GITHUB_TOKEN}",
            "Accept": "application/vnd.github+json",
        }
    )

    assert gh_api_response.status_code == 200, "Bad response from GitHub requested reviewers API."
    
    response_dict: Dict[List[Dict]] = gh_api_response.json()

    return [
        reviewer.get("login")
        for reviewer in response_dict.get("users")
    ]


def get_reviewer_approvals(repository: str, pull_request_number: str) -> Dict[str, bool]:
    """Gets list of reviewer approvals for PR.

    :param repository: repository to get PR from
    :param pull_request_number: PR to get approvals from
    :return: dict of reviewer, reviewer approval statuses for PR
    """
    gh_api_response: requests.Response = requests.get(
        f"https://api.github.com/repos/{repository}/pulls/{pull_request_number}/reviews",
        headers={
            "Authorization": f"Bearer {GITHUB_TOKEN}",
            "Accept": "application/vnd.github+json",
        }
    )

    assert gh_api_response.status_code == 200, "Bad response from GitHub reviews API."
    
    response_list: List[Dict] = gh_api_response.json()

    # get latest review status from each reviewer
    # note: reviews are returned in chronological order
    reviews_by_reviewer: Dict[str, bool] = {}
    for review in response_list:
        approved: bool = review.get("state") == REVIEW_APPROVED
        reviewer: str = review.get("user").get("login")

        reviews_by_reviewer[reviewer] = approved

    # log all reviewers who haven't approved
    for reviewer, approval in reviews_by_reviewer.items():
        if not approval:
            print(f"Non-approving review by reviewer {reviewer}.")

    return reviews_by_reviewer

if __name__ == "__main__":

    import argparse

    parser: argparse.ArgumentParser = argparse.ArgumentParser(prog="Check reviewer approvals")
    parser.add_argument(
        "--repository",
        help="repository to find reviewer approvals for",
    )
    parser.add_argument(
        "--pull-request-number",
        dest="pull_request_number",
        help="number of pull request to get reviewers for",
    )

    args = parser.parse_args()

    # get requested reviewers
    requested_reviewers: List[str] = get_requested_reviewers(
        args.repository,
        args.pull_request_number,
    )

    # get reviewer approvals
    reviewer_approvals: Dict[str, bool] = get_reviewer_approvals(
        args.repository,
        args.pull_request_number,
    )

    # exit w/ non-zero code if not all requested reviewers have reviewed
    all_requested_reviewers_have_reviewed: bool = True
    for requested_reviewer in requested_reviewers:
        if not requested_reviewer in reviewer_approvals:
            print(f"Requested reviewer {requested_reviewer} has not reviewed.")
            all_requested_reviewers_have_reviewed = False

    if not all_requested_reviewers_have_reviewed:
        exit(1)

    # exit w/ non-zero code if not all reviewers approve
    if not all(reviewer_approvals):
        exit(0)
