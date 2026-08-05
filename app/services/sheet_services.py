from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from pathlib import Path
from app.schemas.teams import TeamImport
from app.core.settings import settings

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets.readonly"
]


SERVICE_ACCOUNT_FILE = (
    Path(__file__).resolve().parents[1]
    / "secrets"
    / "google-service-account.json"
)

def get_sheets_service():
    credentials = Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE,
        scopes=SCOPES,
    )

    return build(
        "sheets",
        "v4",
        credentials=credentials,
    )

def get_teams_registrations() -> list[TeamImport]:
    service =  get_sheets_service()

    sheet_id = settings.SHEET_ID
    
    sheet = service.spreadsheets().get(
        spreadsheetId= sheet_id
    ).execute()

    print("ACCESS SUCCESS")
    print("Sheet:", sheet["properties"]["title"])

    result = (
        service.spreadsheets()
        .values()
        .get(
            spreadsheetId=sheet_id,
            range="Sheet1!A:H",
        ).execute())

    rows = result.get("values", [])

    if len(rows) <= 1:
        return []

    headers = rows[0]

    print(50* "=", end="")
    print("Headers", end="")
    print(50* "=")
    print(headers)

    registrations: list[TeamImport] = []

    for row in rows[1:]:
        # Google may omit empty cells at the end
        row += [""] * (len(headers) - len(row))

        data = dict(zip(headers, row))

        registrations.append(
            TeamImport(
                created_at=data["Timestamp"].strip(),
                team_name=data["Team Name"].strip(),
                leader_name=data["Leader Name"].strip(),
                leader_email=data["E-mail"].strip().lower(),
                leader_phone=data["Contact Number"].strip(),
                semester=data["Semester"].strip(),
                course=data["Course"].strip().upper(),
            ))

    print(registrations)
    return registrations