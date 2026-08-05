from email.message import EmailMessage
from pathlib import Path
import smtplib
from app.models.teams import Team
from app.core.settings import settings


def send_registration_email(team: Team):
    qr_path = Path(f"/app/data/qr/teams/{team.id}.png")

    if not qr_path.exists():
        raise FileNotFoundError("QR code not generated for this team")

    msg = EmailMessage()

    msg["Subject"] = "Registration Confirmed — Code Quest"
    msg["From"] = settings.SMTP_EMAIL
    msg["To"] = team.leader_email

    msg.set_content(
        f"Your registration for Code Quest has been confirmed. "
        f"Team: {team.team_name}"
        f"Leader: {team.leader_name}"
    )

    # HTML email
    msg.add_alternative(
        f"""
        <!DOCTYPE html>
        <html>
        <body style="
            margin: 0;
            padding: 30px;
            background: #f4f4f4;
            font-family: Arial, sans-serif;
        ">

            <div style="
                max-width: 600px;
                margin: auto;
                background: white;
                padding: 32px;
                border-radius: 12px;
            ">

                <h1 style="margin-bottom: 8px;">
                    Registration Confirmed
                </h1>

                <p style="font-size: 16px; line-height: 1.7; margin: 0 0 16px 0;">
                    Hey <strong>{team.leader_name}</strong>! 👋
                </p>

                <p style="font-size: 16px; line-height: 1.7; margin: 0 0 16px 0;">
                    Your team, <strong>{team.team_name}</strong>, is officially registered for
                    <strong>Code Quest 2026</strong>.
                </p>

                <p style="font-size: 16px; line-height: 1.7; margin: 0 0 24px 0;">
                    We're looking forward to having you and your team at the competition!
                </p>

                <div style="
                    background: #f7f7f7;
                    padding: 16px;
                    margin: 24px 0;
                    border-radius: 8px;
                ">
                    <strong>Team Details:</strong><br>
                    <strong>Team ID:</strong> {team.id}<br>
                    <strong>Team:</strong> {team.team_name}<br>
                    <br>
                    <strong>Event Details:</strong><br>
                    <strong>Date:</strong> August 7, 2026<br>
                    <strong>Venue:</strong> Saminar Hall <br>

                </div>

                <p>
                    Present this QR code at the event:
                </p>

                <div style="text-align:center; margin: 30px 0;">
                    <img
                        src="cid:team_qr"
                        width="220"
                        height="220"
                        alt="Team QR Code"
                    >
                </div>

                <p style="
                    color: #666;
                    font-size: 14px;
                ">
                    Keep this email accessible on the day of the event.
                </p>

            </div>

        </body>
        </html>
        """,
        subtype="html",
    )

    # Attach QR as inline image
    html_part = msg.get_payload()[-1]

    with open(qr_path, "rb") as f:
        html_part.add_related(
            f.read(),
            maintype="image",
            subtype="png",
            cid="<team_qr>",
        )

    with smtplib.SMTP_SSL(
        settings.SMTP_HOST,
        settings.SMTP_PORT,
    ) as smtp:
        print("Connected")
        smtp.login(
            settings.SMTP_EMAIL,
            settings.SMTP_PASSWORD,
        )
        print("logged in")
        result = smtp.send_message(msg)
        print("SMTP result:", result)
    print("Email accepted by SMTP server")