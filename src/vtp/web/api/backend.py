"""
Backend support for the web-api.  One important aspect of this file is
to support web-api testing in the absense of a live ElectionData
deployment.  An ElectionData deployment is when a
setup-vtp-demo-operation operation has been run, nominally creating a
/opt/VoteTrackerPlus/demo.01 ElectionData folder and the required
subfolders.

With an ElectionData deployment the VTP git commands can be executed
and VoteTracker+ can function as designed.

Without an ElectionData deployment VTP git commands cannot be
executed.  Currently this state is configured by the _MOCK_MODE
variable below.  When set, and when this repo is part of the
VTP-dev-env parent repo (or when the VoteTrackerPlus and
VTP-mock-election.US.xx repos are simply sibling repos of this one),
the commands here do not call into the VoteTrackerPlus repo and
instead stub out the effective IO operations with static, non-varying
mock data.  That mock data is currently nominally stored in (checked
into) the VTP-mock-election.US.xx repo as the mock data is a direct
function of the live ElectionData election configuration and CVR data
found in that repo.  And that is due to two things: 1) the
VTP-mock-election.US.xx holds the configuration of an election such as
the blank ballot definition and 2) it also holds several hundred
pre-cast random ballots so to fill the ballot cache so that
ballot-checks can be immediately produced upon casting a ballot.

Regardless, for the time being the VTP-mock-election.US.xx also holds
checkedin mock values for the data that the web-api and above layers
need when running in mock mode.
"""

import csv
import json

from vtp.core.common import Common
from vtp.ops.accept_ballot_operation import AcceptBallotOperation
from vtp.ops.cast_ballot_operation import CastBallotOperation
from vtp.ops.setup_vtp_demo_operation import SetupVtpDemoOperation
from vtp.ops.tally_contests_operation import TallyContestsOperation
from vtp.ops.verify_ballot_receipt_operation import VerifyBallotReceiptOperation


class VtpBackend:
    """Class to keep the namespace separate"""

    ########
    # backend demo constants
    ########
    # set mock mode
    _MOCK_MODE = False
    # where the blank ballot is stored for the spring demo
    _MOCK_BLANK_BALLOT = "mock-data/blank-ballot.json"
    # where the cast-ballot.json file is stored for the spring demo
    _MOCK_CAST_BALLOT = "mock-data/cast-ballot.json"
    # where the ballot-check is stored for the spring demo
    _MOCK_BALLOT_CHECK = "mock-data/receipts.26.csv"
    _MOCK_VOTER_INDEX = 26
    # default guid - making one up
    _MOCK_GUID = "01d963fd74100ee3f36428740a8efd8afd781839"
    # default mock receipt log
    _MOCK_VERIFY_BALLOT_RECEIPT_LOG = "Hello World"
    # default mock tally log
    _MOCK_TALLY_CONTESTS_LOG = "Good Morning"
    # backend verbosity
    _VERBOSITY = 3
    # backend default address
    _ADDRESS = "123, Main Street, Concord, Massachusetts"

    @staticmethod
    def get_vote_store_id() -> str:
        """
        Endpoint #1: will return a vote_store_id, a.k.a. a guid
        """
        if VtpBackend._MOCK_MODE:
            # in mock mode there is no guid - make one up
            return VtpBackend._MOCK_GUID
        operation = SetupVtpDemoOperation(
            election_data_dir=Common.get_generic_ro_edf_dir(),
            verbosity=VtpBackend._VERBOSITY,
        )
        return operation.run(guid_client_store=True)

    @staticmethod
    def get_empty_ballot(vote_store_id: str) -> dict:
        """
        Endpoint #2: given an existing guid, will return the blank
        ballot
        """
        if VtpBackend._MOCK_MODE:
            # in mock mode there is no guid - make one up
            with open(VtpBackend._MOCK_BLANK_BALLOT, "r", encoding="utf8") as infile:
                json_doc = json.load(infile)
            #            import pdb; pdb.set_trace()
            return json_doc
        # Cet a (the) blank ballot from the backend
        operation = CastBallotOperation(
            election_data_dir=Common.get_guid_based_edf_dir(vote_store_id),
            verbosity=VtpBackend._VERBOSITY,
        )
        return operation.run(
            an_address = VtpBackend._ADDRESS,
            return_bb=True,
        )

    @staticmethod
    def get_all_guid_workspaces() -> list:
        """
        Will return a list of all the existing guid workspaces
        """
        return SetupVtpDemoOperation.get_all_guid_workspaces()

    @staticmethod
    def mock_get_cast_ballot() -> dict:
        """Mock only - return a static cast ballot"""
        with open(VtpBackend._MOCK_CAST_BALLOT, "r", encoding="utf8") as infile:
            json_doc = json.load(infile)
        return json_doc

    @staticmethod
    def mock_get_ballot_check() -> tuple[list, int]:
        """Mock only - return a static cast ballot"""
        with open(VtpBackend._MOCK_BALLOT_CHECK, "r", encoding="utf8") as infile:
            csv_doc = list(csv.reader(infile))
        return csv_doc, VtpBackend._MOCK_VOTER_INDEX

    @staticmethod
    def cast_ballot(vote_store_id: str, cast_ballot: dict) -> dict:
        """
        Endpoint #3: will cast (upload) a cast ballot and return the
        ballot-check and voter-index
        """
        if VtpBackend._MOCK_MODE:
            # Just return a mock ballot-check and voter-index
            return VtpBackend.mock_get_ballot_check()
        # handle the incoming ballot and return the ballot-check and voter-index
        operation = AcceptBallotOperation(
            election_data_dir=Common.get_guid_based_edf_dir(vote_store_id),
            verbosity=VtpBackend._VERBOSITY,
        )
        return operation.run(
            cast_ballot_json=cast_ballot,
            merge_contests=True,
        )

    @staticmethod
    def verify_ballot_check(
        vote_store_id: str,
        incoming_json: dict,
    ) -> str:
        """
        Endpoint #4: will verify a ballot-check and vote-inded, returning an
        undefined string at this time.
        """
        if VtpBackend._MOCK_MODE:
            # Just return a mock verify ballot string
            return VtpBackend._MOCK_VERIFY_BALLOT_RECEIPT_LOG
        # handle the incoming ballot and return the ballot-check and voter-index
        operation = VerifyBallotReceiptOperation(
            election_data_dir=Common.get_guid_based_edf_dir(vote_store_id),
        )
        return operation.run(
            receipt_data=incoming_json["ballot-check"],
            row=incoming_json["vote-index"],
            cvr=True,
        )

    @staticmethod
    def tally_election_check(
        vote_store_id: str,
        incoming_json: dict,
    ) -> str:
        """
        Endpoint #5: will verify a ballot-check and vote-inded,
        returning an undefined string at this time.
        """
        if VtpBackend._MOCK_MODE:
            # Just return a mock tally string
            return VtpBackend._MOCK_TALLY_CONTESTS_LOG
        # handle the incoming ballot and return the ballot-check and voter-index
        operation = TallyContestsOperation(
            election_data_dir=Common.get_guid_based_edf_dir(vote_store_id),
            verbosity=incoming_json["verbosity"],
        )
        return operation.run(
            contest_uid=incoming_json["contest-uids"],
            track_contests=incoming_json["track-contests"],
        )